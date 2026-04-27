from django.contrib import admin

# Register your models here.
from.models import StartListEntry

@admin.register(StartListEntry)
class StartListEntryAdmin(admin.ModelAdmin):
    list_display = ("name_raw", "birth_year", "gender", "stroke", "distance", "serie", "entry_time_sec", "time_sec")
    list_filter = ("gender", "stroke", "distance", "birth_year")
    search_fields = ("name_raw", "club_raw")