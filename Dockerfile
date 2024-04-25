FROM python:3.12-slim-bookworm as installer

WORKDIR /install

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Git for VCS versioning
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Copy files needed for build
COPY .git .git
COPY pyproject.toml README.md LICENSE src ./

# Generate python dependencies wheels
RUN pip wheel --no-cache-dir --wheel-dir /install/wheels .

FROM python:3.12-slim-bookworm

ARG VERSION=latest

LABEL version=${VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH=$PATH:/home/mlflow/.local/bin

RUN useradd -mrU -d /home/mlflow -s /bin/bash mlflow

USER mlflow

WORKDIR /home/mlflow

COPY --chown=mlflow:mlflow --from=installer /install/wheels wheels

RUN pip install --user --no-cache-dir wheels/* && \
    rm -rf wheels

RUN mkdir data

VOLUME ["/home/mlflow/data"]

EXPOSE 5000

CMD [ "mlflow", "server", "--host", "0.0.0.0", "--backend-store-uri", "sqlite:///data/mlflow.db", "--artifacts-destination", "./data/mlartifacts", "--app-name", "sharinghub"]
