# Utiliser une image Python
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Exposer le port
EXPOSE 5000

# Commande pour lancer l'application Flask
CMD ["flask", "run", "--host=0.0.0.0"]
