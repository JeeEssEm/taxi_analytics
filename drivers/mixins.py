from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from orders.models import TaxiOrder


class UserIsDriverOfOrderMixin:
    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(TaxiOrder, pk=self.kwargs.get('pk'))
        if self.order.driver != request.user.taxi:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class DriverInformationMixin:
    def form_valid(self, form):
        context = self.get_context_data()
        car_form = context['car_form']
        if car_form.is_valid():
            car = car_form.save()
            self.object = form.save(commit=False)
            self.object.car = car
            self.object = form.save()

            self.request.user.taxi = self.object
            self.request.user.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))
