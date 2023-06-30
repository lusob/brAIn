# To build the multiarch image and push it ot registry:
# docker buildx build --platform linux/amd64,linux/arm64 --push -t lusob04/brain .
FROM python:3.9-slim-buster

WORKDIR /app


COPY . .


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y make

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
