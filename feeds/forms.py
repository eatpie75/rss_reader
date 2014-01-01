from django import forms


class AddFeedForm(forms.Form):
	url=forms.URLField()


class EditFeedForm(forms.Form):
	title=forms.CharField(max_length=200)
	feed_url=forms.URLField()
	site_url=forms.URLField()
