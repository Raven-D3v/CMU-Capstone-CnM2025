from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator
from django.conf import settings

# Validators
philippine_mobile_regex = RegexValidator(
    regex=r'^09\d{9}$',
    message="Enter a valid Philippine mobile number (e.g. 09123456789)."
)

police_id_regex = RegexValidator(
    regex=r'^PNP-\d{5}$',
    message="Enter a valid Police ID (e.g. PNP-12345)."
)

# Rank Choices
RANK_GROUPED_CHOICES = [
    ("Commissioned Officers", [
        ("Police General", "Police General"),
        ("Police Lieutenant General", "Police Lieutenant General"),
        ("Police Major General", "Police Major General"),
        ("Police Brigadier General", "Police Brigadier General"),
        ("Police Colonel", "Police Colonel"),
        ("Police Lieutenant Colonel", "Police Lieutenant Colonel"),
        ("Police Major", "Police Major"),
        ("Police Captain", "Police Captain"),
        ("Police Lieutenant", "Police Lieutenant"),
    ]),
    ("Non-Commissioned Officers", [
        ("Police Executive Master Sergeant", "Police Executive Master Sergeant"),
        ("Police Chief Master Sergeant", "Police Chief Master Sergeant"),
        ("Police Senior Master Sergeant", "Police Senior Master Sergeant"),
        ("Police Master Sergeant", "Police Master Sergeant"),
        ("Police Staff Sergeant", "Police Staff Sergeant"),
        ("Police Corporal", "Police Corporal"),
        ("Patrolman/Patrolwoman", "Patrolman/Patrolwoman"),
    ]),
]

# Custom Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, police_id, password=None, **extra_fields):
        if not police_id:
            raise ValueError('The Police ID must be set')
        user = self.model(police_id=police_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, police_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(police_id, password, **extra_fields)


# Custom User Model
class UserProfile(AbstractUser):
    username = None  # Remove default username

    police_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[police_id_regex],
        help_text="Enter your official Police ID (e.g. PNP-12345)"
    )
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(
        max_length=11,
        validators=[philippine_mobile_regex],
        help_text="Enter a valid Philippine mobile number (e.g. 09123456789)."
    )
    rank = models.CharField(
        max_length=40,
        choices=RANK_GROUPED_CHOICES,
        default='Patrolman/Patrolwoman',
        help_text="Select your official police rank."
    )

    # ✅ New Fields
    designation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Officer’s current designation/role (e.g. Investigator, Desk Officer, Patrol Unit)."
    )

    area_vicinity = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Assigned area or vicinity of responsibility (e.g. Quezon City, Barangay 123)."
    )

    officer_photo = models.ImageField(
        upload_to='officer_photos/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        help_text="Upload a profile picture of the officer."
    )

    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'police_id'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.rank} {self.last_name}, {self.first_name}"


# Deployment History Model linked via police_id
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('responded', 'Responded'),
    ('resolved', 'Resolved'),
    ('closed', 'Closed'),
]

class DeploymentHistory(models.Model):
    report = models.ForeignKey(
        'reports.EmergencyReport',  # assumes your EmergencyReport is in 'reports' app
        on_delete=models.CASCADE,
        to_field='report_id',
        db_column='report_id',
        related_name='deployments'
    )
    police = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        to_field='police_id',
        db_column='police_id',
        related_name='deployments',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    date_time_responded = models.DateTimeField(null=True, blank=True)
    date_time_resolved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Deployment for {self.report.report_id} - Officer: {self.police} - Status: {self.get_status_display()}"