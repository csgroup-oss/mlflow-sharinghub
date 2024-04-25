##@ Project's Makefile, with utility commands for the project development lifecycle.

PYTHON=python3
PIP=$(PYTHON) -mpip
TOX=$(PYTHON) -mtox
PRE_COMMIT=$(PYTHON) -mpre_commit

TAG=latest
MLFLOW_SERVER_ARGS=--backend-store-uri sqlite:///data/mlflow.db --artifacts-destination ./data/mlartifacts --app-name sharinghub

.PHONY: default help release build install install-dev
.PHONY: run run-dev docker-build docker-run
.PHONY: shell test report lint lint-watch security
.PHONY: clean pipeline pre-commit

# ======================================================= #

default: pipeline

release: ## Bump version, create tag and update CHANGELOG.
	@$(PYTHON) -mcommitizen bump

build: ## Build wheel and tar.gz in 'dist/'.
	@$(PYTHON) -mbuild

install: ## Install in the current python env.
	@$(PIP) install .

install-dev: ## Install in editable mode inside the current python env with dev dependencies.
	@$(PIP) install -r requirements-dev.txt

-create-data-dir:
	@mkdir -p data

run: -create-data-dir ## Run mlflow server with sharinghub plugin
	@$(PYTHON) -m mlflow server $(MLFLOW_SERVER_ARGS)

run-dev: -create-data-dir ## Run dev mlflow server with sharinghub plugin
	@$(PYTHON) -m mlflow server $(MLFLOW_SERVER_ARGS) --dev

docker-build: ## Build docker image.
	@docker build . -t mlflow-sharinghub:$(TAG) --build-arg VERSION=$(git rev-parse --short HEAD)

docker-run: -create-data-dir ## Run docker image locally.
	@docker run --rm -v $(PWD)/data:/home/mlflow/data -p 5000:5000 --env-file .env --name mlflow-sharinghub mlflow-sharinghub:$(TAG)

shell: ## Open Python shell.
	@$(PYTHON) -mbpython

test: ## Invoke pytest to run automated tests.
	@$(TOX)

report: ## Start http server to serve the test report and coverage.
	@printf "Test report: http://localhost:9000\n"
	@printf "Coverage report: http://localhost:9000/coverage\n"
	@$(PYTHON) -mhttp.server -b 0.0.0.0 -d tests-reports 9000 > /dev/null

lint: ## Lint python source code.
	@$(PRE_COMMIT) run --files $(shell find src tests -name "*.py")

lint-watch: ## Run ruff linter with --watch (ruff needs to be installed)
	@$(PYTHON) -mruff check src --fix --watch

security: ## Security check on project dependencies.
	@$(TOX) -e $@

clean: ## Clean temporary files, like python __pycache__, dist build, tests reports.
	@find src tests -regex "^.*\(__pycache__\|\.py[co]\)$$" -delete
	@rm -rf dist tests-reports .coverage* .*_cache

pipeline: security lint test build ## Run security, lint, test, build.

pre-commit: ## Run all pre-commit hooks.
	@$(PRE_COMMIT) run --all-files
	@$(PRE_COMMIT) run --hook-stage push --all-files

# ======================================================= #

HELP_COLUMN=11
help: ## Show this help.
	@printf "\033[1m################\n#     Help     #\n################\033[0m\n"
	@awk 'BEGIN {FS = ":.*##@"; printf "\n"} /^##@/ { printf "%s\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n\n  make \033[36m<target>\033[0m\n\n"} /^[$$()% a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-$(HELP_COLUMN)s\033[0m %s\n", $$1, $$2 } ' $(MAKEFILE_LIST)
	@printf "\n"
