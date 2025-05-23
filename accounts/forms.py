from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            # Personal Information
            'first_name', 'last_name', 'email', 'birth_date', 'bio',
            'phone', 'address', 'profile_picture',
            
            # Work Information
            'department', 'employee_id', 'office_location', 'hire_date',
            
            # Social Media
            'linkedin', 'twitter', 'github',
            
            # Emergency Contact
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            
            # Preferences
            'theme', 'email_notifications'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'theme': forms.Select(attrs={'class': 'form-control'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            # Personal Information
            'first_name': _('Prénom'),
            'last_name': _('Nom'),
            'email': _('Email'),
            'birth_date': _('Date de naissance'),
            'bio': _('Biographie'),
            'phone': _('Téléphone'),
            'address': _('Adresse'),
            'profile_picture': _('Photo de profil'),
            
            # Work Information
            'department': _('Département'),
            'employee_id': _('Matricule'),
            'office_location': _('Localisation bureau'),
            'hire_date': _('Date d\'embauche'),
            
            # Social Media
            'linkedin': _('Profil LinkedIn'),
            'twitter': _('Profil Twitter'),
            'github': _('Profil GitHub'),
            
            # Emergency Contact
            'emergency_contact_name': _('Nom du contact d\'urgence'),
            'emergency_contact_phone': _('Téléphone du contact d\'urgence'),
            'emergency_contact_relation': _('Relation avec le contact d\'urgence'),
            
            # Preferences
            'theme': _('Thème de l\'interface'),
            'email_notifications': _('Recevoir les notifications par email'),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['profile_picture', 'email_notifications']:
                field.widget.attrs['class'] = 'form-control'
        self.fields['profile_picture'].widget.attrs['class'] = 'form-control-file'

class UserRegistrationForm(UserCreationForm):
    # On filtre les rôles pour ne pas afficher 'admin' dans le formulaire d'inscription
    ROLE_CHOICES = [
        (key, label) for key, label in User.ROLE_CHOICES if key != 'admin'
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Rôle")
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label=_('Prénom'), max_length=30, required=True)
    last_name = forms.CharField(label=_('Nom'), max_length=30, required=True)
    phone = forms.CharField(label=_('Téléphone'), max_length=15, required=False)
    department = forms.CharField(label=_('Département'), max_length=100, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'department', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.department = self.cleaned_data['department']
        if commit:
            user.save()
        return user 