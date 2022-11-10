SHELL := /bin/bash
MAX_LINE_LENGTH := 119

help: ## List all commands
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -_]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the project in a Python virtualenv
	python3 -m venv .venv
	.venv/bin/pip install -U pipenv
	.venv/bin/pipenv install

update-requirements: ## Update requirements
	.venv/bin/pipenv update --dev
