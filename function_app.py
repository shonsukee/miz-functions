import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import csv
import io
import os
import json
from datetime import datetime

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

        if isinstance(json_data, list) and len(json_data) > 0:
            machine_id = json_data[0].get("machineID", "unknown")
            timestamp = json_data[0].get("timestamp", "unknown").replace(":", "-")

            # machineIDを削除
            for data_point in json_data:
                data_point.pop("machineID", None)

            # 各データポイントをCSVとして書き込む
            header = json_data[0].keys()
            csv_writer.writerow(header)

            for data_point in json_data:
                csv_writer.writerow(data_point.values())
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON data: {str(e)}")
        return
    finally:
        # メモリを解放
        output.seek(0)

    # 現在のUTC日付
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    day = current_date.day

    # Blob Storageへの接続設定
    connection_string = os.getenv("AzureWebJobsStorage")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_name = f"miz-container"
    blob_name = f"{year}/{month:02d}/{day:02d}/machine-{machine_id.lower()}-data/{machine_id}_{timestamp}.csv"

    try:
        # コンテナが存在しない場合は作成
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # メモリ上のCSVデータをBlobにアップロード
        blob_client.upload_blob(output.getvalue(), overwrite=True)
        logging.info(f"Data saved to Blob Storage in CSV format: {blob_name}")
    except Exception as e:
        logging.error(f"Failed to upload data to Blob Storage: {str(e)}")
    finally:
        output.close()
