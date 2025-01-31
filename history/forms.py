from django import forms

class UploadFileForm(forms.Form):
	file = forms.FileField(label='Upload save file')
	time = forms.CharField(label='Enter a time', max_length=10)

class SearchForm(forms.Form):
	q = forms.CharField(label='Search', required=False)
	p = forms.IntegerField(label='Page', required=False)
	userID = forms.IntegerField(label='User ID', required=False)
	deleted = forms.BooleanField(label='Deleted only', required=False)
	undeleted = forms.BooleanField(label='Not deleted', required=False)
	playable = forms.BooleanField(label='Data available', required=False)
	unplayable = forms.BooleanField(label='Data unavailable', required=False)
	rated = forms.BooleanField(label='Star only', required=False)
	unrated = forms.BooleanField(label='No Star', required=False)
	difficulty = forms.IntegerField(label='Difficulty', required=False)
	wasrated = forms.BooleanField(label='Was rated', required=False)
	wasnotrated = forms.BooleanField(label='Was not rated', required=False)
	featured = forms.BooleanField(label='Featured', required=False)
	unfeatured = forms.BooleanField(label='Not featured', required=False)
	negativefeatured = forms.BooleanField(label='Negative featured', required=False)
	original = forms.IntegerField(label='Original', required=False)
	s = forms.CharField(label='Sort', required=False)

class LevelForm(forms.Form):
	blanks = forms.BooleanField(label='Show blanks', required=False)
	dupes = forms.BooleanField(label='Show dupes', required=False)