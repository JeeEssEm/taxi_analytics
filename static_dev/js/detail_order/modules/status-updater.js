window.StatusUpdater = (function() {
  'use strict';

  let config = {};
  let updateInterval = null;
  let lastKnownStatus = null;
  let lastKnownDriverState = null;
  let lastDriverData = null; // Сохраняем последние данные водителя

  const statusBadge = document.getElementById('status-badge');
  const statusIcon = document.getElementById('status-icon');
  const statusText = document.getElementById('status-text');
  const driverInfo = document.getElementById('driver-info');
  const waitingDriver = document.getElementById('waiting-driver');

  function init(options) {
    console.log('StatusUpdater: Initializing with options:', options);

    config = {
      orderId: options.orderId,
      statusUrl: options.statusUrl,
      updateInterval: options.updateInterval || 5000,
      reviewUrl: options.reviewUrl,
      ...options
    };

    lastKnownStatus = config.initialStatus;
    lastKnownDriverState = config.hasDriver;

    console.log('StatusUpdater: Initial status:', lastKnownStatus);
    console.log('StatusUpdater: Initial hasDriver:', lastKnownDriverState);

    initialStatusSync().then(() => {
      startUpdates();
    });

    setupEventListeners();

    console.log('StatusUpdater: Initialized');
  }

  function initialStatusSync() {
    console.log('StatusUpdater: Performing initial status sync...');

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
      console.log('StatusUpdater: Initial sync received data:', data);

      forceUpdateDisplay(data);

      lastKnownStatus = data.status;
      lastKnownDriverState = data.has_driver;
      if (data.driver) {
        lastDriverData = data.driver;
      }

      console.log('StatusUpdater: Initial sync completed');

      checkForCompletedOrder(data);
    })
    .catch(error => {
      console.error('StatusUpdater: Error during initial sync:', error);
    });
  }

  function forceUpdateDisplay(data) {
    console.log('StatusUpdater: Force updating display with data:', data);

    updateStatusDisplay(data);
    updateDriverDisplay(data);
  }

  function startUpdates() {
    console.log('StatusUpdater: Starting automatic updates every', config.updateInterval, 'ms');

    updateInterval = setInterval(updateStatus, config.updateInterval);

    window.addEventListener('focus', updateStatus);
  }

  function stopUpdates() {
    if (updateInterval) {
      clearInterval(updateInterval);
      updateInterval = null;
      console.log('StatusUpdater: Updates stopped');
    }
  }

  function setupEventListeners() {
    window.addEventListener('beforeunload', stopUpdates);
  }

  function updateStatus() {
    console.log('StatusUpdater: Requesting periodic status update...');

    fetch(config.statusUrl, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => {
      console.log('StatusUpdater: Response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('StatusUpdater: Received periodic data:', data);

      const statusChanged = data.status !== lastKnownStatus;
      const driverChanged = data.has_driver !== lastKnownDriverState;

      // Проверяем, изменились ли данные водителя
      const driverDataChanged = JSON.stringify(data.driver) !== JSON.stringify(lastDriverData);

      console.log('StatusUpdater: Status changed:', statusChanged, `(${lastKnownStatus} -> ${data.status})`);
      console.log('StatusUpdater: Driver changed:', driverChanged, `(${lastKnownDriverState} -> ${data.has_driver})`);
      console.log('StatusUpdater: Driver data changed:', driverDataChanged);

      if (statusChanged) {
        handleStatusChange(data);
      }

      // Обновляем отображение водителя при любых изменениях
      if (driverChanged || driverDataChanged) {
        updateDriverDisplay(data);

        // Показываем уведомление только при назначении нового водителя
        if (driverChanged && data.has_driver && data.driver) {
          if (window.NotificationManager) {
            window.NotificationManager.showSuccess(`Водитель назначен: ${data.driver.name}`);
          }
        }
      }

      // Принудительно проверяем отображение водителя
      verifyDriverDisplay(data);

      lastKnownStatus = data.status;
      lastKnownDriverState = data.has_driver;
      if (data.driver) {
        lastDriverData = data.driver;
      }

      checkForCompletedOrder(data);
    })
    .catch(error => {
      console.error('StatusUpdater: Error updating status:', error);
    });
  }

  function handleStatusChange(data) {
    console.log('StatusUpdater: Handling status change with data:', data);

    updateStatusDisplay(data);
    showChangeNotification(data);
    dispatchStatusChangeEvent(data);
  }

  // Новая функция для проверки корректности отображения водителя
  function verifyDriverDisplay(data) {
    if (data.has_driver && data.driver) {
      // Проверяем, отображается ли блок с водителем
      const isDriverVisible = driverInfo && !driverInfo.classList.contains('hidden');
      const isWaitingVisible = waitingDriver && !waitingDriver.classList.contains('hidden');

      console.log('StatusUpdater: Driver display verification:', {
        hasDriver: data.has_driver,
        driverData: !!data.driver,
        driverVisible: isDriverVisible,
        waitingVisible: isWaitingVisible
      });

      // Если водитель должен отображаться, но блок скрыт - принудительно показываем
      if (!isDriverVisible) {
        console.log('StatusUpdater: Driver should be visible but is hidden, forcing display update');
        updateDriverDisplay(data);

        // Дополнительная проверка через полсекунды
        setTimeout(() => {
          const stillHidden = driverInfo && driverInfo.classList.contains('hidden');
          if (stillHidden) {
            console.error('StatusUpdater: Driver info still hidden after forced update');
            // Последняя попытка
            showDriverInfo(data.driver);
          }
        }, 500);
      }
    }
  }

  function checkForCompletedOrder(data) {
    console.log('StatusUpdater: Checking for completed order, status:', data.status);

    if (data.status === 'DONE' && config.reviewUrl) {
      console.log('StatusUpdater: Order completed, redirecting to review page');

      if (window.NotificationManager) {
        window.NotificationManager.showSuccess('Заказ завершен! Переходим к оценке...');
      }

      setTimeout(() => {
        window.location.href = config.reviewUrl;
      }, 2000);

      stopUpdates();
    }
  }

  function updateStatusDisplay(data) {
    console.log('StatusUpdater: Updating status display:', data.status_display);

    if (statusIcon) statusIcon.textContent = data.status_icon || '📋';
    if (statusText) statusText.textContent = data.status_display || 'Неизвестно';

    if (statusBadge) {
      const colorClasses = ['yellow', 'blue', 'indigo', 'purple', 'green', 'red', 'gray'];
      colorClasses.forEach(color => {
        statusBadge.classList.remove(`bg-${color}-100`, `text-${color}-800`);
      });

      const statusColor = data.status_color || 'gray';
      statusBadge.classList.add(`bg-${statusColor}-100`, `text-${statusColor}-800`);

      if (data.status !== config.initialStatus || data.has_driver !== config.hasDriver) {
        statusBadge.style.transform = 'scale(1.05)';
        setTimeout(() => {
          statusBadge.style.transform = '';
        }, 300);
      }
    }
  }

  function updateDriverDisplay(data) {
    console.log('StatusUpdater: Updating driver display');
    console.log('StatusUpdater: has_driver:', data.has_driver);
    console.log('StatusUpdater: driver data:', data.driver);

    if (!driverInfo || !waitingDriver) {
      console.error('StatusUpdater: Required elements not found', {
        driverInfo: !!driverInfo,
        waitingDriver: !!waitingDriver
      });
      return;
    }

    if (data.has_driver && data.driver) {
      console.log('StatusUpdater: Showing driver info');
      showDriverInfo(data.driver);
    } else {
      console.log('StatusUpdater: Showing waiting state');
      showWaitingState(data);
    }
  }

  function showDriverInfo(driverData) {
    console.log('StatusUpdater: Showing driver info for:', driverData);

    if (!driverInfo || !waitingDriver) {
      console.error('StatusUpdater: Driver info elements not found');
      return;
    }

    if (!driverData || !driverData.name) {
      console.error('StatusUpdater: Invalid driver data', driverData);
      return;
    }

    const driverDetails = document.getElementById('driver-details');
    if (driverDetails) {
      const html = generateDriverHTML(driverData);
      console.log('StatusUpdater: Setting driver HTML');
      driverDetails.innerHTML = html;
    } else {
      console.error('StatusUpdater: driver-details element not found');
    }

    console.log('StatusUpdater: Showing driver-info, hiding waiting-driver');
    driverInfo.classList.remove('hidden');
    waitingDriver.classList.add('hidden');

    // Проверяем результат
    setTimeout(() => {
      const isVisible = !driverInfo.classList.contains('hidden');
      console.log('StatusUpdater: Driver info visibility check:', isVisible);

      if (!isVisible) {
        console.error('StatusUpdater: Failed to show driver info, trying again');
        driverInfo.classList.remove('hidden');
      }
    }, 100);
  }

  function showWaitingState(statusData) {
    console.log('StatusUpdater: Showing waiting state for:', statusData);

    if (!driverInfo || !waitingDriver) {
      console.error('StatusUpdater: Waiting elements not found');
      return;
    }

    const waitingTitle = waitingDriver.querySelector('h3');
    const waitingDescription = waitingDriver.querySelector('p');

    if (waitingTitle && statusData.status_display) {
      waitingTitle.textContent = statusData.status_display;
    }
    if (waitingDescription && statusData.status_description) {
      waitingDescription.textContent = statusData.status_description;
    }

    console.log('StatusUpdater: Hiding driver-info, showing waiting-driver');
    driverInfo.classList.add('hidden');
    waitingDriver.classList.remove('hidden');
  }

  function generateDriverHTML(driver) {
    console.log('StatusUpdater: Generating HTML for driver:', driver);

    if (!driver || !driver.name) {
      console.error('StatusUpdater: Cannot generate HTML for invalid driver data');
      return '<p class="text-red-500">Ошибка загрузки данных водителя</p>';
    }

    const phoneLink = driver.phone ?
      `<a href="tel:${driver.phone}" class="font-medium text-purple-600 hover:text-purple-700">${driver.phone}</a>` :
      '<span class="text-gray-400">Не указан</span>';

    const avatar = driver.image_url ?
      `<img src="${driver.image_url}" alt="Фото водителя" class="w-12 h-12 rounded-full object-cover">` :
      `<div class="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
        ${driver.name.split(' ').map(n => n[0]).join('').toUpperCase()}
      </div>`;

    const html = `
      <div class="flex items-center space-x-4 mb-4">
        ${avatar}
        <div>
          <p class="font-semibold text-gray-800">${driver.name}</p>
          <p class="text-sm text-gray-600">Водитель</p>
        </div>
      </div>
      
      <div class="space-y-3">
        <div class="flex justify-between">
          <span class="text-gray-500">Телефон:</span>
          ${phoneLink}
        </div>
        ${driver.car_model ? `
        <div class="flex justify-between">
          <span class="text-gray-500">Автомобиль:</span>
          <span class="font-medium">${driver.car_model}</span>
        </div>` : ''}
        ${driver.car_number ? `
        <div class="flex justify-between">
          <span class="text-gray-500">Номер:</span>
          <span class="font-medium">${driver.car_number}</span>
        </div>` : ''}
        ${driver.car_color ? `
        <div class="flex justify-between">
          <span class="text-gray-500">Цвет:</span>
          <span class="font-medium">${driver.car_color}</span>
        </div>` : ''}
        ${driver.car_year ? `
        <div class="flex justify-between">
          <span class="text-gray-500">Год:</span>
          <span class="font-medium">${driver.car_year}</span>
        </div>` : ''}
      </div>
      
      ${driver.phone ? `
      <div class="mt-4 pt-4 border-t">
        <a href="tel:${driver.phone}" class="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg transition duration-300 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
          </svg>
          Позвонить водителю
        </a>
      </div>` : ''}
    `;

    return html;
  }

  function showChangeNotification(data) {
    if (window.NotificationManager && data && data.status_display) {
      window.NotificationManager.showStatusChange(data);
    }
  }

  function dispatchStatusChangeEvent(data) {
    const event = new CustomEvent('statusChanged', {
      detail: data
    });
    document.dispatchEvent(event);
  }

  return {
    init: init,
    updateStatus: updateStatus,
    stopUpdates: stopUpdates,
    getCurrentStatus: () => lastKnownStatus,
    forceSync: initialStatusSync,
    verifyDriverDisplay: () => verifyDriverDisplay({ has_driver: lastKnownDriverState, driver: lastDriverData })
  };

})();