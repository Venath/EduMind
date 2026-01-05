FROM apache/airflow:2.8.1-python3.9

# Switch to airflow user to install packages (do NOT use root)
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt