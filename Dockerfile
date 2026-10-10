# 1. Imagen base oficial y ligera de Python
FROM python:3.13-slim

# 2. Evitar escritura de bytecode y habilitar logs limpios
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar e instalar requerimientos
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copiar el código del proyecto
COPY . /app/

# 6. Puerto estándar de Django
EXPOSE 8000

# 7. Comando de ejecución
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]