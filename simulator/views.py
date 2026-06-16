from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import SimulatorForm
from calculator.services import CarbonService

@login_required
def simulator_view(request):
    current_total = None
    future_total = None
    savings = None
    percentage = None

    if request.method == "POST":
        form = SimulatorForm(request.POST)
        if form.is_valid():
            # Format inputs to match CarbonService requirements
            current_data = {
                "transport_km": form.cleaned_data["current_transport"],
                "electricity_units": form.cleaned_data["current_electricity"],
                "meat_meals": form.cleaned_data["current_meat"],
                "waste_kg": form.cleaned_data["current_waste"],
            }
            future_data = {
                "transport_km": form.cleaned_data["future_transport"],
                "electricity_units": form.cleaned_data["future_electricity"],
                "meat_meals": form.cleaned_data["future_meat"],
                "waste_kg": form.cleaned_data["future_waste"],
            }

            current_total = CarbonService.calculate_carbon(current_data)
            future_total = CarbonService.calculate_carbon(future_data)
            
            savings = round(current_total - future_total, 2)
            percentage = round((savings / current_total * 100), 2) if current_total > 0 else 0.0
    else:
        form = SimulatorForm()

    return render(
        request,
        "simulator.html",
        {
            "form": form,
            "current_total": current_total,
            "future_total": future_total,
            "savings": savings,
            "percentage": percentage,
        }
    )