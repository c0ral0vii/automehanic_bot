FROM python:3.12-slim

WORKDIR /app


ENV PATH="/venv/bin:$PATH"

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

RUN alembic upgrade head

CMD ["python", "./bot/main.py"]