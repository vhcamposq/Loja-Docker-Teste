from django.db import models
from django.utils.translation import gettext_lazy as _
from .models import Software

class SoftwareScreenshot(models.Model):
    """Model para armazenar screenshots dos softwares."""
    software = models.ForeignKey(
        Software,
        on_delete=models.CASCADE,
        related_name='screenshots',
        verbose_name=_('Software')
    )
    
    image = models.ImageField(
        _('Imagem'),
        upload_to='software/screenshots/',
        help_text=_('Tamanho recomendado: 800x600 pixels')
    )
    
    caption = models.CharField(
        _('Legenda'),
        max_length=200,
        blank=True,
        help_text=_('Descrição opcional da imagem')
    )
    
    order = models.PositiveIntegerField(
        _('Ordem'),
        default=0,
        help_text=_('Ordem de exibição das imagens')
    )
    
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('Screenshot')
        verbose_name_plural = _('Screenshots')
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.software.name} - {self.caption or 'Sem legenda'}"
    
    def image_preview(self):
        if self.image:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                self.image.url
            )
        return ""
    
    image_preview.short_description = _('Prévia')
    image_preview.allow_tags = True
