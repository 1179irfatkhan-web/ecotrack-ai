from django import forms

class CarbonForm(forms.Form):

    transport_km = forms.FloatField(min_value=0)

    electricity_units = forms.FloatField(min_value=0)

    meat_meals = forms.IntegerField(min_value=0)

    waste_kg = forms.FloatField(min_value=0)