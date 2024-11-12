from django.contrib import admin
from .models import User, Attendance
from django.db.models import Count
from django.utils.timezone import localtime

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'month_days_worked', 'date', 'entry_time', 'exit_time', 'remarks', 'hours_worked')
    list_filter = ('user', 'date')  
    search_fields = ['user__username']

    def month_days_worked(self, obj):
        month = obj.date.month
        year = obj.date.year
        attended_days = Attendance.objects.filter(user=obj.user, date__month=month, date__year=year).distinct('date').count()

        return attended_days

    month_days_worked.admin_order_field = 'date'  
    month_days_worked.short_description = 'Days Worked in Month'

admin.site.register(User)
admin.site.register(Attendance, AttendanceAdmin)
