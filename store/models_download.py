from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Software

User = get_user_model()

class SoftwareDownload(models.Model):
    """Model para rastrear downloads de software."""
    software = models.ForeignKey(
        Software,
        on_delete=models.CASCADE,
        related_name='downloads',
        verbose_name=_('Software')
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Usuário')
    )
    
    downloaded_at = models.DateTimeField(
        _('Data do download'),
        auto_now_add=True
    )
    
    ip_address = models.GenericIPAddressField(
        _('Endereço IP'),
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(
        _('User Agent'),
        blank=True,
        help_text=_('Informações do navegador do usuário')
    )
    
    version = models.CharField(
        _('Versão'),
        max_length=50,
        blank=True,
        help_text=_('Versão do software no momento do download')
    )
    
    class Meta:
        verbose_name = _('Download de Software')
        verbose_name_plural = _('Downloads de Software')
        ordering = ['-downloaded_at']
        indexes = [
            models.Index(fields=['software', 'downloaded_at']),
            models.Index(fields=['user', 'downloaded_at']),
        ]
    
    def __str__(self):
        user = self.user.username if self.user else 'Anônimo'
        return f"{self.software.name} - {user} - {self.downloaded_at}"
    
    @classmethod
    def create_download(cls, software, request):
        """Cria um registro de download para o software."""
        from django.contrib.sessions.models import Session
        
        # Obtém o usuário atual (se autenticado)
        user = request.user if request.user.is_authenticated else None
        
        # Obtém o endereço IP do usuário
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Cria o registro de download
        download = cls.objects.create(
            software=software,
            user=user,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            version=software.version
        )
        
        # Incrementa o contador de downloads do software
        software.download_count = models.F('download_count') + 1
        software.save(update_fields=['download_count'])
        
        return download
