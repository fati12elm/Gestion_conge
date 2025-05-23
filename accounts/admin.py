from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Informations supplémentaires", {
            "fields": (
                "role", "department", "phone", "address", "profile_picture",
                # Ajoute ici tous les champs personnalisés de ton User
            ),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informations supplémentaires", {
            "fields": (
                "role", "department", "phone", "address", "profile_picture",
                # Ajoute ici tous les champs personnalisés de ton User
            ),
        }),
    )
    list_display = ("username", "email", "role", "department", "is_staff", "is_active")
    search_fields = ("username", "email", "role", "department")
