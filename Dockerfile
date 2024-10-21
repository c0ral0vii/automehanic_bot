FROM python:3.12-slim

WORKDIR /

COPY . /

ENV PATH="/venv/bin:$PATH"

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

CMD ["python", "./bot/main.py"]