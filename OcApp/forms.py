from django import forms
from .models import Notification, Hospital

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['reply_message']
        widgets = {
            'reply_message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your reply...'}),
        }


class HospitalVerificationForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['name', 'address', 'contact', 'is_verified']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly', 'rows': 3}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
