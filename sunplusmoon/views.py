import logging

# from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.generic import View

# from common.mixins import LoginRequiredMixin

#logger = logging.getLogger("apps")


class HomeView(View):
    template_name = 'common/base.html'

    def get(self, request, **kwargs):
        return render(request, self.template_name, locals())
