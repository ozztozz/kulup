from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .api_serializers import StartListImportRequestSerializer, ResultImportRequestSerializer
from .models import StartListEntry


def _event_filters(queryset, request):
    event_title = request.query_params.get("event_title")
    event_location = request.query_params.get("event_location")
    event_date = request.query_params.get("event_date")

    if event_title:
        queryset = queryset.filter(event_title=event_title)
    if event_location:
        queryset = queryset.filter(event_location=event_location)
    if event_date:
        queryset = queryset.filter(event_date=event_date)
    return queryset


def _club_filter(queryset, request):
    queryset = _event_filters(queryset, request)
    club_raw = request.query_params.get("club_raw")
    if club_raw:
        queryset = queryset.filter(club_raw=club_raw)
    return queryset


def _item_filter(queryset, request):
    queryset = _club_filter(queryset, request)
    print("Filtering items with query params:", request.query_params)
    gender = request.query_params.get("gender")
    stroke = request.query_params.get("stroke")
    distance = request.query_params.get("distance")

    if gender:
        queryset = queryset.filter(gender=gender)
    if stroke:
        queryset = queryset.filter(stroke=stroke)
    if distance:
        queryset = queryset.filter(distance=distance)
    return queryset


class StartListEventListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = (
            StartListEntry.objects.exclude(event_title__isnull=True)
            .exclude(event_title="")
            .values("event_title", "event_location", "event_date")
            .distinct()
            .order_by("event_title", "event_location", "event_date")
        )
        return Response(list(queryset))


class StartListClubListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = _event_filters(StartListEntry.objects.all(), request)
        queryset = (
            queryset.exclude(club_raw__isnull=True)
            .exclude(club_raw="")
            .values("club_raw")
            .distinct()
            .order_by("club_raw")
        )
        return Response(list(queryset))


class StartListItemListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = _club_filter(StartListEntry.objects.all(), request)
        queryset = (
            queryset.exclude(gender__isnull=True)
            .exclude(gender="")
            .exclude(stroke__isnull=True)
            .exclude(stroke="")
            .values("race_number","gender", "stroke", "distance")
            .distinct()
            .order_by("race_number","gender", "stroke", "distance")
        )
        for entry in queryset:
            entry["cinsiyet"] ="Erkekler" if entry["gender"] == "M" else "Kadınlar"    
        return Response(list(queryset))


class StartListEntryListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = _item_filter(StartListEntry.objects.all(), request)
        queryset = queryset.values(
            "name_raw",
            "serie",
            "start_line",
            "entry_time_txt",
            "time_txt",
            "race_number",
        ).distinct().order_by("serie","start_line","name_raw", )
        return Response(list(queryset))



class StartListImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = StartListImportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        parsed_entries = serializer.validated_data.get("parsed_entries")
        replace_existing = serializer.validated_data["replace_existing"]




        if not parsed_entries:
            return Response(
                {
           
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
        print("Parsed entries to import:", len(parsed_entries))
        for entry in parsed_entries:

            objects_to_create.append(
                StartListEntry(
                    event_url=entry.get("event_url"),
                    event_title=str(entry.get("event_title", "")).strip(),
                    event_location=str(entry.get("event_location", "")).strip(),
                    event_date=str(entry.get("event_date", "")).strip(),
                    name_raw=str(entry.get("name_raw", "")).strip(),
                    birth_year=entry.get("birth_year"),
                    gender=entry.get("gender"),
                    stroke=str(entry.get("stroke", "")).strip(),
                    distance=entry.get("distance"),
                    race_number=str(entry.get("race_number", "")).strip(),
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

                "parsed_count": len(parsed_entries),
                "created_count": len(created),
                "skipped_count": skipped_count,
                "replace_existing": replace_existing,
            },
            status=status.HTTP_201_CREATED,
        )


class LastResultListAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        requested_event_url = request.POST.get("event_url")
        print("Received event_url:", requested_event_url)
        # 1. Get the latest entry dictionary or None
        latest_entry = StartListEntry.objects.filter(
            event_url=requested_event_url,
            time_txt__isnull=False
        ).exclude(
            time_txt=""
        ).order_by("-race_number").values("race_number").first()

        # 2. Handle the fallback and response
        if not latest_entry:
            # Return the same structure as a successful query
            latest_entry = [{"race_number": 0}]
        else:
            latest_entry = list(latest_entry)
        
        # Since latest_entry is already a dict, we just return it
        return Response(latest_entry, status=status.HTTP_200_OK)


class ResultImportAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]


    def post(self, request):
        serializer = ResultImportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

   
        parsed_entries = serializer.validated_data.get("parsed_entries")
        replace_existing = serializer.validated_data["replace_existing"]
        found=0
        for result in parsed_entries:
            #print("Processing result:", result)

            result_time_sec = result.get("time_sec")
            result_name_raw = result.get("name_raw")
            result_time_txt = result.get("time_txt")
            result_birth_year = result.get("birth_year")
            result_event_url = result.get("event_url")
            result_race_number = result.get("race_number")
            result_club_raw = result.get("club_raw")

            start=StartListEntry.objects.filter(
                name_raw=result_name_raw,
                birth_year=result_birth_year,
                race_number=result_race_number,
                club_raw=result_club_raw,
                event_url=result_event_url,)
            found=found+1
            if start.exists():
                start_entry = start.first()
                start_entry.time_sec = result_time_sec
                start_entry.time_txt = result_time_txt
                start_entry.save()


            
    
        return Response(
                    {'message': f'{found} Result import completed.' },
                    status=status.HTTP_200_OK,
                        )