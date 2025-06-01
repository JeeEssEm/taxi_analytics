from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.http import HttpResponse


class IndexView(TemplateView):
    template_name = "home/index.html"
