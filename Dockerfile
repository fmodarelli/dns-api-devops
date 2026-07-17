# Etapa 1: construir las dependencias
FROM python:3.12-slim AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip wheel \
    --no-cache-dir \
    --wheel-dir /wheels \
    -r requirements.txt


# Etapa 2: imagen final de ejecución
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear un usuario sin privilegios
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser

# Instalar dependencias generadas en la etapa anterior
COPY --from=builder /wheels /wheels
COPY requirements.txt .

RUN pip install \
    --no-cache-dir \
    --no-index \
    --find-links=/wheels \
    -r requirements.txt \
    && rm -rf /wheels

# Copiar la aplicación
COPY app ./app

# Ejecutar sin permisos de root
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
