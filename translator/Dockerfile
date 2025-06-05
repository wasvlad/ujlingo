FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY data/production data/production
COPY data/uk_en_translation_model data/uk_en_translation_model

COPY main.py main.py

ENV MODEL_PATH=/app/data/uk_en_translation_model

EXPOSE 3002

CMD ["python", "main.py"]