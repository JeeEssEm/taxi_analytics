window.NotificationManager = (function() {
  'use strict';

  function showStatusChange(data) {
    const notification = createNotification(`
      <div class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-${data.status_color}-100 rounded-full flex items-center justify-center">
            <span class="text-${data.status_color}-600">${data.status_icon}</span>
          </div>
        </div>
        <div>
          <p class="font-medium text-gray-800">Статус изменен</p>
          <p class="text-sm text-gray-600">${data.status_display}</p>
        </div>
      </div>
    `, 'info');

    showNotification(notification);
  }

  function showSuccess(message) {
    const notification = createNotification(`
      <div class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
          </svg>
        </div>
        <p class="font-medium text-gray-800">${message}</p>
      </div>
    `, 'success');

    showNotification(notification);
  }

  function showError(message) {
    const notification = createNotification(`
      <div class="flex items-center space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
          </svg>
        </div>
        <p class="font-medium text-gray-800">${message}</p>
      </div>
    `, 'error');

    showNotification(notification);
  }

  function createNotification(content, type) {
    const colorClasses = {
      success: 'bg-green-100 border-green-200 text-green-800',
      error: 'bg-red-100 border-red-200 text-red-800',
      info: 'bg-blue-100 border-blue-200 text-blue-800'
    };

    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 ${colorClasses[type] || colorClasses.info} border rounded-lg shadow-lg p-4 z-50 transform translate-x-full transition-transform duration-300 max-w-sm`;

    notification.innerHTML = `
      ${content}
      <button class="absolute top-2 right-2 text-gray-500 hover:text-gray-700" onclick="this.parentElement.remove()">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
        </svg>
      </button>
    `;

    return notification;
  }

  function showNotification(notification) {
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.classList.remove('translate-x-full');
    }, 100);

    setTimeout(() => {
      if (notification.parentElement) {
        notification.classList.add('translate-x-full');
        setTimeout(() => {
          if (notification.parentElement) {
            notification.remove();
          }
        }, 300);
      }
    }, 5000);
  }

  return {
    showStatusChange: showStatusChange,
    showSuccess: showSuccess,
    showError: showError
  };

})();