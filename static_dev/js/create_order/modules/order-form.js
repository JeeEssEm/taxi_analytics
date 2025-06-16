import {Utils} from "./utils.js";

export class OrderForm {
    constructor(priceCalculator, mapManager, routeManager) {
        this.priceCalculator = priceCalculator;
        this.mapManager = mapManager;
        this.routeManager = routeManager;
        this.timePicker = null;
    }

    init() {
        this.initTimePicker();
        this.setupPassengersControl();
        this.setupEventListeners();
        this.setupFormValidation();

        // Подписываемся на изменения координат
        this.mapManager.onCoordsChange(() => {
            this.routeManager.calculateRoute();
            this.priceCalculator.scheduleCalculatePrice();
        });

        setTimeout(() => {
            this.priceCalculator.scheduleCalculatePrice();
        }, 500);
    }

    initTimePicker() {
        this.timePicker = flatpickr('#scheduled-time', {
            enableTime: true,
            noCalendar: false,
            dateFormat: "Z",
            altFormat: "d.m.Y H:i",
            altInput: true,
            time_24hr: true,
            minuteIncrement: 5,
            locale: "ru",
            defaultDate: new Date().setHours(new Date().getHours()),
            minDate: new Date(),
            minTime: "now",
            maxDate: new Date().setDate(new Date().getDate() + 3),
            maxTime: "23:59",
        });
    }

    setupPassengersControl() {
        const passengersInput = document.getElementById('passengers');
        const passengersValue = document.getElementById('passengers-value');
        const passengersTrack = document.getElementById('passengers-track');

        const updatePassengers = (value) => {
            passengersValue.textContent = value;
            passengersInput.value = value;
            passengersTrack.style.width = `${(value - 1) * 33.33}%`;
            this.priceCalculator.scheduleCalculatePrice();
        };

        updatePassengers(passengersInput.value);

        passengersInput.addEventListener('input', function () {
            updatePassengers(this.value);
        });

        document.getElementById('decrease-passengers').addEventListener('click', () => {
            let value = parseInt(passengersInput.value);
            if (value > 1) {
                updatePassengers(value - 1);
            }
        });

        document.getElementById('increase-passengers').addEventListener('click', () => {
            let value = parseInt(passengersInput.value);
            if (value < 4) {
                updatePassengers(value + 1);
            }
        });
    }

    setupEventListeners() {
        document.querySelectorAll('input[name="time_type"]').forEach(radio => {
            radio.addEventListener('change', function () {
                const timePickerContainer = document.getElementById('time-picker-container');
                if (timePickerContainer.classList.contains('hidden'))
                    timePickerContainer.classList.remove('hidden')
                else
                    timePickerContainer.classList.add('hidden')
                this.priceCalculator.scheduleCalculatePrice();
            }.bind(this));
        });

        document.querySelectorAll('input[name="payment_type"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.priceCalculator.scheduleCalculatePrice();
            });
        });

        document.getElementById('scheduled-time').addEventListener('change', () => {
            this.priceCalculator.scheduleCalculatePrice();
        });

        document.getElementById('comment').addEventListener('input',
            Utils.debounce(() => {
                this.priceCalculator.scheduleCalculatePrice();
            }, 1000)
        );
    }

    setupFormValidation() {
        document.getElementById('taxi-order-form').addEventListener('submit', (e) => {
            if (!this.priceCalculator.hasValidOrderData()) {
                e.preventDefault();
                alert('Пожалуйста, дождитесь расчета стоимости поездки');
                return false;
            }
            const scheduledTimeRadio = document.querySelector('input[name="time_type"][value="later"]');
            if (scheduledTimeRadio && scheduledTimeRadio.checked) {
                const timeInput = document.getElementById('scheduled-time');

                if (timeInput && timeInput.value) {
                    const selectedDateTime = new Date(timeInput.value);
                    const now = new Date();
                    if (selectedDateTime <= now) {
                        e.preventDefault();
                        alert('Время поездки должно быть в будущем. Пожалуйста, выберите корректное время.');
                        timeInput.focus();
                        return false;
                    }
                }
                return true;
            }
        })
    }
}