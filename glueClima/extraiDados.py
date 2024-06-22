import requests
import json
from datetime import datetime
from awsglue.utils import getResolvedOptions
import sys
import boto3

argsGlue = getResolvedOptions(
    sys.argv, [
        'bucketDataLakeStaging',
        'pastaArqs',
        'api_key',
        'cidade'
    ]
)

URL_BASE = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = argsGlue['api_key']
CIDADE = "cidade" #"Atibaia"

url = f"{URL_BASE}q={CIDADE}&appid={API_KEY}"
response = requests.get(url).json()
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
s3 = boto3.resource('s3')
object = s3.Object(
    bucket_name=argsGlue['bucketDataLakeStaging'], 
    key=f"{argsGlue['pastaArqs']}/dadosClima{timestamp}.json"
)

object.put(Body=json.dumps(response))

# with open(f"s3://{argsGlue['bucketDataLakeStaging']}/{argsGlue['pastaArqs']}/dadosClima{timestamp}.json", "w") as arquivo:
#     arquivo.write(json.dumps(response))
