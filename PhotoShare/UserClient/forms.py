__author__ = 'chenyoake'

from django import forms

class RegisterUserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    nickname = forms.CharField()

class LoginUserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UploadPhotoForm(forms.Form):
    upload_photo = forms.ImageField()
    description = forms.CharField()

class UserComment(forms.Form):
    content = forms.CharField()
    comm_img_id = forms.CharField()

class UserChangeInfo(forms.Form):
    nickname = forms.CharField()
    signature = forms.CharField()
    headshot = forms.FileField()