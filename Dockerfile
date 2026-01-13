FROM python:3.12-slim

WORKDIR /app

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY app.py .

# Sécurité : utilisateur non-root
RUN useradd -m appuser
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]
