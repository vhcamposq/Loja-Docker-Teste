#!/usr/bin/env sh
set -e

# Caminhos padrão baseados no settings atual (ver settings.py)
# MEDIA_ROOT deve ser /app/media e STATIC_ROOT deve ser /app/staticfiles
MEDIA_DIR="/app/media"
STATICFILES_DIR="/app/staticfiles"
DATA_DIR="/app/data"

# Se variáveis de ambiente estiverem definidas (opção mais flexível), use-as
if [ -n "$MEDIA_ROOT" ]; then
  MEDIA_DIR="$MEDIA_ROOT"
fi
if [ -n "$STATIC_ROOT" ]; then
  STATICFILES_DIR="$STATIC_ROOT"
fi

# Garante que os diretórios existam
mkdir -p "$MEDIA_DIR" "$STATICFILES_DIR" "$DATA_DIR"

# Migrações
python manage.py migrate --noinput

# Coleta arquivos estáticos (seguro repetir)
python manage.py collectstatic --noinput || true

# Executa o comando final passado (por CMD ou docker-compose:command)
exec "$@"
