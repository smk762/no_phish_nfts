#!/bin/bash
source .env
poetry run uvicorn main:app --host 0.0.0.0 --port ${FASTAPI_PORT} --reload
