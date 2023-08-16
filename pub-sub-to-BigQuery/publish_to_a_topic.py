# https://youtu.be/TqvPEf5iJ2o

# schema = [
#     bigquery.SchemaField("age", "INTEGER", mode="REQUIRED"),
#     bigquery.SchemaField("gender", "STRING", mode="REQUIRED"),
#     bigquery.SchemaField("physical_attributes", "STRING", mode="REPEATED"),
#     bigquery.SchemaField("symptoms", "STRING", mode="REPEATED"),
#     bigquery.SchemaField("diagnosis", "STRING", mode="REQUIRED"),
#     bigquery.SchemaField("suggested_tests", "STRING", mode="REPEATED"),
#     bigquery.SchemaField("suggested_medicine", "STRING", mode="REPEATED"),
#     bigquery.SchemaField("advice", "STRING", mode="REPEATED"),
# ]

sample_data = {
        "age": 65,
        "gender": "F",
        "symptoms": ["Fatigue", "Shortness of breath", "Swollen ankles"],
        "diagnosis": "Congestive heart failure",
        "suggested_tests": ["Echocardiogram", "B-type natriuretic peptide (BNP) test"],
        "suggested_medicine": ["Diuretics", "ACE inhibitors"],
        "advice": ["Limit salt intake", "Monitor weight daily"],
        "random_field" : "Test value",
    }

from google.cloud import pubsub_v1
import json
import os

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "/home/mmk/4_1_codes/mobile-doc-backend/pub-sub-to-BigQuery/mobile-doc-backend-analytics-sa.json"


publisher = pubsub_v1.PublisherClient()
topic_path = "projects/mobile-doc-backend/topics/pub_sub_bq_prescription"

# Data must be a bytestring
data = json.dumps(sample_data).encode("utf-8")

# Publish the message
future = publisher.publish(topic_path, data)
message_id = future.result()

print(f"Published message {message_id} to topic")
