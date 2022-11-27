from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# Oggetto form che utilizzo per permettere all'utente di loggarsi nel sito
class LoginUserForm(AuthenticationForm):

    class Meta:
        model = User

# Oggetto form che utilizzo per ottenere le informazioni necessarie per creare un nuovo utente
class DataUserForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(), max_length=25)
    email = forms.CharField(widget=forms.EmailInput(), required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

# Oggetto form che utilizzo per permettere all'utente di modificare i suoi dati
class AccountForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(), required=False)
    last_name = forms.CharField(widget=forms.TextInput(), required=False)
    email = forms.CharField(widget=forms.EmailInput(), required=False)
    password1 = forms.CharField(widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')


