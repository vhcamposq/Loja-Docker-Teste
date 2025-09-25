from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Software
from .models_suggestion import SoftwareSuggestion
from .forms import SoftwareSuggestionForm
from .models_task import InstallationTask
from .kace import get_latest_hostname_for_user

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class SoftwareListView(ListView):
    model = Software
    template_name = 'store/software_list.html'
    context_object_name = 'softwares'
    paginate_by = 12

    def get_queryset(self):
        queryset = Software.objects.filter(is_active=True)
        
        # Filtro por categoria
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        # Filtro por busca
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = dict(Software.CATEGORY_CHOICES)
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        # Usa hostname resolvido em sessão; se ausente, busca no KACE e armazena
        resolved_hostname = self.request.session.get('resolved_hostname')
        if resolved_hostname is None:
            username = (self.request.user.email or self.request.user.username or '').split('@')[0]
            resolved_hostname = get_latest_hostname_for_user(username)
            self.request.session['resolved_hostname'] = resolved_hostname
        context['resolved_hostname'] = resolved_hostname
        return context

class SoftwareDetailView(DetailView):
    model = Software
    template_name = 'store/software_detail.html'
    context_object_name = 'software'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resolved_hostname = self.request.session.get('resolved_hostname')
        if resolved_hostname is None:
            username = (self.request.user.email or self.request.user.username or '').split('@')[0]
            resolved_hostname = get_latest_hostname_for_user(username)
            self.request.session['resolved_hostname'] = resolved_hostname
        context['resolved_hostname'] = resolved_hostname
        return context

@login_required
def install_software(request, slug):
    software = get_object_or_404(Software, slug=slug, is_active=True)
    
    # Segurança: hostname só é válido se vier do KACE; usa cache da sessão quando disponível
    hostname = request.session.get('resolved_hostname')
    if hostname is None:
        username = (request.user.email or request.user.username or '').split('@')[0]
        hostname = get_latest_hostname_for_user(username)
        request.session['resolved_hostname'] = hostname

    if not hostname:
        messages.error(
            request,
            'Não foi possivel encontrar sua maquina, por motivo de segurança, não é possivel executar nenhuma instalação.',
            extra_tags='alert-danger'
        )
        # Redireciona de volta para a página de detalhes se estiver vindo de lá
        if 'HTTP_REFERER' in request.META and 'detail' in request.META['HTTP_REFERER']:
            return redirect('store:software_detail', slug=slug)
        return redirect('store:software_list')

    # Cria a tarefa de instalação
    try:
        # Gera a URL do instalador
        installer_url = request.build_absolute_uri(software.installer.url)
        
        # Cria a tarefa
        task = InstallationTask.objects.create(
            software=software,
            hostname=hostname,
            installer_url=installer_url,
            status='pending'
        )
        
        # Adiciona mensagem de sucesso
        messages.success(
            request,
            'A instalação começará em instantes, por favor aguarde.',
            extra_tags='alert-success'
        )
        
        # Atualiza o contador de downloads
        software.download_count = models.F('download_count') + 1
        software.save(update_fields=['download_count'])
        
    except Exception as e:
        messages.error(
            request,
            f'Erro ao criar tarefa de instalação: {str(e)}',
            extra_tags='alert-danger'
        )
        if 'HTTP_REFERER' in request.META and 'detail' in request.META['HTTP_REFERER']:
            return redirect('store:software_detail', slug=slug)
        return redirect('store:software_list')
    
    return redirect('store:software_list')

@login_required
def suggest_software(request):
    if request.method == 'POST':
        form = SoftwareSuggestionForm(request.POST)
        if form.is_valid():
            suggestion: SoftwareSuggestion = form.save(commit=False)
            suggestion.requester = request.user
            suggestion.save()
            messages.success(request, 'Obrigado! Sua sugestão foi enviada para avaliação.')
            return redirect('store:software_list')
        else:
            messages.error(request, 'Por favor, corrija os erros do formulário.')
    else:
        form = SoftwareSuggestionForm()
    return render(request, 'store/suggest_software.html', {'form': form})
