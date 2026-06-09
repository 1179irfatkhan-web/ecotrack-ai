from django import forms

class SimulatorForm(forms.Form):

    current_transport = forms.FloatField(min_value=0)
    current_electricity = forms.FloatField(min_value=0)
    current_meat = forms.IntegerField(min_value=0)
    current_waste = forms.FloatField(min_value=0)

    future_transport = forms.FloatField(min_value=0)
    future_electricity = forms.FloatField(min_value=0)
    future_meat = forms.IntegerField(min_value=0)
    future_waste = forms.FloatField(min_value=0)