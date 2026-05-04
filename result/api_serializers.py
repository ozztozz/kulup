from rest_framework import serializers


class ParsedStartListEntrySerializer(serializers.Serializer):
    event_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    event_title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    event_location = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    event_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    name_raw = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    birth_year = serializers.IntegerField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    stroke = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    distance = serializers.IntegerField(required=False, allow_null=True)
    race_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    serie = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    series_total = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    start_line = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    club_raw = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    entry_time_sec = serializers.FloatField(required=False, allow_null=True)
    entry_time_txt = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time_sec = serializers.FloatField(required=False, allow_null=True)
    time_txt = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class StartListImportRequestSerializer(serializers.Serializer):

    parsed_entries = ParsedStartListEntrySerializer(many=True, required=False)
    replace_existing = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
       
        parsed_entries = attrs.get("parsed_entries")

        if  not parsed_entries:
            raise serializers.ValidationError(
                "Provide either event_url or parsed_entries."
            )

        return attrs

class ParsedResultEntrySerializer(serializers.Serializer):
    event_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    name_raw = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    birth_year = serializers.IntegerField(required=False, allow_null=True)
    club_raw = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    entry_time_sec = serializers.FloatField(required=False, allow_null=True)
    entry_time_txt = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    time_sec = serializers.FloatField(required=False, allow_null=True)
    time_txt = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    race_number= serializers.CharField(required=False, allow_blank=True, allow_null=True)



class ResultImportRequestSerializer(serializers.Serializer):
    
    parsed_entries = ParsedResultEntrySerializer(many=True, required=False)
    replace_existing = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        
        parsed_entries = attrs.get("parsed_entries")

        if  not parsed_entries:
            raise serializers.ValidationError(
                "Provide either event_url or parsed_entries."
            )

        return attrs