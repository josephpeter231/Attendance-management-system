from django.db import models
from datetime import datetime
import pytz
from datetime import date

# Use IST time zone
IST = pytz.timezone('Asia/Kolkata')

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)  
    last_login = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.username
    
class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('leave', 'Leave'),
        ('permission', 'Permission')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    request_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    date = models.DateField(default=date.today)
    hours = models.PositiveIntegerField(null=True, blank=True)  # Only for permission type
    reason = models.TextField(blank=True, null=True)
    approved = models.BooleanField(default=False)
    hours_requested = models.PositiveIntegerField(null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} - {self.request_type} - {self.date}"

class Attendance(models.Model):
    user = models.ForeignKey(User, related_name='attendances', on_delete=models.CASCADE)
    date = models.DateField(default=datetime.today)
    entry_time = models.TimeField(null=True, blank=True)
    exit_time = models.TimeField(null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    hours_worked = models.FloatField(null=True, blank=True)  
    def __str__(self):
        return f"{self.user.username} - {self.date}"

    def calculate_hours(self):
        """Method to calculate worked hours between entry and exit time in IST."""
        if self.entry_time and self.exit_time:
            entry = datetime.combine(self.date, self.entry_time)
            exit = datetime.combine(self.date, self.exit_time)

            
            entry = IST.localize(entry)
            exit = IST.localize(exit)

          
            delta = exit - entry

            
            self.hours_worked = round(delta.seconds / 3600, 2)

    def save(self, *args, **kwargs):
        self.calculate_hours()
        super().save(*args, **kwargs)
