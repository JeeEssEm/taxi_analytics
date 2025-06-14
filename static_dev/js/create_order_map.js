document.addEventListener('DOMContentLoaded', function() {
  let map;
  let activeField = null;
  let placemarkFrom = null;
  let placemarkTo = null;
  let routeObject = null;

  let fromCoords = null;
  let toCoords = null;

  let searchTimeout = null;
  let priceCalculationTimeout = null;

  // Добавляем переменные для данных заказа
  let lastOrderData = null;
  let lastOrderSignature = null;

  ymaps.ready(initMap);

  const timePicker = flatpickr('#scheduled-time', {
    enableTime: true,
    noCalendar: true,
    dateFormat: "H:i",
    time_24hr: true,
    minuteIncrement: 5,
    locale: "ru",
    defaultDate: new Date().setHours(new Date().getHours() + 1),
    minTime: "now",
    maxTime: "23:59"
  });

  // Переключение между "Сейчас" и "Позже"
  document.querySelectorAll('input[name="time_type"]').forEach(radio => {
    radio.addEventListener('change', function() {
      document.getElementById('time-picker-container').style.display =
        this.value === 'later' ? 'block' : 'none';
      scheduleCalculatePrice(); // Добавляем пересчет цены
    });
  });

  const passengersInput = document.getElementById('passengers');
  const passengersValue = document.getElementById('passengers-value');
  const passengersTrack = document.getElementById('passengers-track');

  function updatePassengers(value) {
    passengersValue.textContent = value;
    passengersInput.value = value;
    passengersTrack.style.width = `${(value - 1) * 33.33}%`;
    scheduleCalculatePrice();
  }

  updatePassengers(passengersInput.value);

  passengersInput.addEventListener('input', function() {
    updatePassengers(this.value);
  });

  document.getElementById('decrease-passengers').addEventListener('click', function() {
    let value = parseInt(passengersInput.value);
    if (value > 1) {
      updatePassengers(value - 1);
    }
  });

  document.getElementById('increase-passengers').addEventListener('click', function() {
    let value = parseInt(passengersInput.value);
    if (value < 4) {
      updatePassengers(value + 1);
    }
  });

  document.querySelectorAll('input[name="payment_method"]').forEach(radio => {
    radio.addEventListener('change', scheduleCalculatePrice);
  });

  document.getElementById('scheduled-time').addEventListener('change', scheduleCalculatePrice);
  document.getElementById('comment').addEventListener('input', debounce(scheduleCalculatePrice, 1000));

  setupAddressAutocomplete('from-address', 'from-suggestions');
  setupAddressAutocomplete('to-address', 'to-suggestions');

  function setupAddressAutocomplete(inputId, suggestionsId) {
    const input = document.getElementById(inputId);
    const suggestions = document.getElementById(suggestionsId);

    input.addEventListener('input', function() {
      const query = this.value.trim();

      if (query.length < 3) {
        hideSuggestions(suggestionsId);
        return;
      }

      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }

      searchTimeout = setTimeout(() => {
        searchAddresses(query, suggestionsId, inputId);
      }, 300);
    });

    input.addEventListener('blur', function() {
      setTimeout(() => {
        hideSuggestions(suggestionsId);
      }, 200);
    });

    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (this.value.trim()) {
          geocodeAddress(this.value.trim(), inputId);
          hideSuggestions(suggestionsId);
        }
      }
    });
  }

  function searchAddresses(query, suggestionsId, inputId) {
    if (!ymaps || !ymaps.suggest) {
      console.log('Suggest API недоступен, используем геокодирование');
      return;
    }

    ymaps.suggest(query, {
      results: 5,
      boundedBy: [[55.142627, 36.803164], [56.021281, 38.967407]]
    }).then(function(items) {
      showSuggestions(items, suggestionsId, inputId);
    }).catch(function(error) {
      console.log('Ошибка поиска адресов:', error);
      hideSuggestions(suggestionsId);
    });
  }

  function showSuggestions(items, suggestionsId, inputId) {
    const suggestions = document.getElementById(suggestionsId);
    suggestions.innerHTML = '';

    if (items.length === 0) {
      hideSuggestions(suggestionsId);
      return;
    }

    items.forEach(function(item) {
      const div = document.createElement('div');
      div.className = 'suggestion-item';
      div.textContent = item.displayName;
      div.addEventListener('click', function() {
        document.getElementById(inputId).value = item.displayName;
        geocodeAddress(item.displayName, inputId);
        hideSuggestions(suggestionsId);
      });
      suggestions.appendChild(div);
    });

    suggestions.classList.remove('hidden');
  }

  function hideSuggestions(suggestionsId) {
    document.getElementById(suggestionsId).classList.add('hidden');
  }

  document.getElementById('from-address').addEventListener('input', function() {
    if (this.value.trim() === '') {
      clearPoint('from');
    }
  });

  document.getElementById('to-address').addEventListener('input', function() {
    if (this.value.trim() === '') {
      clearPoint('to');
    }
  });

  function initMap() {
    map = new ymaps.Map('map', {
      center: [55.751574, 37.573856],
      zoom: 12,
      controls: ['zoomControl', 'geolocationControl', 'trafficControl']
    });

    document.getElementById('set-from-map').addEventListener('click', function() {
      activateField('from-address');
    });

    document.getElementById('set-to-map').addEventListener('click', function() {
      activateField('to-address');
    });

    document.getElementById('clear-map').addEventListener('click', clearAll);
    document.getElementById('cancel-map-selection').addEventListener('click', deactivateField);

    document.getElementById('get-location').addEventListener('click', function() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
          const coords = [position.coords.latitude, position.coords.longitude];
          setPointOnMap(coords, 'from-address');
          map.setCenter(coords, 15);
        }, function(error) {
          console.log('Ошибка геолокации:', error);
          alert('Не удалось определить ваше местоположение');
        });
      } else {
        alert('Геолокация не поддерживается браузером');
      }
    });

    map.events.add('click', function(e) {
      if (!activeField) return;

      e.preventDefault();
      e.stopPropagation();

      const coords = e.get('coords');
      setPointOnMap(coords, activeField);
      deactivateField();
    });

    // Восстановление состояния после ошибки
    const fromCoordsValue = document.getElementById('from-coords').value;
    const toCoordsValue = document.getElementById('to-coords').value;

    if (fromCoordsValue) {
      const coords = fromCoordsValue.split(',').map(parseFloat);
      setPointOnMap(coords, 'from-address', false);
    }

    if (toCoordsValue) {
      const coords = toCoordsValue.split(',').map(parseFloat);
      setPointOnMap(coords, 'to-address', false);
    }
  }

  function geocodeAddress(address, fieldId) {
    if (!address.trim()) return;

    ymaps.geocode(address, {
      results: 1,
      boundedBy: [[55.142627, 36.803164], [56.021281, 38.967407]]
    }).then(function(res) {
      const firstGeoObject = res.geoObjects.get(0);
      if (firstGeoObject) {
        const coords = firstGeoObject.geometry.getCoordinates();
        const preciseName = firstGeoObject.getAddressLine();

        document.getElementById(fieldId).value = preciseName;
        setPointOnMap(coords, fieldId, false);
      } else {
        console.log('Адрес не найден:', address);
      }
    }).catch(function(error) {
      console.log('Ошибка геокодирования:', error);
    });
  }

  function setPointOnMap(coords, fieldId, updateAddress = true) {
    if (fieldId === 'from-address' && placemarkFrom) {
      map.geoObjects.remove(placemarkFrom);
    }
    if (fieldId === 'to-address' && placemarkTo) {
      map.geoObjects.remove(placemarkTo);
    }

    const placemark = new ymaps.Placemark(coords, {
      balloonContent: fieldId === 'from-address' ? 'Точка отправления' : 'Точка назначения'
    }, {
      preset: fieldId === 'from-address' ?
        'islands#blueCircleDotIcon' :
        'islands#greenCircleDotIcon',
      draggable: true
    });

    placemark.events.add('dragend', function() {
      const newCoords = placemark.geometry.getCoordinates();
      setCoordinates(newCoords, fieldId);
      updateAddressFromCoords(newCoords, fieldId);
      autoCalculateRoute();
    });

    map.geoObjects.add(placemark);

    if (fieldId === 'from-address') {
      placemarkFrom = placemark;
      fromCoords = coords;
    } else {
      placemarkTo = placemark;
      toCoords = coords;
    }

    setCoordinates(coords, fieldId);

    if (updateAddress && !document.getElementById(fieldId).value.trim()) {
      updateAddressFromCoords(coords, fieldId);
    }

    autoCalculateRoute();
  }

  function clearPoint(type) {
    if (type === 'from') {
      fromCoords = null;
      document.getElementById('from-coords').value = '';
      if (placemarkFrom) {
        map.geoObjects.remove(placemarkFrom);
        placemarkFrom = null;
      }
    } else {
      toCoords = null;
      document.getElementById('to-coords').value = '';
      if (placemarkTo) {
        map.geoObjects.remove(placemarkTo);
        placemarkTo = null;
      }
    }
    clearRoute();
    resetPrice();
  }

  function setCoordinates(coords, fieldId) {
    const coordsField = fieldId === 'from-address' ? 'from-coords' : 'to-coords';
    document.getElementById(coordsField).value = coords[0] + ',' + coords[1];
    scheduleCalculatePrice();
  }

  function updateAddressFromCoords(coords, fieldId) {
    ymaps.geocode(coords, { results: 1 }).then(function(res) {
      const firstGeoObject = res.geoObjects.get(0);
      if (firstGeoObject) {
        document.getElementById(fieldId).value = firstGeoObject.getAddressLine();
      }
    }).catch(function(error) {
      console.log('Ошибка обратного геокодирования:', error);
    });
  }

  function autoCalculateRoute() {
    if (!fromCoords || !toCoords) {
      return;
    }

    clearRoute();

    ymaps.route([fromCoords, toCoords], {
      multiRoute: false,
      routingMode: 'auto'
    }).then(function(route) {
      routeObject = route;
      map.geoObjects.add(route);

      const activeRoute = route.getActiveRoute();
      const distance = Math.round(activeRoute.properties.get('distance') / 1000 * 10) / 10;
      const duration = Math.round(activeRoute.properties.get('duration') / 60);

      document.getElementById('route-distance').textContent = distance + ' км';
      document.getElementById('route-duration').textContent = duration + ' мин';

      document.getElementById('route-info').classList.remove('hidden');

      map.setBounds(route.getBounds(), {
        checkZoomRange: true,
        zoomMargin: 50
      });
    }).catch(function(error) {
      console.log('Не удалось построить маршрут:', error);
    });
  }

  function scheduleCalculatePrice() {
    if (priceCalculationTimeout) {
      clearTimeout(priceCalculationTimeout);
    }
    showPriceLoading();

    priceCalculationTimeout = setTimeout(() => {
      calculatePriceFromServer();
    }, 800);
  }

  function showPriceLoading() {
    const priceElement = document.getElementById('price');
    const routePriceElement = document.getElementById('route-price');

    priceElement.classList.add('price-loading');
    routePriceElement.classList.add('price-loading');
  }

  function hidePriceLoading() {
    const priceElement = document.getElementById('price');
    const routePriceElement = document.getElementById('route-price');

    priceElement.classList.remove('price-loading');
    routePriceElement.classList.remove('price-loading');
  }

  function calculatePriceFromServer() {
    const fromCoordsValue = document.getElementById('from-coords').value;
    const toCoordsValue = document.getElementById('to-coords').value;
    const passengers = document.getElementById('passengers').value;
    const paymentMethod = document.querySelector('input[name="payment_method"]:checked')?.value || 'cash';
    const timeType = document.querySelector('input[name="time_type"]:checked')?.value || 'now';
    const scheduledTime = document.getElementById('scheduled-time').value;
    const comment = document.getElementById('comment').value;

    if (!fromCoordsValue || !toCoordsValue) {
      resetPrice();
      return;
    }

    const orderData = {
      pickup_coords: fromCoordsValue,
      dropoff_coords: toCoordsValue,
      passengers: parseInt(passengers),
      payment_method: paymentMethod,
      time_type: timeType,
      scheduled_time: timeType === 'later' ? scheduledTime : '',
      comment: comment.trim()
    };

    fetch(window.CALCULATE_PRICE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: JSON.stringify(orderData)
    })
    .then(response => response.json())
    .then(data => {
      hidePriceLoading();

      if (data.success) {
        lastOrderData = data.order_data;
        lastOrderSignature = data.order_signature;

        updatePriceDisplay(
          data.price,
          data.distance,
          data.duration,
          data.tariff,
          data.calculation_method
        );

        updateHiddenFormFields();
      } else {
        console.log('Ошибка расчета цены:', data.error);
        resetPrice();
        lastOrderData = null;
        lastOrderSignature = null;
      }
    })
    .catch(error => {
      hidePriceLoading();
      console.log('Ошибка запроса цены:', error);
      resetPrice();
      lastOrderData = null;
      lastOrderSignature = null;
    });
  }

  function updateHiddenFormFields() {
    if (!lastOrderData || !lastOrderSignature) return;

    const form = document.getElementById('taxi-order-form');
    const oldSignatureField = form.querySelector('input[name="order_signature"]');
    const oldDataField = form.querySelector('input[name="order_data"]');

    if (oldSignatureField) oldSignatureField.remove();
    if (oldDataField) oldDataField.remove();

    const signatureField = document.createElement('input');
    signatureField.type = 'hidden';
    signatureField.name = 'order_signature';
    signatureField.value = lastOrderSignature;
    form.appendChild(signatureField);

    const dataField = document.createElement('input');
    dataField.type = 'hidden';
    dataField.name = 'order_data';
    dataField.value = JSON.stringify(lastOrderData);
    form.appendChild(dataField);
  }

  function updatePriceDisplay(price, distance, duration) {
    document.getElementById('price').textContent = price + ' ₽';
    document.getElementById('route-price').textContent = price + ' ₽';

    if (distance) {
      document.getElementById('distance').textContent = distance + ' км';
    }
    if (duration) {
      document.getElementById('duration').textContent = duration + ' мин';
    }
  }

  function resetPrice() {
    hidePriceLoading();
    document.getElementById('price').textContent = '-';
    document.getElementById('route-price').textContent = '-';
    document.getElementById('distance').textContent = '-';
    document.getElementById('duration').textContent = '-';

    lastOrderData = null;
    lastOrderSignature = null;
    updateHiddenFormFields();
  }

  function clearRoute() {
    if (routeObject) {
      map.geoObjects.remove(routeObject);
      routeObject = null;
    }
    document.getElementById('route-info').classList.add('hidden');
  }

  function clearAll() {
    document.getElementById('from-address').value = '';
    document.getElementById('to-address').value = '';
    clearPoint('from');
    clearPoint('to');

    hideSuggestions('from-suggestions');
    hideSuggestions('to-suggestions');

    map.setCenter([55.751574, 37.573856], 12);
  }

  function activateField(fieldId) {
    document.querySelectorAll('.address-field').forEach(field => {
      field.classList.remove('address-field-active');
    });

    activeField = fieldId;
    document.getElementById(fieldId).classList.add('address-field-active');
    document.getElementById('cancel-map-selection').classList.remove('hidden');
    document.getElementById('map').classList.add('map-selection-mode');

    map.balloon.open(map.getCenter(), {
      contentHeader: 'Выбор на карте',
      contentBody: `Кликните на карте, чтобы установить адрес для поля "${fieldId === 'from-address' ? 'Откуда' : 'Куда'}"`,
      contentFooter: '<em>Адрес будет определен автоматически</em>'
    });
  }

  function deactivateField() {
    if (!activeField) return;

    document.getElementById(activeField).classList.remove('address-field-active');
    activeField = null;
    document.getElementById('cancel-map-selection').classList.add('hidden');
    document.getElementById('map').classList.remove('map-selection-mode');
    map.balloon.close();
  }

  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Валидация формы перед отправкой
  document.getElementById('taxi-order-form').addEventListener('submit', function(e) {
    if (!lastOrderData || !lastOrderSignature) {
      e.preventDefault();
      alert('Пожалуйста, дождитесь расчета стоимости поездки');
      return false;
    }

    return true;
  });

  document.addEventListener('click', function(e) {
    if (!e.target.closest('.relative')) {
      hideSuggestions('from-suggestions');
      hideSuggestions('to-suggestions');
    }
  });
});