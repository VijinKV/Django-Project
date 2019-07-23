from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Stocks(models.Model):
    symbol = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (('symbol','user'),)
    
