# Reddit Data ETL Pipeline

A data engineering project that extracts Reddit data using **Apify**, stores raw data in **Amazon S3**, transforms the data using **PySpark in Databricks**, and builds curated datasets in a **Delta Lake Gold layer**.

The pipeline also includes a separate user-data ingestion path using **PostgreSQL hosted on AWS EC2** and **Fivetran** for ingestion into Databricks.

---

## Architecture

The pipeline follows two ingestion paths that converge in Databricks.

```text
                           Reddit
                              │
                           Apify
                              │
                  ┌───────────┴───────────┐
                  │                       │
          Posts / Comments /           Users
           Communities Data              │
                  │                      │
                  ▼                      ▼
             Amazon S3              PostgreSQL
             Raw JSON              AWS EC2 Instance
                  │                      │
                  │                   Fivetran
                  │                      │
                  │                      ▼
                  │                 Databricks
                  │                  Catalog
                  │                      │
                  └──────────┬───────────┘
                             │
                             ▼
                        Databricks
                          PySpark
                             │
                      Transformations
                             │
                             ▼
                         Gold Layer
                        Delta Lake
