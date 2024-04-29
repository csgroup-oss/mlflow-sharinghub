FROM python:3.12-slim-bookworm as installer

WORKDIR /install

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build requirements
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc git python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy files needed for build
COPY .git .git
COPY pyproject.toml README.md LICENSE src ./

# Generate python dependencies wheels
RUN pip wheel --no-cache-dir --wheel-dir /install/wheels .[all]

FROM python:3.12-slim-bookworm

ARG VERSION=latest

LABEL version=${VERSION}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=$PATH:/home/mlflow/.local/bin

ENV MLFLOW_HOST=0.0.0.0
ENV MLFLOW_PORT=5000
ENV MLFLOW_BACKEND_STORE_URI=sqlite:///data/mlflow.db
ENV MLFLOW_ARTIFACTS_DESTINATION=./data/mlartifacts

# Install runtime requirements
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -mrU -d /home/mlflow -s /bin/bash mlflow

USER mlflow

WORKDIR /home/mlflow

COPY --chown=mlflow:mlflow --from=installer /install/wheels wheels

RUN pip install --user --no-cache-dir wheels/* && \
    rm -rf wheels

RUN mkdir data

VOLUME ["/home/mlflow/data"]

EXPOSE 5000

CMD [ "mlflow", "server", "--app-name", "sharinghub"]
