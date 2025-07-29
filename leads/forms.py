from django import forms
from .models import Lead , Agent , Category
from django.contrib.auth.forms import UserCreationForm, UsernameField

from django.contrib.auth import get_user_model      # we can also import from .models but this is another way

class LeadModelForm(forms.ModelForm):
    class Meta:     # this is where we speicfy info about the form
        model=Lead
        fields=(
            'first_name',
            'last_name',
            'age',
            'agent',
            'description',
            'phone_number',
            'emails',
        )

class CategoryModelForm(forms.ModelForm):
    class Meta:
        model=Category
        fields=(
            'name',
        )

class LeadForm(forms.Form):     #so we are inheriting from djangos form
    first_name= forms.CharField()
    last_name= forms.CharField()
    age= forms.IntegerField(min_value=0)



User=get_user_model()
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}


class AssignAgentForm(forms.Form):
    agent = forms.ModelChoiceField(queryset=Agent.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        agents = Agent.objects.filter(organisaton=request.user.userprofile)
        super(AssignAgentForm, self).__init__(*args, **kwargs)
        self.fields["agent"].queryset = agents


class LeadCategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            'category',
        )