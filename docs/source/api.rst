API Documentation
=================

.. toctree::
   :maxdepth: 4

.. autoclass:: cars.models.TaxiCar

.. autoclass:: reviews.models.TaxiReview

.. autoclass:: drivers.models.TaxiDriver

.. autoclass:: drivers.forms.DriverForm

.. autoclass:: drivers.forms.CarForm

.. autoclass:: drivers.managers.DriversManager

.. autoclass:: drivers.views.BecomeDriverView

.. autoclass:: drivers.views.ChangeDriverActivityView

.. autoclass:: drivers.views.UpdateDriverInformationView

.. autoclass:: drivers.views.OrdersListView

.. autoclass:: orders.forms.CreateOrderForm

.. autoclass:: orders.managers.OrderManager

.. autoclass:: orders.models.TaxiOrder

.. autofunction:: orders.serializers.OrderSerializer.get_user_image

.. autofunction:: orders.serializers.OrderSerializer.get_orders

.. autofunction:: orders.utils.get_route_summary
.. autofunction:: orders.utils.get_order_summary
.. autofunction:: orders.utils.get_address_coords
.. autofunction:: orders.utils.create_order_signature

.. autoclass:: users.models.TaxiUser
