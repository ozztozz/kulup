from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm
from django.db import models
from team.models import TeamMember, Team, Questionnaire, QuestionnaireResponse, Training, Payment

from datetime import date, time as time_obj
# Create your views here.


def landing_view(request):
    """
    Landing page for swimming club
    """
    teams = Team.objects.all().order_by('name')
    team_count = teams.count()
    member_count = TeamMember.objects.filter(is_active=True).count()
    members = TeamMember.objects.filter(is_active=True, photo__isnull=False).order_by('?')[:15]
    
    context = {
        'teams': teams,
        'team_count': team_count,
        'member_count': member_count,
        'members': members,
        'title': 'Yüzme Kulübü - Anasayfa'
    }
    return render(request, 'user/landing.html', context)


def register_view(request):
    """
    View for user registration
    """
    if request.user.is_authenticated:
        return redirect('user:home')  # Redirect if already logged in

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Hoş geldiniz {user.adi}! Hesabınız başarıyla oluşturuldu.')
            return redirect('user:home')
        else:
            messages.error(request, 'Lütfen aşağıdaki hataları düzeltin.')
    else:
        form = UserRegistrationForm()

    return render(request, 'user/register.html', {'form': form})


def login_view(request):
    """
    View for user login
    """
    if request.user.is_authenticated:
        return redirect('user:home')  # Redirect if already logged in

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # username field contains email
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Tekrar hoş geldiniz, {user.adi}!')
                return redirect('user:home')
            else:
                messages.error(request, 'Geçersiz e-posta veya şifre.')
        else:
            messages.error(request, 'Lütfen aşağıdaki hataları düzeltin.')
    else:
        form = UserLoginForm()

    return render(request, 'user/login.html', {'form': form})


def logout_view(request):
    """
    View for user logout
    """
    logout(request)
    messages.info(request, 'Başarıyla çıkış yaptınız.')
    return redirect('user:login')


@login_required
def home_view(request):
    """
    Home view for logged-in users
    Staff users see the old home page, regular users go to dashboard
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return render(request, 'user/home.html', {'user': request.user})
        else:
            user_team_members = TeamMember.objects.filter(user=request.user, is_active=True)
            team_ids = list(user_team_members.values_list('team_id', flat=True))
            member_ids = list(user_team_members.values_list('id', flat=True))
            today = date.today()
            current_month = today.replace(day=1)

            questionnaires = Questionnaire.objects.filter(
                (models.Q(teams__id__in=team_ids) | models.Q(teams__isnull=True)) &
                (models.Q(begin_date__isnull=True) | models.Q(begin_date__lte=today)) &
                (models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)),
                is_active=True
            ).prefetch_related('teams').select_related('created_by').distinct().order_by('-created_at')

            responses = QuestionnaireResponse.objects.filter(
                member_id__in=member_ids
            ).select_related('questionnaire').values_list('questionnaire_id', 'member_id')
            responded_set = set(responses)

            # Get all responses for displaying answered questionnaires
            all_responses = QuestionnaireResponse.objects.filter(
                member_id__in=member_ids
            ).select_related('questionnaire').order_by('-created_at')

            unanswered_by_member = []
            answered_by_member = []
            
            for member in user_team_members:
                unanswered_questionnaires = []
                answered_responses = []
                
                for questionnaire in questionnaires:
                    questionnaire_team_ids = [t.id for t in questionnaire.teams.all()]
                    if not questionnaire_team_ids or member.team_id in questionnaire_team_ids:
                        if (questionnaire.id, member.id) not in responded_set:
                            unanswered_questionnaires.append(questionnaire)

                if unanswered_questionnaires:
                    unanswered_by_member.append({
                        'member': member,
                        'questionnaires': unanswered_questionnaires
                    })
                
                # Collect answered questionnaires for this member
                member_responses = all_responses.filter(member=member)
                if member_responses.exists():
                    answered_by_member.append({
                        'member': member,
                        'responses': member_responses
                    })

            # Get trainings for user's teams
            day_names = {1: 'Pazartesi', 2: 'Salı', 3: 'Çarşamba', 4: 'Perşembe', 5: 'Cuma', 6: 'Cumartesi', 7: 'Pazar'}
            day_abbrev = {1: 'Pz', 2: 'Sa', 3: 'Ça', 4: 'Pe', 5: 'Cu', 6: 'Ct', 7: 'Pz'}
            
            # Get all unique trainings across user's teams with member names
            trainings_dict = {}
            for member in user_team_members:
                team_trainings = Training.objects.filter(team=member.team).order_by('day_of_week', 'time')
                for training in team_trainings:
                    key = (training.id, member.team_id)
                    if key not in trainings_dict:
                        trainings_dict[key] = {
                            'training': training,
                            'members': []
                        }
                    trainings_dict[key]['members'].append(member)
            
            # Create calendar with combined trainings
            calendar_days = []
            for day_num in range(1, 8):
                day_trainings = []
                for (train_id, team_id), data in trainings_dict.items():
                    if data['training'].day_of_week == day_num:
                        day_trainings.append(data)
                
                # Sort trainings by time
                day_trainings.sort(key=lambda x: x['training'].time)
                
                # Split trainings into morning and evening (16:00+)
                morning_trainings = [t for t in day_trainings if t['training'].time < time_obj(16, 0)]
                evening_trainings = [t for t in day_trainings if t['training'].time >= time_obj(16, 0)]
                
                calendar_days.append({
                    'day_num': day_num,
                    'day_name': day_names[day_num],
                    'day_abbrev': day_abbrev[day_num],
                    'morning_trainings': morning_trainings,
                    'evening_trainings': evening_trainings
                })
            
            training_calendar = {
                'calendar': calendar_days
            }

            today_day_num = today.isoweekday()
            today_day_name = day_names[today_day_num]
            today_morning_trainings = []
            today_evening_trainings = []
            for day in calendar_days:
                if day['day_num'] == today_day_num:
                    today_morning_trainings = day['morning_trainings']
                    today_evening_trainings = day['evening_trainings']
                    break

            today_trainings = {
                'morning_trainings': today_morning_trainings,
                'evening_trainings': today_evening_trainings,
            }

            monthly_payments = Payment.objects.filter(
                member_id__in=member_ids,
                month=current_month
            ).select_related('member')
            payment_by_member_id = {payment.member_id: payment for payment in monthly_payments}

            payment_info_by_member = []
            for member in user_team_members:
                payment = payment_by_member_id.get(member.id)
                payment_info_by_member.append({
                    'member': member,
                    'payment': payment,
                })

            context = {
                'user': request.user,
                'user_team_members': user_team_members,
                'unanswered_by_member': unanswered_by_member,
                'answered_by_member': answered_by_member,
                'training_calendar': training_calendar,
                'today_day_name': today_day_name,
                'today_trainings': today_trainings,
                'current_month': current_month,
                'payment_info_by_member': payment_info_by_member,
                'title': 'Anasayfa'
            }
            return render(request, 'user/non_staff_home.html', context)
    return redirect('user:landing')


@login_required
def profile_view(request):
    """
    View for displaying user profile
    """
    return render(request, 'user/profile.html', {'user': request.user})
@login_required
def profile_detail(request, member_id):
    """
    View for displaying user profile details
    """
    member = get_object_or_404(TeamMember, id=member_id)
    current_month = date.today().replace(day=1)
    current_payment = member.payments.filter(month=current_month).first()
    return render(request, 'user/profile_detail.html', {'member': member, 'current_payment': current_payment})