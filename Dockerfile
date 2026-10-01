FROM python:3.11-slim

WORKDIR /srv

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY static ./static
COPY fonts ./fonts
COPY tests ./tests

ENV SAHAYI_HOST=0.0.0.0
ENV SAHAYI_PORT=8080
ENV SAHAYI_DB=/data/sahayi.db
ENV SAHAYI_PDF_DIR=/data/pdfs
RUN mkdir -p /data/pdfs

EXPOSE 8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${SAHAYI_PORT}"]
