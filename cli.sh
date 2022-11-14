#!/bin/sh

set -ex

exec .venv/bin/python -m pysmartmeter "$@"

