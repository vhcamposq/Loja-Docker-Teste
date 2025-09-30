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

echo "[entrypoint] Garantindo diretórios: $MEDIA_DIR $STATICFILES_DIR $DATA_DIR"
mkdir -p "$MEDIA_DIR" "$STATICFILES_DIR" "$DATA_DIR"

echo "[entrypoint] Rodando migrações"
python manage.py migrate --noinput || true

echo "[entrypoint] Coletando arquivos estáticos"
python manage.py collectstatic --noinput || true

# Se nenhum comando foi passado, define padrão para iniciar o servidor de desenvolvimento
if [ "$#" -eq 0 ]; then
  echo "[entrypoint] Nenhum comando fornecido. Iniciando runserver padrão em 0.0.0.0:8000"
  set -- python manage.py runserver 0.0.0.0:8000
fi

# Executa o comando final passado (por CMD ou docker-compose:command)
echo "[entrypoint] Executando comando: $@"
exec "$@"
