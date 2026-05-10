from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import StartListEntry

def startlist_page_old(request):
	return render(request, "result/startlist.html")


def startlist_page(request):
	events = (
		StartListEntry.objects.exclude(event_title__isnull=True)
		.exclude(event_title="")
		.values("event_title", "event_location", "event_date")
		.distinct()
		.order_by("event_date","event_title", "event_location",)
	)
	clubs=(
		StartListEntry.objects.exclude(club_raw__isnull=True)
		.exclude(club_raw="")
		.values("club_raw")
		.order_by("club_raw")
		.distinct()
	)
	
	print("Clubs:", len(clubs))
	return render(request, "result/startlist.html", {"events": events, "clubs": clubs})


def htmx_club_list(request):
	club_raw = request.GET.get("club_search")
	if club_raw:
		clubs = StartListEntry.objects.filter(club_raw__icontains=club_raw).values("club_raw").order_by("club_raw").distinct()
	else:
		clubs = StartListEntry.objects.values("club_raw").distinct()
	return render(request, "result/partials/htmx_club_list.html", {"clubs": clubs})

def htmx_swimmer_list(request):
	swimmer_name = request.GET.get("swimmer_search")
	if swimmer_name:
		swimmers = StartListEntry.objects.filter(name_raw__icontains=swimmer_name).values("name_raw").order_by("name_raw").distinct()
	else:
		swimmers = StartListEntry.objects.values("name_raw").distinct()
	return render(request, "result/partials/htmx_swimmer_list.html", {"swimmers": swimmers})

def htmx_result_list(request):
	club_raw = request.GET.get("club_search")
	swimmer_name = request.GET.get("swimmer_search")
	results = StartListEntry.objects.all().order_by('race_number', 'serie', 'start_line')
	if club_raw:
		results = results.filter(club_raw__icontains=club_raw)
	if swimmer_name:
		results = results.filter(name_raw__icontains=swimmer_name)
	return render(request, "result/partials/htmx_result_list.html", {"results": results})