""" GCP module. """
import os
import sys
from google.cloud import storage
from google.cloud import pubsub_v1
import json

path_absolute = os.path.abspath("app/models/credentials.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=path_absolute
project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'desarrollo-de-sw-en-la-nube-04')


def blob_exists(bucket_name, blob_name):
   """ Check if a blob exists in the bucket. """
   client = storage.Client()
   bucket = client.get_bucket(bucket_name)
   blob = bucket.blob(blob_name)
   return blob.exists()


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


def pub_message(task_id, gcp_bucket, gcp_path):
    """ Publishes a message to a Pub/Sub topic. """
    topic = 'desarrollo-de-software-en-la-nube'
    topic_name = f'projects/{project_id}/topics/{topic}'
  

    publisher = pubsub_v1.PublisherClient()
    topic_name = f'projects/{project_id}/topics/{topic}'
    # publisher.create_topic(name=topic_name)
    data = {
        "task_id": str(task_id),
        "gcp_bucket": str(gcp_bucket),
        "gcp_path": str(gcp_path)
    }
    data = json.dumps(data).encode("utf-8")
    future = publisher.publish(topic_name, data, spam='backend-video')
    future.result()

    print(f'Message published on with ID {future.result()}')




# service_account_info = json.load(open("service-account-info.json"))
# audience = "https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"

# credentials = jwt.Credentials.from_service_account_info(
#     service_account_info, audience=audience
# )

# subscriber = pubsub_v1.SubscriberClient(credentials=credentials)

# # The same for the publisher, except that the "audience" claim needs to be adjusted
# publisher_audience = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"
# credentials_pub = credentials.with_claims(audience=publisher_audience)
# publisher = pubsub_v1.PublisherClient(credentials=credentials_pub)
