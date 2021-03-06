from django.conf import settings
from django.db import models

from aida.models.health import Health
from shared.utils import dt


class Sleep(Health):
    slept_at = models.DateTimeField(help_text="Enter the date and time you went to sleep, format: YYYY-MM-DD HH:MM")
    awoke_at = models.DateTimeField(help_text="Enter the date and time you woke up at, format: YYYY-MM-DD HH:MM")
    duration = models.PositiveIntegerField(default=0, help_text="Duration of sleep")

    class Meta:
        verbose_name_plural = "Sleep metrics"
        ordering = ["-slept_at", ]

    def __str__(self) -> str:
        return f"From {self.slept_at.date()} to {self.awoke_at.date()}"

    def save(self, *args, **kwargs):
        self.duration = int((self.awoke_at - self.slept_at).total_seconds())
        super().save(*args, **kwargs)

    def duration_formatted(self) -> str:
        total_minutes = self.duration / 60
        minutes = total_minutes % 60
        hours = (total_minutes - minutes) / 60
        return f"{hours:.0f} h {minutes:.0f} min"

    def awoke_at_table_format(self) -> str:
        return Sleep.datetime_table_format(self.awoke_at)

    def slept_at_table_format(self) -> str:
        return Sleep.datetime_table_format(self.slept_at)

    # region DataConvertableMixin

    @staticmethod
    def create(slept_at: str, awoke_at: str) -> "Sleep":
        """Creates a Sleep object, stores it in the database and returns the object.

        Args:
            slept_at (str): the date and time of falling asleep in the format YYYY-MM-DD HH:MM:SStz.
            awoke_at (str): the date and time of awakening in the format YYYY-MM-DD HH:MM:SStz.

        Returns:
            Sleep: the Sleep object that was created.
        """

        return Sleep.objects.create(slept_at=dt.parse_datetime(slept_at), awoke_at=dt.parse_datetime(awoke_at))

    @staticmethod
    def db_data_to_csv():
        header = ["slept_at", "awoke_at"]
        return header, Sleep.db_data_to_json()["data"]

    @staticmethod
    def db_data_to_json():
        sleeps = Sleep.find_all()
        content = {
            "category": "sleep",
            "timezone": settings.TIME_ZONE,
            "data": [],
        }
        for sleep in sleeps:
            content["data"].append({"slept_at": str(sleep.slept_at), "awoke_at": str(sleep.awoke_at)})
        return content

    # endregion DataConvertableMixin

    # region ViewUrlsMixin

    @property
    def detail_url(self) -> str:
        return "aida:sleep-detail"

    @property
    def update_url(self) -> str:
        return "aida:sleep-update"

    @property
    def delete_url(self) -> str:
        return "aida:sleep-delete"

    # endregion ViewUrlsMixin

    @classmethod
    def all_to_chart_data(cls) -> dict:
        queryset = cls.objects.all().order_by("awoke_at")

        dates = [sleep.date_table_format(sleep.awoke_at) for sleep in queryset]
        durations = [round(sleep.duration / 60 / 60, 1) for sleep in queryset]

        return {
            "labels": dates,
            "chart_data": durations,
            "chart_label": "Hours slept vs Date"
        }
