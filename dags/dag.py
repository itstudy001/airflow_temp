from datetime import datetime
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="unscheduled", start_date=datetime(2019, 1, 1), schedule_interval=None
)


fetch_events = BashOperator(
    task_id="fetch_events",
    bash_command=(
        "curl -o /tmp/events.json http://127.0.0.1:5000/events"
    ),
    dag=dag,
)

def _calculate_stats(input_path, output_path):

    Path(output_path).parent.mkdir(exist_ok=True)

    events = pd.read_json(input_path)
    stats = events.groupby(["date", "user"]).size().reset_index()

    stats.to_csv(output_path, index=False)

calculate_stats = PythonOperator(
    task_id="calculate_stats",
    python_callable=_calculate_stats,
    op_kwargs={"input_path": "/tmp/events.json", "output_path": "/tmp/stats.csv"},
    dag=dag,
)

fetch_events >> calculate_stats
