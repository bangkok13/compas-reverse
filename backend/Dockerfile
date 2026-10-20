FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/lock.txt \
    && useradd --create-home workshop
COPY . .
RUN mkdir -p media private staticfiles && chown -R workshop:workshop /app
USER workshop
EXPOSE 8000
CMD ["sh", "entrypoint.sh"]
