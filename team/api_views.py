from datetime import date, datetime

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .api_serializers import (
    ActiveQuestionnaireForMemberSerializer,
    PaymentCreateSerializer,
    PaymentSerializer,
    QuestionnaireSerializer,
    QuestionnaireResponseCreateSerializer,
    TeamCreateSerializer,
    TeamMemberSerializer,
    TeamMemberCreateSerializer,
    TeamSerializer,
    TrainingCreateSerializer,
    TrainingSerializer,
)
from .models import Payment, Questionnaire, QuestionnaireResponse, Team, TeamMember, Training


class TeamListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TeamCreateSerializer
        return TeamSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Team.objects.all().order_by("name")
        if user.is_staff:
            return queryset
        return queryset.filter(members__user=user, members__is_active=True).distinct()


class TeamMembersAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TeamMemberCreateSerializer
        return TeamMemberSerializer

    def get_queryset(self):
        user = self.request.user
        team_id = self.kwargs["team_id"]
        queryset = TeamMember.objects.filter(team_id=team_id).select_related("team", "user")
        if user.is_staff:
            return queryset.order_by("name", "surname")
        return queryset.filter(user=user, is_active=True).order_by("name", "surname")

    def perform_create(self, serializer):
        serializer.save(team_id=self.kwargs["team_id"])


class TrainingListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TrainingCreateSerializer
        return TrainingSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Training.objects.select_related("team", "trainer").order_by("day_of_week", "time")

        team_id = self.request.query_params.get("team")
        if team_id:
            queryset = queryset.filter(team_id=team_id)

        if user.is_staff:
            return queryset
        return queryset.filter(team__members__user=user, team__members__is_active=True).distinct()

    def perform_create(self, serializer):
        trainer = serializer.validated_data.get("trainer")
        if trainer is None:
            serializer.save(trainer=self.request.user)
            return
        serializer.save()


class PaymentListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PaymentCreateSerializer
        return PaymentSerializer

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


class QuestionnaireDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ActiveQuestionnaireForMemberSerializer
    permission_classes = [IsAuthenticated]
    queryset = Questionnaire.objects.prefetch_related("teams")

    def retrieve(self, request, *args, **kwargs):
        questionnaire = self.get_object()
        user = request.user

        member_param = request.query_params.get("member")
        member = None
        if member_param:
            member = get_object_or_404(
                TeamMember.objects.select_related("team", "user"),
                pk=member_param,
                is_active=True,
            )

            if not user.is_staff and member.user_id != user.id:
                raise ValidationError("You can only view your own member questionnaires.")

        if member is None and not user.is_staff:
            member = TeamMember.objects.filter(user=user, is_active=True).select_related("team", "user").first()

        if questionnaire.teams.exists():
            applicable_members = TeamMember.objects.filter(
                is_active=True,
                team__in=questionnaire.teams.all(),
            ).select_related("team", "user")
        else:
            applicable_members = TeamMember.objects.filter(is_active=True).select_related("team", "user")

        if user.is_staff:
            members = applicable_members.order_by("team__name", "name", "surname")
        else:
            members = applicable_members.filter(user=user).order_by("team__name", "name", "surname")

        responses = QuestionnaireResponse.objects.filter(
            questionnaire=questionnaire,
            member__in=members,
        ).select_related("member", "member__team", "member__user")

        response_map = {resp.member_id: resp for resp in responses}

        responded_rows = []
        not_responded_rows = []
        for m in members:
            response = response_map.get(m.id)
            row = {
                "member": TeamMemberSerializer(m, context={"request": request}).data,
                "has_responded": response is not None,
                "response_created_at": response.created_at.isoformat() if response else None,
            }
            if response:
                responded_rows.append(row)
            else:
                not_responded_rows.append(row)

        selected_response = None
        if member is not None:
            selected_response = response_map.get(member.id)

        questions_with_stats = []
        schema_questions = questionnaire.schema.get("questions", []) if isinstance(questionnaire.schema, dict) else []

        for question in schema_questions:
            if not isinstance(question, dict):
                continue

            question_data = {
                "id": question.get("id"),
                "label": question.get("label"),
                "type": question.get("type", "text"),
                "required": question.get("required", True),
                "help": question.get("help"),
            }

            raw_choices = question.get("choices") or []
            if isinstance(raw_choices, list) and raw_choices:
                choice_counts = {}
                choice_members = {}
                for choice in raw_choices:
                    if not isinstance(choice, dict):
                        continue
                    value = choice.get("value")
                    choice_counts[value] = 0
                    choice_members[value] = []

                for resp in responses:
                    answer = resp.answers.get(question.get("id"))
                    if answer is None:
                        continue

                    if question.get("type") == "multi" and isinstance(answer, list):
                        for ans_value in answer:
                            if ans_value in choice_counts:
                                choice_counts[ans_value] += 1
                                choice_members[ans_value].append(
                                    TeamMemberSerializer(resp.member, context={"request": request}).data
                                )
                    else:
                        if answer in choice_counts:
                            choice_counts[answer] += 1
                            choice_members[answer].append(
                                TeamMemberSerializer(resp.member, context={"request": request}).data
                            )

                choices = []
                for choice in raw_choices:
                    if not isinstance(choice, dict):
                        continue
                    value = choice.get("value")
                    choices.append(
                        {
                            "value": value,
                            "label": choice.get("label", value),
                            "count": choice_counts.get(value, 0),
                            "members": choice_members.get(value, []),
                        }
                    )
                question_data["choices"] = choices

            questions_with_stats.append(question_data)

        payload = {
            "questionnaire": QuestionnaireSerializer(questionnaire, context={"request": request}).data,
            "member": TeamMemberSerializer(member, context={"request": request}).data if member else None,
            "response": {
                "id": selected_response.id,
                "answers": selected_response.answers,
                "created_at": selected_response.created_at.isoformat(),
            }
            if selected_response
            else None,
            "responded_rows": responded_rows,
            "not_responded_rows": not_responded_rows,
            "questions_with_stats": questions_with_stats,
            "counts": {
                "total_members": members.count(),
                "responded": len(responded_rows),
                "not_responded": len(not_responded_rows),
            },
        }
        return Response(payload)


class QuestionnaireResponseCreateAPIView(generics.CreateAPIView):
    serializer_class = QuestionnaireResponseCreateSerializer
    permission_classes = [IsAuthenticated]
