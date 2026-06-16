from django.db import models
from django.contrib.auth.models import User


class CarbonRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    transport_km = models.FloatField()
    electricity_units = models.FloatField()
    meat_meals = models.IntegerField()
    waste_kg = models.FloatField()

    total_carbon = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.total_carbon} kg CO2"