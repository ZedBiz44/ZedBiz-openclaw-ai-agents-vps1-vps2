FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

RUN addgroup -S -g 10001 allocator && adduser -S -D -H -u 10001 -G allocator allocator \
    && mkdir -p /data && chown -R allocator:allocator /app /data

USER allocator
EXPOSE 8788
CMD ["uvicorn", "app.main:create_default_app", "--factory", "--host", "0.0.0.0", "--port", "8788", "--workers", "1"]
