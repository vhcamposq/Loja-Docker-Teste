#!/bin/bash
echo "Configurando o ambiente de desenvolvimento..."

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python 3 não encontrado. Certifique-se de que o Python 3.8+ está instalado."
    exit 1
fi

# Cria e ativa o ambiente virtual
echo "Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instala as dependências
echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Cria o arquivo .env se não existir
if [ ! -f .env ]; then
    echo "Criando arquivo .env a partir do modelo..."
    cp .env.example .env
    echo "Por favor, edite o arquivo .env com as configurações apropriadas."
fi

# Aplica as migrações
echo "Aplicando migrações..."
python manage.py migrate

# Cria um superusuário se não existir
echo "Criando superusuário..."
python manage.py createsuperuser --username=admin --email=admin@example.com || echo "Superusuário já existe ou ocorreu um erro."

echo -e "\nConfiguração concluída com sucesso!"
echo -e "\nPara iniciar o servidor de desenvolvimento, execute:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
