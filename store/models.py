from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class Software(models.Model):
    CATEGORY_CHOICES = [
        ('OFFICE', _('Pacote Office')),
        ('BROWSER', _('Navegadores')),
        ('DEVELOPMENT', _('Desenvolvimento')),
        ('DESIGN', _('Design')),
        ('SECURITY', _('Segurança')),
        ('UTILITIES', _('Utilitários')),
        ('OTHER', _('Outros')),
    ]

    # Parâmetros adicionais para instalação
    install_args = models.CharField(
        _('Parâmetros adicionais'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Parâmetros de linha de comando adicionais para o instalador (ex: /S, /VERYSILENT, /qn, etc)')
    )

    
    name = models.CharField(_('Nome'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True, blank=True)
    description = models.TextField(_('Descrição'), blank=True)
    version = models.CharField(_('Versão'), max_length=50)
    category = models.CharField(
        _('Categoria'),
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='OTHER'
    )
    
    # Arquivos
    icon = models.ImageField(
        _('Ícone'),
        upload_to='software/icons/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text=_('Ícone do software (formato PNG ou JPG)')
    )
    
    installer = models.FileField(
        _('Arquivo de Instalação'),
        upload_to='software/installers/%Y/%m/%d/',
        help_text=_('Arquivo executável ou pacote de instalação')
    )
    
    # Metadados
    is_active = models.BooleanField(_('Ativo'), default=True)
    is_featured = models.BooleanField(_('Destaque'), default=False)
    download_count = models.PositiveIntegerField(_('Downloads'), default=0, editable=False)
    
    # Relacionamentos
    related_software = models.ManyToManyField(
        'self',
        verbose_name=_('Softwares Relacionados'),
        blank=True,
        symmetrical=False,
        through='SoftwareRelationship',
        through_fields=('from_software', 'to_software'),
    )
    
    # Datas
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    # Campos para o script de instalação
    install_script = models.TextField(
        _('Script de Instalação'),
        blank=True,
        help_text=_('Comandos para instalação (opcional)')
    )

    class Meta:
        verbose_name = _('Software')
        verbose_name_plural = _('Softwares')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['created_at']),
        ]
        permissions = [
            ('can_download_software', _('Pode baixar softwares')),
            ('can_manage_software', _('Pode gerenciar softwares')),
        ]

    def __str__(self):
        return f"{self.name} ({self.version})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name} {self.version}")
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('store:software_detail', kwargs={'slug': self.slug})
    
    def get_install_url(self):
        return reverse('store:install_software', kwargs={'slug': self.slug})
    
    def get_download_url(self):
        return reverse('store:download_software', kwargs={'pk': self.pk})
    
    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
    
    def record_download(self, request):
        """Registra um download deste software."""
        from .models_download import SoftwareDownload
        return SoftwareDownload.create_download(self, request)
    
    def get_related_software(self, limit=5):
        """Retorna softwares relacionados."""
        return self.related_software.filter(is_active=True)[:limit]
    
    def get_screenshots(self):
        """Retorna as screenshots do software."""
        return self.screenshots.all().order_by('order')
    
    def get_absolute_admin_url(self):
        """Retorna a URL de edição no admin."""
        from django.urls import reverse
        return reverse('admin:store_software_change', args=[self.id])


class SoftwareRelationship(models.Model):
    """Model intermediário para relacionamento entre softwares."""
    from_software = models.ForeignKey(
        Software,
        on_delete=models.CASCADE,
        related_name='related_from_software',
        verbose_name=_('Software de Origem')
    )
    
    to_software = models.ForeignKey(
        Software,
        on_delete=models.CASCADE,
        related_name='related_to_software',
        verbose_name=_('Software Relacionado')
    )
    
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Relacionamento de Software')
        verbose_name_plural = _('Relacionamentos de Software')
        unique_together = ('from_software', 'to_software')
    
    def __str__(self):
        return f"{self.from_software} -> {self.to_software}"


# Importa os modelos dos outros arquivos
from .models_screenshot import SoftwareScreenshot
from .models_download import SoftwareDownload
from .models_suggestion import SoftwareSuggestion
