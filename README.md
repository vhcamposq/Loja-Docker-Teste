# Loja de Software

Uma aplicação web para gerenciar e distribuir softwares em uma rede corporativa, permitindo que os usuários instalem aplicativos pré-aprovados sem a necessidade de privilégios administrativos.

## Recursos

- Catálogo de softwares organizados por categorias
- Autenticação LDAP integrada
- Interface amigável e responsiva
- Upload de instaladores e ícones
- Scripts de instalação personalizáveis
- Controle de versão
- Painel administrativo completo

## Requisitos

- Python 3.8+
- Django 4.2+
- Banco de dados (SQLite, PostgreSQL, MySQL, etc.)
- Servidor LDAP (opcional, para autenticação)

## Instalação

1. Clone o repositório:
   ```bash
   git clone [URL_DO_REPOSITORIO]
   cd software_store
   ```

2. Crie um ambiente virtual e ative-o:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
   ```
   SECRET_KEY=sua_chave_secreta_aqui
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. Execute as migrações:
   ```bash
   python manage.py migrate
   ```

6. Crie um superusuário para acessar o painel administrativo:
   ```bash
   python manage.py createsuperuser
   ```

7. Inicie o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

8. Acesse a aplicação em [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Importando Softwares

Você pode importar softwares de um arquivo JSON ou de um diretório contendo os instaladores.

### Exemplo de importação de um arquivo JSON:

```bash
python manage.py import_software sample_software.json
```

### Estrutura do arquivo JSON:

```json
{
  "name": "Nome do Software",
  "version": "1.0.0",
  "description": "Descrição detalhada do software",
  "category": "CATEGORIA",
  "icon": "caminho/para/icone.png",
  "installer": "caminho/para/instalador.exe",
  "install_script": "@echo off\necho Instalando...\nstart /wait instalador.exe /silent",
  "is_active": true
}
```

### Categorias disponíveis:

- `OFFICE`: Pacote Office
- `BROWSER`: Navegadores
- `DEVELOPMENT`: Desenvolvimento
- `DESIGN`: Design
- `SECURITY`: Segurança
- `UTILITIES`: Utilitários
- `OTHER`: Outros

## Configuração LDAP (Opcional)

Para habilitar a autenticação LDAP, descomente e configure as seguintes linhas no arquivo `settings.py`:

```python
# Configurações LDAP
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Configurações do servidor LDAP
AUTH_LDAP_SERVER_URI = "ldap://seu-servidor-ldap:389"
AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "ou=usuarios,dc=empresa,dc=com",
    ldap.SCOPE_SUBTREE,
    "(sAMAccountName=%(user)s)",
)

# Mapeamento de atributos LDAP para o modelo de usuário do Django
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}
```

## Personalização

### Adicionando um novo tema

1. Crie um novo arquivo CSS em `static/css/themes/`
2. Adicione o link para o tema no template base (`templates/base.html`)
3. Atualize a configuração `THEME` no arquivo `settings.py`

### Adicionando um novo tipo de instalação

1. Crie um novo manipulador em `store/installers.py`
2. Adicione a lógica de instalação específica
3. Atualize a view `install_software` para usar o novo manipulador

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Desenvolvimento

Para contribuir com o projeto, siga estas etapas:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Suporte

Para suporte, entre em contato com a equipe de TI ou abra uma issue no repositório.
