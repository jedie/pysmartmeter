SHELL := /bin/bash
MAX_LINE_LENGTH := 119

help: ## List all commands
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -_]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the project in a Python virtualenv
	python3 -m venv .venv
	.venv/bin/pip install -U pip-tools
	.venv/bin/pip-sync requirements/develop.txt

update-requirements: ## Update requirements via pip-compile
	.venv/bin/pip-compile --upgrade --allow-unsafe --generate-hashes requirements/production.in --output-file requirements/production.txt
	.venv/bin/pip-compile --upgrade --allow-unsafe --generate-hashes requirements/production.in requirements/develop.in --output-file requirements/develop.txt
	.venv/bin/pip-sync requirements/develop.txt
