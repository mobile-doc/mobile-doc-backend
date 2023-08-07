from pydantic import BaseModel, constr
from typing import Optional, List
from google.cloud import bigquery
import os

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "/home/mmk/4_1_codes/mobile-doc-backend/pub-sub-to-BigQuery/mobile-doc-backend-analytics-sa.json"


PROJECT_NAME = "mobile-doc-backend"
DATASET_NAME = "analytics"
table_name = "prescription"
table_id = f"{PROJECT_NAME}.{DATASET_NAME}.{table_name}"


class Prescription(BaseModel):
    age: int
    gender: constr(regex="M|F|O")
    physical_attributes: Optional[List[str]]
    symptoms: List[str]
    diagnosis: str
    suggested_tests: Optional[List[str]]
    suggested_medicine: Optional[List[str]]
    advice: Optional[List[str]]


# Define the schema fields for the Prescription class
schema = [
    bigquery.SchemaField("age", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("gender", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("physical_attributes", "STRING", mode="REPEATED"),
    bigquery.SchemaField("symptoms", "STRING", mode="REPEATED"),
    bigquery.SchemaField("diagnosis", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("suggested_tests", "STRING", mode="REPEATED"),
    bigquery.SchemaField("suggested_medicine", "STRING", mode="REPEATED"),
    bigquery.SchemaField("advice", "STRING", mode="REPEATED"),
]


# Construct a BigQuery client object.
client = bigquery.Client()

print(f"deleting current {table_id=}")
client.delete_table(table_id, not_found_ok=True)
print(f"Table is deleted")

table = bigquery.Table(table_id, schema=schema)
table = client.create_table(table)  # Make an API request.
print("Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))
