from django import forms
from .models import User, Attendance,LeaveRequest


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['date', 'hours_requested', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['user', 'date', 'entry_time', 'exit_time', 'remarks']
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())