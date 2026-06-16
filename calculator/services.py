from django.db.models import Sum, Avg, Count
from .models import CarbonRecord

class CarbonService:
    @staticmethod
    def calculate_carbon(data):
        """
        Calculate total carbon emissions in kg CO2.
        - Transport: 0.21 kg per km
        - Electricity: 0.82 kg per unit (kWh)
        - Meat Meals: 3.30 kg per meal
        - Waste: 0.57 kg per kg
        """
        transport = data.get("transport_km", 0.0) * 0.21
        electricity = data.get("electricity_units", 0.0) * 0.82
        food = data.get("meat_meals", 0) * 3.3
        waste = data.get("waste_kg", 0.0) * 0.57
        
        total = transport + electricity + food + waste
        return round(total, 2)

    @classmethod
    def create_record(cls, user, form_data):
        """
        Calculates and creates a new CarbonRecord for the specified user.
        """
        total = cls.calculate_carbon(form_data)
        record = CarbonRecord.objects.create(
            user=user,
            transport_km=form_data.get('transport_km', 0.0),
            electricity_units=form_data.get('electricity_units', 0.0),
            meat_meals=form_data.get('meat_meals', 0),
            waste_kg=form_data.get('waste_kg', 0.0),
            total_carbon=total
        )
        return record

    @staticmethod
    def get_user_records(user):
        """
        Retrieve all carbon records for a specific user, sorted from newest to oldest.
        Uses .only() database optimization to select necessary fields.
        """
        return CarbonRecord.objects.filter(user=user).only(
            'id', 'transport_km', 'electricity_units', 'meat_meals', 'waste_kg', 'total_carbon', 'created_at'
        ).order_by('-created_at')

    @staticmethod
    def get_user_stats(user):
        """
        Perform database-level aggregation to fetch user statistics efficiently.
        Returns:
            dict: {total_records, total_carbon, avg_carbon, total_transport, total_electricity, total_meals, total_waste}
        """
        stats = CarbonRecord.objects.filter(user=user).aggregate(
            total_records=Count('id'),
            sum_carbon=Sum('total_carbon'),
            avg_carbon=Avg('total_carbon'),
            total_transport=Sum('transport_km'),
            total_electricity=Sum('electricity_units'),
            total_meals=Sum('meat_meals'),
            total_waste=Sum('waste_kg')
        )
        # Handle None values from empty querysets gracefully
        return {
            'total_records': stats['total_records'] or 0,
            'total_carbon': round(stats['sum_carbon'] or 0.0, 2),
            'avg_carbon': round(stats['avg_carbon'] or 0.0, 2),
            'total_transport': round(stats['total_transport'] or 0.0, 2),
            'total_electricity': round(stats['total_electricity'] or 0.0, 2),
            'total_meals': stats['total_meals'] or 0,
            'total_waste': round(stats['total_waste'] or 0.0, 2),
        }
