from django import forms
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'police_id', 
            'rank',              
            'password1', 
            'password2'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'id': 'id_first_name', 'class': 'form-input', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'id': 'id_last_name', 'class': 'form-input', 'placeholder': 'Enter Last Name'}),
            'email': forms.EmailInput(attrs={'id': 'id_email', 'class': 'form-input', 'placeholder': 'Enter Email Address'}),
            'phone_number': forms.TextInput(attrs={'id': 'id_phone_number', 'class': 'form-input', 'placeholder': 'Enter Phone Number'}),
            'police_id': forms.TextInput(attrs={'id': 'id_police_id', 'class': 'form-input', 'placeholder': 'Enter Police ID'}),
            'rank': forms.Select(attrs={'id': 'id_rank', 'class': 'form-input'}),
            'password1': forms.PasswordInput(attrs={
                'id': 'id_password1',
                'class': 'form-input',
                'placeholder': 'Enter Password',
                'autocomplete': 'new-password'
            }),
            'password2': forms.PasswordInput(attrs={
                'id': 'id_password2',
                'class': 'form-input',
                'placeholder': 'Confirm Password',
                'autocomplete': 'new-password'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['first_name', 'last_name', 'email', 'phone_number', 'police_id', 'rank']:
            self.fields[field_name].required = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match!")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_police_id(self):
        police_id = self.cleaned_data.get("police_id")
        if UserProfile.objects.filter(police_id=police_id).exists():
            raise forms.ValidationError("A user with this Police ID already exists.")
        return police_id

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if UserProfile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Account disabled until approved by admin
        if commit:
            user.save()
        return user
