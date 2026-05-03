from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def startlist_page(request):
	return render(request, "result/startlist.html")
