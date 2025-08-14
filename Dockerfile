# Dockerfile para Sistema de Gestão de Projetos v2.0.0
# Versão refatorada com estrutura modular

FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app_producao.py
ENV FLASK_ENV=production

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements_producao.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements_producao.txt

# Criar diretórios necessários com permissões corretas
RUN mkdir -p logs static/uploads && \
    chmod 755 logs static/uploads

# Copiar código da aplicação
COPY . .

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app && \
    chmod -R 755 /app/logs /app/static

USER app

# Expor porta
EXPOSE 5000

# Health check (usando Python em vez de curl)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Comando para iniciar a aplicação
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app_producao:app"] 