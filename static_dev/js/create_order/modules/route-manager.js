export class RouteManager {
  constructor(mapManager) {
    this.mapManager = mapManager;
    this.routeObject = null;
  }

  calculateRoute() {
    const coords = this.mapManager.getCoords();

    if (!coords.from || !coords.to) {
      return;
    }

    this.clearRoute();

    ymaps.route([coords.from, coords.to], {
      multiRoute: false,
      routingMode: 'auto'
    }).then((route) => {
      this.routeObject = route;
      this.mapManager.getMap().geoObjects.add(route);

      const activeRoute = route.getActiveRoute();
      const distance = Math.round(activeRoute.properties.get('distance') / 1000 * 10) / 10;
      const duration = Math.round(activeRoute.properties.get('duration') / 60);

      document.getElementById('route-distance').textContent = distance + ' км';
      document.getElementById('route-duration').textContent = duration + ' мин';

      document.getElementById('route-info').classList.remove('hidden');

      this.mapManager.getMap().setBounds(route.getBounds(), {
        checkZoomRange: true,
        zoomMargin: 50
      });
    }).catch((error) => {
      console.log('Не удалось построить маршрут:', error);
    });
  }

  clearRoute() {
    if (this.routeObject) {
      this.mapManager.getMap().geoObjects.remove(this.routeObject);
      this.routeObject = null;

    }
    document.getElementById('route-info').classList.add('hidden');
  }
}