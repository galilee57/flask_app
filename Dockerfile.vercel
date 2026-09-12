# syntax=docker/dockerfile:1
FROM node:24-alpine AS styles
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY input.css ./
COPY app ./app
RUN npm run build:css

FROM python:3.14-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    FLASK_CONFIG=production CONTAINER_MODE=true FLASK_INSTANCE_PATH=/tmp/flask-instance PORT=8080
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock \
    && groupadd --gid 10001 flask \
    && useradd --uid 10001 --gid flask --no-create-home flask
COPY app ./app
COPY migrations ./migrations
COPY wsgi.py gunicorn.conf.py ./
COPY --from=styles /build/app/main/static/css/output.css ./app/main/static/css/output.css
USER flask
EXPOSE 8080
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
