from django import forms
from .models import Newsletter,Comments
from ckeditor.widgets import CKEditorWidget


class NewNewsForm(forms.ModelForm):
	content = forms.CharField(required = False,widget=CKEditorWidget())
	image = forms.ImageField(required = False)

	class Meta:
		model = Newsletter
		fields = ['topics','title','content','tags','image']

class NewCommentForm(forms.ModelForm):

	class Meta:
		model = Comments
		fields = ['newscomment']