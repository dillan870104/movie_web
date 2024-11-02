from django import forms


class RegisterForm(forms.Form):
    acc = forms.CharField(
        max_length=20,
        min_length=8,
        error_messages={
            "max_length": "長度最多20字元",
            "min_length": "長度最少8字元",
        },
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "name": "acc",
                "placeholder": "acc",
            }
        ),
    )
    pwd = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "name": "Passwordd",
                "placeholder": "pwd",
            }
        ),
    )
    email = forms.EmailField(
        max_length=50,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "name": "email",
                "placeholder": "email",
            }
        ),
    )
    username = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "name": "username",
                "placeholder": "username",
            }
        ),
    )
    tel = forms.CharField(
        max_length=10,
        min_length=10,
        error_messages={
            "max_length": "請輸入正確手機號碼",
            "min_length": "長度最少8字元",
        },
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "name": "acc",
                "placeholder": "acc",
            }
        ),
    )

    # profile_pic = forms.ImageField(required=False)


def __init__(self, *args, **kwargs):
    super(RegisterForm, self).__init__(*args, **kwargs)
