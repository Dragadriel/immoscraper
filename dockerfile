FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Kein playwright install hier!

# Beim Start: erst Browser installieren, dann Skript ausführen
CMD ["bash", "-c", "playwright install --with-deps && python main.py"]
