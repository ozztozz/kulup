from datetime import date

from rest_framework import serializers

from .models import Payment, Questionnaire, QuestionnaireResponse, Team, TeamMember, Training


class TeamSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "description",
            "logo_url",
            "founded_date",
            "created_at",
            "updated_at",
        ]

    def get_logo_url(self, obj):
        if not obj.logo:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.logo.url)
        return obj.logo.url


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "description",
            "logo",
            "founded_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeamMemberSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = [
            "id",
            "team",
            "name",
            "surname",
            "photo_url",
            "birthdate",
            "school",
            "joined_date",
            "is_active",
            "notes",
        ]

    def get_photo_url(self, obj):
        if not obj.photo:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.photo.url)
        return obj.photo.url


class TeamMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = [
            "id",
            "team",
            "user",
            "name",
            "surname",
            "photo",
            "birthdate",
            "school",
            "is_active",
            "notes",
            "joined_date",
        ]
        read_only_fields = ["id", "joined_date"]


class TrainingSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    trainer_name = serializers.SerializerMethodField()
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)

    class Meta:
        model = Training
        fields = [
            "id",
            "team",
            "day_of_week",
            "day_name",
            "time",
            "end_time",
            "location",
            "trainer",
            "trainer_name",
            "notes",
            "created_at",
            "updated_at",
        ]

    def get_trainer_name(self, obj):
        if not obj.trainer:
            return None
        return f"{obj.trainer.adi} {obj.trainer.soyadi}".strip()


class TrainingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = [
            "id",
            "team",
            "day_of_week",
            "time",
            "end_time",
            "location",
            "trainer",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PaymentSerializer(serializers.ModelSerializer):
    member = TeamMemberSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "member",
            "month",
            "amount",
            "is_paid",
            "paid_date",
            "created_at",
            "updated_at",
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "member",
            "month",
            "amount",
            "is_paid",
            "paid_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        is_paid = attrs.get("is_paid", False)
        paid_date = attrs.get("paid_date")

        if is_paid and not paid_date:
            raise serializers.ValidationError({"paid_date": "Paid date is required when payment is marked as paid."})

        if not is_paid and paid_date:
            raise serializers.ValidationError({"paid_date": "Paid date must be empty when payment is not paid."})

        return attrs


class QuestionnaireSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = Questionnaire
        fields = [
            "id",
            "title",
            "description",
            "schema",
            "teams",
            "is_active",
            "begin_date",
            "end_date",
            "created_at",
            "updated_at",
        ]


class ActiveQuestionnaireForMemberSerializer(serializers.Serializer):
    member = TeamMemberSerializer(read_only=True)
    questionnaire = QuestionnaireSerializer(read_only=True)
    has_responded = serializers.BooleanField()


class QuestionnaireResponseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionnaireResponse
        fields = ["id", "questionnaire", "member", "answers", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        request = self.context["request"]
        member = attrs["member"]
        questionnaire = attrs["questionnaire"]
        today = date.today()

        if not request.user.is_staff and member.user_id != request.user.id:
            raise serializers.ValidationError("You can only answer questionnaires for your own members.")

        if not member.is_active:
            raise serializers.ValidationError("Questionnaire response is not allowed for inactive members.")

        if not questionnaire.is_active:
            raise serializers.ValidationError("This questionnaire is not active.")

        if questionnaire.begin_date and questionnaire.begin_date > today:
            raise serializers.ValidationError("This questionnaire has not started yet.")

        if questionnaire.end_date and questionnaire.end_date < today:
            raise serializers.ValidationError("This questionnaire is expired.")

        if questionnaire.teams.exists() and not questionnaire.teams.filter(id=member.team_id).exists():
            raise serializers.ValidationError("This questionnaire is not assigned to the member's team.")

        exists = QuestionnaireResponse.objects.filter(
            questionnaire=questionnaire,
            member=member,
        ).exists()
        if exists:
            raise serializers.ValidationError("This member has already responded to the questionnaire.")

        return attrs

    def create(self, validated_data):
        validated_data["responder"] = self.context["request"].user
        return super().create(validated_data)


class QuestionnaireResponseSerializer(serializers.ModelSerializer):
    questionnaire = QuestionnaireSerializer(read_only=True)
    member = TeamMemberSerializer(read_only=True)

    class Meta:
        model = QuestionnaireResponse
        fields = ["id", "questionnaire", "member", "answers", "created_at"]
