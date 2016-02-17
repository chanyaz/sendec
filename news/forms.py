from django import forms
from .models import News#, NewsComments, NewsCommentsReplies
from django.forms import ModelForm
from nocaptcha_recaptcha.fields import NoReCaptchaField
#
# class NewsCommentsForm(ModelForm):
#     class Meta:
#         model = NewsComments
#         fields = ["comments_text"]
#
#
# class NewsCommentsRepliesForm(ModelForm):
#     class Meta:
#         model = NewsCommentsReplies
#         fields = ["reply_text"]


class SendReportForm(forms.Form):
    captcha = NoReCaptchaField()
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'form-control',
                                                                               'required': 'required',
                                                                               'name': 'username',
                                                                               'placeholder': 'Username'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control',
                                                                           'required': 'required',
                                                                           'pattern': "^[-a-z0-9!#$%&'*+/=?^_`{|}~]+(?:\.[-a-z0-9!#$%&'*+/=?^_`{|}~]+)*@(?:[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?\.)*(?:aero|arpa|asia|biz|cat|com|coop|edu|gov|info|int|jobs|mil|mobi|museum|name|net|org|pro|tel|travel|[a-z][a-z])$",
                                                                           'placeholder': 'email@example.com',
                                                                           'name': 'email'}))
    message = forms.Textarea(attrs={'class': 'form-control',
                                    'name': 'message',
                                    'required': 'required',
                                    'rows': 10,
                                    'placeholder': 'Message',
                                    'style': "resize: none;"})
