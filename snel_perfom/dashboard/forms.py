from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(
        widget=forms.PasswordInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update(
            {
                'class': 'form-control form-icon-input',
                'id': 'email',
                'placeholder': 'exemple@snel.cd',
            }
        )
        self.fields['password'].widget.attrs.update(
            {
                'class': 'form-control form-icon-input pe-6',
                'id': "password",
                'type': 'password',
                'placeholder': 'Password',
                'data-password-input': 'data-password-input',
            }
        )
