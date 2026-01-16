FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app



# --- AQUÍ ESTÁ EL CAMBIO IMPORTANTE ---
# Agregamos 'ffmpeg' a la lista de programas que se instalan
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
# --------------------------------------



COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles

ENV SECRET_KEY="BUILD_TIME_FAKE_KEY"
ENV MONGO_URI="docker-build-placeholder"

WORKDIR /app/web_skill 
RUN python manage.py collectstatic --noinput --clear

EXPOSE 8080

# Ejecutar directamente con bash en lugar de usar el script
CMD ["bash", "-c", "cd /app/web_skill && python manage.py migrate --noinput --traceback && exec gunicorn web_skill.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 --log-level debug --access-logfile - --error-logfile -"]