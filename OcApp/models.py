from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserInfo(models.Model):
    USER_ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('donor', 'Donor'),
        ('recipient', 'Recipient'),
        ('facility', 'Facility'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    userRole = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default='not specified')

    def __str__(self):
        return f"{self.fullname} ({self.userRole})"
    
class Hospital(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=15)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="doctors")
    specialization = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"
    
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="staff")

    def __str__(self):
        return f"{self.user.get_full_name()} at {self.hospital.name}"

class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    blood_type = models.CharField(max_length=5)
    organs = models.TextField()  
    medical_history = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    registered_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Recipient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    fullname = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    blood_type = models.CharField(max_length=5)
    required_organ = models.CharField(max_length=50)
    urgency = models.CharField(max_length=50)
    disease = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default="Waiting") # Waiting, Matched, Transplanted
    requested_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.organ_needed}"

class Organ(models.Model):
    ORGAN_TYPES = [
        ('Heart', 'Heart'),
        ('Lungs', 'Lungs'),
        ('Liver', 'Liver'),
        ('Kidneys', 'Kidneys'),
        ('Pancreas', 'Pancreas'),
        ('Corneas', 'Corneas'),
    ]
    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-')
    ]
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    organ_type = models.CharField(choices=ORGAN_TYPES, max_length=50)
    blood_type = models.CharField(choices=BLOOD_TYPES, max_length=3,default='---')
    medical_history = models.TextField()
    status = models.CharField(max_length=50, default='Available')  # Available, Pending, Allocated, Transplanted
    added_date = models.DateTimeField(auto_now_add=True)
    transplanted_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.organ_type} - {self.status}"
    
class OrganMatch(models.Model):
    organ = models.ForeignKey(Organ, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    hospital = models.ForeignKey('Hospital', on_delete=models.SET_NULL, null=True)
    doctor = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, default="Pending")  # Pending, Approved, Rejected
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="approvals")
    reviewed_at = models.DateTimeField(auto_now=True)
    operation_schedule_date = models.DateTimeField(blank=True, null=True)

class Notification(models.Model):
    type = models.CharField(max_length=50,default="")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_notifications")
    organ_match = models.ForeignKey(OrganMatch, on_delete=models.CASCADE, related_name="organ_notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    reply_message = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    operation_schedule_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Notification from {self.sender.username} to {self.receiver.username}"

class Review(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    review_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.get_gender_display()}"