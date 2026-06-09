from django.http import HttpResponse
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet

from calculator.models import CarbonRecord


def generate_report(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="EcoTrack_Report.pdf"'

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "EcoTrack AI Sustainability Report",
            styles['Title']
        )
    )

    story.append(Spacer(1,20))

    latest = CarbonRecord.objects.last()

    if latest:

        story.append(
            Paragraph(
                f"Transport: {latest.transport_km} km",
                styles['Normal']
            )
        )

        story.append(
            Paragraph(
                f"Electricity: {latest.electricity_units}",
                styles['Normal']
            )
        )

        story.append(
            Paragraph(
                f"Meat Meals: {latest.meat_meals}",
                styles['Normal']
            )
        )

        story.append(
            Paragraph(
                f"Waste: {latest.waste_kg} kg",
                styles['Normal']
            )
        )

        story.append(
            Paragraph(
                f"<b>Total Carbon:</b> {latest.total_carbon} kg CO₂",
                styles['Normal']
            )
        )

    doc.build(story)

    return response