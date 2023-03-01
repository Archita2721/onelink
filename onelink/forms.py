from django import forms  
from django.contrib.auth.forms import UserCreationForm ,AuthenticationForm
from django.contrib.auth.models import User  
from django.core.exceptions import ValidationError
from .models import linkModel

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def clean_email(self):
			email = self.cleaned_data['email']
			if User.objects.filter(email=email).exists():
				raise ValidationError("Email already exists")
			return email
	
class linkform(forms.ModelForm):
	android_link = forms.URLField(label="Google Play store(Android)")
	ios_link = forms.URLField(label="Apple App store(ios)")
	fallback_link = forms.URLField(label="Fallback link")
	class Meta:
		model = linkModel
		fields = ("android_link", "ios_link","fallback_link")


   
