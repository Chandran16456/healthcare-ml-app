import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "db", "healthcare_ml.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

query = """
DROP TABLE IF EXISTS kidney_labels;
CREATE TABLE kidney_labels AS
SELECT 
    PATIENT,
    1 AS has_kidney_disease
FROM conditions
WHERE LOWER(DESCRIPTION) LIKE '%kidney%'
   OR LOWER(DESCRIPTION) LIKE '%renal%';

DROP TABLE IF EXISTS kidney_dataset;
CREATE TABLE kidney_dataset AS
SELECT 
    p.*,
    COALESCE(k.has_kidney_disease, 0) AS has_kidney_disease
FROM patients_clean p
LEFT JOIN kidney_labels k
ON p.Id = k.PATIENT;

DROP TABLE IF EXISTS final_kidney_dataset;
CREATE TABLE final_kidney_dataset AS
SELECT 
    k.*,
    o.glucose,
    o.bmi,
    o.systolic_bp,
    o.diastolic_bp,
    o.hba1c
FROM kidney_dataset k
LEFT JOIN observations_features o
ON k.Id = o.Id;
"""

cursor.executescript(query)

conn.commit()
conn.close()

print("Heart dataset pipeline created successfully!")
