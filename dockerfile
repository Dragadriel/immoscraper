FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Wichtig: Playwright-Browser explizit installieren!
RUN playwright install --with-deps

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

CMD ["python", "main.py"]
