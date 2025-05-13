FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

WORKDIR /app

# Kopiere die Anforderungen und installiere sie
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Anwendungscodes
COPY . .

# Setze die Umgebungsvariable für den Browserpfad
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

CMD ["python", "main.py"]
