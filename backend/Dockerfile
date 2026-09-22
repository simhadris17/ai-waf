FROM python:3.11-slim

WORKDIR /app

# System deps for psycopg2 + torch (torch is optional; skip if using requirements-deploy.txt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Accept build arg to choose which requirements file to use:
#   docker build --build-arg REQUIREMENTS=requirements-deploy.txt .  (lightweight, no torch)
#   docker build .                                                    (full, with torch)
ARG REQUIREMENTS=requirements.txt
COPY requirements.txt requirements-deploy.txt ./
RUN pip install --no-cache-dir -r ${REQUIREMENTS}

COPY . .

# model/ is populated either by mounting a volume with a pre-trained model,
# or by running `python -m app.ml.train` inside the container.
RUN mkdir -p /app/model/final

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
