from datetime import datetime, timezone
from django.db.models.functions import ExtractDay
from django.db.models import F

def return_days_valid():
    return ExtractDay(F('not_valid_after') - datetime.now(timezone.utc))