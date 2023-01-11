FROM python:3.10-slim AS builder

RUN apt-get update && \
    apt-get install -y libpq-dev gcc

# Create the virtual environment
RUN python -m venv /opt/venv
# Activate the virtual env
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY /src /app/

ENTRYPOINT [ "python", "main.py" ]