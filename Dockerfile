FROM python:3.11-slim

WORKDIR /app

COPY connect_ai/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

ENV PORT=5000
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "connect_ai.app:app"]
