
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY classroom2.py .
COPY db.py .

EXPOSE 5000

CMD ["flask", "--app", "classroom2.py", "run", "--host=0.0.0.0", "--port=5000"]
