# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app
COPY . .

# Test/eval dependency (the simulator itself is stdlib-only)
RUN pip install --no-cache-dir --quiet pytest

# Default command runs the scripted demo. Override to run tests/evals/CLI:
#   docker run --rm <image> python sim/cli.py
#   docker run --rm <image> python evals/run.py
#   docker run --rm <image> python -m pytest sim/tests/ -q
CMD ["python", "sim/run.py"]
