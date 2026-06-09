from django.shortcuts import render
from .forms import CarbonForm
from .utils import calculate_carbon
from .models import CarbonRecord
from django.contrib.auth.decorators import login_required
from ai_coach.gemini_service import get_ai_advice



@login_required
def calculator_view(request):

    result = None
    advice = None

    if request.method == "POST":

        form = CarbonForm(request.POST)

        if form.is_valid():

            result = calculate_carbon(
                form.cleaned_data
            )

            CarbonRecord.objects.create(
                user=request.user,

                transport_km=form.cleaned_data['transport_km'],
                electricity_units=form.cleaned_data['electricity_units'],
                meat_meals=form.cleaned_data['meat_meals'],
                waste_kg=form.cleaned_data['waste_kg'],

                total_carbon=result
            )

            try:

                advice = get_ai_advice({
                    "transport_km": form.cleaned_data["transport_km"],
                    "electricity_units": form.cleaned_data["electricity_units"],
                    "meat_meals": form.cleaned_data["meat_meals"],
                    "waste_kg": form.cleaned_data["waste_kg"],
                    "total_carbon": result
                })

            except Exception as e:

                advice = f"AI Service Error: {e}"

    else:

        form = CarbonForm()

    return render(
        request,
        'calculator.html',
        {
            'form': form,
            'result': result,
            'advice': advice
        }
    )