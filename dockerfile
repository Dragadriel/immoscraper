FROM python:3.12-slim

# Installiere Systemabhängigkeiten
RUN apt-get update && apt-get install -y \
    libx11-xcb1 \
    libnss3 \
    libgdk-pixbuf2.0-0 \
    libgbm1 \
    libatk1.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Installiere Playwright und die notwendigen Browser
RUN pip install playwright
RUN playwright install

# Installiere andere Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install -r requirements.txt

# Kopiere die Anwendung und starte sie
COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
