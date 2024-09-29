from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import uuid
import logging
import os

account_url = "https://"+os.getenv("AzureBlobStorageName")+".blob.core.windows.net"
try:
    default_credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(account_url, credential=default_credential)
except Exception as e:
    logging.error(f"Failed to authenticate: {e}")
    raise

# コンテナの作成
container_name = str(uuid.uuid4())
container_client = blob_service_client.create_container(container_name)

# コンテナにBlobをアップロードする
local_path = "./data"
if not os.path.exists(local_path):
    os.mkdir(local_path)

# Create a file in the local data directory to upload and download
local_file_name = str(uuid.uuid4()) + ".txt"
upload_file_path = os.path.join(local_path, local_file_name)

# Write text to the file
with open(upload_file_path, mode='w') as file:
    file.write("Hello, World!")

# Create a blob client using the local file name as the name for the blob
blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

logging.basicConfig(filename='./data/log.log', level=logging.DEBUG)


# Upload the created file
with open(file=upload_file_path, mode="rb") as data:
    blob_client.upload_blob(data)

# コンテナ内のBlobを一覧表示
print("\nListing blobs...")

# List the blobs in the container
blob_list = container_client.list_blobs()
for blob in blob_list:
    print("\t" + blob.name)

# Blobをダウンロード
# Add 'DOWNLOAD' before the .txt extension so you can see both files in the data directory
download_file_path = os.path.join(local_path, str.replace(local_file_name ,'.txt', 'DOWNLOAD.txt'))
container_client = blob_service_client.get_container_client(container= container_name) 
print("\nDownloading blob to \n\t" + download_file_path)

try:
    with open(file=download_file_path, mode="wb") as download_file:
        download_file.write(container_client.download_blob(blob.name).readall())
except Exception as e:
    logging.error(f"Failed to download blob: {e}")
    raise

# コンテナの削除
print("\nPress the Enter key to begin clean up")
input()

print("Deleting blob container...")
container_client.delete_container()

print("Deleting the local source and downloaded files...")
os.remove(upload_file_path)
os.remove(download_file_path)
os.rmdir(local_path)

print("Done")