window.DriverActions = (function() {
  'use strict';

  let config = {};
  let currentActions = [];
  let isProcessing = false;

  // DOM элементы
  const actionsContainer = document.getElementById('actions-container');
  const confirmationModal = document.getElementById('confirmation-modal');
  const modalTitle = document.getElementById('modal-title');
  const modalDescription = document.getElementById('modal-description');
  let confirmBtn = document.getElementById('confirm-action');
  const cancelBtn = document.getElementById('cancel-action');

  function init(options) {
    console.log('DriverActions: Initializing with options:', options);

    config = {
      updateStatusUrl: options.updateStatusUrl,
      ...options
    };

    isProcessing = false;
    setupEventListeners();
    renderActions(options.initialActions || []);

    console.log('DriverActions: Initialized');
  }

  function setupEventListeners() {
    console.log('DriverActions: Setting up event listeners');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', function(e) {
        console.log('DriverActions: Cancel button clicked');
        e.preventDefault();
        hideConfirmationModal();
      });
    }
    if (confirmationModal) {
      confirmationModal.addEventListener('click', function(e) {
        if (e.target === confirmationModal) {
          console.log('DriverActions: Modal backdrop clicked');
          hideConfirmationModal();
        }
      });
    }
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && confirmationModal && !confirmationModal.classList.contains('hidden')) {
        console.log('DriverActions: Escape key pressed');
        hideConfirmationModal();
      }
    });

    document.addEventListener('statusChanged', function(event) {
      console.log('DriverActions: Received statusChanged event:', event.detail);
      updateActions(event.detail.available_actions);
    });
  }

  function renderActions(actions) {
    console.log('DriverActions: Rendering actions:', actions);

    currentActions = actions;
    isProcessing = false;

    if (!actionsContainer) {
      console.error('DriverActions: Actions container not found');
      return;
    }

    if (!actions || actions.length === 0) {
      actionsContainer.innerHTML = `
        <div class="text-center py-6">
          <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-gray-500 font-medium">Нет доступных действий</p>
          <p class="text-sm text-gray-400 mt-1">Ожидайте дальнейших инструкций</p>
        </div>
      `;
      return;
    }

    const actionsHtml = actions.map((action, index) => `
      <button class="action-btn w-full mb-3 bg-${action.color}-600 hover:bg-${action.color}-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg transition duration-300 flex items-center justify-center"
              data-action="${action.action}"
              data-requires-confirmation="${action.requires_confirmation || false}"
              data-label="${action.label}"
              data-description="${action.description}"
              data-index="${index}">
        <span class="mr-2 text-lg">${action.icon}</span>
        <div class="text-left">
          <div class="font-medium">${action.label}</div>
          <div class="text-sm opacity-90">${action.description}</div>
        </div>
      </button>
    `).join('');

    actionsContainer.innerHTML = actionsHtml;

    const actionButtons = actionsContainer.querySelectorAll('.action-btn');
    actionButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();

        console.log('DriverActions: Action button clicked:', this.dataset.action);
        if (this.disabled || isProcessing) {
          console.log('DriverActions: Button disabled or processing in progress');
          return;
        }

        const action = this.dataset.action;
        const requiresConfirmation = this.dataset.requiresConfirmation === 'true';
        const label = this.dataset.label;
        const description = this.dataset.description;

        console.log('DriverActions: Action details:', {
          action,
          requiresConfirmation,
          label,
          description
        });

        if (requiresConfirmation) {
          showConfirmationModal(action, label, description);
        } else {
          executeAction(action);
        }
      });
    });

    console.log('DriverActions: Actions rendered and event listeners attached');
  }

  function updateActions(actions) {
    console.log('DriverActions: Updating actions from:', currentActions, 'to:', actions);
    renderActions(actions);
  }

  function showConfirmationModal(action, label, description) {
    console.log('DriverActions: Showing confirmation modal for action:', action);

    if (!confirmationModal || !modalTitle || !modalDescription) {
      console.error('DriverActions: Modal elements not found');
      return;
    }

    modalTitle.textContent = label;
    modalDescription.textContent = `Вы уверены, что хотите ${description.toLowerCase()}?`;

    const oldConfirmBtn = document.getElementById('confirm-action');
    if (oldConfirmBtn) {
      const newConfirmBtn = oldConfirmBtn.cloneNode(true);
      oldConfirmBtn.parentNode.replaceChild(newConfirmBtn, oldConfirmBtn);
      confirmBtn = newConfirmBtn; // Обновляем ссылку

      confirmBtn.addEventListener('click', function(e) {
        console.log('DriverActions: Confirm button clicked for action:', action);
        e.preventDefault();
        executeAction(action);
        hideConfirmationModal();
      });
    }

    confirmationModal.classList.remove('hidden');
    confirmationModal.classList.add('flex');
    document.body.style.overflow = 'hidden';

    console.log('DriverActions: Modal shown');
  }

  function hideConfirmationModal() {
    console.log('DriverActions: Hiding confirmation modal');

    if (!confirmationModal) return;

    confirmationModal.classList.add('hidden');
    confirmationModal.classList.remove('flex');
    document.body.style.overflow = '';

    console.log('DriverActions: Modal hidden');
  }

  function executeAction(action) {
    console.log('DriverActions: Executing action:', action);

    if (isProcessing) {
      console.log('DriverActions: Already processing action, ignoring');
      return;
    }

    isProcessing = true;

    showLoadingState();

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';

    console.log('DriverActions: CSRF token found:', !!csrfToken);
    console.log('DriverActions: Making request to:', config.updateStatusUrl);
    console.log('DriverActions: Request payload:', { status: action });

    fetch(config.updateStatusUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({
        status: action
      })
    })
    .then(response => {
      console.log('DriverActions: Response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    })
    .then(data => {
      console.log('DriverActions: Response data:', data);

      isProcessing = false;

      if (data.success) {
        console.log('DriverActions: Action executed successfully');

        if (window.NotificationManager) {
          window.NotificationManager.showSuccess(data.message || 'Статус успешно обновлен');
        }
        showCompletionState(data.new_status);
        if (data.new_status === "DONE" && data.redirect_url) {
          console.log('DriverActions: Redirect URL provided:', data.redirect_url);

          setTimeout(() => {
            console.log('DriverActions: Redirecting to:', data.redirect_url);
            window.location.href = data.redirect_url;
          }, 2000);
        } else {
          console.log('DriverActions: No redirect, updating status');

          // Для обычных переходов обновляем статус
          if (window.DriverStatusUpdater) {
            setTimeout(() => {
              window.DriverStatusUpdater.updateStatus();
            }, 500);
          } else {
            console.error('DriverActions: DriverStatusUpdater not available');
            showErrorState('Модуль обновления статуса недоступен');
          }
        }
      } else {
        console.error('DriverActions: Server returned error:', data.error);
        isProcessing = false;

        if (window.NotificationManager) {
          window.NotificationManager.showError(data.error || 'Не удалось выполнить действие');
        }

        showErrorState(data.error || 'Произошла ошибка на сервере');
      }
    })
    .catch(error => {
      console.error('DriverActions: Request failed:', error);
      isProcessing = false;

      if (window.NotificationManager) {
        window.NotificationManager.showError('Произошла ошибка при выполнении действия');
      }

      showErrorState(`Ошибка: ${error.message}`);
    });
  }

  function showLoadingState() {
    console.log('DriverActions: Showing loading state');

    if (!actionsContainer) return;

    const loadingHtml = `
      <div class="text-center py-6">
        <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <p class="text-blue-600 font-medium">Обновляем статус...</p>
        <p class="text-sm text-gray-500 mt-1">Пожалуйста, подождите</p>
      </div>
    `;

    actionsContainer.innerHTML = loadingHtml;
  }

  function showCompletionState(newStatus) {
    console.log('DriverActions: Showing completion state for status:', newStatus);

    if (!actionsContainer) return;

    let message = 'Поездка завершена!';
    let icon = '🏁';
    let color = 'green';

    if (newStatus === 'CANCELLED') {
      message = 'Заказ отменен';
      icon = '❌';
      color = 'red';
    }

    const completionHtml = `
      <div class="text-center py-6">
        <div class="w-16 h-16 bg-${color}-100 rounded-full flex items-center justify-center mx-auto mb-3">
          <span class="text-2xl">${icon}</span>
        </div>
        <p class="text-${color}-600 font-medium">${message}</p>
        <p class="text-sm text-gray-500 mt-1">Переходим к оценке...</p>
      </div>
    `;

    actionsContainer.innerHTML = completionHtml;
  }

  function showErrorState(errorMessage) {
    console.log('DriverActions: Showing error state:', errorMessage);

    if (!actionsContainer) return;

    const errorHtml = `
      <div class="text-center py-6">
        <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p class="text-red-600 font-medium">Ошибка</p>
        <p class="text-sm text-gray-500 mt-1 mb-3">${errorMessage}</p>
        <button onclick="window.location.reload()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition duration-300">
          Обновить страницу
        </button>
      </div>
    `;

    actionsContainer.innerHTML = errorHtml;
  }

  return {
    init: init,
    updateActions: updateActions,
    executeAction: executeAction
  };

})();