from django.urls import path

from .views import dashboard_view
from .pdf_report import generate_report

urlpatterns = [

    path('', dashboard_view,
         name='dashboard'),

    path(
        'report/',
        generate_report,
        name='report'
    ),

]