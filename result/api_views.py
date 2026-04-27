from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_serializers import StartListImportRequestSerializer
from .models import StartListEntry



class StartListImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = StartListImportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_url = serializer.validated_data.get("event_url")
        parsed_entries = serializer.validated_data.get("parsed_entries")
        replace_existing = serializer.validated_data["replace_existing"]


        if not parsed_entries:
            return Response(
                {
                    "event_url": event_url,
                    "parsed_count": 0,
                    "created_count": 0,
                    "message": "No start list entries parsed from provided URL.",
                },
                status=status.HTTP_200_OK,
            )

        if replace_existing:
            StartListEntry.objects.all().delete()

        objects_to_create = []
        skipped_count = 0

        for entry in parsed_entries:
            gender = str(entry.get("gender", "")).strip().upper()
            if gender not in {"M", "F"}:
                skipped_count += 1
                continue

            distance = entry.get("distance")
            if distance is None:
                skipped_count += 1
                continue

            try:
                distance = int(distance)
            except (TypeError, ValueError):
                skipped_count += 1
                continue

            objects_to_create.append(
                StartListEntry(
                    event_title=str(entry.get("event_title", "")).strip(),
                    event_location=str(entry.get("event_location", "")).strip(),
                    event_date=str(entry.get("event_date", "")).strip(),
                    name_raw=str(entry.get("name_raw", "")).strip(),
                    birth_year=entry.get("birth_year"),
                    gender=gender,
                    stroke=str(entry.get("stroke", "")).strip(),
                    distance=distance,
                    serie=str(entry.get("serie", "")).strip(),
                    series_total=str(entry.get("series_total", "")).strip(),
                    start_line=str(entry.get("start_line", "")).strip(),
                    club_raw=str(entry.get("club_raw", "")).strip(),
                    entry_time_sec=entry.get("entry_time_sec"),
                    entry_time_txt=str(entry.get("entry_time_txt", "")).strip(),
                    time_sec=entry.get("time_sec"),
                    time_txt=str(entry.get("time_txt", "")).strip(),
                )
            )

        created = StartListEntry.objects.bulk_create(objects_to_create) if objects_to_create else []

        return Response(
            {
                "event_url": event_url,
                "parsed_count": len(parsed_entries),
                "created_count": len(created),
                "skipped_count": skipped_count,
                "replace_existing": replace_existing,
            },
            status=status.HTTP_201_CREATED,
        )
