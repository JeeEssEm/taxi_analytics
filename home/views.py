from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.urls import reverse_lazy


class IndexView(TemplateView):
    template_name = "home/index.html"


class RedirectView(View):
    def dispatch(self, request, *args, **kwargs):
        return redirect(reverse_lazy("orders:create_order"))
