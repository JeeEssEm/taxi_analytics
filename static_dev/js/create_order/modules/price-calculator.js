export class PriceCalculator {
    constructor() {
        this.priceCalculationTimeout = null;
        this.lastOrderSignature = null;
        this.orderData = null;
    }

    scheduleCalculatePrice() {
        if (this.priceCalculationTimeout) {
            clearTimeout(this.priceCalculationTimeout);
        }

        const fromCoordsValue = document.getElementById('from-coords').value;
        const toCoordsValue = document.getElementById('to-coords').value;

        if (!fromCoordsValue || !toCoordsValue) {
            this.resetPrice();
            return;
        }

        this.showPriceLoading();

        this.priceCalculationTimeout = setTimeout(() => {
            this.calculatePriceFromServer();
        }, 800);
    }

    showPriceLoading() {
        const priceElement = document.getElementById('price');
        const routePriceElement = document.getElementById('route-price');

        priceElement.classList.add('price-loading');
        routePriceElement.classList.add('price-loading');
    }

    hidePriceLoading() {
        const priceElement = document.getElementById('price');
        const routePriceElement = document.getElementById('route-price');

        priceElement.classList.remove('price-loading');
        routePriceElement.classList.remove('price-loading');
    }

    calculatePriceFromServer() {
        const fromCoordsValue = document.getElementById('from-coords').value;
        const toCoordsValue = document.getElementById('to-coords').value;
        const passengers = document.getElementById('passengers').value;

        if (!fromCoordsValue || !toCoordsValue) {
            this.resetPrice();
            return;
        }

        const orderData = {
            pickup_coords: fromCoordsValue,
            dropoff_coords: toCoordsValue,
            passengers: parseInt(passengers)
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
                this.hidePriceLoading();

                if (data.success) {
                    this.lastOrderSignature = data.order_signature;
                    this.orderData = data;

                    this.updatePriceDisplay(
                        data.price,
                        data.distance,
                        data.duration,
                    );
                    this.updateHiddenFormFields();
                } else {
                    console.log('Ошибка расчета цены:', data.error);
                    this.resetPrice();
                }
            })
            .catch(error => {
                this.hidePriceLoading();
                console.log('Ошибка запроса цены:', error);
                this.resetPrice();
            });
    }

    updateHiddenFormFields() {
        if (!this.lastOrderSignature) return;

        this.updateHiddenFormField("order_signature", this.lastOrderSignature);
        this.updateHiddenFormField("expected_duration", this.orderData.duration);
        this.updateHiddenFormField("distance", this.orderData.distance);
        this.updateHiddenFormField("order_price", this.orderData.price);
    }

    updateHiddenFormField(inputName, value) {
        const form = document.getElementById('taxi-order-form');
        const field = form.querySelector(`input[name='${inputName}']`);
        field.value = value;
    }

    updatePriceDisplay(price, distance, duration) {
        document.getElementById('price').textContent = price + ' ₽';
        document.getElementById('route-price').textContent = price + ' ₽';

        if (distance) {
            document.getElementById('distance_field').textContent = distance + ' км';
        }
        if (duration) {
            document.getElementById('duration').textContent = duration + ' мин';
        }
    }

    resetPrice() {
        this.hidePriceLoading();
        document.getElementById('price').textContent = '-';
        document.getElementById('route-price').textContent = '-';
        document.getElementById('distance').textContent = '-';
        document.getElementById('duration').textContent = '-';

        this.lastOrderData = null;
        this.lastOrderSignature = null;
        this.updateHiddenFormFields();

        if (this.priceCalculationTimeout) {
            clearTimeout(this.priceCalculationTimeout);
            this.priceCalculationTimeout = null;
        }
    }
    hasValidOrderData() {
        return document.getElementById('price').textContent !== '-';
    }
}