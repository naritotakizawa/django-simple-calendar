from django import forms
from .models import Schedule


class ScheduleForm(forms.ModelForm):
    """Bootstrapに対応するためのModelForm."""

    class Meta:
        model = Schedule
        fields = ('memo',)
        widgets = {
            'memo': forms.Textarea(attrs={
                'class': 'form-control',
            }),
        }
