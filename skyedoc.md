EventData
- 32 rows
- linking key is `event_code`
Specimen Data
- 1,105 rows
- each specimen has a `lot_id`
- each specimen links to an `event_code`
DNAExtractions
- 781 rows
- each has an `extraction_id`
- each links to a `lot_id`
Genomic Libraries
- 10 rows
- each references an `extraction_id`

Event->Specimen->Extraction->Library

SQLite stores entire database as a single `.db` file

1. Load and clean CSVs with pandas
2. Create database with proper links
3. Load all 4 Panama datasets
4. Test queries

[DB Browser for SQLite](https://sqlitebrowser.org) -- possible early-stage GUI

>**Inspect all data before touching it!**

**Schema are the rules the db enforces**
PRIMARY KEY: every row has a unique identifier
FOREIGN KEY: a column in one table must match a valid value in another table
Data types: TEXT, INTEGER, REAL, etc

**Querying**
WHERE: filter by a condition
JOIN ... ON: combine information across tables by matching shared ID columns
GROUP BY with COUNT(*): lets you ask aggregate questions e.g. "how many specimens per species?"
LIKE 'USNM%': pattern match, where % means "anything after this"