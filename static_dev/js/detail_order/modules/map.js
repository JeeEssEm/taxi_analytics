window.OrderMap = (function() {
  'use strict';

  let map = null;
  let routeObject = null;
  let pickupPlacemark = null;
  let dropoffPlacemark = null;

  const mapElement = document.getElementById('map');
  const mapLoading = document.getElementById('map-loading');

  /**
   * Инициализация модуля карты
   */
  function init(orderData) {
    console.log('OrderMap: Initializing...');

    if (!mapElement) {
      console.error('OrderMap: Map element not found');
      return;
    }

    if (typeof ymaps === 'undefined') {
      console.error('OrderMap: Yandex Maps API not loaded');
      showError('Ошибка загрузки карт');
      return;
    }

    ymaps.ready(() => {
      createMap(orderData);
    });
  }


  function createMap(orderData) {
    try {
      console.log('OrderMap: Creating map...');

      map = new ymaps.Map('map', {
        center: [55.751574, 37.573856],
        zoom: 12,
        controls: ['zoomControl', 'trafficControl']
      });

      console.log('OrderMap: Map created successfully');

      if (orderData.fromCoords && orderData.toCoords) {
        displayRoute(orderData);
      } else {
        console.warn('OrderMap: No route coordinates available');
        hideLoading();
      }

    } catch (error) {
      console.error('OrderMap: Error creating map:', error);
      showError('Ошибка создания карты');
    }
  }


  function displayRoute(orderData) {
    console.log('OrderMap: Displaying route');

    const { fromCoords, toCoords, fromAddress, toAddress } = orderData;

    try {
      createPlacemarks(fromCoords, toCoords, fromAddress, toAddress);

      buildRoute(fromCoords, toCoords);

    } catch (error) {
      console.error('OrderMap: Error displaying route:', error);
      showError('Ошибка отображения маршрута');
    }
  }


  function createPlacemarks(fromCoords, toCoords, fromAddress, toAddress) {
    pickupPlacemark = new ymaps.Placemark(fromCoords, {
      balloonContent: `<strong>Откуда:</strong><br>${fromAddress}`,
      hintContent: 'Точка отправления'
    }, {
      preset: 'islands#blueCircleDotIcon'
    });

    dropoffPlacemark = new ymaps.Placemark(toCoords, {
      balloonContent: `<strong>Куда:</strong><br>${toAddress}`,
      hintContent: 'Точка назначения'
    }, {
      preset: 'islands#greenCircleDotIcon'
    });

    map.geoObjects.add(pickupPlacemark);
    map.geoObjects.add(dropoffPlacemark);

    console.log('OrderMap: Placemarks created');
  }


  function buildRoute(fromCoords, toCoords) {
    ymaps.route([fromCoords, toCoords], {
      multiRoute: false,
      routingMode: 'auto'
    })
    .then(function(route) {
      console.log('OrderMap: Route built successfully');

      routeObject = route;
      map.geoObjects.add(route);

      map.setBounds(route.getBounds(), {
        checkZoomRange: true,
        zoomMargin: 50
      });

      hideLoading();
    })
    .catch(function(error) {
      console.warn('OrderMap: Could not build route, centering on points:', error);

      const bounds = [fromCoords, toCoords];
      map.setBounds(bounds, {
        checkZoomRange: true,
        zoomMargin: 50
      });

      hideLoading();
    });
  }

  function hideLoading() {
    if (mapLoading) {
      mapLoading.style.display = 'none';
    }
  }

  function showError(message) {
    if (mapLoading) {
      mapLoading.innerHTML = `
        <div class="text-center">
          <div class="text-red-600 mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p class="text-gray-600">${message}</p>
        </div>
      `;
    }
  }

  function destroy() {
    if (routeObject && map) {
      map.geoObjects.remove(routeObject);
    }
    if (pickupPlacemark && map) {
      map.geoObjects.remove(pickupPlacemark);
    }
    if (dropoffPlacemark && map) {
      map.geoObjects.remove(dropoffPlacemark);
    }

    map = null;
    routeObject = null;
    pickupPlacemark = null;
    dropoffPlacemark = null;
  }

  return {
    init: init,
    destroy: destroy
  };

})();