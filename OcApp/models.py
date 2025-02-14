from django.db import models
from django.contrib.auth.models import User

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
    email = models.EmailField(unique=True)
    admin = models.OneToOneField(User, on_delete=models.CASCADE)  # Hospital Admin

    def __str__(self):
        return self.name

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
    status = models.CharField(max_length=20, default="Pending")  # Pending, Approved, Rejected
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="approvals")
    reviewed_at = models.DateTimeField(auto_now=True)

class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification from {self.sender.username} to {self.receiver.username}"
