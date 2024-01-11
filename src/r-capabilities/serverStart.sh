#!/bin/bash
gunicorn  main:app -w 1 -k uvicorn.workers.UvicornWorker -b :8081
