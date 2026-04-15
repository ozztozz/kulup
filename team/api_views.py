from datetime import date, datetime

from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .api_serializers import (
    ActiveQuestionnaireForMemberSerializer,
    PaymentSerializer,
    QuestionnaireResponseCreateSerializer,
    TeamMemberSerializer,
    TeamSerializer,
    TrainingSerializer,
)
from .models import Payment, Questionnaire, QuestionnaireResponse, Team, TeamMember, Training


class TeamListAPIView(generics.ListAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Team.objects.all().order_by("name")
        if user.is_staff:
            return queryset
        return queryset.filter(members__user=user, members__is_active=True).distinct()


class TeamMembersAPIView(generics.ListAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        team_id = self.kwargs["team_id"]
        queryset = TeamMember.objects.filter(team_id=team_id).select_related("team", "user")
        if user.is_staff:
            return queryset.order_by("name", "surname")
        return queryset.filter(user=user, is_active=True).order_by("name", "surname")


class TrainingListAPIView(generics.ListAPIView):
    serializer_class = TrainingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Training.objects.select_related("team", "trainer").order_by("day_of_week", "time")

        team_id = self.request.query_params.get("team")
        if team_id:
            queryset = queryset.filter(team_id=team_id)

        if user.is_staff:
            return queryset
        return queryset.filter(team__members__user=user, team__members__is_active=True).distinct()


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Payment.objects.select_related("member", "member__team", "member__user").order_by("-month", "member_id")
        month_param = self.request.query_params.get("month")
        if month_param:
            try:
                month_date = datetime.strptime(month_param, "%Y-%m-%d").date()
                queryset = queryset.filter(month=month_date)
            except ValueError:
                pass

        if user.is_staff:
            return queryset
        return queryset.filter(member__user=user, member__is_active=True)


class ActiveQuestionnaireListAPIView(generics.ListAPIView):
    serializer_class = ActiveQuestionnaireForMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Questionnaire.objects.none()

    def list(self, request, *args, **kwargs):
        user = request.user
        today = date.today()

        questionnaires = Questionnaire.objects.filter(
            (Q(teams__isnull=True) | Q(teams__members__is_active=True))
            & (Q(begin_date__isnull=True) | Q(begin_date__lte=today))
            & (Q(end_date__isnull=True) | Q(end_date__gte=today)),
            is_active=True,
        ).prefetch_related("teams").distinct().order_by("-created_at")

        if user.is_staff:
            members = TeamMember.objects.filter(is_active=True).select_related("team", "user").order_by("team__name", "name", "surname")
        else:
            members = TeamMember.objects.filter(user=user, is_active=True).select_related("team", "user").order_by("team__name", "name", "surname")

        responses = QuestionnaireResponse.objects.filter(
            member__in=members,
            questionnaire__in=questionnaires,
        ).values_list("questionnaire_id", "member_id")
        responded_pairs = set(responses)

        rows = []
        for member in members:
            for questionnaire in questionnaires:
                team_ids = list(questionnaire.teams.values_list("id", flat=True))
                if team_ids and member.team_id not in team_ids:
                    continue
                rows.append(
                    {
                        "member": member,
                        "questionnaire": questionnaire,
                        "has_responded": (questionnaire.id, member.id) in responded_pairs,
                    }
                )

        serializer = self.get_serializer(rows, many=True)
        return Response(serializer.data)


class QuestionnaireResponseCreateAPIView(generics.CreateAPIView):
    serializer_class = QuestionnaireResponseCreateSerializer
    permission_classes = [IsAuthenticated]
