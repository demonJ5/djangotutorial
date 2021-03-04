from django import forms

class SearchForm(forms.Form):
    artist = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}))
    from_year = forms.IntegerField(required=False)
    to_year = forms.IntegerField(required=False)

# NOTE HERE
class CuratorForm(forms.Form):
    id_title = forms.CharField(widget=forms.TextInput(attrs={'size': '50'}))
    id_acousticness_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '10'}))
    id_danceability_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '10'}))
    id_energy_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '10'}))
    id_instrumentalness_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '10'}))
    id_key_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '10'}))
    id_liveness_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '10'}))
    id_loudness_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '10'}))
    id_mode_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '10'}))
    id_speechiness_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '10'}))
    id_tempo_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '10'}))
    id_valence_weight = forms.IntegerField(widget=forms.NumberInput(attrs={'type':'range', 'step': '1', 'min': '0', 'max': '10'}))
