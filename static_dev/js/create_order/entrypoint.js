import {MapManager} from './modules/map-manager.js';
import {AddressAutocomplete} from './modules/address-autocomplete.js';
import {OrderForm} from './modules/order-form.js';
import {PriceCalculator} from './modules/price-calculator.js';
import {RouteManager} from './modules/route-manager.js';
import {Utils} from './modules/utils.js';

document.addEventListener('DOMContentLoaded', function () {
    const mapManager = new MapManager();
    const routeManager = new RouteManager(mapManager);
    const priceCalculator = new PriceCalculator();
    const addressAutocomplete = new AddressAutocomplete(mapManager, routeManager);
    const orderForm = new OrderForm(priceCalculator, mapManager, routeManager);

    mapManager.setDependencies(routeManager, priceCalculator);

    ymaps.ready(() => {
        mapManager.init();
        orderForm.init();
        addressAutocomplete.init();

        setTimeout(() => {
            priceCalculator.scheduleCalculatePrice();
        }, 200);
    });
});