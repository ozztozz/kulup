from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0012_alter_training_trainer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='Başlık')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Açıklama')),
                ('schema', models.JSONField(default=dict, verbose_name='Soru Şeması')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktif mi?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_questionnaires', to=settings.AUTH_USER_MODEL, verbose_name='Oluşturan')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questionnaires', to='team.teammember', verbose_name='Üye')),
            ],
            options={
                'verbose_name': 'Anket',
                'verbose_name_plural': 'Anketler',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='QuestionnaireResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answers', models.JSONField(default=dict, verbose_name='Cevaplar')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questionnaire_responses', to='team.teammember', verbose_name='Üye')),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='team.questionnaire', verbose_name='Anket')),
                ('responder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questionnaire_responses', to=settings.AUTH_USER_MODEL, verbose_name='Cevaplayan')),
            ],
            options={
                'verbose_name': 'Anket Cevabı',
                'verbose_name_plural': 'Anket Cevapları',
                'ordering': ['-created_at'],
                'unique_together': {('questionnaire', 'member')},
            },
        ),
    ]
