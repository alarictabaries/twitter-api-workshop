from django import forms


class TwitterQuery(forms.Form):
    keyword = forms.CharField(label='Keyword', max_length=100)
    count = forms.IntegerField(label="Number of tweets")
    language = forms.ChoiceField(label="Language", choices=(('fr', 'French'), ('en', 'English')))