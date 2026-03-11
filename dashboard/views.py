from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from dashboard.services import build_dashboard_context


@login_required
def dashboard_view(request):
    contexto = build_dashboard_context(request)
    return render(request, 'dashboard_view.html', contexto)