FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY data/production data/production
COPY data/marian_finetuned_uk_en_v1/marian_finetuned_uk_en_v1

ENV MODEL_PATH=/app/data/marian_finetuned_uk_en_v1

EXPOSE 3002

CMD ["python", "main.py"]