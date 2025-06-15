/**
 * Модуль для автоматического обновления статуса заказа для водителя
 */
window.DriverStatusUpdater = (function() {
  'use strict';

  // Приватные переменные
  let config = {};
  let updateInterval = null;
  let lastKnownStatus = null;

  // DOM элементы
  const statusBadge = document.getElementById('status-badge');
  const statusIcon = document.getElementById('status-icon');
  const statusText = document.getElementById('status-text');
  const statusDescription = document.getElementById('status-description');

  // Статусы, при которых не нужно продолжать опросы
  const finalStatuses = ['DONE', 'CANCELLED'];

  // Статусы, когда отмена уже невозможна (клиент сел в машину)
  const noCheckStatuses = ['ON_THE_WAY', 'DONE'];

  /**
   * Инициализация модуля
   */
  function init(options) {
    console.log('DriverStatusUpdater: Initializing with options:', options);

    config = {
      orderId: options.orderId,
      statusUrl: options.statusUrl,
      updateInterval: options.updateInterval || 5000,
      ...options
    };

    lastKnownStatus = config.initialStatus;

    console.log('DriverStatusUpdater: Initial status:', lastKnownStatus);

    // Проверяем нужно ли вообще запускать обновления
    if (finalStatuses.includes(lastKnownStatus)) {
      console.log('DriverStatusUpdater: Order already in final status, skipping updates');
      return;
    }

    // Сразу при инициализации получаем актуальные данные с сервера
    initialStatusSync().then(() => {
      // Только после синхронизации запускаем периодические обновления
      if (!finalStatuses.includes(lastKnownStatus)) {
        startUpdates();
      }
    });

    setupEventListeners();

    console.log('DriverStatusUpdater: Initialized');
  }

  /**
   * Первоначальная синхронизация статуса при загрузке страницы
   */
  function initialStatusSync() {
    console.log('DriverStatusUpdater: Performing initial status sync...');

    return fetch(config.statusUrl, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('DriverStatusUpdater: Initial sync received data:', data);

      // Принудительно обновляем интерфейс на основе актуальных данных
      forceUpdateDisplay(data);

      // Обновляем наши переменные состояния
      lastKnownStatus = data.status;

      console.log('DriverStatusUpdater: Initial sync completed');
    })
    .catch(error => {
      console.error('DriverStatusUpdater: Error during initial sync:', error);
    });
  }

  /**
   * Принудительное обновление интерфейса (для начальной синхронизации)
   */
  function forceUpdateDisplay(data) {
    console.log('DriverStatusUpdater: Force updating display with data:', data);

    updateStatusDisplay(data);
    updateActions(data.available_actions);
  }

  /**
   * Запуск автоматических обновлений
   */
  function startUpdates() {
    console.log('DriverStatusUpdater: Starting automatic updates every', config.updateInterval, 'ms');

    // Обновляем каждые N секунд
    updateInterval = setInterval(updateStatus, config.updateInterval);

    // Обновляем при фокусе на страницу
    window.addEventListener('focus', updateStatus);
  }

  /**
   * Остановка обновлений
   */
  function stopUpdates() {
    if (updateInterval) {
      clearInterval(updateInterval);
      updateInterval = null;
      console.log('DriverStatusUpdater: Updates stopped');
    }
  }

  /**
   * Настройка событий
   */
  function setupEventListeners() {
    // Остановка обновлений при уходе со страницы
    window.addEventListener('beforeunload', stopUpdates);
  }

  /**
   * Обновление статуса с сервера (для периодических проверок)
   */
  function updateStatus() {
    // Если заказ в финальном статусе или клиент уже в машине, не проверяем
    if (finalStatuses.includes(lastKnownStatus)) {
      console.log('DriverStatusUpdater: Order in final status, stopping updates');
      stopUpdates();
      return;
    }

    if (noCheckStatuses.includes(lastKnownStatus)) {
      console.log('DriverStatusUpdater: Client is in car, no need to check cancellation');
      return;
    }

    console.log('DriverStatusUpdater: Requesting periodic status update...');

    fetch(config.statusUrl, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => {
      console.log('DriverStatusUpdater: Response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('DriverStatusUpdater: Received periodic data:', data);

      // Проверяем изменение статуса
      const statusChanged = data.status !== lastKnownStatus;

      console.log('DriverStatusUpdater: Status changed:', statusChanged, `(${lastKnownStatus} -> ${data.status})`);

      if (statusChanged) {
        console.log('DriverStatusUpdater: Processing status change...');
        handleStatusChange(data);
        lastKnownStatus = data.status;

        // Если новый статус финальный, останавливаем обновления
        if (finalStatuses.includes(data.status)) {
          console.log('DriverStatusUpdater: New status is final, stopping updates');
          stopUpdates();
        }
      } else {
        console.log('DriverStatusUpdater: No changes detected');
      }
    })
    .catch(error => {
      console.error('DriverStatusUpdater: Error updating status:', error);
    });
  }

  /**
   * Обработка изменения статуса (только для изменений, не для инициализации)
   */
  function handleStatusChange(data) {
    console.log('DriverStatusUpdater: Handling status change with data:', data);

    updateStatusDisplay(data);
    updateActions(data.available_actions);
    showChangeNotification(data);

    // Уведомляем другие модули об изменении
    dispatchStatusChangeEvent(data);
  }

  /**
   * Обновление отображения статуса
   */
  function updateStatusDisplay(data) {
    console.log('DriverStatusUpdater: Updating status display:', data.status_display);

    if (statusIcon) statusIcon.textContent = data.status_icon;
    if (statusText) statusText.textContent = data.status_display;
    if (statusDescription) statusDescription.textContent = data.status_description;

    if (statusBadge) {
      // Удаляем все возможные цветовые классы
      const colorClasses = ['yellow', 'blue', 'indigo', 'purple', 'green', 'red', 'gray'];
      colorClasses.forEach(color => {
        statusBadge.classList.remove(`bg-${color}-100`, `text-${color}-800`);
      });

      // Добавляем новые
      statusBadge.classList.add(`bg-${data.status_color}-100`, `text-${data.status_color}-800`);

      // Анимация обновления
      statusBadge.style.transform = 'scale(1.05)';
      setTimeout(() => {
        statusBadge.style.transform = '';
      }, 300);
    }
  }

  /**
   * Обновление доступных действий
   */
  function updateActions(actions) {
    console.log('DriverStatusUpdater: Updating actions:', actions);

    // Уведомляем модуль действий об обновлении
    if (window.DriverActions) {
      window.DriverActions.updateActions(actions);
    }
  }

  /**
   * Показ уведомления об изменении статуса
   */
  function showChangeNotification(data) {
    if (window.NotificationManager) {
      window.NotificationManager.showStatusChange(data);
    }
  }

  /**
   * Отправка события об изменении статуса
   */
  function dispatchStatusChangeEvent(data) {
    const event = new CustomEvent('statusChanged', {
      detail: data
    });
    document.dispatchEvent(event);
  }

  // Публичный API
  return {
    init: init,
    updateStatus: updateStatus,
    stopUpdates: stopUpdates,
    getCurrentStatus: () => lastKnownStatus
  };

})();