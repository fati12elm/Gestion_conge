from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from .models import LeaveRequest, LeaveType, LeaveBalance
from .forms import LeaveRequestForm, LeaveValidationForm, LeaveAttachmentForm
from notifications.signals import notify
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model

User = get_user_model()

# Helpers pour les rôles

def is_employee(user):
    return user.role == 'employee'

def is_manager(user):
    return user.role == 'manager'

def is_hr(user):
    return user.role == 'hr'

def is_admin(user):
    return user.role == 'admin'

def is_hr_or_admin(user):
    return user.role in ['hr', 'admin']

def is_manager_hr_admin(user):
    return user.role in ['manager', 'hr', 'admin']

# Vue : liste des demandes (employé = ses demandes, manager/hr/admin = tout voir)
class LeaveRequestListView(LoginRequiredMixin, ListView):
    model = LeaveRequest
    template_name = 'leaves/leave_request_list.html'
    context_object_name = 'leave_requests'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.role in ['hr', 'admin']:
            return LeaveRequest.objects.all().order_by('-created_at')
        elif user.role == 'manager':
            return LeaveRequest.objects.filter(employee__department=user.department).order_by('-created_at')
        else:
            return LeaveRequest.objects.filter(employee=user).order_by('-created_at')

# Vue : création de demande (employé uniquement)
from django.utils.decorators import method_decorator

@method_decorator(user_passes_test(is_employee), name='dispatch')
class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'leaves/leave_request_form.html'
    success_url = reverse_lazy('leaves:leave_request_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Nouvelle demande de congé')
        context['submit_text'] = _('Soumettre la demande')
        return context

    def form_valid(self, form):
        form.instance.employee = self.request.user
        form.instance.status = 'pending'
        messages.success(self.request, _('Votre demande de congé a été soumise avec succès.'))
        return super().form_valid(form)

# Vue : validation/refus (manager = son département, hr/admin = tout)
@login_required
def validate_leave_request(request, pk):
    user = request.user
    if user.role not in ['admin', 'hr', 'manager'] and not user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas les droits pour valider/refuser les congés.")
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    # Manager : ne peut valider que les demandes de son département
    if user.role == 'manager' and leave_request.employee.department != user.department:
        return HttpResponseForbidden("Vous ne pouvez valider que les demandes de votre département.")
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            leave_request.status = 'approved'
            messages.success(request, "La demande de congé a été validée avec succès.")
        elif action == 'reject':
            leave_request.status = 'rejected'
            messages.warning(request, "La demande de congé a été refusée.")
        leave_request.save()
        return redirect('leaves:leave_request_detail', pk=pk)
    return render(request, 'leaves/validate_leave.html', {'leave_request': leave_request})

# Vue : détail (employé = ses demandes, manager/hr/admin = tout voir)
class LeaveRequestDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = LeaveRequest
    template_name = 'leaves/leave_request_detail.html'
    context_object_name = 'leave_request'

    def test_func(self):
        leave_request = self.get_object()
        user = self.request.user
        return (
            user == leave_request.employee or
            user.role in ['hr', 'admin'] or
            user.is_superuser or
            (user.role == 'manager' and user.department == leave_request.employee.department)
        )

@login_required
def add_attachment(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if request.user != leave_request.user:
        messages.error(request, _('Vous ne pouvez pas ajouter de pièces jointes à cette demande.'))
        return redirect('leave_request_detail', pk=pk)
    
    if request.method == 'POST':
        form = LeaveAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.leave_request = leave_request
            attachment.save()
            messages.success(request, _('La pièce jointe a été ajoutée avec succès.'))
            return redirect('leave_request_detail', pk=pk)
    else:
        form = LeaveAttachmentForm()
    
    return render(request, 'leaves/attachment_form.html', {
        'form': form,
        'leave_request': leave_request
    })

@login_required
def leave_request_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, request.FILES)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = request.user
            leave_request.status = 'pending'
            leave_request.save()
            messages.success(request, _('Votre demande de congé a été soumise avec succès.'))
            return redirect('leaves:leave_request_list')
    else:
        form = LeaveRequestForm()
    
    return render(request, 'leaves/leave_request_form.html', {
        'form': form,
        'title': _('Nouvelle demande de congé'),
        'submit_text': _('Soumettre la demande')
    })

@login_required
def leave_request_list(request):
    leave_requests = LeaveRequest.objects.filter(employee=request.user).order_by('-created_at')
    return render(request, 'leaves/leave_request_list.html', {
        'leave_requests': leave_requests
    })

@login_required
def admin_dashboard(request):
    user = request.user
    if user.role not in ['admin', 'hr', 'manager'] and not user.is_superuser:
        return HttpResponseForbidden("Accès réservé à l'administration RH/Manager/Admin.")
    # Filtres simples (par statut, type, employé)
    status = request.GET.get('status')
    leave_type = request.GET.get('type')
    employee = request.GET.get('employee')
    leave_requests = LeaveRequest.objects.all().order_by('-created_at')
    if status:
        leave_requests = leave_requests.filter(status=status)
    if leave_type:
        leave_requests = leave_requests.filter(leave_type__id=leave_type)
    if employee:
        leave_requests = leave_requests.filter(employee__id=employee)
    # Stats rapides
    stats = {
        'pending': LeaveRequest.objects.filter(status='pending').count(),
        'approved': LeaveRequest.objects.filter(status='approved').count(),
        'rejected': LeaveRequest.objects.filter(status='rejected').count(),
        'total': LeaveRequest.objects.count(),
    }
    leave_types = LeaveType.objects.all()
    employees = User.objects.all()
    return render(request, 'leaves/admin_dashboard.html', {
        'leave_requests': leave_requests,
        'stats': stats,
        'leave_types': leave_types,
        'employees': employees,
        'status': status,
        'leave_type_selected': leave_type,
        'employee_selected': employee,
    }) 