#!/bin/bash

# Script de Deploy - Sistema de Gestão de Projetos v2.0.0
# Versão refatorada com estrutura modular

set -e

echo "🚀 Iniciando deploy da aplicação..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERRO: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] AVISO: $1${NC}"
}

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    error "Docker não está instalado!"
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose não está instalado!"
    exit 1
fi

# Verificar arquivo .env
if [ ! -f .env ]; then
    error "Arquivo .env não encontrado!"
    echo "Crie um arquivo .env com as seguintes variáveis:"
    echo "SUPABASE_URL=sua_url_do_supabase"
    echo "SUPABASE_KEY=sua_chave_do_supabase"
    echo "SECRET_KEY=sua_chave_secreta"
    exit 1
fi

# Criar diretórios necessários
log "Criando diretórios..."
mkdir -p logs
mkdir -p static/uploads
mkdir -p ssl

# Parar containers existentes
log "Parando containers existentes..."
docker-compose down --remove-orphans

# Remover imagens antigas (opcional)
if [ "$1" = "--clean" ]; then
    log "Removendo imagens antigas..."
    docker-compose down --rmi all --volumes --remove-orphans
fi

# Construir nova imagem
log "Construindo nova imagem..."
docker-compose build --no-cache

# Iniciar serviços
log "Iniciando serviços..."
docker-compose up -d

# Aguardar aplicação estar pronta
log "Aguardando aplicação estar pronta..."
sleep 30

# Verificar health check
log "Verificando health check..."
for i in {1..10}; do
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        log "✅ Aplicação está funcionando!"
        break
    else
        warning "Tentativa $i/10 - Aguardando aplicação..."
        sleep 10
    fi
    
    if [ $i -eq 10 ]; then
        error "Aplicação não respondeu ao health check!"
        docker-compose logs app
        exit 1
    fi
done

# Verificar status
log "Verificando status da aplicação..."
curl -s http://localhost:5000/status | python -m json.tool

# Mostrar logs
log "Logs da aplicação:"
docker-compose logs --tail=20 app

# Informações finais
echo ""
log "🎉 Deploy concluído com sucesso!"
echo ""
echo "📋 Informações:"
echo "   🌐 URL: http://localhost"
echo "   🔧 Health Check: http://localhost:5000/health"
echo "   📊 Status: http://localhost:5000/status"
echo ""
echo "📝 Comandos úteis:"
echo "   docker-compose logs -f app    # Ver logs em tempo real"
echo "   docker-compose restart app     # Reiniciar aplicação"
echo "   docker-compose down           # Parar todos os serviços"
echo "" 