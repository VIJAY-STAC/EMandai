import uuid
from django.db import models
from django.conf import settings
import boto3
import base64
from botocore.exceptions import ClientError
from .models import File, Products, Category

class S3Client(object):
    def __init__(
        self,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        bucket_name=settings.AWS_STORAGE_BUCKET_NAME,
    ):
        session = boto3.Session(aws_access_key_id, aws_secret_access_key)
        s3 = session.resource("s3")
        self.bucket = s3.Bucket(bucket_name)

    def upload_file(self, file, key):
        decoded_file = base64.b64decode(file)
        try:
            s3_object = self.bucket.put_object(
                Key=key, Body=decoded_file, ACL="public-read"
            )
        except ClientError as error:
            return "error : %s" % error, False

        return None, True

    def delete_file(self, key):
        try:
            s3_object = self.bucket.delete_objects(Delete={"Objects": [{"Key": key}]})
        except ClientError as error:
            return "error : %s" % error, False

        return None, True


S3_PATH_URL = "https://{bucket}.s3.ap-south-1.amazonaws.com/{key}"

def product_image_upload(
    product_id, base64_file, key, file_name, file_type, file_size
):
    s3client = S3Client()
    uploaded_file, success = s3client.upload_file(file=base64_file, key=str(key))

    if not success:
        upload_url = ""

    upload_url = S3_PATH_URL.format(
        key=key, bucket=settings.AWS_STORAGE_BUCKET_NAME
    )

    file = File.objects.create(
        name=file_name, key=key, url=upload_url, size=file_size, file_type=file_type
    )

    pro=Products.objects.get(id=product_id)

    file.product_images.add(pro)

    return file.id


def category_image_upload(
    cat_id, base64_file, key, file_name, file_type, file_size
):
    s3client = S3Client()
    uploaded_file, success = s3client.upload_file(file=base64_file, key=str(key))

    print("*****",success)

    if not success:
        upload_url = ""

    upload_url = S3_PATH_URL.format(
        key=key, bucket=settings.AWS_STORAGE_BUCKET_NAME
    )

    file = File.objects.create(
        name=file_name, key=key, url=upload_url, size=file_size, file_type=file_type
    )

    cat=Category.objects.get(id=cat_id)

    file.cat_images.add(cat)

    return file.id