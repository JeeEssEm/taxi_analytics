document.addEventListener('DOMContentLoaded', function() {
  console.log('Order detail page initialized');

  if (!window.ORDER_DATA) {
    console.error('ORDER_DATA not found');
    return;
  }

  try {
    if (window.OrderMap) {
      window.OrderMap.init(window.ORDER_DATA);
    }

    if (window.StatusUpdater) {
      window.StatusUpdater.init({
        orderId: window.ORDER_ID,
        statusUrl: window.ORDER_STATUS_URL,
        initialStatus: window.ORDER_DATA.status,
        hasDriver: window.ORDER_DATA.hasDriver,
        reviewUrl: window.REVIEW_URL,
      });
    }

    if (window.UserActions) {
      window.UserActions.init({
        cancelUrl: window.CANCEL_ORDER_URL,
        isCustomer: window.ORDER_DATA.isCustomer
      });
    }

  } catch (error) {
    console.error('Error initializing modules:', error);
  }

  console.log('All modules initialized');
});