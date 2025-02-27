from django import forms
from .models import Notification

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['reply_message']
        widgets = {
            'reply_message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your reply...'}),
        }
