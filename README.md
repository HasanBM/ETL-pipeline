# Project Onyx

## Table of Contents
- [Introduction](#introduction)
- [Extract](#1-extract)
- [Transform](#2-transform)
- [Load](#3-load)
- [Analytics](#4-analytics)
- [Code Documentation](#code-documentation)
- [Links](#links)

## Totesys ETL Infrastructure
<img src="./src/Totesys ETL Pipeline.jpeg" alt="ETL Pipeline"></img>

## Introduction

Team Onyx consists of: Shuhaan, Ayub, Hasan, Arif, Saif and Ewan

Project objectives:
1. Extract data periodically from database in to ingested data S3 bucket
2. Transform data in to processed data S3 bucket
3. Upload transformed data to data warehouse
4. Carry out analysis of data for presentation

# Stage 

## Stage 1: Extract

### Task 1: Extract due

- **Check and extract** from Totesys PostGRES Database to an S3 bucket at maximum intervals of 30 minutes.

### Task 2: Infrastructure Setup

- **Terraform** to create infrastructure and Lambda Function:
  - Create two S3 buckets for the data:
    - **Ingestion Bucket** and **Processed Data Bucket** to hold data.
  - Create one bucket for the code itself.
  - One bucket for Terraform state and one bucket to hold the code.
    - The first time we run Terraform, we need a **Terraform state bucket** already in existence on S3 in order to hold the TF state.

### Task 3: Lambda Function for Data Extraction

- Lambda function to extract data:
  - Initially upload all tables to the bucket, later upload modifications of database to the bucket.
  - Upload as **JSON files**.
  - Database may not change every 5 minutes, but duplication is avoided by only taking the delta.  
  - Data in the database is modified (e.g., a transaction gets changed or cancelled), and a history of every modification and new data in Totesys DB by using **timestamps**.
- Extraction triggers a message to **CloudWatch**.
- All errors and status are logged to **CloudWatch**:
  - CloudWatch will send an email in case of a major error.

## Stage 2: Transform

### Task 1: Transform Lambda Function

- AWS Transform Lambda function triggers every time there is new data in the Ingestion bucket.
- **Pass the transformed data** to the Processed Data Bucket.

### Task 2: OLTP → OLAP Transformation Schema

- ERD here: [https://dbdiagram.io/d/Final_ERD-66bb73418b4bb5230e01b5bf](https://dbdiagram.io/d/Final_ERD-66bb73418b4bb5230e01b5bf)

## Stage 3: Load

### Task 1: Loading Processed Data

- Take data from the Processed Data bucket and load it into the **Warehouse**.
- Data is now in **OLAP format** and can be queried by Business Intelligence or Data Science tools:
  - Other tools may include Jupyter notebooks and/or pandas.

## Stage 4: Analytics

### Task 1: Data Validation and Analysis

- **Data Validation:** Ensure the data's suitability for analytics.
- **Analysis:** Carry out analysis using **Power BI**.

# Code Documentation

Do this in terminal before using pytest:


`export PYTHONPATH=src/extract_lambda:src/transform_lambda`


**Going to put link to Code Documentation here**

# Software Development Tools

- Python
    - `moto, boto3, mock, pytest, pg8000, prettyprint, pandas, unittest, datetime, python-dotenv, logger, sqlalchemy`
- Terraform
- SQL
- Makefile - contains commands to install requirements, run-checks and deploy terraform
- GitHub and GitHub Actions
- AWS S3, IAM, Lambda, CloudWatch, EventBridge and Secrets Manager
- `dbdiagram.io`
- Terminal Shell
- Trello

# Links

Github Project: [https://github.com/Shuhaan/project-onyx](https://github.com/Shuhaan/project-onyx)

Kanban Board: [https://trello.com/b/6e1BUT13/northcoders-final-project](https://trello.com/b/6e1BUT13/northcoders-final-project)
