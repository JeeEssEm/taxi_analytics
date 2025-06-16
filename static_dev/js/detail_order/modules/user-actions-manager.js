window.UserActions = (function() {
  'use strict';

  let config = {};

  const cancelBtn = document.getElementById('cancel-order-btn');
  const cancelModal = document.getElementById('cancel-modal');
  const confirmCancelBtn = document.getElementById('confirm-cancel');
  const closeModalBtn = document.getElementById('close-modal');

  function init(options) {
    console.log('UserActions: Initializing...');

    config = {
      cancelUrl: options.cancelUrl,
      isCustomer: options.isCustomer,
      ...options
    };

    setupEventListeners();
    setupStatusListener();

    console.log('UserActions: Initialized');
  }

  function setupEventListeners() {
    if (cancelBtn) {
      cancelBtn.addEventListener('click', showCancelModal);
    }

    if (confirmCancelBtn) {
      confirmCancelBtn.addEventListener('click', cancelOrder);
    }

    if (closeModalBtn) {
      closeModalBtn.addEventListener('click', hideCancelModal);
    }

    if (cancelModal) {
      cancelModal.addEventListener('click', function(e) {
        if (e.target === cancelModal) {
          hideCancelModal();
        }
      });
    }

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && cancelModal && !cancelModal.classList.contains('hidden')) {
        hideCancelModal();
      }
    });
  }

  function setupStatusListener() {
    document.addEventListener('statusChanged', function(event) {
      updateCancelButtonState(event.detail.status);
    });
  }

  function updateCancelButtonState(status) {
    if (!cancelBtn) return;

    const cancellableStatuses = ['PENDING', 'WAITING_FOR_DRIVER'];

    if (cancellableStatuses.includes(status)) {
      cancelBtn.disabled = false;
      cancelBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    } else {
      cancelBtn.disabled = true;
      cancelBtn.classList.add('opacity-50', 'cursor-not-allowed');
    }
  }

  function showCancelModal() {
    console.log('UserActions: Showing cancel modal');

    if (cancelModal) {
      cancelModal.classList.remove('hidden');
      cancelModal.classList.add('flex');
      document.body.style.overflow = 'hidden';
    }
  }


  function hideCancelModal() {
    console.log('UserActions: Hiding cancel modal');

    if (cancelModal) {
      cancelModal.classList.add('hidden');
      cancelModal.classList.remove('flex');
      document.body.style.overflow = '';
    }
  }


  function cancelOrder() {
    console.log('UserActions: Cancelling order...');

    if (confirmCancelBtn) {
      confirmCancelBtn.disabled = true;
      confirmCancelBtn.textContent = 'Отменяем...';
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

    fetch(config.cancelUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.json())
    .then(data => {
      console.log('UserActions: Cancel response:', data);

      if (data.success) {
        hideCancelModal();

        // Обновляем статус немедленно
        if (window.StatusUpdater) {
          window.StatusUpdater.updateStatus();
        }

        // Показываем уведомление
        if (window.NotificationManager) {
          window.NotificationManager.showSuccess(data.message);
        }

      } else {
        if (window.NotificationManager) {
          window.NotificationManager.showError(data.error || 'Не удалось отменить заказ');
        }
      }
    })
    .catch(error => {
      console.error('UserActions: Cancel error:', error);
      if (window.NotificationManager) {
        window.NotificationManager.showError('Произошла ошибка при отмене заказа');
      }
    })
    .finally(() => {
      if (confirmCancelBtn) {
        confirmCancelBtn.disabled = false;
        confirmCancelBtn.textContent = 'Да, отменить';
      }
    });
  }

  return {
    init: init,
    showCancelModal: showCancelModal,
    hideCancelModal: hideCancelModal
  };

})();