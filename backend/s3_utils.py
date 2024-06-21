import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os

BUCKET_NAME = 'lista5filesmanager'  # Replace with your bucket name
AWS_REGION = 'us-east-1'  # Replace with your AWS region

def create_s3_client():
    return boto3.client('s3', region_name=AWS_REGION)

def create_bucket_if_not_exists(bucket_name):
    s3 = create_s3_client()
    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # If a client error is thrown, then the bucket does not exist
            try:
                s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={
                    'LocationConstraint': AWS_REGION})
            except ClientError as e:
                raise Exception(f"Could not create bucket: {e}")
        elif error_code == '403':
            raise Exception(f"Access to the bucket {bucket_name} is forbidden. Check your permissions.")
        else:
            raise Exception(f"Unexpected error: {e}")

def upload_file_to_s3(file_name, bucket_name, object_name=None):
    s3 = create_s3_client()
    if object_name is None:
        object_name = os.path.basename(file_name)
    try:
        s3.upload_file(file_name, bucket_name, object_name)
        return f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
    except NoCredentialsError:
        raise Exception("Credentials not available")
    except ClientError as e:
        raise Exception(f"Error uploading file: {e}")

def list_files_in_s3(bucket_name):
    s3 = create_s3_client()
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        return [{'name': item['Key'], 'url': f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{item['Key']}"} for item in response.get('Contents', [])]
    except ClientError as e:
        raise Exception(f"Error listing files: {e}")

def generate_presigned_url(bucket_name, object_name, expiration=3600):
    s3 = create_s3_client()
    try:
        response = s3.generate_presigned_url('get_object',
                                             Params={'Bucket': bucket_name, 'Key': object_name},
                                             ExpiresIn=expiration)
    except ClientError as e:
        raise Exception(f"Error generating presigned URL: {e}")
    return response

def rename_file_in_s3(bucket_name, old_object_name, new_object_name):
    s3 = create_s3_client()
    try:
        # Copy the object to a new key
        s3.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': old_object_name}, Key=new_object_name)
        # Delete the old object
        s3.delete_object(Bucket=bucket_name, Key=old_object_name)
        return f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{new_object_name}"
    except ClientError as e:
        raise Exception(f"Error renaming file: {e}")
