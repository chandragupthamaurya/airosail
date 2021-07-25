from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ValidationError
from .models import Profile,Messages
from ckeditor.widgets import CKEditorWidget

class registerForm(UserCreationForm):
	email = forms.EmailField(required = True, error_messages={'exists':'this already exists!'})
	username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'company name/username'}))

	class Meta:
		model = User
		fields = ('username','email' , 'password1', 'password2')

	def clean_email(self):
		email = self.cleaned_data.get('email')

		try:
			match = User.objects.get(email = email)
		except User.DoesNotExist:
			return email
		raise forms.ValidationError('this email already exists')

class UserUpdateForm(forms.ModelForm):
	email = forms.EmailField()

	class Meta:
		model = User
		fields = ('username','email')

class ProfileUpdateForm(forms.ModelForm):
	About = forms.CharField(widget= CKEditorWidget())


	class Meta:
		model = Profile
		fields = ('bio','image','About','url','profile_type','phone','address','city','state','country')

class ContactForm(forms.Form):
	name = forms.CharField(required=True)
	email = forms.EmailField(required=True)
	content = forms.CharField(required=True,widget=forms.Textarea)

class MessageForm(forms.ModelForm):

	class Meta:
		model = Messages
		fields = ('message',)
