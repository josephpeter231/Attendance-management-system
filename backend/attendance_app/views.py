from django.contrib.auth.models import User as AuthUser
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Attendance, LeaveRequest
from .forms import LoginForm, AttendanceForm, LeaveRequestForm

def home(request):
    return render(request, 'home.html')
@login_required
def user_attendance_summary(request, user_id):
    user = get_object_or_404(User, id=user_id)
    year = 2024
    month = 11

    attendances = Attendance.objects.filter(
        user=user,
        date__year=year,
        date__month=month
    ).order_by('date')

    leave_requests = LeaveRequest.objects.filter(user=user, date__year=year, date__month=month)

    return render(request, 'user_attendance_summary.html', {
        'user': user,
        'attendances': attendances,
        'leave_requests': leave_requests,
        'year': year,
        'month': month
    })

# Login View
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                auth_user = AuthUser.objects.get(username=username)
                if auth_user.check_password(password):
                    login(request, auth_user)
                    # Check for `next` parameter in the GET request to redirect after login
                    next_url = request.GET.get('next')
                    return redirect(next_url or 'user_attendance_summary', user_id=auth_user.id)
            except AuthUser.DoesNotExist:
                pass  
            try:
                custom_user = User.objects.get(username=username)
                if custom_user.password == password:  
                    login(request, custom_user, backend='django.contrib.auth.backends.ModelBackend')
                    # Check for `next` parameter in the GET request to redirect after login
                    next_url = request.GET.get('next')
                    return redirect(next_url or 'user_attendance_summary', user_id=custom_user.id)
                else:
                    form.add_error(None, 'Invalid password for custom user')
            except User.DoesNotExist:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def add_attendance(request):
    if not request.user.is_staff: 
        return redirect('home') 
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.calculate_hours()  
            attendance.save()
            messages.success(request, "Attendance record added successfully.")
            return redirect('home')
    else:
        form = AttendanceForm()
    return render(request, 'add_attendance.html', {'form': form})
 
@login_required
def leave_request(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            
            monthly_permission_hours = LeaveRequest.objects.filter(
                user=request.user,
                date__month=leave_request.date.month,
                date__year=leave_request.date.year,
                status='approved'
            ).aggregate(sum('hours_requested'))['hours_requested__sum'] or 0

            if leave_request.hours_requested > 2:
                messages.error(request, "You can only request up to 2 hours of permission per day.")
            elif monthly_permission_hours + leave_request.hours_requested > 4:
                messages.error(request, "You have exceeded the maximum of 4 hours of permission for this month.")
            else:
                leave_request.status = 'pending'  
                leave_request.save()
                messages.success(request, "Your leave request has been submitted and is pending approval.")
                return redirect('user_attendance_summary', user_id=request.user.id)
    else:
        form = LeaveRequestForm()

    return render(request, 'leave_request.html', {'form': form})

@login_required
def approve_leave(request, leave_request_id):
    if not request.user.is_staff:
        return redirect('home')

    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
    if request.method == 'POST':
        leave_request.status = 'approved'
        leave_request.save()
        messages.success(request, f"Leave request for {leave_request.user.username} has been approved.")
        return redirect('user_attendance_summary', user_id=leave_request.user.id)

    return render(request, 'approve_leave.html', {'leave_request': leave_request})
