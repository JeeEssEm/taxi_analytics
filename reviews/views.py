from logging import getLogger

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View

from reviews.models import TaxiReview
from orders.models import TaxiOrder

LOGGER = getLogger(__name__)


class CreateReviewView(LoginRequiredMixin, View):
    template_name = "reviews/review.html"

    def get(self, request, pk):
        order: TaxiOrder = get_object_or_404(TaxiOrder, pk=pk)
        if order.status not in (
            TaxiOrder.StatusChoices.CANCELLED,
            TaxiOrder.StatusChoices.DONE
        ) or not order.driver:  # если заказ выполняется или нет водителя, то нафиг такой запрос шлем
            return HttpResponseBadRequest()

        if request.user != order.driver.user and request.user != order.client:
            return HttpResponseForbidden()
        review: TaxiReview = TaxiReview.objects.filter(order=order).first()
        if review:
            if request.user == order.client and review.client_mark:
                return HttpResponseForbidden()
            if request.user == order.driver.user and review.driver_mark:
                return HttpResponseForbidden()

        target_person = order.client
        user_role = "driver"
        back_url = reverse_lazy("drivers:history")
        if request.user == order.client:
            target_person = order.driver.user
            user_role = "client"
            back_url = reverse_lazy("orders:history")

        return render(request, self.template_name, {
            "order": order,
            "target_person": target_person,
            "user_role": user_role,
            "back_url": back_url,
        })

    def post(self, request, pk):
        data = request.POST

        if "comment" not in data.keys() or "rating" not in data.keys():
            return HttpResponseBadRequest()
        rating = data["rating"]
        if rating.isdigit():
            rating = int(rating)
            if rating < 0 or rating > 5:
                return HttpResponseBadRequest()

        order: TaxiOrder = get_object_or_404(TaxiOrder, id=pk)
        review = TaxiReview.objects.filter(order=order).first()
        if not review:
            review = TaxiReview.objects.create(
                order=order
            )
        try:
            if order.client == request.user:
                review.client_mark = rating
                review.client_review = data["comment"]
                redirected = reverse_lazy("reviews:client_pending_reviews")
            else:
                review.driver_mark = rating
                review.driver_review = data["comment"]
                redirected = reverse_lazy("reviews:driver_pending_reviews")
            review.save()

            return redirect(redirected)
        except Exception as exc:
            LOGGER.exception(f"Exception occurred during creating review: {exc}")
            return HttpResponseBadRequest()


class DriverPendingReviewsView(LoginRequiredMixin, ListView):
    template_name = 'reviews/pending_reviews.html'
    context_object_name = 'pending_orders'
    paginate_by = 10

    def get_queryset(self):
        return TaxiOrder.objects.get_unrated_orders_by_driver(self.request.user.taxi)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user_role': 'driver',
            'page_title': 'Оценить клиентов',
            'empty_title': 'Все заказы оценены!',
            'empty_description': 'У вас нет заказов, ожидающих оценки',
            'back_url': reverse_lazy("drivers:history"),
            'back_text': 'К истории заказов'
        })
        return context


class ClientPendingReviewsView(DriverPendingReviewsView):
    def get_queryset(self):
        return TaxiOrder.objects.get_unrated_orders_by_client(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user_role': 'client',
            'page_title': 'Оценить клиентов',
            'empty_title': 'Все заказы оценены!',
            'empty_description': 'У вас нет заказов, ожидающих оценки',
            'back_url': reverse_lazy("orders:history"),
            'back_text': 'К истории заказов'
        })
        return context
