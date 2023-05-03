FROM python:3.9-slim-buster

WORKDIR /app


COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y make

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
