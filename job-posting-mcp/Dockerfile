FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY web_server.py .

EXPOSE 8000

CMD ["python", "web_server.py"]