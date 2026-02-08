from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm
from team.models import TeamMember, Team

from datetime import date
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
            return redirect('team:dashboard')
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