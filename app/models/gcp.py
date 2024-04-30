""" GCP module. """
import os
import sys
from google.cloud import storage
path_absolute = os.path.abspath("app/models/credentials.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=path_absolute


def download_blob(bucket_name, blob_name, destination_file_name):
    """ Downloads a blob from the bucket. """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(destination_file_name)
    print(f'-> Downloaded storage object {blob_name} from bucket {bucket_name}')

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """ Uploads a file to the bucket. """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)

        print(f'\n-> Updaload storage object {blob.name} to bucket {bucket_name} to {destination_blob_name}')

    except Exception as e:
        print(f'Error uploading file: {str(e)}')
        sys.exit(1)