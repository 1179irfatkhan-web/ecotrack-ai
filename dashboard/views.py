from django.shortcuts import render
from calculator.models import CarbonRecord
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):

    records = CarbonRecord.objects.filter(
    user=request.user
).order_by('-created_at')

    return render(
        request,
        'dashboard.html',
        {
            'records': records
        }
    )