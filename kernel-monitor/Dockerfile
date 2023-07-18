FROM python:3.9

# Copia il file Python nel container
COPY kernel_monitor.py .
COPY requirements.txt .
COPY send_data.py .
# Installa le dipendenze del file Python se necessario
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y strace

# Comando CMD che esegue il file Python utilizzando l'argomento dalla variabile d'ambiente
CMD ["python3", "kernel_monitor.py"]
