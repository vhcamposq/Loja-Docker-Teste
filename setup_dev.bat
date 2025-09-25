@echo off
echo Configurando o ambiente de desenvolvimento...

:: Verifica se o Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Erro: Python não encontrado. Certifique-se de que o Python 3.8+ está instalado e adicionado ao PATH.
    pause
    exit /b 1
)

:: Cria e ativa o ambiente virtual
echo Criando ambiente virtual...
python -m venv venv
call venv\Scripts\activate

:: Instala as dependências
echo Instalando dependências...
pip install --upgrade pip
pip install -r requirements.txt

:: Cria o arquivo .env se não existir
if not exist .env (
    echo Criando arquivo .env a partir do modelo...
    copy .env.example .env
    echo Por favor, edite o arquivo .env com as configurações apropriadas.
)

:: Aplica as migrações
echo Aplicando migrações...
python manage.py migrate

:: Cria um superusuário se não existir
echo Criando superusuário...
python manage.py createsuperuser --username=admin --email=admin@example.com || echo Superusuário já existe ou ocorreu um erro.

echo.
echo Configuração concluída com sucesso!
echo.
echo Para iniciar o servidor de desenvolvimento, execute:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
pause
