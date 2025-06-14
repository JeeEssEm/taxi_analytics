/**
 * Основной скрипт страницы детального просмотра заказа
 * Координирует работу всех модулей
 */
document.addEventListener('DOMContentLoaded', function() {
  console.log('Order detail page initialized');

  // Проверяем наличие необходимых данных
  if (!window.ORDER_DATA) {
    console.error('ORDER_DATA not found');
    return;
  }

  // Инициализируем модули
  try {
    // Инициализируем карту
    if (window.OrderMap) {
      window.OrderMap.init(window.ORDER_DATA);
    }

    // Инициализируем обновление статуса
    if (window.StatusUpdater) {
      window.StatusUpdater.init({
        orderId: window.ORDER_ID,
        statusUrl: window.ORDER_STATUS_URL,
        initialStatus: window.ORDER_DATA.status,
        hasDriver: window.ORDER_DATA.hasDriver
      });
    }

    // Инициализируем действия пользователя
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