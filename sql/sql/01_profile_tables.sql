SELECT 'patients' AS table_name, COUNT(*) AS row_count FROM patients
UNION ALL
SELECT 'encounters', COUNT(*) FROM encounters
UNION ALL
SELECT 'conditions', COUNT(*) FROM conditions
UNION ALL
SELECT 'observations', COUNT(*) FROM observations
UNION ALL
SELECT 'medications', COUNT(*) FROM medications;
