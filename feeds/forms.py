from django import forms
from feeds.models import Category


class AddFeedForm(forms.Form):
	url=forms.URLField()


class EditFeedForm(forms.Form):
	title=forms.CharField(max_length=500)
	feed_url=forms.URLField()
	site_url=forms.URLField()
	category=forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
