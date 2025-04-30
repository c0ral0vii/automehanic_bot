FROM python:3.12-slim

WORKDIR /app

ENV PATH="/venv/bin:$PATH"

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

CMD ["gunicorn", "bot.run_admin_worker:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]