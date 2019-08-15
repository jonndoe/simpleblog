from django import forms
from .models import MyComment

'''
class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)
'''

class MyCommentForm(forms.ModelForm):
    class Meta:
        model = MyComment
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    query = forms.CharField()
