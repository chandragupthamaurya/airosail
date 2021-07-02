from django import forms
from .models import comments, Post,PostImages,Like
from ckeditor.widgets import CKEditorWidget


class NewPostForm(forms.ModelForm):
	disc = forms.CharField(required = False,widget=CKEditorWidget())

	class Meta:
		model = Post
		fields = ['title','disc', 'price', 'buyurl','tags',]
		
class NewCommentForm(forms.ModelForm):

	class Meta:
		model = comments
		fields = ['comment']

"""class NewPostImage(NewPostForm): #extending form
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta(NewPostForm.Meta):
        fields = NewPostForm.Meta.fields + ['images',]"""

class NewPostImage(forms.ModelForm):
	images = forms.FileField(required=False,widget=forms.ClearableFileInput(attrs={'multiple': True,}))

	class Meta:
		model = PostImages
		fields = ['images',]