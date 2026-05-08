from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import StartListEntry

@login_required
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