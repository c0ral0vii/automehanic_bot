FROM python:3.12-slim

WORKDIR /app


ENV PATH="/venv/bin:$PATH"


COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . /app

CMD ["sh", "-c", "python bot/run_admin_worker.py"]