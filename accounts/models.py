from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('employee', 'Employé'),
        ('manager', 'Manager'),
        ('hr', 'Responsable RH'),
        ('admin', 'Administrateur'),
    )
    
    THEME_CHOICES = (
        ('light', 'Thème clair'),
        ('dark', 'Thème sombre'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # New fields - Personal Information
    bio = models.TextField(_('biographie'), blank=True)
    birth_date = models.DateField(_('date de naissance'), null=True, blank=True)
    
    # Social Media
    linkedin = models.URLField(_('profil LinkedIn'), blank=True)
    twitter = models.URLField(_('profil Twitter'), blank=True)
    github = models.URLField(_('profil GitHub'), blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(_('contact d\'urgence - nom'), max_length=100, blank=True)
    emergency_contact_phone = models.CharField(_('contact d\'urgence - téléphone'), max_length=15, blank=True)
    emergency_contact_relation = models.CharField(_('contact d\'urgence - relation'), max_length=50, blank=True)
    
    # Work Information
    hire_date = models.DateField(_('date d\'embauche'), null=True, blank=True)
    employee_id = models.CharField(_('matricule'), max_length=20, blank=True)
    office_location = models.CharField(_('localisation bureau'), max_length=100, blank=True)
    
    # Preferences
    theme = models.CharField(_('thème'), max_length=10, choices=THEME_CHOICES, default='light')
    email_notifications = models.BooleanField(_('notifications par email'), default=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Assigner automatiquement le groupe correspondant au rôle
            group_name = self.role.capitalize()
            group, created = Group.objects.get_or_create(name=group_name)
            self.groups.add(group)
            
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        
    def get_age(self):
        from datetime import date
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
        
    def get_years_of_service(self):
        from datetime import date
        if self.hire_date:
            today = date.today()
            return today.year - self.hire_date.year - ((today.month, today.day) < (self.hire_date.month, self.hire_date.day))
        return None 