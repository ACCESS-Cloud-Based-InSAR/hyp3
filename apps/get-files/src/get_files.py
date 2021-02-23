from datetime import datetime
from os import environ
from os.path import basename

import boto3

S3_CLIENT = boto3.client('s3')


def get_download_url(bucket, key):
    region = environ['AWS_REGION']
    return f'https://{bucket}.s3.{region}.amazonaws.com/{key}'


def get_expiration_time(bucket, key):
    s3_object = S3_CLIENT.get_object(Bucket=bucket, Key=key)
    expiration_string = s3_object['Expiration'].split('"')[1]
    expiration_datetime = datetime.strptime(expiration_string, '%a, %d %b %Y %H:%M:%S %Z')
    return expiration_datetime.isoformat(timespec='seconds') + '+00:00'


def get_object_file_type(bucket, key):
    response = S3_CLIENT.get_object_tagging(Bucket=bucket, Key=key)
    for tag in response['TagSet']:
        if tag['Key'] == 'file_type':
            return tag['Value']
    return None


def get_products(files):
    return [{
        'url': item['download_url'],
        'size': item['size'],
        'filename': item['filename'],
        's3': item['s3'],
    } for item in files if item['file_type'] == 'product']


def get_file_urls_by_type(files_list, type):
    files = [item for item in files_list if type in item['file_type']]
    sorted_files = sorted(files, key=lambda x: x['file_type'])
    urls = [item['download_url'] for item in sorted_files]
    return urls


def organize_files(files_dict, bucket):
    all_files = []
    expiration = None
    for item in files_dict:
        download_url = get_download_url(bucket, item['Key'])
        file_type = get_object_file_type(bucket, item['Key'])
        all_files.append({
            'download_url': download_url,
            'file_type': file_type,
            'size': item['Size'],
            'filename': basename(item['Key']),
            's3': {
                'bucket': bucket,
                'key': item['Key'],
            },
        })
        if file_type == 'log':
            expiration = get_expiration_time(bucket, item['Key'])

    return {
        'files': get_products(all_files),
        'browse_images': get_file_urls_by_type(all_files, 'browse'),
        'thumbnail_images': get_file_urls_by_type(all_files, 'thumbnail'),
        'logs': get_file_urls_by_type(all_files, 'log'),
        'expiration_time': expiration
    }


def lambda_handler(event, context):
    bucket = environ['BUCKET']

    response = S3_CLIENT.list_objects_v2(Bucket=bucket, Prefix=event['job_id'])
    return organize_files(response['Contents'], bucket)
