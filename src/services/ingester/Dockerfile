FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py sicecar.py ./

EXPOSE 8003

CMD ["gunicorn", "-b", "0.0.0.0:8003", "-w", "2", "app:app"]