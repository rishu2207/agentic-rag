"""Smoke-test DAG.

Probes the FastAPI backend, the Postgres database, and prints a heartbeat.
Kept deliberately small — its only job is to verify that the Airflow worker
can reach the rest of the stack. Use the real ingestion DAG
(``arxiv_paper_ingestion``) for production work.
"""

from datetime import datetime, timedelta

import psycopg2
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator


def heartbeat():
    """Log a simple heartbeat so we know the scheduler is firing."""
    print("Agentic RAG Platform — Airflow heartbeat OK")
    return "success"


def check_services():
    """Verify that the API and the shared Postgres database are reachable."""
    try:
        response = requests.get("http://rag-api:8000/api/v1/health", timeout=5)
        print(f"API health: {response.status_code}")

        conn = psycopg2.connect(
            host="postgres",
            port=5432,
            database="rag_db",
            user="rag_user",
            password="rag_password",
        )
        print("Database: Connected successfully")
        conn.close()

        return "Services are accessible"
    except Exception as exc:
        print(f"Service check failed: {exc}")
        raise


default_args = {
    "owner": "agentic-rag",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "smoke_test",
    default_args=default_args,
    description="Smoke test for the Agentic RAG Platform — API + database reachability",
    schedule=None,
    catchup=False,
    tags=["smoke-test", "health"],
)

heartbeat_task = PythonOperator(
    task_id="heartbeat",
    python_callable=heartbeat,
    dag=dag,
)

service_check_task = PythonOperator(
    task_id="check_services",
    python_callable=check_services,
    dag=dag,
)

heartbeat_task >> service_check_task
