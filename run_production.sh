#!/bin/bash
# Run with Gunicorn
gunicorn wsgi:application \
    --bind 0.0.0.0:8050 \
    --workers 4 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --capture-output \
    --preload 