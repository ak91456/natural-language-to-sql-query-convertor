from django import forms

class DatabaseForm(forms.Form):
    db_name = forms.CharField(label='Database Name', max_length=100)
    db_user = forms.CharField(label='User', max_length=100)
    db_password = forms.CharField(label='Password', widget=forms.PasswordInput)
    db_host = forms.CharField(label='Host', max_length=100)
    db_port = forms.CharField(label='Port', max_length=10)
    table_name = forms.CharField(label='Table Name', max_length=100)
    natural_language_query = forms.CharField(label='Your Query', widget=forms.Textarea)
