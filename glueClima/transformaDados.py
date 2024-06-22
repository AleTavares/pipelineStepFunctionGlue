import sys
from pyspark.context import SparkContext 
from awsglue.context import GlueContext
import json
from awsglue.utils import getResolvedOptions
from datetime import datetime, timedelta
from lib.tradutor import tradutor
import pandas as pd
from deltalake import DeltaTable, write_deltalake
import boto3
import logging
from pyspark.conf import SparkConf
from pyspark.sql.types import StructField, StructType, StringType, DateType, DecimalType
from pyspark.sql.functions import *
from pyspark.sql.functions import from_utc_timestamp, from_unixtime
from pyspark.sql import Row

conf = SparkConf()
logger   = logging.getLogger() 
logger.setLevel("INFO")

argsGlue = getResolvedOptions(
    sys.argv, [
        'key',
        'bucketDataLakeStaging',
        'bucketDataLakeSilver',
        'pastaArqs',
        'bucketDataLakeBronze'
    ]
)
warehouse_path = f"s3://{argsGlue['bucketDataLakeSilver']}"

conf.set("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions,org.apache.iceberg:iceberg-aws-bundle:1.5.2")\
        .set("spark.sql.defaultCatalog", "glue_catalog")\
        .set("spark.sql.catalog.glue_catalog.warehouse", warehouse_path)\
        .set("spark.sql.catalog.my_catalog.type", 'glue')\
        .set("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog")\
        .set("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog")\
        .set("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO")\

sc = SparkContext(conf=conf)
glueContext = GlueContext(sc)
spark= glueContext.spark_session


s3_resource = boto3.resource(
    's3',
)
for item in s3_resource.Bucket(argsGlue['bucketDataLakeStaging']).objects.filter(Prefix = f"{argsGlue['pastaArqs']}/"):
    s3_object_type = item.key.split('/')[-1].split('.')[-1]
    print(item.key)
    if s3_object_type == "json":
        def tradusTexto(texto):
            return tradutor(texto, argsGlue['key'])
        traduz_udf = udf(tradusTexto)

        logger.error(f"Lendo os dados do bucket {argsGlue['bucketDataLakeStaging']} e pasta {item.key}.")
        df = spark.read.option("multiLine", "true").json(f"s3://{argsGlue['bucketDataLakeStaging']}/{item.key}")
        df = df.withColumn("data_hora", to_timestamp(df["dt"]).cast('timestamp'))
        df = df.withColumn("temperatura", round(df['main']['temp'] - 273.15, 2).cast(DecimalType()))
        df = df.withColumn("temperatura_max", round(df['main']['temp_max'] - 273.15, 2).cast(DecimalType()))
        df = df.withColumn("temperatura_min", round(df['main']['temp_min'] - 273.15, 2).cast(DecimalType()))
        df = df.withColumn("clima", traduz_udf(df['weather'][0]['description']))
        df = df.withColumn("pais", df['sys']['country'])
        df = df.withColumn("cidade", df['name'])
        columns_to_drop = ['coord', 'weather', 'base', 'main', 'visibility', 'wind', 'clouds', 'dt', 'sys', 'timezone', 'id', 'name', 'cod' ]
        dfNew = df.drop(*columns_to_drop)
        
        try:
            dfNew.writeTo("glue_catalog.silver.clima") \
            .tableProperty("format-version", "2") \
            .append()
        except:
            dfNew.writeTo("glue_catalog.silver.clima") \
            .tableProperty("format-version", "2") \
            .create()
        # client = boto3.client('s3')
        s3_resource.Object(argsGlue['bucketDataLakeBronze'], f"{argsGlue['pastaArqs']}/{item.key}").copy_from(CopySource=f"{argsGlue['bucketDataLakeStaging']}/{item.key}")
        s3_resource.Object(argsGlue['bucketDataLakeStaging'], item.key).delete()

