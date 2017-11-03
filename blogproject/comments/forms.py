from django import forms
from .models import Comments

class CommentForm(forms.ModelForm):
    #内部类 Meta 里指定一些和表单相关的东西
    class Meta:
        model = Comments
        fields = ['name', 'email', 'url', 'text']