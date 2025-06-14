export class AddressAutocomplete {
  constructor(mapManager, routeManager) {
    this.mapManager = mapManager;
    this.routeManager = routeManager;
    this.searchTimeout = null;
  }

  init() {
    this.setupAddressAutocomplete('from-address', 'from-suggestions');
    this.setupAddressAutocomplete('to-address', 'to-suggestions');
    this.setupClearHandlers();
    this.setupGlobalClickHandler();
  }

  setupClearHandlers() {
    document.getElementById('from-address').addEventListener('input', (e) => {
      if (e.target.value.trim() === '') {
        this.mapManager.clearPoint('from');
      }
    });

    document.getElementById('to-address').addEventListener('input', (e) => {
      if (e.target.value.trim() === '') {
        this.mapManager.clearPoint('to');
      }
    });
  }

  setupAddressAutocomplete(inputId, suggestionsId) {
    const input = document.getElementById(inputId);

    input.addEventListener('input', () => {
      const query = input.value.trim();

      if (query.length < 3) {
        this.hideSuggestions(suggestionsId);
        return;
      }

      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }

      this.searchTimeout = setTimeout(() => {
        this.searchAddresses(query, suggestionsId, inputId);
      }, 300);
    });

    input.addEventListener('blur', () => {
      setTimeout(() => {
        this.hideSuggestions(suggestionsId);
      }, 200);
    });

    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        if (input.value.trim()) {
          this.geocodeAddress(input.value.trim(), inputId);
          this.hideSuggestions(suggestionsId);
        }
      }
    });
  }

  setupGlobalClickHandler() {
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.relative')) {
        this.hideSuggestions('from-suggestions');
        this.hideSuggestions('to-suggestions');
      }
    });
  }

  searchAddresses(query, suggestionsId, inputId) {
    if (!ymaps || !ymaps.suggest) {
      console.log('Suggest API недоступен, используем геокодирование');
      return;
    }

    ymaps.suggest(query, {
      results: 5,
      boundedBy: [[55.142627, 36.803164], [56.021281, 38.967407]]
    }).then((items) => {
      this.showSuggestions(items, suggestionsId, inputId);
    }).catch((error) => {
      console.log('Ошибка поиска адресов:', error);
      this.hideSuggestions(suggestionsId);
    });
  }

  showSuggestions(items, suggestionsId, inputId) {
    const suggestions = document.getElementById(suggestionsId);
    suggestions.innerHTML = '';

    if (items.length === 0) {
      this.hideSuggestions(suggestionsId);
      return;
    }

    items.forEach((item) => {
      const div = document.createElement('div');
      div.className = 'suggestion-item';
      div.textContent = item.displayName;
      div.addEventListener('click', () => {
        document.getElementById(inputId).value = item.displayName;
        this.geocodeAddress(item.displayName, inputId);
        this.hideSuggestions(suggestionsId);
      });
      suggestions.appendChild(div);
    });

    suggestions.classList.remove('hidden');
  }

  hideSuggestions(suggestionsId) {
    document.getElementById(suggestionsId).classList.add('hidden');
  }

  geocodeAddress(address, fieldId) {
    if (!address.trim()) return;

    ymaps.geocode(address, {
      results: 1,
      boundedBy: [[55.142627, 36.803164], [56.021281, 38.967407]]
    }).then((res) => {
      const firstGeoObject = res.geoObjects.get(0);
      if (firstGeoObject) {
        const coords = firstGeoObject.geometry.getCoordinates();
        const preciseName = firstGeoObject.getAddressLine();

        document.getElementById(fieldId).value = preciseName;
        this.mapManager.setPointOnMap(coords, fieldId, false);
      } else {
        console.log('Адрес не найден:', address);
      }
    }).catch((error) => {
      console.log('Ошибка геокодирования:', error);
    });
  }
}