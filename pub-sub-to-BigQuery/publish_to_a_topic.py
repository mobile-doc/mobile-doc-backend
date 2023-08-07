# https://youtu.be/TqvPEf5iJ2o
sample_prescription = [
    {
        "age": 65,
        "gender": "F",
        "symptoms": ["Fatigue", "Shortness of breath", "Swollen ankles"],
        "diagnosis": "Congestive heart failure",
        "suggested_tests": ["Echocardiogram", "B-type natriuretic peptide (BNP) test"],
        "suggested_medicine": ["Diuretics", "ACE inhibitors"],
        "advice": ["Limit salt intake", "Monitor weight daily"],
    },
    {
        "age": 22,
        "gender": "F",
        "symptoms": ["Rash", "Itching", "Redness"],
        "diagnosis": "Allergic reaction",
        "suggested_tests": ["Allergy skin tests"],
        "suggested_medicine": ["Antihistamines", "Topical corticosteroids"],
        "advice": ["Avoid known allergens", "Keep the affected area clean"],
    },
    {
        "age": 22,
        "gender": "F",
        "symptoms": ["Rash", "Itching", "Redness"],
        "diagnosis": "Allergic reaction",
        "suggested_tests": ["Allergy skin tests"],
        "suggested_medicine": ["Antihistamines", "Topical corticosteroids"],
        "advice": ["Avoid known allergens", "Keep the affected area clean"],
    },
    {
        "age": 38,
        "gender": "M",
        "symptoms": ["Severe headache", "Nausea", "Blurred vision"],
        "diagnosis": "Migraine",
        "suggested_tests": ["None"],
        "suggested_medicine": ["Triptans", "NSAIDs"],
        "advice": ["Find and avoid triggers", "Rest in a dark and quiet room"],
    },
    {
        "age": 30,
        "gender": "O",
        "symptoms": ["Chest pain", "Shortness of breath", "Irregular heartbeat"],
        "diagnosis": "Arrhythmia",
        "suggested_tests": ["Electrocardiogram (ECG)", "Holter monitor"],
        "suggested_medicine": ["Beta-blockers", "Calcium channel blockers"],
        "advice": ["Avoid caffeine and alcohol", "Follow up with a cardiologist"],
    },
]


from google.cloud import pubsub_v1
import json
import os

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "/home/mmk/4_1_codes/mobile-doc-backend/pub-sub-to-BigQuery/mobile-doc-backend-analytics-sa.json"


publisher = pubsub_v1.PublisherClient()
topic_path = "projects/mobile-doc-backend/topics/pub_sub_bq_prescription"

# Data must be a bytestring
data = json.dumps(sample_prescription[1]).encode("utf-8")

# Publish the message
future = publisher.publish(topic_path, data)
message_id = future.result()

print(f"Published message {message_id} to topic")
