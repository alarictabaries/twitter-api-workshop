from django import forms


class TwitterQuery(forms.Form):
    subject = forms.CharField(label='Subject ', max_length=100)
    count = forms.IntegerField(label="Number of tweets ")
    language = forms.ChoiceField(label="Language ", choices=(('fr', 'French'), ('en', 'English')))