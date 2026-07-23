FROM python:3.11.13-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV FLASK_DEBUG=0

RUN apt-get update \
	&& apt-get upgrade -y \
	&& rm -rf /var/lib/apt/lists/*

RUN groupadd --system appgroup && useradd --system --gid appgroup appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 5000

CMD ["sh", "-c", "python seed.py && flask run --host=0.0.0.0 --port=5000"]
