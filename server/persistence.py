import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.cosmos import exceptions, CosmosClient, PartitionKey
import logging

def bootstrap_persistence():
    blob_connection_str = os.environ["BLOB_CONNECTION"]
    blob_container = os.environ.get("BLOB_CONTAINER", "requests-v1")
    blob_service_client = BlobServiceClient.from_connection_string(blob_connection_str)

    cosmo_endpoint = os.environ["COSMO_ENDPOINT"]
    cosmo_key = os.environ["COSMO_KEY"]
    cosmo_db = os.environ.get("COSMO_DB", "default")
    cosmo_container = os.environ.get("COSMO_CONTAINER", "requests-v1")
    cosmo_client = CosmosClient(cosmo_endpoint, cosmo_key)
    cosmo_db_client = cosmo_client.create_database_if_not_exists(id=cosmo_db)
    cosmo_container_client = cosmo_db_client.create_container_if_not_exists(
        id=cosmo_container, 
        partition_key=PartitionKey(path="/id"),
        offer_throughput=400
    )

    return PersistenceFacade(blob_service_client, blob_container, cosmo_container_client)

class PersistenceFacade:
    def __init__(
        self,
        blob_service_client: BlobServiceClient,
        blob_container: str,
        cosmo_container_client,
    ):
        self.__blob_service_client = blob_service_client
        self.__blob_container = blob_container
        self.__cosmo_container_client = cosmo_container_client
            
    def _upload_raw_input(self, request_id: str, local_path: str):
        logging.debug("uploading raw input")
        blob_name = f"{request_id}.raw.ogg"
        blob_client = self.__blob_service_client.get_blob_client(container=self.__blob_container, blob=blob_name)

        with open(local_path, "rb") as data:
            blob_client.upload_blob(data)

        logging.debug("raw input uploaded successfuly")

    def _append_request_record(self, request_id, request_body: dict, work_unit, work_result: dict, received_on: float):
        logging.debug("appending request record")

        document = dict(
            id=str(request_id),
            receivedOn=received_on,
            userData=request_body.get("userData", {}),
            results=work_result,
            params=dict(
                cleansing=work_unit.cleansing_params._asdict(),
                segmentation=work_unit.segmentation_params._asdict(),
                mel_spec=work_unit.mel_spec_params._asdict(),
                color_spec=work_unit.color_spec_params._asdict(),
            ),
        )
        
        self.__cosmo_container_client.create_item(body=document)
        logging.debug("request record appended successfuly")

    def track_request_sample(self, request_id, request_body, work_unit, work_result, received_on):
        self._upload_raw_input(request_id, work_unit.source_file)
        self._append_request_record(request_id, request_body, work_unit, work_result, received_on)
