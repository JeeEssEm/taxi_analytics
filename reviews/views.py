from django.shortcuts import render
from django.views import View


class ReviewView(View):
    def get(self, request):
        return render(request, "reviews/review.html")
