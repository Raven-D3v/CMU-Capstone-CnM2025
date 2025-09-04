from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, check_password

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
    password = models.CharField(max_length=128)  # will store **hashed** password
    date_registered = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        """Hashes and stores the password safely."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Checks if the raw password matches the stored hash."""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"
