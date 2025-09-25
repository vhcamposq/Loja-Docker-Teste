import os
import logging
from django.db.models.signals import pre_save, post_delete
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from django.dispatch import receiver
from django.conf import settings
from .models import Software
from .kace import get_latest_hostname_for_user

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Software)
def update_software_slug(sender, instance, **kwargs):
    """Atualiza o slug do software antes de salvar."""
    if not instance.slug:
        from django.utils.text import slugify
        instance.slug = slugify(f"{instance.name} {instance.version}")


@receiver(post_delete, sender=Software)
def delete_software_files(sender, instance, **kwargs):
    """Remove os arquivos associados a um software quando ele é excluído."""
    try:
        # Remove o ícone se existir
        if instance.icon:
            icon_path = os.path.join(settings.MEDIA_ROOT, str(instance.icon))
            if os.path.isfile(icon_path):
                os.remove(icon_path)
                logger.info(f"Ícone removido: {icon_path}")
        
        # Remove o instalador se existir
        if instance.installer:
            installer_path = os.path.join(settings.MEDIA_ROOT, str(instance.installer))
            if os.path.isfile(installer_path):
                os.remove(installer_path)
                logger.info(f"Arquivo instalador removido: {installer_path}")
    
    except Exception as e:
        logger.error(f"Erro ao remover arquivos do software {instance.name}: {str(e)}", exc_info=True)


@receiver(user_logged_in)
def resolve_hostname_on_login(sender, user, request, **kwargs):
    """Ao efetuar login, resolve o hostname via KACE e guarda na sessão.
    Se não encontrar ou ocorrer erro, informa o usuário e impede instalações.
    """
    try:
        username = (getattr(user, 'email', '') or getattr(user, 'username', '')).split('@')[0]
        hostname = get_latest_hostname_for_user(username)
        request.session['resolved_hostname'] = hostname
        if not hostname:
            messages.error(
                request,
                'Não foi possivel encontrar sua maquina, por motivo de segurança, não é possivel executar nenhuma instalação.',
                extra_tags='alert-danger'
            )
    except Exception:
        logger.exception('Falha ao consultar KACE na autenticação do usuário.')
        request.session['resolved_hostname'] = None
        messages.error(
            request,
            'Não foi possivel encontrar sua maquina, por motivo de segurança, não é possivel executar nenhuma instalação.',
            extra_tags='alert-danger'
        )

def ready():
    """Importa os sinais quando o aplicativo estiver pronto."""
    # Esta função será chamada no método ready() do AppConfig
    pass
