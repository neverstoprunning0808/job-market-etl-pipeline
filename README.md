# Job Market ETL Pipeline

## 1. Overview

This project implements an automated **ETL (Extract, Transform, Load) pipeline** for job market data.

The pipeline performs the following steps:

```text
CSV File
   ↓
Extract
   ↓
Transform
   ↓
Check Existing Records
   ↓
Load New Records into MySQL
   ↓
Scheduler runs the pipeline automatically
```

The main objectives are:

- Extract job data from a CSV file.
- Clean and transform raw job data.
- Load processed data into MySQL.
- Prevent duplicate records with the current ones in database before loading.
- Automatically run the pipeline on a schedule.
- Handle common pipeline errors.

---

# 2. Extract

The Extract stage reads the raw job dataset from a CSV file using Pandas.

The Extract stage handles common problems such as:

- CSV file does not exist.
- CSV file contains no data.
- Unexpected errors while reading the file.

---

# 3. Transform

The Transform stage cleans and restructures the raw data before loading it into the database.

The main transformations include:

- Removing duplicate records.
- Cleaning salary information.
- Extracting minimum and maximum salary.
- Identifying salary currency.
- Normalizing job titles into job categories.
- Parsing addresses into city and district.
- Exploding jobs with multiple locations into multiple records.

The transformation flow is:

```text
Raw Data
   ↓
Remove Duplicates
   ↓
Clean Salary
   ↓
Normalize Job Title
   ↓
Parse Address
   ↓
Explode Multiple Locations
   ↓
Cleaned DataFrame
```

### Salary Transformation

Raw salary values may have different formats, for example:

```text
10 - 20 triệu
Tới 35 triệu
Trên 10 triệu
600 - 1,300 USD
Thoả thuận
```

These values are converted into structured columns:

```text
min_salary
max_salary
salary_unit
```

Example:

| salary          | min_salary | max_salary | salary_unit |
| --------------- | ---------: | ---------: | ----------- |
| 10 - 20 triệu   |   10000000 |   20000000 | VND         |
| 600 - 1,300 USD |        600 |       1300 | USD         |
| Thoả thuận      |       NULL |       NULL | NULL        |

---

## 4. Job Title Normalization

Job titles can have many different names even when they represent similar roles.

For example:

```text
Senior Java Developer
Python Developer
.NET Developer
Software Engineer
```

These titles can be normalized into:

```text
Software Developer
```

Other normalized categories include:

```text
AI/ML Engineer
Data Scientist
Data Engineer
Data Analyst
Database Administrator
Cybersecurity
Cloud Engineer
DevOps/SRE
Network Engineer
System/Infrastructure
Business Analyst
QA/Tester
UI/UX Designer
Frontend Developer
Backend Developer
Full-stack Developer
Mobile Developer
Embedded/IoT Developer
Game Development
Software Developer
IT Support
IT Hardware/Technician
IT General
Other
```

This makes the dataset easier to analyze and aggregate.

---

# 5. Address Transformation

A job may contain multiple cities and districts in the original address.

For example:

```text
Hồ Chí Minh: Quận 9: Hà Nội: Cầu Giấy
```

The address is parsed into:

```text
Hồ Chí Minh → Quận 9
Hà Nội      → Cầu Giấy
```

After exploding the locations, the resulting data becomes:

| link_description | city        | district |
| ---------------- | ----------- | -------- |
| job_A            | Hồ Chí Minh | Quận 9   |
| job_A            | Hà Nội      | Cầu Giấy |

Therefore, the same `link_description` may legitimately appear multiple times.

These rows are not considered duplicates because they represent different job locations.

---

# 6. Duplicate Identification

Because one job may have multiple locations, `link_description` alone cannot be used as the unique identifier.

Instead, each record is identified using the combination:

```text
(link_description, city, district)
```

For example:

```text
job_A | Hà Nội      | Cầu Giấy
job_A | Hà Nội      | Ba Đình
job_A | Hồ Chí Minh | Quận 1
```

All three records are valid because the locations are different.

However:

```text
job_A | Hà Nội | Cầu Giấy
job_A | Hà Nội | Cầu Giấy
```

is considered a duplicate.

Duplicates inside the transformed dataset can therefore be removed using:

```python
df = df.drop_duplicates(
    subset=[
        "link_description",
        "city",
        "district"
    ]
)
```

---

# 7. Database Connection

SQLAlchemy is used to connect Python to MySQL.

The database is automatically created if it does not already exist.

The process is:

```text
Connect to MySQL Server
        ↓
Check Database
        ↓
Create Database if it does not exist
        ↓
Close Server Connection
        ↓
Create Engine connected to the Database
```

---

# 8. Incremental Load

The pipeline uses an **incremental loading** approach.

Instead of replacing the entire database table every time the pipeline runs, only new records are inserted.

The loading process is:

```text
Transformed DataFrame
        ↓
Read Existing Keys from MySQL
        ↓
Compare:
(link_description, city, district)
        ↓
Remove Existing Records
        ↓
Keep New Records
        ↓
Append New Records to MySQL
```

Existing records can be retrieved using:

```sql
SELECT
    link_description,
    city,
    district
FROM jobs;
```

The Python pipeline then compares the incoming records with the existing database records.

Only `new_df` is inserted into MySQL.

---

# 9. Example of Incremental Loading

### First Run

Suppose:

```text
CSV records      = 1,933
Database records = 0
```

The pipeline inserts:

```text
1,933 new records
```

---

### Second Run

If the CSV has not changed:

```text
CSV records      = 1,933
Database records = 1,933
```

All records already exist.

Therefore:

```text
0 new records
```

are inserted.

---

### Later Run

Suppose new job data has been added:

```text
CSV records      = 1,983
Database records = 1,933
```

The pipeline identifies the new records and inserts only:

```text
50 new records
```

This prevents the scheduler from inserting the same data every time the pipeline runs.

---

# 10. Load Function

The Load stage combines the duplicate check and database insertion.

---

# 11. ETL Pipeline

The three stages are combined into one pipeline:

```text
Extract
   ↓
Transform
   ↓
Load
```

The complete data flow becomes:

```text
                    ┌──────────────┐
                    │   data.csv   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Extract    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Transform   │
                    │              │
                    │ Salary       │
                    │ Job Title    │
                    │ Date         │
                    │ Address      │
                    └──────┬───────┘
                           │
                           ▼
                 ┌─────────────────────┐
                 │ Duplicate Checking  │
                 │                     │
                 │ link + city +       │
                 │ district            │
                 └─────────┬───────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │     Load     │
                    │    append    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    MySQL     │
                    │ jobs table   │
                    └──────────────┘
```

---

# 12. Pipeline Scheduling

The pipeline can be automated using APScheduler.

The scheduler remains running and waits for the configured execution time.

With:

```python
trigger="cron",
hour=0,
minute=0
```

the pipeline runs every day at:

```text
00:00
```

The scheduler flow is:

```text
Start Scheduler
      ↓
Wait
      ↓
00:00
      ↓
Run ETL Pipeline
      ↓
Pipeline Completes
      ↓
Wait
      ↓
Next Day 00:00
      ↓
Run Again
```

For development and testing, an interval schedule can also be used:

```python
scheduler.add_job(
    run_pipeline,
    trigger="interval",
    minutes=2
)
```

This runs the pipeline every five minutes.

---

# 13. Logging

Logging can be used instead of relying only on `print()` statements.

Example pipeline logs:

```text
2026-10-01 00:00:00 | INFO | Pipeline started
2026-10-01 00:00:01 | INFO | Extracted 1933 rows
2026-10-01 00:00:02 | INFO | Transformed 2094 rows
2026-10-01 00:00:03 | INFO | Loaded 50 new rows
2026-10-01 00:00:03 | INFO | Pipeline completed successfully
```

If an error occurs:

```python
logging.exception(
    f"Pipeline failed: {e}"
)
```

records both the error message and stack trace.

---

# 16. Final Pipeline Architecture

The final architecture is:

```text
                         Scheduler
                             │
                             │ triggers
                             ▼
                      run_pipeline()
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
           Extract       Transform         Load
              │              │              │
              │              │              │
          data.csv       Clean Data       MySQL
                             │
                             ├─ Salary
                             ├─ Job Title
                             └─ Location
                                             │
                                             ▼
                                    Check Existing Keys
                                             │
                                             ▼
                                      Append New Data
```

Overall:

```text
CSV
 ↓
Extract
 ↓
Transform
 ↓
Remove Duplicate Job-Locations
 ↓
Connect to MySQL
 ↓
Check Existing Records
 ↓
Insert Only New Records
 ↓
Store in jobs Table
 ↓
Scheduler Repeats the Pipeline Automatically
```

This design creates a simple automated ETL pipeline while preventing duplicate data and handling common extraction, transformation, and database errors.
