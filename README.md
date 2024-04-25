# MLflow SharingHub

![License](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)
[![Language](https://img.shields.io/badge/language-Python-3776ab?style=flat-square&logo=Python)](https://www.python.org/)
![Style](https://img.shields.io/badge/style-ruff-9a9a9a?style=flat-square)
![Lint](https://img.shields.io/badge/lint-ruff-brightgreen?style=flat-square)
![Security](https://img.shields.io/badge/security-bandit,%20pip%20audit-purple?style=flat-square)
![Stability](https://img.shields.io/badge/stability-experimental-orange?style=flat-square)
![Contributions](https://img.shields.io/badge/contributions-welcome-orange?style=flat-square)

[Merge Request](https://gitlab.si.c-s.fr/space_applications/mlops-services/mlflow-sharinghub/merge_requests) **·**
[Bug Report](https://gitlab.si.c-s.fr/space_applications/mlops-services/mlflow-sharinghub/issues/new?issuable_template=bug_report) **·**
[Feature Request](https://gitlab.si.c-s.fr/space_applications/mlops-services/mlflow-sharinghub/issues/new?issuable_template=feature_request)

MLflow is a platform to streamline machine learning development, including tracking experiments, packaging code into reproducible runs, and sharing and deploying models.

SharingHub is an AI-focused web portal designed to help you discover, navigate, and analyze your AI-related Git projects hosted on GitLab.

This repository hosts a MLflow "app" plugin that integrates it with the GitLab authentication and permission system. The plugin also isolates the GitLab projects experiments and models from each others. The goal is to integrate this MLflow version

## Table of Contents

- [Getting started](#getting-started)
  - [Installation](#installation)
  - [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Getting started

### Installation

```bash
pip install git+https://gitlab.si.c-s.fr/space_applications/mlops-services/mlflow-sharinghub
# pip install git+https://gitlab.si.c-s.fr/space_applications/mlops-services/mlflow-sharinghub@<tag>
```

### Configuration

MLflow SharingHub is tied to a GitLab instance, you will need to configure it.

First, copy `.env.template` as `.env` and edit the content:

```txt
CACHE_TIMEOUT=30
LOGIN_AUTO_REDIRECT=false
GITLAB_URL=https://gitlab.si.c-s.fr
GITLAB_OAUTH_CLIENT_ID=<client-id>
GITLAB_OAUTH_CLIENT_SECRET=<client-secret>
```

The client-id and client-secret can be created in your GitLab User settings (Preferences).
You must create an "Application" with the scopes `api read_user openid profile email`.
The callback URL is `http://localhost:5000/auth/authorize`.

### Usage

#### Local

Being an MLflow plugin, in order to use it you'll have to install this project first. It is recommended to use a virtualenv.

```bash
pip install .
# OR
make install
```

Now you can run the mlflow server, you just need to add the parameter `--app-name sharinghub` to enable the plugin.

Example:

```bash
mlflow server --app-name sharinghub
```

And to enable hot-reload, add the `--dev`.

```bash
mlflow server --app-name sharinghub --dev
```

> Note: the make targets `run` and `run-dev` should be preferred as they add more arguments.

#### Docker

Build the image:

```bash
docker build . -t mlflow-sharinghub:latest --build-arg VERSION=$(git rev-parse --short HEAD)
# OR
make docker-build
```

```bash
docker run --rm -v $(pwd)/data:/home/mlflow/data -p 5000:5000 --env-file .env --name mlflow-sharinghub mlflow-sharinghub:latest
# OR
make docker-run
```

## Contributing

If you want to contribute to this project or understand how it works,
please check [CONTRIBUTING.md](CONTRIBUTING.md).

Any contribution is greatly appreciated.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more
information.
