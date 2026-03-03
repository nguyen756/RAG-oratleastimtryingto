#!/bin/bash
set -e
docker compose down
rm -rf data_storage/*
rm -f data/metadata.json
rm -f data/vector_database.index
docker compose up -d --build
