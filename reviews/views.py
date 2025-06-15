from logging import getLogger

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from drivers.mixins import UserIsDriverOfOrderMixin
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
        if request.user == order.client:
            target_person = order.driver.user

        return render(request, self.template_name, {
            "order": order,
            "target_person": target_person,
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
            else:
                review.driver_mark = rating
                review.driver_review = data["comment"]
            review.save()

            return JsonResponse({"success": True})
        except Exception as exc:
            LOGGER.exception(f"Exception occurred during creating review: {exc}")
            return HttpResponseBadRequest()


class DriverPendingReviewsView(LoginRequiredMixin, UserIsDriverOfOrderMixin, View):
    template_name = 'reviews/pending_reviews.html'
    context_object_name = 'pending_orders'
    paginate_by = 10
