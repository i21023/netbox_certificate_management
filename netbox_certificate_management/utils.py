from datetime import datetime, timezone
from django.db.models.functions import ExtractDay, Now
from django.db.models import F
from . import models


def return_days_valid():
    return ExtractDay(F("not_valid_after") - Now())
