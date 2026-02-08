from django.contrib import admin
from .models import Team, TeamMember, Training, Questionnaire, QuestionnaireResponse

# Register your models here.


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """
    Admin configuration for Team model
    """
    list_display = ('name', 'founded_date', 'created_at')
    list_filter = ('founded_date', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'description', 'logo')
        }),
        ('Tarih Bilgileri', {
            'fields': ('founded_date', 'created_at', 'updated_at')
        }),
    )


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """
    Admin configuration for TeamMember model
    """
    list_display = ('user', 'team', 'name', 'surname', 'photo', 'birthdate', 'school', 'is_active', 'joined_date')
    list_filter = ('team', 'is_active', 'joined_date', 'birthdate')
    search_fields = ('user__adi', 'user__soyadi', 'user__email', 'team__name', 'name', 'surname', 'school')
    ordering = ('team', 'user__adi', 'user__soyadi')
    readonly_fields = ('joined_date',)

    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('team', 'user')
        }),
        ('Kişisel Bilgiler', {
            'fields': ('name', 'surname', 'photo', 'birthdate', 'school')
        }),
        ('Durum', {
            'fields': ('is_active', 'joined_date', 'notes')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('team', 'user')


@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ('team', 'day_of_week', 'time', 'end_time', 'trainer', 'location')
    list_filter = ('team', 'day_of_week', 'location')
    search_fields = ('team__name', 'trainer', 'location', 'notes')
    ordering = ('day_of_week', 'time')


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_teams', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'teams', 'created_at')
    search_fields = ('title', 'created_by__adi', 'created_by__soyadi')
    ordering = ('-created_at',)
    filter_horizontal = ('teams',)
    
    def get_teams(self, obj):
        return ", ".join([team.name for team in obj.teams.all()]) if obj.teams.exists() else "Tüm takımlar"
    get_teams.short_description = 'Takımlar'


@admin.register(QuestionnaireResponse)
class QuestionnaireResponseAdmin(admin.ModelAdmin):
    list_display = ('questionnaire', 'member', 'responder', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('questionnaire__title', 'member__name', 'member__surname', 'member__user__adi', 'member__user__soyadi')
    ordering = ('-created_at',)
