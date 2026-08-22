# syntax=docker/dockerfile:1.7

FROM python:3.12-alpine AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY catalog.json ./
COPY stories/ stories/
COPY scripts/ scripts/
COPY site/ site/
COPY tests/ tests/

RUN python3 -m unittest -v \
    && python3 scripts/novel.py validate \
    && python3 scripts/novel.py build

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist/ /usr/share/nginx/html/

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
