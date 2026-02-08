from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from datetime import date, datetime, timedelta, time as dt_time
from django.db import models
from .models import Team, TeamMember, Payment, Training, Questionnaire, QuestionnaireResponse
from .forms import TeamForm, TeamMemberForm, PaymentForm, TrainingForm, QuestionnaireForm, QuestionnaireResponseForm


# Create your views here.


@login_required
@staff_member_required
def team_create(request):
    """
    Create a new team
    """
    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES)
        if form.is_valid():
            team = form.save()
            messages.success(request, f'"{team.name}" takımı başarıyla oluşturuldu!')
            return redirect('team:detail', pk=team.pk)
    else:
        form = TeamForm()

    context = {
        'form': form,
        'title': 'Yeni Takım Oluştur'
    }
    return render(request, 'team/team_form.html', context)


@login_required
@staff_member_required
def team_update(request, pk):
    """
    Update an existing team
    """
    team = get_object_or_404(Team, pk=pk)

    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES, instance=team)
        if form.is_valid():
            team = form.save()
            messages.success(request, f'"{team.name}" takımı başarıyla güncellendi!')
            return redirect('team:detail', pk=team.pk)
    else:
        form = TeamForm(instance=team)

    context = {
        'form': form,
        'team': team,
        'title': f'{team.name} - Düzenle'
    }
    return render(request, 'team/team_form.html', context)


@login_required
@staff_member_required
def team_list(request):
    """
    Display list of all teams
    """
    teams = Team.objects.all().order_by('name')
    # Add member count to each team for template use
    for team in teams:
        team.active_member_count = team.members.filter(is_active=True).count()

    context = {
        'teams': teams,
        'title': 'Takımlar'
    }
    return render(request, 'team/team_list.html', context)


@login_required
@staff_member_required
def team_detail(request, pk):
    """
    Display details of a specific team
    """
    team = get_object_or_404(Team, pk=pk)
    members = team.members.filter(is_active=True).select_related('user')
    context = {
        'team': team,
        'members': members,
        'title': f'{team.name} - Detaylar'
    }
    return render(request, 'team/team_detail.html', context)


@login_required
@staff_member_required
def team_members(request, pk):
    """
    Display all members of a specific team
    """
    team = get_object_or_404(Team, pk=pk)
    members = team.members.all().select_related('user').order_by('-joined_date', 'name', 'surname')
    context = {
        'team': team,
        'members': members,
        'title': f'{team.name} - Üyeler'
    }
    return render(request, 'team/team_members.html', context)


@login_required
@staff_member_required
def team_member_create(request, team_pk):
    """
    Create a new team member
    """
    team = get_object_or_404(Team, pk=team_pk)

    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save(commit=False)
            member.team = team
            member.save()
            messages.success(request, f'{member.name} {member.surname} başarıyla takıma eklendi!')
            return redirect('team:members', pk=team.pk)
    else:
        form = TeamMemberForm()

    context = {
        'form': form,
        'team': team,
        'title': f'{team.name} - Yeni Üye Ekle'
    }
    return render(request, 'team/team_member_form.html', context)


@login_required
@staff_member_required
def team_member_update(request, pk):
    """
    Update an existing team member
    """
    member = get_object_or_404(TeamMember, pk=pk)

    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'{member.name} {member.surname} bilgileri güncellendi!')
            return redirect('team:members', pk=member.team.pk)
    else:
        form = TeamMemberForm(instance=member)

    context = {
        'form': form,
        'member': member,
        'team': member.team,
        'title': f'{member.name} {member.surname} - Düzenle'
    }
    return render(request, 'team/team_member_form.html', context)


@login_required
def team_member_detail(request, pk):
    """
    Display details of a specific team member
    """
    member = get_object_or_404(TeamMember, pk=pk)
    
    # Check permissions: staff can view all, regular users can only view their own profile
    if not request.user.is_staff and member.user != request.user:
        raise PermissionDenied("Bu profili görüntüleme yetkiniz yok.")
    
    team = member.team
    
    # Get payments for this member
    payments = member.payments.all().order_by('-month')
    
    # Calculate statistics
    paid_count = payments.filter(is_paid=True).count()
    total_paid = payments.filter(is_paid=True).aggregate(total=models.Sum('amount'))['total'] or 0

    # Get today's date for filtering
    today = date.today()
    
    # Count questionnaires within date range (if dates are set)
    questionnaire_count = Questionnaire.objects.filter(
        models.Q(teams=member.team) | models.Q(teams__isnull=True),
        models.Q(begin_date__isnull=True) | models.Q(begin_date__lte=today),
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
    ).distinct().count()
    response_count = member.questionnaire_responses.count()
    
    context = {
        'member': member,
        'questionnaire_count': questionnaire_count,
        'response_count': response_count,
        'team': team,
        'payments': payments,
        'paid_count': paid_count,
        'total_paid': total_paid,
        'title': f'{member.name} {member.surname} - Detaylar'
    }
    return render(request, 'team/team_member_detail.html', context)


@login_required
@staff_member_required
def team_member_delete(request, pk):
    """
    Delete a team member
    """
    member = get_object_or_404(TeamMember, pk=pk)
    team = member.team


    if request.method == 'POST':
        member_name = f'{member.name} {member.surname}'
        member.delete()
        messages.success(request, f'{member_name} takımdan çıkarıldı!')
        return redirect('team:members', pk=team.pk)

    context = {
        'member': member,
        'team': team,
        'title': f'{member.name} {member.surname} - Sil'
    }
    return render(request, 'team/team_member_confirm_delete.html', context)


def _ensure_member_access(request, member):
    if request.user.is_staff:
        return
    if request.user != member.user:
        raise PermissionDenied


@login_required
@staff_member_required
def questionnaire_staff_list(request):
    questionnaires = (
        Questionnaire.objects.prefetch_related('teams').select_related('created_by')
        .annotate(response_count=models.Count('responses'))
        .order_by('-created_at')
    )
    context = {
        'questionnaires': questionnaires,
        'title': 'Anketler'
    }
    return render(request, 'team/questionnaire_staff_list.html', context)


@login_required
@staff_member_required
def questionnaire_create_global(request):
    if request.method == 'POST':
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            questionnaire = form.save(commit=False)
            questionnaire.created_by = request.user
            questionnaire.save()
            # Save M2M relationship
            form.save_m2m()
            messages.success(request, 'Anket başarıyla oluşturuldu!')
            return redirect('team:questionnaire_staff_list')
    else:
        form = QuestionnaireForm()

    context = {
        'form': form,
        'member': None,
        'team': None,
        'title': 'Yeni Anket'
    }
    return render(request, 'team/questionnaire_form.html', context)


@login_required
def questionnaire_list(request, member_pk):
    member = get_object_or_404(TeamMember, pk=member_pk)
    _ensure_member_access(request, member)

    # Get today's date for filtering
    today = date.today()

    # Show questionnaires for this member's team and global questionnaires (teams empty)
    # Filter by date range if begin_date or end_date is set
    questionnaires = Questionnaire.objects.filter(
        models.Q(teams=member.team) | models.Q(teams__isnull=True),
        models.Q(begin_date__isnull=True) | models.Q(begin_date__lte=today),
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
    ).prefetch_related('teams').select_related('created_by').distinct().order_by('-created_at')
    
    responses = QuestionnaireResponse.objects.filter(member=member, questionnaire__in=questionnaires)
    response_map = {response.questionnaire_id: response for response in responses}

    context = {
        'member': member,
        'team': member.team,
        'questionnaires': questionnaires,
        'response_map': response_map,
        'title': f'{member.name} {member.surname} - Anketler'
    }
    return render(request, 'team/questionnaire_list.html', context)


@login_required
@staff_member_required
def questionnaire_create(request, member_pk):
    member = get_object_or_404(TeamMember, pk=member_pk)

    if request.method == 'POST':
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            questionnaire = form.save(commit=False)
            questionnaire.created_by = request.user
            questionnaire.save()
            # Handle M2M relationship - save teams after the questionnaire is created
            form.save_m2m()
            # Auto-add member's team if no teams specified
            if not questionnaire.teams.exists():
                questionnaire.teams.add(member.team)
            messages.success(request, 'Anket başarıyla oluşturuldu!')
            return redirect('team:questionnaire_list', member_pk=member.pk)
    else:
        form = QuestionnaireForm(initial={'teams': [member.team]})

    context = {
        'form': form,
        'member': member,
        'team': member.team,
        'title': f'{member.name} {member.surname} - Yeni Anket'
    }
    return render(request, 'team/questionnaire_form.html', context)


@login_required
def questionnaire_update(request, pk):
    questionnaire = get_object_or_404(Questionnaire, pk=pk)
    
    # Allow staff or the creator to update
    if not request.user.is_staff and questionnaire.created_by != request.user:
        raise PermissionDenied("Bu anketi düzenleme yetkiniz yok.")
    
    member = None
    if request.GET.get('member'):
        member = get_object_or_404(TeamMember, pk=request.GET.get('member'))
        _ensure_member_access(request, member)

    if request.method == 'POST':
        form = QuestionnaireForm(request.POST, instance=questionnaire)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anket başarıyla güncellendi!')
            return redirect('team:questionnaire_detail', pk=questionnaire.pk)
    else:
        form = QuestionnaireForm(instance=questionnaire)

    context = {
        'form': form,
        'member': member,
        'team': member.team if member else None,
        'title': f'{questionnaire.title} - Düzenle'
    }
    return render(request, 'team/questionnaire_form.html', context)


@login_required
@staff_member_required
def questionnaire_delete(request, pk):
    """
    Delete a questionnaire
    """
    questionnaire = get_object_or_404(Questionnaire, pk=pk)

    if request.method == 'POST':
        questionnaire.delete()
        messages.success(request, f'Anket başarıyla silindi!')
        return redirect('team:questionnaire_staff_list')

    context = {
        'questionnaire': questionnaire,
        'title': 'Anket Sil'
    }
    return render(request, 'team/questionnaire_confirm_delete.html', context)


@login_required
@staff_member_required
def questionnaire_detail(request, pk):
    questionnaire = get_object_or_404(Questionnaire.objects.prefetch_related('teams').select_related('created_by').filter(pk=pk))
    member = None
    if request.user.is_staff and request.GET.get('member'):
        member = get_object_or_404(TeamMember, pk=request.GET.get('member'))
    elif not request.user.is_staff:
        member = TeamMember.objects.filter(user=request.user).first()

    if member:
        _ensure_member_access(request, member)

    response = None
    if member:
        response = QuestionnaireResponse.objects.filter(questionnaire=questionnaire, member=member).first()
    
    # Get all applicable team members
    questionnaire_teams = questionnaire.teams.all()
    if questionnaire_teams.exists():
        # Team-specific questionnaire - get members from all assigned teams
        all_members = TeamMember.objects.filter(
            team__in=questionnaire_teams, 
            is_active=True
        ).select_related('user', 'team').order_by('team__name', 'name', 'surname')
    else:
        # Global questionnaire - get all active members
        all_members = TeamMember.objects.filter(
            is_active=True
        ).select_related('user', 'team').order_by('team__name', 'name', 'surname')
    
    # Get all responses for this questionnaire
    responses = QuestionnaireResponse.objects.filter(
        questionnaire=questionnaire
    ).select_related('member', 'responder')
    
    # Create a response map for quick lookup
    response_map = {resp.member_id: resp for resp in responses}
    
    # Calculate choice statistics for each question
    questions_with_stats = []
    for question in questionnaire.schema.get('questions', []):
        question_data = question.copy()
        
        if question.get('choices'):
            # Initialize counts and member lists for each choice
            choice_counts = {}
            choice_members = {}
            for choice in question['choices']:
                choice_counts[choice['value']] = 0
                choice_members[choice['value']] = []
            
            # Count responses and track members for each choice
            for resp in responses:
                answer = resp.answers.get(question['id'])
                if answer:
                    if question['type'] == 'multi':
                        # Multiple choice - answer is a list
                        if isinstance(answer, list):
                            for ans_value in answer:
                                if ans_value in choice_counts:
                                    choice_counts[ans_value] += 1
                                    choice_members[ans_value].append(resp.member)
                    else:
                        # Single choice - answer is a string
                        if answer in choice_counts:
                            choice_counts[answer] += 1
                            choice_members[answer].append(resp.member)
            
            # Add counts and members to choices
            choices_with_counts = []
            for choice in question['choices']:
                choice_with_count = choice.copy()
                choice_with_count['count'] = choice_counts.get(choice['value'], 0)
                choice_with_count['members'] = choice_members.get(choice['value'], [])
                choices_with_counts.append(choice_with_count)
            
            question_data['choices'] = choices_with_counts
        
        questions_with_stats.append(question_data)
    
    # Build member status list
    responded_members = []
    not_responded_members = []
    
    for m in all_members:
        if m.id in response_map:
            responded_members.append({
                'member': m,
                'response': response_map[m.id]
            })
        else:
            not_responded_members.append(m)
    
    context = {
        'questionnaire': questionnaire,
        'member': member,
        'team': member.team if member else None,
        'response': response,
        'responded_members': responded_members,
        'not_responded_members': not_responded_members,
        'questions_with_stats': questions_with_stats,
        'title': questionnaire.title
    }
    return render(request, 'team/questionnaire_detail.html', context)


@login_required
def questionnaire_respond(request, pk):
    questionnaire = get_object_or_404(Questionnaire, pk=pk, is_active=True)
    member = None
    if request.user.is_staff and request.GET.get('member'):
        member = get_object_or_404(TeamMember, pk=request.GET.get('member'))
    elif not request.user.is_staff:
        member = TeamMember.objects.filter(pk=request.GET.get('member')).first()

    if not member:
        messages.error(request, 'Lütfen önce bir üye seçin.')
        return redirect('team:questionnaire_staff_list')

    _ensure_member_access(request, member)

    existing_response = QuestionnaireResponse.objects.filter(questionnaire=questionnaire, member=member).first()
    form_seed = QuestionnaireResponseForm(questionnaire.schema)
    initial_data = {}
    
    # Get current question IDs from the schema
    current_question_ids = {q['id'] for q in questionnaire.schema.get('questions', [])}
    
    if existing_response:
        # Only populate data for questions that still exist in current schema
        for field_name, qid, qtype in form_seed._field_map:
            if qid in current_question_ids:
                value = existing_response.answers.get(qid)
                if qtype == 'multi' and value is None:
                    value = []
                initial_data[field_name] = value

    if request.method == 'POST':
        form = QuestionnaireResponseForm(questionnaire.schema, request.POST)
        if form.is_valid():
            answers = form.get_answers()
            
            # Clean up old answers - only keep answers for current questions
            cleaned_answers = {qid: answer for qid, answer in answers.items() if qid in current_question_ids}
            
            if existing_response:
                existing_response.answers = cleaned_answers
                existing_response.responder = request.user
                existing_response.save()
            else:
                QuestionnaireResponse.objects.create(
                    questionnaire=questionnaire,
                    member=member,
                    responder=request.user,
                    answers=cleaned_answers
                )
            messages.success(request, 'Cevaplar kaydedildi!')
            if request.user.is_staff:
                return redirect('team:questionnaire_detail', pk=questionnaire.pk)
            else:
                return redirect('team:questionnaire_list', member_pk=member.pk)
            
    else:
        form = QuestionnaireResponseForm(questionnaire.schema, initial=initial_data)

    context = {
        'form': form,
        'questionnaire': questionnaire,
        'member': member,
        'team': member.team,
        'title': f'{questionnaire.title} - Yanıtla'
    }
    return render(request, 'team/questionnaire_response_form.html', context)


@login_required
@staff_member_required
def payment_list(request):
    """

    List all payments grouped by team
    """
    payments = Payment.objects.select_related('member__team', 'member__user').order_by('member__team__name', '-month', 'member')
    
    # Group payments by team
    payments_by_team = {}
    for payment in payments:
        team_name = payment.member.team.name
        if team_name not in payments_by_team:
            payments_by_team[team_name] = []
        payments_by_team[team_name].append(payment)
    
    # Get current month
    current_month = date.today().replace(day=1)
    
    # Get members who have paid this month
    paid_member_ids = Payment.objects.filter(
        month=current_month,
        is_paid=True
    ).values_list('member_id', flat=True)
    
    # Get unpaid active members grouped by team
    unpaid_members = TeamMember.objects.filter(
        is_active=True
    ).exclude(

        id__in=paid_member_ids
    ).select_related('team', 'user').order_by('team__name')
    
    unpaid_by_team = {}
    for member in unpaid_members:
        team_name = member.team.name
        if team_name not in unpaid_by_team:
            unpaid_by_team[team_name] = []
        unpaid_by_team[team_name].append(member)
    
    # Calculate summary statistics
    total_payments = len(paid_member_ids)+len(unpaid_members)
    paid_payments = payments.filter(is_paid=True).count()
    unpaid_payments = total_payments - paid_payments
    total_amount = payments.filter(is_paid=True).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Calculate team statistics
    team_summaries = []
    for team_name, team_payments in payments_by_team.items():
        paid_count = sum(1 for p in team_payments if p.is_paid)
        unpaid_count = len(unpaid_members.filter(team__name=team_name)) 
        team_total = sum(p.amount for p in team_payments if p.is_paid)

        team_summaries.append({
            'name': team_name,
            'payments': team_payments,
            'total_payments': len(team_payments),
            'paid_payments': paid_count,
            'unpaid_payments': unpaid_count,
            'total_amount': team_total,
            'unpaid_members': len(unpaid_by_team.get(team_name, []))
        })
    
    context = {
        'team_summaries': team_summaries,
        'unpaid_by_team': unpaid_by_team,
        'current_month': current_month,
        'total_payments': total_payments,

        'paid_payments': paid_payments,
        'unpaid_payments': unpaid_payments,
        'total_amount': total_amount,
        'title': 'Ödemeler'
    }
    return render(request, 'team/payment_list.html', context)


@login_required
@staff_member_required
def payment_create(request):
    """
    Create a new payment
    """
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Ödeme başarıyla oluşturuldu!')
            return redirect('team:payment_list')
    else:
        initial = {}
        if 'member' in request.GET:
            initial['member'] = request.GET['member']
        if 'month' in request.GET:
            initial['month'] = request.GET['month']
        form = PaymentForm(initial=initial)

    context = {
        'form': form,
        'title': 'Yeni Ödeme Oluştur'
    }
    return render(request, 'team/payment_form.html', context)


@login_required
@staff_member_required
def payment_update(request, pk):
    """
    Update an existing payment
    """
    payment = get_object_or_404(Payment, pk=pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Ödeme başarıyla güncellendi!')
            return redirect('team:payment_list')
    else:
        form = PaymentForm(instance=payment)

    context = {
        'form': form,
        'payment': payment,
        'title': 'Ödeme Düzenle'
    }
    return render(request, 'team/payment_form.html', context)


@login_required
@staff_member_required
def payment_delete(request, pk):
    """
    Delete a payment
    """
    payment = get_object_or_404(Payment, pk=pk)

    if request.method == 'POST':
        payment.delete()
        messages.success(request, f'Ödeme başarıyla silindi!')
        return redirect('team:payment_list')

    context = {
        'payment': payment,
        'title': 'Ödeme Sil'
    }
    return render(request, 'team/payment_confirm_delete.html', context)

@login_required
@staff_member_required 
def training_create(request):
    """
    Create a new training session
    """
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        if form.is_valid():
            training = form.save()
            messages.success(request, f'Antrenman başarıyla oluşturuldu!')
            return redirect('team:training_list')
    else:
        form = TrainingForm()

    context = {
        'form': form,
        'title': 'Yeni Antrenman Oluştur'
    }
    return render(request, 'team/training_form.html', context)

@login_required
@staff_member_required 
def training_list(request):
    """
    List all training sessions
    """
    trainings = Training.objects.select_related('team').order_by('day_of_week', 'time')
    context = {
        'trainings': trainings,
        'title': 'Antrenmanlar'
    }
    return render(request, 'team/training_list.html', context)  

def training_update(request, pk):
    """
    Update an existing training session
    """
    training = get_object_or_404(Training, pk=pk)

    if request.method == 'POST':
        form = TrainingForm(request.POST, instance=training)
        if form.is_valid():
            training = form.save()
            messages.success(request, f'Antrenman başarıyla güncellendi!')
            return redirect('team:training_list')
    else:
        form = TrainingForm(instance=training)

    context = {
        'form': form,
        'training': training,
        'title': 'Antrenman Düzenle'
    }
    return render(request, 'team/training_form.html', context)      

@login_required
@staff_member_required  
def training_delete(request, pk):
    """
    Delete a training session
    """
    training = get_object_or_404(Training, pk=pk)

    if request.method == 'POST':
        training.delete()
        messages.success(request, f'Antrenman başarıyla silindi!')
        return redirect('team:training_list')

    context = {
        'training': training,
        'title': 'Antrenman Sil'
    }   



@login_required
def training_weekly(request):
    """
    Display weekly training schedule organized by day
    """
    # Get all trainings
    trainings = Training.objects.select_related('team').order_by('day_of_week', 'time')
    
    # Determine today's day of week (1=Monday, 7=Sunday)
    from django.utils import timezone
    try:
        current_day = timezone.localdate().isoweekday()
    except Exception:
        import datetime
        current_day = datetime.date.today().isoweekday()
    
    # Organize trainings by day of week (1=Monday, 7=Sunday)
    days_of_week = {
        1: {'number': 1, 'name': 'Pazartesi', 'trainings': []},
        2: {'number': 2, 'name': 'Salı', 'trainings': []},
        3: {'number': 3, 'name': 'Çarşamba', 'trainings': []},
        4: {'number': 4, 'name': 'Perşembe', 'trainings': []},
        5: {'number': 5, 'name': 'Cuma', 'trainings': []},
        6: {'number': 6, 'name': 'Cumartesi', 'trainings': []},
        7: {'number': 7, 'name': 'Pazar', 'trainings': []},
    }
    
    # Populate trainings by day
    for training in trainings:
        days_of_week[training.day_of_week]['trainings'].append(training)
    
    # Mark today and compute afternoon separators
    for i in range(1, 8):
        days_of_week[i]['is_today'] = (i == current_day)
        # ensure trainings sorted by time
        days_of_week[i]['trainings'].sort(key=lambda t: t.time)
        seen_pm = False
        for t in days_of_week[i]['trainings']:
            setattr(t, 'show_pm_separator', False)
            if not seen_pm and t.time >= dt_time(13, 0):
                setattr(t, 'show_pm_separator', True)
                seen_pm = True
    
    # Convert to list for easier template iteration
    weekly_schedule = [days_of_week[i] for i in range(1, 8)]
    
    # Get summary statistics
    total_trainings = trainings.count()
    locations = set(t.location for t in trainings)

    # Training stats by team: count and total duration (minutes) if end_time available
    import datetime as _dt
    training_stats_by_team = {}
    for t in trainings:
        team_name = t.team.name
        if team_name not in training_stats_by_team:
            training_stats_by_team[team_name] = {'name': team_name, 'count': 0, 'minutes': 0}
        training_stats_by_team[team_name]['count'] += 1
        if t.end_time:
            start_dt = _dt.datetime.combine(_dt.date.today(), t.time)
            end_dt = _dt.datetime.combine(_dt.date.today(), t.end_time)
            if end_dt > start_dt:
                delta_minutes = int((end_dt - start_dt).total_seconds() // 60)
                training_stats_by_team[team_name]['minutes'] += delta_minutes

    training_stats_by_team = sorted(training_stats_by_team.values(), key=lambda x: x['name'])

    # Compute upcoming trainings (next occurrences in the weekly cycle)
    import datetime
    now = timezone.localtime()
    today_iso = now.isoweekday()
    upcoming = []
    for t in trainings:
        t_day = t.day_of_week
        days_ahead = (t_day - today_iso) % 7
        # If same day but already passed, push to next week
        if days_ahead == 0 and t.time <= now.time():
            days_ahead = 7
        next_date = timezone.localdate() + datetime.timedelta(days=days_ahead)
        next_dt = datetime.datetime.combine(next_date, t.time)
        upcoming.append((next_dt, t))
    upcoming.sort(key=lambda x: x[0])
    upcoming_trainings = []
    for next_dt, t in upcoming[:3]:
        upcoming_trainings.append({
            'training': t,
            'day_name': days_of_week[t.day_of_week]['name'],
            'next_datetime': next_dt,
        })
    
    context = {
        'weekly_schedule': weekly_schedule,
        'days_of_week': days_of_week,
        'total_trainings': total_trainings,
        'training_stats_by_team': training_stats_by_team,
        'locations': locations,
        'upcoming_trainings': upcoming_trainings,
        'title': 'Haftalık Antrenman Programı'
    }
    return render(request, 'team/training_weekly.html', context)


@login_required
@staff_member_required
def training_edit_inline(request, pk):
    """
    Inline edit view for training using HTMX
    """
    training = get_object_or_404(Training, pk=pk)
    
    if request.method == 'POST':
        form = TrainingForm(request.POST, instance=training)
        if form.is_valid():
            training = form.save()
            # Return the updated training row/card
            context = {
                'training': training,
                'day_name': dict(Training.DAYS_OF_WEEK)[training.day_of_week]
            }
            # Check if request is from card view or table view
            if request.headers.get('HX-Target', '').startswith('training-card-'):
                return render(request, 'team/partials/training_card.html', context)
            else:
                return render(request, 'team/partials/training_row.html', context)
        else:
            # Return the form with errors
            context = {
                'training': training,
                'form': form
            }
            if request.headers.get('HX-Target', '').startswith('training-card-'):
                return render(request, 'team/partials/training_card_edit.html', context, status=400)
            else:
                return render(request, 'team/partials/training_edit_form.html', context, status=400)
    else:
        form = TrainingForm(instance=training)
        context = {
            'training': training,
            'form': form
        }
        # Check if request is from card view or table view
        if request.headers.get('HX-Target', '').startswith('training-card-'):
            return render(request, 'team/partials/training_card_edit.html', context)
        else:
            return render(request, 'team/partials/training_edit_form.html', context)


@login_required
@staff_member_required
def training_view_inline(request, pk):
    """
    View to display a single training (for HTMX)
    """
    training = get_object_or_404(Training, pk=pk)
    context = {
        'training': training,
        'day_name': dict(Training.DAYS_OF_WEEK)[training.day_of_week]
    }
    # Check if request is from card view or table view
    if request.headers.get('HX-Target', '').startswith('training-card-'):
        return render(request, 'team/partials/training_card.html', context)
    else:
        return render(request, 'team/partials/training_row.html', context)


@login_required
@staff_member_required
def training_delete_inline(request, pk):
    """
    Delete training and update DOM via HTMX
    """
    training = get_object_or_404(Training, pk=pk)
    
    if request.method == 'POST':
        training.delete()
        # Return empty response - HTMX will remove the element
        return render(request, 'team/partials/empty.html')
    
    context = {
        'training': training
    }
    return render(request, 'team/partials/training_delete_confirm.html', context)

@login_required
@staff_member_required
def training_create_inline(request):
    """
    HTMX view for creating new training inline
    """
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        if form.is_valid():
            training = form.save()
            # Determine if we're in card or table view based on HX-Target
            hx_target = request.headers.get('HX-Target', '')
            if 'card' in hx_target.lower():
                return render(request, 'team/partials/training_card.html', {'training': training})
            else:
                return render(request, 'team/partials/training_row.html', {
                    'training': training,
                    'day_name': dict(Training.DAYS_OF_WEEK)[training.day_of_week]
                })
        else:
            # Return form with errors
            hx_target = request.headers.get('HX-Target', '')
            if 'card' in hx_target.lower():
                return render(request, 'team/partials/training_card_create.html', {'form': form})
            else:
                return render(request, 'team/partials/training_create_form.html', {'form': form})
    
    # GET request - show empty form
    form = TrainingForm()
    hx_target = request.headers.get('HX-Target', '')
    if 'card' in hx_target.lower():
        return render(request, 'team/partials/training_card_create.html', {'form': form})
    else:
        return render(request, 'team/partials/training_create_form.html', {'form': form})


@login_required
def user_dashboard(request):
    """
    Dashboard for users showing their info, team memberships, and unanswered questionnaires
    """
    user = request.user
    
    # Get all team members for this user
    user_team_members = TeamMember.objects.filter(user=user, is_active=True)
   
    # Get team IDs for the user's memberships
    team_ids = list(user_team_members.values_list('team_id', flat=True))
    

    # Get today's date for filtering
    today = date.today()
    
    # Get all active questionnaires for user's teams or global questionnaires (teams empty)
    # Filter by date range if begin_date or end_date is set
    questionnaires = Questionnaire.objects.filter(
        (models.Q(teams__id__in=team_ids) | models.Q(teams__isnull=True)) &
        (models.Q(begin_date__isnull=True) | models.Q(begin_date__lte=today)) &
        (models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)),
        is_active=True
    ).prefetch_related('teams').select_related('created_by').distinct().order_by('-created_at')
    
    # Get all responses by this user's team members
    member_ids = list(user_team_members.values_list('id', flat=True))
    responses = QuestionnaireResponse.objects.filter(
        member_id__in=member_ids
    ).values_list('questionnaire_id', 'member_id')
    
    # Create a set of (questionnaire_id, member_id) tuples for responded questionnaires
    responded_set = set(responses)
    
    # Build unanswered questionnaires per team member
    unanswered_by_member = []
    for member in user_team_members:
        member_questionnaires = []
        for questionnaire in questionnaires:
            # Check if questionnaire is for this member's team or is global
            questionnaire_team_ids = [t.id for t in questionnaire.teams.all()]
            if not questionnaire_team_ids or member.team_id in questionnaire_team_ids:
                # Check if not responded yet
                if (questionnaire.id, member.id) not in responded_set:
                    member_questionnaires.append(questionnaire)
        
        if member_questionnaires:
            unanswered_by_member.append({
                'member': member,
                'questionnaires': member_questionnaires
            })
    
    context = {
        'user': user,
        'user_team_members': user_team_members,
        'unanswered_by_member': unanswered_by_member,
        'title': 'Anasayfa'
    }
    return render(request, 'team/user_dashboard.html', context)