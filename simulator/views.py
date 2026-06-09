from django.shortcuts import render
from .forms import SimulatorForm
from django.contrib.auth.decorators import login_required



@login_required
def simulator_view(request):

    current_total = None
    future_total = None
    savings = None
    percentage = None

    if request.method == "POST":

        form = SimulatorForm(request.POST)

        if form.is_valid():

            current_total = (
                form.cleaned_data["current_transport"] * 0.21 +
                form.cleaned_data["current_electricity"] * 0.82 +
                form.cleaned_data["current_meat"] * 3.3 +
                form.cleaned_data["current_waste"] * 0.57
            )

            future_total = (
                form.cleaned_data["future_transport"] * 0.21 +
                form.cleaned_data["future_electricity"] * 0.82 +
                form.cleaned_data["future_meat"] * 3.3 +
                form.cleaned_data["future_waste"] * 0.57
            )

            savings = current_total - future_total

            percentage = (
                savings / current_total * 100
            ) if current_total else 0

    else:
        form = SimulatorForm()

    return render(
        request,
        "simulator.html",
        {
            "form": form,
            "current_total": round(current_total,2) if current_total else None,
            "future_total": round(future_total,2) if future_total else None,
            "savings": round(savings,2) if savings else None,
            "percentage": round(percentage,2) if percentage else None,
        }
    )