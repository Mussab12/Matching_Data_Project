from django.shortcuts import render
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


# Create your views here.


@login_required(login_url="/login")
def matchconfiguration(request):

    template = loader.get_template(
        'applications/projects/matchconfig/matchconfig.html')
    context = {"breadcrumb": {
        "parent": "Dashboard", "child": "Matching Config"}}
    return HttpResponse(template.render(context, request))
