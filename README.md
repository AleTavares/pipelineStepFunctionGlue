# Pipe Line de Dados
## Cloudwatch Event Rule -> Stepfunction -> Glue

Este projeto tem como objetivo desenvolver um pipeline de ETL (Extração, Transformação 
e Carga) utilizando o Cloudwatch Event Rule para fazer o agendamento de Execução, Step Function para orquestrar a execução e o GLue para processar os dados. 
A solução envolve a captura de dados via API, processamento e transformação 
dos dados conforme necessário e finalmente a carga dos dados transformados em um bucket S3 para armazenamento.

Tudo isso comtruido com IaC utilizando o Terraform.

## Prerquisitos
Para este projeto precisaremos de alguns pontos:
- [Terraform Intalado](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- [Chave da API de Clima para extração dos Dados](https://openweathermap.org/price)
- [Chave da API de Tradução de Texto do Azurem para enriquecimento de dados](https://learn.microsoft.com/pt-br/azure/ai-services/translator/reference/rest-api-guide)

## Arquitetura
