from django.db import models
from django.core.validators import RegexValidator

philippine_mobile_regex = RegexValidator(
    regex=r'^09\d{9}$',
    message="Enter a valid Philippine mobile number (e.g. 09123456789)."
)

class Caller(models.Model):
    caller_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[philippine_mobile_regex]
    )
    email = models.EmailField(unique=True, blank=True, null=True)
    password = models.CharField(max_length=128)  # if you’ll allow login
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"
