#!/usr/bin/env bash

uv run ruff check --select I --fix "$@" # isort
uv run ruff format "$@" # black

# see the following issue for progress on a unified command that does both
# https://github.com/astral-sh/ruff/issues/8232
