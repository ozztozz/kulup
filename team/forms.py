from django import forms
from .models import Team, TeamMember, Payment, Training, Questionnaire, QuestionnaireResponse
from user.models import User
from django.forms import formset_factory    
import re


class TeamForm(forms.ModelForm):
    """
    Form for creating and editing teams
    """
    class Meta:
        model = Team
        fields = ['name', 'description', 'logo', 'founded_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 placeholder-gray-500 bg-gray-50 focus:bg-white text-sm md:text-base',
                'placeholder': 'Takım adı'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 placeholder-gray-500 bg-gray-50 focus:bg-white resize-none text-sm md:text-base',
                'placeholder': 'Takım hakkında açıklama',
                'rows': 4
            }),
            'logo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 text-sm md:text-base'
            }),
            'founded_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white text-sm md:text-base',
                'type': 'date'
            }),
        }
        labels = {
            'name': 'Takım Adı',
            'description': 'Açıklama',
            'logo': 'Logo',
            'founded_date': 'Kuruluş Tarihi',
        }


class TeamMemberForm(forms.ModelForm):
    """
    Form for creating and editing team members
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users who are not already team members
        existing_member_users = TeamMember.objects.values_list('user', flat=True)
        self.fields['user'].queryset = User.objects.filter(is_staff=False)
    class Meta:
        model = TeamMember
        fields = ['user','team','name','surname', 'photo', 'birthdate', 'school', 'is_active', 'notes']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white text-sm md:text-base'
            }),
            'team': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white text-sm md:text-base'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 placeholder-gray-500 bg-gray-50 focus:bg-white text-sm md:text-base',
                'placeholder': 'Üyenin adı'
            }),
            'surname': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 placeholder-gray-500 bg-gray-50 focus:bg-white text-sm md:text-base',
                'placeholder': 'Üyenin adı'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 text-sm md:text-base'
            }),
            'birthdate': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white text-sm md:text-base',
                'type': 'date'
            }),
            'school': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 placeholder-gray-500 bg-gray-50 focus:bg-white text-sm md:text-base',
                'placeholder': 'Üyenin okulu'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 focus:ring-2'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 placeholder-gray-500 bg-gray-50 focus:bg-white resize-none text-sm md:text-base',
                'placeholder': 'Ek notlar',
                'rows': 3
            }),
        }
        labels = {
            'user': 'Kullanıcı',
            'team': 'Takım',
            'photo': 'Fotoğraf',
            'birthdate': 'Doğum Tarihi',
            'school': 'Okulu',
            'is_active': 'Aktif mi?',
            'notes': 'Notlar',
        }


class PaymentForm(forms.ModelForm):
    """
    Form for creating and editing payments
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set today's date as default for paid_date if creating new payment
        if not self.instance.pk:
            from datetime import date
            self.fields['paid_date'].initial = date.today()

    class Meta:
        model = Payment
        fields = ['member', 'month', 'amount', 'is_paid', 'paid_date']
        widgets = {
            'member': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white text-sm md:text-base'
            }),
            'month': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white text-sm md:text-base',
                'type': 'date'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white text-sm md:text-base',
                'step': '0.01'
            }),
            'is_paid': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 focus:ring-2'
            }),
            'paid_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white text-sm md:text-base',
                'type': 'date'
            }),
        }
        labels = {
            'member': 'Üye',
            'month': 'Ay',
            'amount': 'Tutar',
            'is_paid': 'Ödendi mi?',
            'paid_date': 'Ödeme Tarihi',
        }

class TrainingForm(forms.ModelForm):
    """
    Form for creating and editing trainings
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trainer'].queryset = User.objects.filter(is_staff=True)

    class Meta:
        model = Training
        fields = ['team', 'location','day_of_week','time','end_time','trainer','notes']
        widgets = {
            'team': forms.Select(attrs={
                'class': 'w-full px-2 py-1 border border-base-300 rounded-md text-xs bg-base-100 text-base-content focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
            }),
            'day_of_week': forms.Select(attrs={
                'class': 'w-full px-2 py-1 border border-base-300 rounded-md text-xs bg-base-100 text-base-content focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'w-full px-2 py-1 border border-base-300 rounded-md text-xs bg-base-100 text-base-content focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'type': 'time',
                'step': '60'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'w-full px-2 py-1 border border-base-300 rounded-md text-xs bg-base-100 text-base-content focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'type': 'time',
                'step': '60'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-2 py-1 border border-base-300 rounded-md text-xs bg-base-100 text-base-content placeholder-base-content/40 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Antrenman yeri'
            }),
            'trainer': forms.Select(attrs={
                'class': 'w-full px-2 py-1 border border-base-300 rounded-md text-xs bg-base-100 text-base-content focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary',
                'placeholder': 'Antrenör seçin'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-2 py-1 border border-base-300 rounded-md text-xs bg-base-100 text-base-content placeholder-base-content/40 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary resize-y',
                'placeholder': 'Ek notlar',
                'rows': 2
            }),
        }
        labels = {
            'team': 'Takım',
            'day_of_week': 'Gün',
            'time': 'Saat',
            'end_time': 'Bitiş Saati',
            'location': 'Yer',
            'trainer': 'Antrenör',
            'notes': 'Notlar',
        }   

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('time')
        end = cleaned_data.get('end_time')
        if start and end and end <= start:
            self.add_error('end_time', 'Bitiş saati başlangıç saatinden sonra olmalıdır.')
        return cleaned_data
class TrainingFormSet(forms.BaseFormSet):
    def clean(self):
        """
        Add custom validation to ensure no duplicate training sessions for the same team at the same time.
        """
        if any(self.errors):
            return

        seen_trainings = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            team = form.cleaned_data.get('team')
            day_of_week = form.cleaned_data.get('day_of_week')
            time = form.cleaned_data.get('time')

            training_tuple = (team, day_of_week, time)
            if training_tuple in seen_trainings:
                raise forms.ValidationError("Aynı takım için aynı gün ve saatte birden fazla antrenman olamaz.")
            seen_trainings.append(training_tuple)       


def _normalize_field_name(raw_id):
    safe = re.sub(r'[^a-zA-Z0-9_]+', '_', str(raw_id)).strip('_')
    if not safe:
        safe = 'question'
    return f"q_{safe}"


def _validate_questionnaire_schema(schema):
    if not isinstance(schema, dict):
        raise forms.ValidationError('Soru şeması bir JSON nesnesi olmalıdır.')
    questions = schema.get('questions')
    if not isinstance(questions, list) or not questions:
        raise forms.ValidationError('Soru şeması içinde "questions" listesi olmalıdır.')

    seen_ids = set()
    for index, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            raise forms.ValidationError(f"{index}. soru bir JSON nesnesi olmalıdır.")
        qid = question.get('id')
        label = question.get('label')
        qtype = question.get('type')
        if not qid or not isinstance(qid, str):
            raise forms.ValidationError(f"{index}. soru için geçerli bir 'id' alanı gerekli.")
        if qid in seen_ids:
            raise forms.ValidationError(f"Soru 'id' değerleri benzersiz olmalıdır: {qid}.")
        seen_ids.add(qid)
        if not label or not isinstance(label, str):
            raise forms.ValidationError(f"{index}. soru için geçerli bir 'label' alanı gerekli.")
        if qtype not in ['single', 'multi', 'text']:
            raise forms.ValidationError(f"{index}. soru için 'type' sadece single, multi veya text olabilir.")
        if qtype in ['single', 'multi']:
            choices = question.get('choices')
            if not isinstance(choices, list) or not choices:
                raise forms.ValidationError(f"{index}. soru için 'choices' listesi gerekli.")
            for choice in choices:
                if not isinstance(choice, dict):
                    raise forms.ValidationError(f"{index}. soru için seçimler JSON nesnesi olmalıdır.")
                if 'value' not in choice or 'label' not in choice:
                    raise forms.ValidationError(f"{index}. soru için seçimlerde 'value' ve 'label' alanları gerekli.")


class QuestionnaireForm(forms.ModelForm):
    """
    Form for creating and editing questionnaires.
    """
    schema = forms.JSONField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Questionnaire
        fields = ['title', 'description', 'teams', 'begin_date', 'end_date', 'schema', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 placeholder-gray-500 bg-gray-50 focus:bg-white text-sm md:text-base',
                'placeholder': 'Anket başlığı'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 placeholder-gray-500 bg-gray-50 focus:bg-white resize-none text-sm md:text-base',
                'placeholder': 'Kısa açıklama (isteğe bağlı)',
                'rows': 3
            }),
            'teams': forms.CheckboxSelectMultiple(attrs={
                'class': 'team-checkbox'
            }),
            'begin_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white text-sm md:text-base',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 bg-gray-50 focus:bg-white text-sm md:text-base',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 focus:ring-2'
            })
        }
        labels = {
            'title': 'Başlık',
            'description': 'Açıklama',
            'teams': 'Takımlar (İsteğe Bağlı - Boş bırakırsanız tüm takımlar)',
            'begin_date': 'Başlangıç Tarihi',
            'end_date': 'Bitiş Tarihi',
            'is_active': 'Aktif mi?'
        }

    def clean_schema(self):
        schema = self.cleaned_data.get('schema')
        if schema:
            _validate_questionnaire_schema(schema)
        return schema


class QuestionnaireResponseForm(forms.Form):
    """
    Dynamic form generated from questionnaire schema.
    """
    def __init__(self, schema, *args, **kwargs):
        self.schema = schema or {}
        super().__init__(*args, **kwargs)
        self._field_map = []

        questions = self.schema.get('questions', [])
        for index, question in enumerate(questions, start=1):
            qid = question.get('id')
            label = question.get('label')
            qtype = question.get('type')
            required = question.get('required', True)
            field_name = _normalize_field_name(f"{index}_{qid}")
            help_text = question.get('help')

            if qtype == 'text':
                field = forms.CharField(
                    required=required,
                    label=label,
                    help_text=help_text,
                    widget=forms.Textarea(attrs={
                        'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all duration-200 text-gray-900 placeholder-gray-500 bg-gray-50 focus:bg-white resize-none text-sm md:text-base',
                        'rows': 3
                    })
                )
            else:
                choices = [(c.get('value'), c.get('label')) for c in question.get('choices', [])]
                if qtype == 'multi':
                    field = forms.MultipleChoiceField(
                        required=required,
                        label=label,
                        help_text=help_text,
                        choices=choices,
                        widget=forms.CheckboxSelectMultiple
                    )
                else:
                    field = forms.ChoiceField(
                        required=required,
                        label=label,
                        help_text=help_text,
                        choices=choices,
                        widget=forms.RadioSelect
                    )

            self.fields[field_name] = field
            self._field_map.append((field_name, qid, qtype))

    def get_answers(self):
        answers = {}
        for field_name, qid, qtype in self._field_map:
            value = self.cleaned_data.get(field_name)
            if qtype == 'multi' and value is None:
                value = []
            answers[qid] = value
        return answers
