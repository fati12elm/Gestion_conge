from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from leaves.models import LeaveType, LeaveBalance, LeaveRequest

User = get_user_model()

class Command(BaseCommand):
    help = 'Crée des données de test pour l\'application de gestion des congés'

    def handle(self, *args, **kwargs):
        self.stdout.write('Création des données de test...')

        # Création des types de congés
        leave_types = [
            ('Congé annuel', 25),
            ('RTT', 12),
            ('Congé maladie', 0),
            ('Congé sans solde', 0),
        ]

        for name, days in leave_types:
            leave_type, created = LeaveType.objects.get_or_create(
                name=name,
                defaults={'default_days': days}
            )
            if created:
                self.stdout.write(f'Type de congé créé : {name}')

        # Création des utilisateurs de test
        test_users = [
            {
                'username': 'employee1',
                'email': 'employee1@example.com',
                'password': 'testpass123',
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'role': 'employee',
                'department': 'Développement',
                'phone': '0123456789',
            },
            {
                'username': 'manager1',
                'email': 'manager1@example.com',
                'password': 'testpass123',
                'first_name': 'Marie',
                'last_name': 'Martin',
                'role': 'manager',
                'department': 'Développement',
                'phone': '0123456790',
            },
            {
                'username': 'hr1',
                'email': 'hr1@example.com',
                'password': 'testpass123',
                'first_name': 'Sophie',
                'last_name': 'Dubois',
                'role': 'hr',
                'department': 'Ressources Humaines',
                'phone': '0123456791',
            },
        ]

        for user_data in test_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                    'department': user_data['department'],
                    'phone': user_data['phone'],
                    'is_active': True,
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'Utilisateur créé : {user.get_full_name()} ({user.role})')

                # Création des soldes de congés pour le nouvel utilisateur
                for leave_type in LeaveType.objects.all():
                    LeaveBalance.objects.get_or_create(
                        user=user,
                        leave_type=leave_type,
                        year=timezone.now().year,
                        defaults={
                            'initial_balance': leave_type.default_days,
                            'used_balance': 0,
                        }
                    )

        # Création de quelques demandes de congés
        employee = User.objects.get(username='employee1')
        manager = User.objects.get(username='manager1')
        annual_leave = LeaveType.objects.get(name='Congé annuel')

        # Demande en attente
        LeaveRequest.objects.get_or_create(
            user=employee,
            leave_type=annual_leave,
            start_date=timezone.now().date() + timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=35),
            defaults={
                'reason': 'Vacances d\'été',
                'status': 'pending',
            }
        )

        # Demande approuvée
        LeaveRequest.objects.get_or_create(
            user=employee,
            leave_type=annual_leave,
            start_date=timezone.now().date() + timedelta(days=60),
            end_date=timezone.now().date() + timedelta(days=65),
            defaults={
                'reason': 'Vacances d\'hiver',
                'status': 'approved',
                'validated_by': manager,
                'validation_date': timezone.now(),
            }
        )

        self.stdout.write(self.style.SUCCESS('Données de test créées avec succès !')) 