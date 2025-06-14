from django.forms import ModelForm

import orders.models as orders_models


class CreateOrderForm(ModelForm):
    class Meta:
        model = orders_models.TaxiOrder
        fields = (
            orders_models.TaxiOrder.payment_type.field.name,
            orders_models.TaxiOrder.pickup_coords.field.name,
            orders_models.TaxiOrder.pickup_datetime.field.name,
            orders_models.TaxiOrder.dropoff_coords.field.name,
            orders_models.TaxiOrder.passenger_count.field.name,
            orders_models.TaxiOrder.expected_duration.field.name,
        )
