window.StatusUpdater = (function() {
  'use strict';

  let config = {};
  let updateInterval = null;
  let lastKnownStatus = null;
  let lastKnownDriverState = null;

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

      console.log('StatusUpdater: Initial sync completed');
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

      console.log('StatusUpdater: Status changed:', statusChanged, `(${lastKnownStatus} -> ${data.status})`);
      console.log('StatusUpdater: Driver changed:', driverChanged, `(${lastKnownDriverState} -> ${data.has_driver})`);

      if (statusChanged || driverChanged) {
        console.log('StatusUpdater: Processing changes...');
        handleStatusChange(data);
        lastKnownStatus = data.status;
        lastKnownDriverState = data.has_driver;
      } else {
        console.log('StatusUpdater: No changes detected');
      }
    })
    .catch(error => {
      console.error('StatusUpdater: Error updating status:', error);
    });
  }

  function handleStatusChange(data) {
    console.log('StatusUpdater: Handling status change with data:', data);

    updateStatusDisplay(data);
    updateDriverDisplay(data);
    showChangeNotification(data);

    dispatchStatusChangeEvent(data);
  }

  function updateStatusDisplay(data) {
    console.log('StatusUpdater: Updating status display:', data.status_display);

    if (statusIcon) statusIcon.textContent = data.status_icon;
    if (statusText) statusText.textContent = data.status_display;

    if (statusBadge) {
      const colorClasses = ['yellow', 'blue', 'indigo', 'purple', 'green', 'red', 'gray'];
      colorClasses.forEach(color => {
        statusBadge.classList.remove(`bg-${color}-100`, `text-${color}-800`);
      });

      statusBadge.classList.add(`bg-${data.status_color}-100`, `text-${data.status_color}-800`);

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
    console.log('StatusUpdater: driverInfo element:', driverInfo);
    console.log('StatusUpdater: waitingDriver element:', waitingDriver);

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
      console.error('StatusUpdater: Driver info elements not found', {
        driverInfo: !!driverInfo,
        waitingDriver: !!waitingDriver
      });
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

    setTimeout(() => {
      console.log('StatusUpdater: Display state after driver update:', {
        driverVisible: !driverInfo.classList.contains('hidden'),
        waitingVisible: !waitingDriver.classList.contains('hidden'),
        driverClasses: driverInfo.className,
        waitingClasses: waitingDriver.className
      });
    }, 100);
  }

  function showWaitingState(statusData) {
    console.log('StatusUpdater: Showing waiting state for:', statusData);

    if (!driverInfo || !waitingDriver) {
      console.error('StatusUpdater: Waiting elements not found', {
        driverInfo: !!driverInfo,
        waitingDriver: !!waitingDriver
      });
      return;
    }

    const waitingTitle = waitingDriver.querySelector('h3');
    const waitingDescription = waitingDriver.querySelector('p');

    if (waitingTitle) {
      waitingTitle.textContent = statusData.status_display;
      console.log('StatusUpdater: Updated waiting title to:', statusData.status_display);
    }
    if (waitingDescription) {
      waitingDescription.textContent = statusData.status_description;
      console.log('StatusUpdater: Updated waiting description to:', statusData.status_description);
    }

    console.log('StatusUpdater: Hiding driver-info, showing waiting-driver');
    driverInfo.classList.add('hidden');
    waitingDriver.classList.remove('hidden');

    setTimeout(() => {
      console.log('StatusUpdater: Display state after waiting update:', {
        driverVisible: !driverInfo.classList.contains('hidden'),
        waitingVisible: !waitingDriver.classList.contains('hidden'),
        driverClasses: driverInfo.className,
        waitingClasses: waitingDriver.className
      });
    }, 100);
  }


  function generateDriverHTML(driver) {
    console.log('StatusUpdater: Generating HTML for driver:', driver);

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
    if (window.NotificationManager) {
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
    forceSync: initialStatusSync
  };

})();