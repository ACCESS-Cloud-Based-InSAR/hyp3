import connexion
import boto3

connexion_app = connexion.App(__name__)
BATCH_CLIENT = boto3.client('batch')

from hyp3_api import definitions