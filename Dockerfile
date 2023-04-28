FROM python:3.9-slim-buster

WORKDIR /app

# Set the MARKDOWN_FILES environment variable from the markdown_files build argument
ARG markdown_files
ENV MARKDOWN_FILES=${markdown_files}

# Set the OPENAI_API_KEY environment variable from the openai_key build argument
ARG openai_key
ENV OPENAI_API_KEY=${openai_key}

# Validate that the MARKDOWN_FILES and OPENAI_API_KEY environment variables are set
RUN if [ -z "${MARKDOWN_FILES}" ]; then echo "ERROR: markdown_files parameter is not set"; exit 1; fi
RUN if [ -z "${OPENAI_API_KEY}" ]; then echo "ERROR: openai_key parameter is not set"; exit 1; fi

# Mount the host folder specified in the MARKDOWN_FILES environment variable
VOLUME [${MARKDOWN_FILES}, "/app/markdowns"]

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y make
RUN make ingest

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
