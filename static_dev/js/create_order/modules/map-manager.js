// Управление картой и метками
export class MapManager {
    constructor() {
        this.map = null;
        this.activeField = null;
        this.placemarkFrom = null;
        this.placemarkTo = null;
        this.fromCoords = null;
        this.toCoords = null;
        this.callbacks = {
            onCoordsChange: []
        };
        this.routeManager = null;
        this.priceCalculator = null;

    }

    init() {
        this.map = new ymaps.Map('map', {
            center: [55.751574, 37.573856],
            zoom: 12,
            controls: ['zoomControl', 'geolocationControl', 'trafficControl']
        });

        this.setupEventListeners();
        this.restoreStateFromInputs();
    }

    setDependencies(routeManager, priceCalculator) {
        this.routeManager = routeManager;
        this.priceCalculator = priceCalculator;
    }


    setupEventListeners() {
        document.getElementById('set-from-map').addEventListener('click', () => {
            this.activateField('from-address');
        });

        document.getElementById('set-to-map').addEventListener('click', () => {
            this.activateField('to-address');
        });

        document.getElementById('clear-map').addEventListener('click', () => {
            this.clearAll();
        });

        document.getElementById('cancel-map-selection').addEventListener('click', () => {
            this.deactivateField();
        });

        document.getElementById('get-location').addEventListener('click', () => {
            this.getCurrentLocation();
        });

        this.map.events.add('click', (e) => {
            if (!this.activeField) return;

            e.preventDefault();
            e.stopPropagation();

            const coords = e.get('coords');
            this.setPointOnMap(coords, this.activeField);
            this.deactivateField();
        });
    }

    activateField(fieldId) {
        document.querySelectorAll('.address-field').forEach(field => {
            field.classList.remove('address-field-active');
        });

        this.activeField = fieldId;
        document.getElementById(fieldId).classList.add('address-field-active');
        document.getElementById('cancel-map-selection').classList.remove('hidden');
        document.getElementById('map').classList.add('map-selection-mode');

        this.map.balloon.open(this.map.getCenter(), {
            contentHeader: 'Выбор на карте',
            contentBody: `Кликните на карте, чтобы установить адрес для поля "${fieldId === 'from-address' ? 'Откуда' : 'Куда'}"`,
            contentFooter: '<em>Адрес будет определен автоматически</em>'
        });
    }

    deactivateField() {
        if (!this.activeField) return;

        document.getElementById(this.activeField).classList.remove('address-field-active');
        this.activeField = null;
        document.getElementById('cancel-map-selection').classList.add('hidden');
        document.getElementById('map').classList.remove('map-selection-mode');
        this.map.balloon.close();
    }

    setPointOnMap(coords, fieldId, updateAddress = true) {
        if (fieldId === 'from-address' && this.placemarkFrom) {
            this.map.geoObjects.remove(this.placemarkFrom);
        }
        if (fieldId === 'to-address' && this.placemarkTo) {
            this.map.geoObjects.remove(this.placemarkTo);
        }

        const placemark = new ymaps.Placemark(coords, {
            balloonContent: fieldId === 'from-address' ? 'Точка отправления' : 'Точка назначения'
        }, {
            preset: fieldId === 'from-address' ?
                'islands#blueCircleDotIcon' :
                'islands#greenCircleDotIcon',
            draggable: true
        });

        placemark.events.add('dragend', () => {
            const newCoords = placemark.geometry.getCoordinates();
            this.setCoordinates(newCoords, fieldId);
            this.updateAddressFromCoords(newCoords, fieldId);
            this.triggerCoordsChange();
        });

        this.map.geoObjects.add(placemark);

        if (fieldId === 'from-address') {
            this.placemarkFrom = placemark;
            this.fromCoords = coords;
        } else {
            this.placemarkTo = placemark;
            this.toCoords = coords;
        }

        this.setCoordinates(coords, fieldId);

        if (updateAddress && !document.getElementById(fieldId).value.trim()) {
            this.updateAddressFromCoords(coords, fieldId);
        }

        this.triggerCoordsChange();
    }

    clearPoint(type) {
        if (type === 'from') {
            this.fromCoords = null;
            document.getElementById('from-coords').value = '';
            if (this.placemarkFrom) {
                this.placemarkFrom = null;
            }
        } else {
            this.toCoords = null;
            document.getElementById('to-coords').value = '';
            if (this.placemarkTo) {
                this.placemarkTo = null;
            }
        }
        this.triggerCoordsChange();
    }

    setCoordinates(coords, fieldId) {
        const coordsField = fieldId === 'from-address' ? 'from-coords' : 'to-coords';
        document.getElementById(coordsField).value = coords[0] + ',' + coords[1];
        this.triggerCoordsChange();
    }

    updateAddressFromCoords(coords, fieldId) {
        ymaps.geocode(coords, {results: 1}).then((res) => {
            const firstGeoObject = res.geoObjects.get(0);
            if (firstGeoObject) {
                document.getElementById(fieldId).value = firstGeoObject.getAddressLine();
            }
        }).catch((error) => {
            console.log('Ошибка обратного геокодирования:', error);
        });
    }

    getCurrentLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((position) => {
                const coords = [position.coords.latitude, position.coords.longitude];
                this.setPointOnMap(coords, 'from-address');
                this.map.setCenter(coords, 15);
            }, (error) => {
                console.log('Ошибка геолокации:', error);
                alert('Не удалось определить ваше местоположение');
            });
        } else {
            alert('Геолокация не поддерживается браузером');
        }
    }

    clearAll() {
        document.getElementById('from-address').value = '';
        document.getElementById('to-address').value = '';

        this.clearPoint('from');
        this.clearPoint('to');
        this.getMap().geoObjects.removeAll();

        // Скрытие подсказок
        const fromSuggestions = document.getElementById('from-suggestions');
        const toSuggestions = document.getElementById('to-suggestions');
        if (fromSuggestions) fromSuggestions.classList.add('hidden');
        if (toSuggestions) toSuggestions.classList.add('hidden');

        this.map.setCenter([55.751574, 37.573856], 12);
    }


    restoreStateFromInputs() {
        const fromCoordsValue = document.getElementById('from-coords').value;
        const toCoordsValue = document.getElementById('to-coords').value;

        if (fromCoordsValue) {
            const coords = fromCoordsValue.split(',').map(parseFloat);
            this.setPointOnMap(coords, 'from-address', false);
        }

        if (toCoordsValue) {
            const coords = toCoordsValue.split(',').map(parseFloat);
            this.setPointOnMap(coords, 'to-address', false);
        }
    }

    // Система колбэков для уведомления других модулей об изменениях
    onCoordsChange(callback) {
        this.callbacks.onCoordsChange.push(callback);
    }

    triggerCoordsChange() {
        this.callbacks.onCoordsChange.forEach(callback => callback());
    }

    getCoords() {
        return {
            from: this.fromCoords,
            to: this.toCoords
        };
    }

    getMap() {
        return this.map;
    }
}