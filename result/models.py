from django.db import models


class StartListEntry(models.Model):
        GENDER_MALE = "M"
        GENDER_FEMALE = "F"
        GENDER_CHOICES = (
                (GENDER_MALE, "Erkekler"),
                (GENDER_FEMALE, "Kadınlar"),
        )
        event_url = models.URLField(max_length=2048, null=True, blank=True)
        event_title = models.CharField(max_length=255,null=True, blank=True)
        event_location = models.CharField(max_length=255,null=True, blank=True)
        event_date = models.CharField(null=True, blank=True)
        name_raw = models.CharField(max_length=255)
        birth_year = models.PositiveSmallIntegerField(null=True, blank=True)
        gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
        stroke = models.CharField(max_length=64)
        distance = models.PositiveSmallIntegerField()
        race_number = models.PositiveSmallIntegerField(max_length=16, blank=True, default=0)
        serie = models.PositiveSmallIntegerField(max_length=16, blank=True, default=0)
        series_total = models.PositiveSmallIntegerField(max_length=16, blank=True, default=0)
        start_line = models.PositiveSmallIntegerField(max_length=16, blank=True, default=0)
        club_raw = models.CharField(max_length=255, blank=True, default="")
        entry_time_sec = models.FloatField(null=True, blank=True)
        entry_time_txt = models.CharField(max_length=32, blank=True, default="")
        time_sec = models.FloatField(null=True, blank=True)
        time_txt = models.CharField(max_length=32, blank=True, default="")
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
                ordering = ["stroke", "distance", "entry_time_sec", "name_raw"]
                indexes = [
                        models.Index(fields=["gender", "stroke", "distance"]),
                        models.Index(fields=["birth_year"]),
                ]

        def __str__(self) -> str:
                return f"{self.name_raw} - {self.distance}m {self.stroke}"