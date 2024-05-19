#!/usr/bin/env bash

docker build -t cat_clicker:latest .
docker run --rm -it cat_clicker
