from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from ldap3 import Server, Connection, ALL, NTLM
from django.conf import settings

User = get_user_model()

class LDAPBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        ldap_server = getattr(settings, 'LDAP_SERVER_URI', None)
        ldap_domain = getattr(settings, 'LDAP_DOMAIN', None)
        ldap_search_base = getattr(settings, 'LDAP_SEARCH_BASE', None)
        if not (ldap_server and ldap_domain and ldap_search_base):
            return None

        # Sempre usa o formato UPN para autenticação SIMPLE
        if '@' in username:
            user_dn = username
            user_filter = username.split('@')[0]
        else:
            user_dn = f'{username}@{ldap_domain}'
            user_filter = username
        server = Server(ldap_server, get_info=ALL)
        try:
            conn = Connection(server, user=user_dn, password=password, authentication='SIMPLE', auto_bind=True)
            conn.search(ldap_search_base, f'(sAMAccountName={user_filter})', attributes=['givenName', 'sn', 'mail', 'memberOf'])
            if conn.entries:
                entry = conn.entries[0]
                # Verifica se usuário pertence ao grupo SoftwareStoreUsers
                grupos = entry.memberOf.values if 'memberOf' in entry else []
                grupo_permitido = 'CN=Softplan Users'
                if not any(grupo_permitido in g for g in grupos):
                    return None  # Não está no grupo permitido
                user, created = User.objects.get_or_create(username=user_filter)
                user.first_name = entry.givenName.value if 'givenName' in entry else ''
                user.last_name = entry.sn.value if 'sn' in entry else ''
                user.email = entry.mail.value if 'mail' in entry else ''
                user.set_unusable_password()  # senha nunca salva no banco
                user.save()
                return user
        except Exception as e:
            import logging
            logging.error(f'Erro LDAP: {e}')
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
