#!/bin/sh

set -ex

exec poetry run python -m pysmartmeter "$@"

