from django import forms
from django.utils.translation import gettext_lazy as _
from .models import LeaveRequest, LeaveAttachment

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason', 'attachment']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'leave_type': _('Type de congé'),
            'start_date': _('Date de début'),
            'end_date': _('Date de fin'),
            'reason': _('Motif'),
            'attachment': _('Pièce jointe (optionnel)'),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError(_('La date de début doit être antérieure à la date de fin.'))

        return cleaned_data

class LeaveAttachmentForm(forms.ModelForm):
    class Meta:
        model = LeaveAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

class LeaveValidationForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['status', 'validation_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'validation_comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('approved', _('Approuver')),
            ('rejected', _('Rejeter')),
        ] 