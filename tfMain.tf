terraform {
  required_version = ">= 1.6.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.42.0"
    }
  }

  backend "s3" {
    bucket = "353818015911-remotestate"
    key    = "prj-glueColeraAPI/terraform.tfstate"
    region = "us-east-1"
  }
}
