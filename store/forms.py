from django import forms
from django.core.exceptions import ValidationError
from .models import Software
from .models_suggestion import SoftwareSuggestion

class SoftwareForm(forms.ModelForm):
    class Meta:
        model = Software
        fields = [
            'name', 'slug', 'description', 'version', 'category',
            'icon', 'installer', 'install_script', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'install_script': forms.Textarea(attrs={'rows': 8, 'class': 'font-monospace'}),
        }
    
    def clean_installer(self):
        installer = self.cleaned_data.get('installer')
        if installer:
            # Verifica se o arquivo tem uma extensão permitida
            valid_extensions = ['.exe', '.msi', '.bat', '.ps1', '.zip', '.msix', '.appx']
            if not any(installer.name.lower().endswith(ext) for ext in valid_extensions):
                raise ValidationError('Tipo de arquivo não suportado. Use .exe, .msi, .bat, .ps1, .zip, .msix ou .appx')
        return installer
    
    def clean_icon(self):
        icon = self.cleaned_data.get('icon')
        if icon:
            # Verifica se o arquivo de ícone é uma imagem
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico']
            if not any(icon.name.lower().endswith(ext) for ext in valid_extensions):
                raise ValidationError('Formato de imagem não suportado. Use JPG, PNG, GIF, SVG ou ICO')
        return icon


class SoftwareSuggestionForm(forms.ModelForm):
    class Meta:
        model = SoftwareSuggestion
        fields = ['title', 'description', 'category', 'reference_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
