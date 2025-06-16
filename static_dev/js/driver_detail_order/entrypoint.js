document.addEventListener('DOMContentLoaded', function() {
  console.log('Driver order detail page initialized');

  if (!window.ORDER_DATA) {
    console.error('ORDER_DATA not found');
    return;
  }

  try {
    if (window.OrderMap) {
      window.OrderMap.init(window.ORDER_DATA);
    }

    if (window.DriverStatusUpdater) {
      window.DriverStatusUpdater.init({
        orderId: window.ORDER_ID,
        statusUrl: window.ORDER_STATUS_URL,
        initialStatus: window.ORDER_DATA.status,
        availableActions: window.ORDER_DATA.availableActions
      });
    }

    if (window.DriverActions) {
      window.DriverActions.init({
        updateStatusUrl: window.UPDATE_STATUS_URL,
        initialActions: window.ORDER_DATA.availableActions
      });
    }

  } catch (error) {
    console.error('Error initializing driver modules:', error);
  }

  console.log('All driver modules initialized');
});