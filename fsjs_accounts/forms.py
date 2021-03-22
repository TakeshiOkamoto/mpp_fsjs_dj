from django import forms


# 検索フォーム
class FindForm(forms.Form):
    name = forms.CharField(initial='')