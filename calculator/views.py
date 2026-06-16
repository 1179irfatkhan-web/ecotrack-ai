from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CarbonForm
from .services import CarbonService
from ai_coach.gemini_service import get_ai_advice

@login_required
def calculator_view(request):
    result = None
    advice = None

    if request.method == "POST":
        form = CarbonForm(request.POST)
        if form.is_valid():
            try:
                # Create the CarbonRecord using the CarbonService
                record = CarbonService.create_record(request.user, form.cleaned_data)
                result = record.total_carbon
                
                messages.success(
                    request, 
                    f"Successfully calculated and saved your footprint! Total: {result} kg CO2."
                )

                # Fetch recommendations from the coach
                try:
                    advice = get_ai_advice({
                        "transport_km": record.transport_km,
                        "electricity_units": record.electricity_units,
                        "meat_meals": record.meat_meals,
                        "waste_kg": record.waste_kg,
                        "total_carbon": result
                    })
                except Exception as e:
                    advice = f"AI Coach suggestion could not be retrieved: {str(e)}"

            except Exception as e:
                messages.error(request, f"Failed to record carbon data: {str(e)}")
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