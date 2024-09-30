import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import csv
import io
import os
import json

app = func.FunctionApp()

@app.function_name(name="IoTHubToBlobFunction")
@app.event_hub_message_trigger(arg_name="event",
                               event_hub_name=os.getenv("EVENTHUB_NAME"),
                               connection=os.getenv("CONNECTION_STRING"),
                               consumer_group="$Default")
def main(event: func.EventHubEvent):
    logging.info('Received event from IoT Hub')

    # イベントデータをJSON形式で取得
    event_data = event.get_body().decode('utf-8')

    # CSVに変換するために一旦メモリ上にファイルを作成
    output = io.StringIO()
    csv_writer = csv.writer(output)

    # JSONのキーに基づいてヘッダとデータを書き込む
    try:
        json_data = json.loads(event_data)
        header = json_data.keys()
        csv_writer.writerow(header)
        csv_writer.writerow(json_data.values())
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON data: {str(e)}")
        return


    # Blob Storageへの接続設定
    connection_string = os.getenv("AzureWebJobsStorage")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_name = os.getenv("AzureContainerName")
    blob_name = f"event-data-{event.sequence_number}.csv"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    try:
        # メモリ上のCSVデータをBlobにアップロード
        blob_client.upload_blob(output.getvalue(), overwrite=True)
        logging.info(f"Data saved to Blob Storage in CSV format: {blob_name}")
    except Exception as e:
        logging.error(f"Failed to upload data to Blob Storage: {str(e)}")
