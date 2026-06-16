from django.contrib.auth.decorators import login_required
from calculator.services import CarbonService
from .services import PDFService

@login_required
def generate_report(request):
    # Retrieve only the logged-in user's carbon records
    records = CarbonService.get_user_records(request.user)
    
    # Delegate to PDFService to generate the styled report
    return PDFService.build_sustainability_report(request.user, records)