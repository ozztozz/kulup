from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for User model with email as username
    """
    model = User

    # Fields to display in the admin list view
    list_display = ('email', 'adi', 'soyadi', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')

    # Fields to search
    search_fields = ('email', 'adi', 'soyadi')

    # Ordering
    ordering = ('email',)

    # Fieldsets for the add/edit forms
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('adi', 'soyadi')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fieldsets for adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'adi', 'soyadi', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    # Since email is the username field, we need to override some methods
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
