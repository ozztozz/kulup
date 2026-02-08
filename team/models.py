from django.db import models
from django.conf import settings
from django.urls import reverse

# Create your models here.


class Team(models.Model):
    """
    Model for representing a team/club
    """
    name = models.CharField(max_length=100, verbose_name='Takım Adı')
    description = models.TextField(blank=True, null=True, verbose_name='Açıklama')
    logo = models.ImageField(upload_to='team_logos/', blank=True, null=True, verbose_name='Logo')
    founded_date = models.DateField(blank=True, null=True, verbose_name='Kuruluş Tarihi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Takım'
        verbose_name_plural = 'Takımlar'
        ordering = ['name']

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    """
    Model for team members (players, coaches, staff)
    """

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members', verbose_name='Takım')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='members', verbose_name='Kullanıcı')
    name=models.CharField(max_length=30, blank=True, verbose_name='Adı')
    surname=models.CharField(max_length=30, blank=True, verbose_name='Soyadı')
    photo=models.ImageField(upload_to='team_members/', blank=True, null=True, verbose_name='Fotoğraf')
    birthdate=models.DateField(blank=True, null=True, verbose_name='Doğum Tarihi')
    school=models.CharField(max_length=100, blank=True, verbose_name='Okulu')
    joined_date = models.DateField(auto_now_add=True, verbose_name='Katılma Tarihi')
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')
    notes = models.TextField(blank=True, null=True, verbose_name='Notlar')

    class Meta:
        verbose_name = 'Takım Üyesi'
        verbose_name_plural = 'Takım Üyeleri'
        ordering = ['team', 'user__adi', 'user__soyadi']

    def __str__(self):
        return f"{self.name} {self.surname} - {self.team.name}"


class Payment(models.Model):
    """
    Model for tracking monthly payments for team members
    """
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='payments', verbose_name='Üye')
    month = models.DateField(verbose_name='Ay')  # First day of the month
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Tutar')
    is_paid = models.BooleanField(default=False, verbose_name='Ödendi mi?')
    paid_date = models.DateField(null=True, blank=True, verbose_name='Ödeme Tarihi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ödeme'
        verbose_name_plural = 'Ödemeler'
        ordering = ['-month', 'member']
        unique_together = ['member', 'month']  # One payment per member per month

    def __str__(self):
        return f"{self.member} - {self.month.strftime('%Y-%m')} - {'Ödendi' if self.is_paid else 'Ödenmedi'}"

class Training (models.Model):
    LOCATIONS = [
            ('TOBB', 'TOBB'), 
            ('AYTEN SABAN', 'AYTEN SABAN'), 
            ('Diğer', 'Diğer'),]
    DAYS_OF_WEEK = [
            (1, 'Pazartesi'),
            (2, 'Salı'),
            (3, 'Çarşamba'),
            (4, 'Perşembe'),
            (5, 'Cuma'),
            (6, 'Cumartesi'),
            (7, 'Pazar'),
        ]
    """
    Model for team training sessions
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='trainings', verbose_name='Takım')
    day_of_week = models.IntegerField(verbose_name='Gün', choices=DAYS_OF_WEEK)  # 0=Monday, 6=Sunday
    time = models.TimeField(verbose_name='Saat')
    end_time = models.TimeField(verbose_name='Bitiş Saati', blank=True, null=True)
    location = models.CharField(max_length=200, verbose_name='Lokasyon',
                                choices=LOCATIONS)
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='trainings', verbose_name='Antrenör')
    notes = models.TextField(blank=True, null=True, verbose_name='Notlar')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Antrenman'
        verbose_name_plural = 'Antrenmanlar'
        ordering = ['-day_of_week', 'time']

    def __str__(self):
        return f"{self.team.name} - {self.day_of_week} {self.time}"
    




class Questionnaire(models.Model):
    """
    Questionnaire schema stored as JSON.
    """
    title = models.CharField(max_length=150, verbose_name='Başlık')
    description = models.TextField(blank=True, null=True, verbose_name='Açıklama')
    schema = models.JSONField(default=dict, verbose_name='Soru Şeması')
    teams = models.ManyToManyField(Team, blank=True, related_name='questionnaires', verbose_name='Takımlar')
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')
    begin_date = models.DateField(null=True, blank=True, verbose_name='Başlangıç Tarihi')
    end_date = models.DateField(null=True, blank=True, verbose_name='Bitiş Tarihi')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_questionnaires', verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Anket'
        verbose_name_plural = 'Anketler'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('team:questionnaire_detail', kwargs={'pk': self.pk})


class QuestionnaireResponse(models.Model):
    """
    Responses for a questionnaire stored as JSON answers.
    """
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='responses', verbose_name='Anket')
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='questionnaire_responses', verbose_name='Üye')
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='questionnaire_responses', verbose_name='Cevaplayan')
    answers = models.JSONField(default=dict, verbose_name='Cevaplar')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Anket Cevabı'
        verbose_name_plural = 'Anket Cevapları'
        ordering = ['-created_at']
        unique_together = ['questionnaire', 'member']

    def __str__(self):
        return f"{self.member} - {self.questionnaire.title}"
    