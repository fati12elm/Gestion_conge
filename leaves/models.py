from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone

class LeaveType(models.Model):
    name = models.CharField(_('Nom'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    max_days_per_year = models.PositiveIntegerField(_('Jours maximum par an'), default=0)
    requires_attachment = models.BooleanField(_('Pièce justificative requise'), default=False)

    class Meta:
        verbose_name = _('Type de congé')
        verbose_name_plural = _('Types de congé')

    def __str__(self):
        return self.name

class LeaveBalance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(_('année'))
    initial_balance = models.DecimalField(_('solde initial'), max_digits=5, decimal_places=1)
    used_balance = models.DecimalField(_('solde utilisé'), max_digits=5, decimal_places=1, default=0)
    
    @property
    def remaining_balance(self):
        return self.initial_balance - self.used_balance
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.leave_type.name} ({self.year})"
    
    class Meta:
        verbose_name = _('solde de congé')
        verbose_name_plural = _('soldes de congés')
        unique_together = ('user', 'leave_type', 'year')

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('approved', _('Approuvé')),
        ('rejected', _('Rejeté')),
        ('cancelled', _('Annulé')),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name=_('Employé'),
        null=True,
        default=None
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        verbose_name=_('Type de congé')
    )
    start_date = models.DateField(_('Date de début'))
    end_date = models.DateField(_('Date de fin'))
    reason = models.TextField(_('Motif'))
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    attachment = models.FileField(
        _('Pièce jointe'),
        upload_to='leave_attachments/%Y/%m/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(_('Date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Date de modification'), auto_now=True)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_leaves',
        verbose_name=_('Validé par')
    )
    validation_date = models.DateTimeField(_('Date de validation'), null=True, blank=True)
    validation_comment = models.TextField(_('Commentaire de validation'), blank=True)

    class Meta:
        verbose_name = _('Demande de congé')
        verbose_name_plural = _('Demandes de congé')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} au {self.end_date})"

    def get_status_color(self):
        return {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
        }.get(self.status, 'primary')

    @property
    def duration(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_('La date de fin doit être postérieure à la date de début.'))
            if self.start_date < timezone.now().date():
                raise ValidationError(_('La date de début ne peut pas être dans le passé.'))
    
    def save(self, *args, **kwargs):
        if self.status in ['approved', 'rejected'] and not self.validation_date:
            self.validation_date = timezone.now()
        super().save(*args, **kwargs)

class LeaveAttachment(models.Model):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='leave_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pièce jointe pour {self.leave_request}"
    
    class Meta:
        verbose_name = _('pièce jointe')
        verbose_name_plural = _('pièces jointes') 