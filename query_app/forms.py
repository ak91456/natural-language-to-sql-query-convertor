from django import forms


class ConnectionForm(forms.Form):
    db_name = forms.CharField(label="Database Name", max_length=100)
    db_user = forms.CharField(label="Username", max_length=100)
    db_password = forms.CharField(label="Password", widget=forms.PasswordInput)
    db_host = forms.CharField(label="Host", max_length=100, initial="localhost")
    db_port = forms.IntegerField(label="Port", initial=5432)
