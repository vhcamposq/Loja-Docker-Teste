/**
 * Script principal para a Loja de Software
 * Lida com interações do usuário, como instalação de softwares
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configura o tooltip do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Configura os botões de instalação
    setupInstallButtons();
    
    // Configura o botão de voltar ao topo
    setupBackToTopButton();
});

/**
 * Configura os botões de instalação
 */
function setupInstallButtons() {
    const installButtons = document.querySelectorAll('.install-btn');
    
    installButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const softwareName = this.getAttribute('data-software');
            const installUrl = this.getAttribute('data-install-url');
            
            // Mostra o modal de confirmação
            const modal = new bootstrap.Modal(document.getElementById('installModal'));
            const modalTitle = document.getElementById('installModalLabel');
            const confirmButton = document.getElementById('confirmInstall');
            
            // Atualiza o título do modal
            if (modalTitle) {
                modalTitle.textContent = `Instalar ${softwareName}`;
            }
            
            // Configura o botão de confirmação
            if (confirmButton) {
                confirmButton.href = installUrl;
                confirmButton.addEventListener('click', function() {
                    // Mostra o indicador de carregamento
                    const originalText = confirmButton.innerHTML;
                    confirmButton.disabled = true;
                    confirmButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Instalando...';
                    
                    // Simula um atraso para a instalação (remova isso em produção)
                    setTimeout(() => {
                        // Redireciona para a URL de instalação
                        window.location.href = installUrl;
                    }, 1500);
                });
            }
            
            // Mostra o modal
            modal.show();
        });
    });
}

/**
 * Configura o botão de voltar ao topo
 */
function setupBackToTopButton() {
    const backToTopButton = document.getElementById('backToTop');
    
    if (backToTopButton) {
        // Mostra/oculta o botão ao rolar a página
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        // Rola suavemente para o topo ao clicar no botão
        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

/**
 * Exibe uma mensagem de notificação
 * @param {string} message - A mensagem a ser exibida
 * @param {string} type - O tipo de mensagem (success, danger, warning, info)
 */
function showNotification(message, type = 'success') {
    const notificationContainer = document.getElementById('notification-container');
    
    if (notificationContainer) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.role = 'alert';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        `;
        
        notificationContainer.appendChild(alert);
        
        // Remove a notificação após 5 segundos
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alert.remove();
            }, 150);
        }, 5000);
    }
}
