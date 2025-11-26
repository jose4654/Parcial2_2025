from django import forms

class BusquedaForm(forms.Form):
    """Formulario para búsqueda de scraping"""
    palabra_clave = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese una palabra clave para buscar'
        }),
        label='Palabra Clave'
    )

