from google.cloud import bigquery
import os

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "/home/mmk/4_1_codes/mobile-doc-backend/pub-sub-to-BigQuery/mobile-doc-backend-analytics-sa.json"

PROJECT_NAME = "mobile-doc-backend"
DATASET_NAME = "analytics"
table_name = "prescription"
table_id = f"{PROJECT_NAME}.{DATASET_NAME}.{table_name}"

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

sample_prescription = [
    {
        "age": 35,
        "gender": "M",
        "symptoms": ["Fever", "Cough", "Headache"],
        "diagnosis": "Common cold",
        "suggested_tests": ["CBC", "Throat swab"],
        "suggested_medicine": ["Acetaminophen", "Cough syrup"],
        "advice": ["Get plenty of rest", "Stay hydrated"],
    },
    {
        "age": 42,
        "gender": "F",
        "symptoms": ["Fatigue", "Joint pain", "Fever"],
        "diagnosis": "Viral infection",
        "suggested_tests": ["Complete blood count", "PCR test"],
        "suggested_medicine": ["Ibuprofen", "Antiviral medication"],
        "advice": ["Avoid contact with others", "Take the prescribed medication"],
    },
    {
        "age": 55,
        "gender": "O",
        "symptoms": ["Shortness of breath", "Chest pain"],
        "diagnosis": "Pneumonia",
        "suggested_tests": ["Chest X-ray", "Blood gases"],
        "suggested_medicine": ["Antibiotics", "Bronchodilators"],
        "advice": ["Follow the prescribed treatment", "Avoid smoking"],
    },
    {
        "age": 28,
        "gender": "F",
        "symptoms": ["Nausea", "Vomiting", "Abdominal pain"],
        "diagnosis": "Gastroenteritis",
        "suggested_tests": ["Stool culture", "Electrolyte panel"],
        "suggested_medicine": ["Anti-emetic", "Oral rehydration solution"],
        "advice": ["Stay hydrated", "Consume light and bland foods"],
    },
    {
        "age": 50,
        "gender": "M",
        "symptoms": ["Dizziness", "Tinnitus", "Hearing loss"],
        "diagnosis": "Vertigo",
        "suggested_tests": ["Audiometry", "VNG test"],
        "suggested_medicine": ["Antihistamines", "Vestibular suppressants"],
        "advice": ["Avoid sudden head movements", "Consult with an ENT specialist"],
    },
]

client = bigquery.Client()

table = client.get_table(table_id)  # API request


### Converts schema dictionary to BigQuery's expected format for job_config.schema

### Define schema as on BigQuery table, i.e. the fields id, first_name and last_name


job_config = bigquery.LoadJobConfig(
    schema=schema,
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
)


# job_config = bigquery.LoadJobConfig()
# job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
job = client.load_table_from_json(sample_prescription, table, job_config=job_config)

print(job.result())
