from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login,logout , authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import make_aware
from .models import UserInfo, Donor, Recipient ,Organ, OrganAllocation, Notification
import json, datetime

def index(request):
    return render(request,'index.html')

def register(request):
    if request.method == 'POST':
        
        fullname = request.POST['name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        user_role = request.POST['role']

        user = User.objects.create_user(username=username, email=email, password=password)

        UserInfo.objects.create(user=user, fullname=fullname, email=email, userRole=user_role)

        messages.success(request, 'Your account has been created successfully!')
        return redirect('login')
    return render(request,'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            if user.is_superuser:
                return redirect('admin_dash')
            if user.userinfo.userRole =="doctor":
                return redirect('doctor_dash')
            if user.userinfo.userRole =="donor":
                return redirect('donor_dash')
            if user.userinfo.userRole =="recipient":
                return redirect('recipient_dash')
            if user.userinfo.userRole =="facility":
                return redirect('facility_dash')
            
        else:
            messages.error(request, 'Invalid username or password')
    return render(request,'login.html')

def log_out(request):
    logout(request)
    return redirect('login')

def admin_dash(request):
    return render(request,'admin_dash.html')

def doctor_dash(request):
    return render(request,'doctor_dash.html')

def donor_dash(request):
    return render(request,'donor_dash.html')

def recipient_dash(request):
    return render(request,'recipient_dash.html')

def facility_dash(request):
    return render(request,'facility_dash.html')

def manage_users(request):
    users = UserInfo.objects.all()
    return render(request,'users.html',{'users':users})

def donor_console(request):
    return render(request,'donor_console.html')

@login_required
def save_donor(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user 
            
            # Check if donor profile already exists for the user
            if Donor.objects.filter(user=user).exists():
                return JsonResponse({"error": "You have already registered as a donor!"}, status=400)

            donor = Donor.objects.create(
                user=user,
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                blood_type=data["bloodType"],
                organs=", ".join(data["organs"])
            )

            return JsonResponse({"message": "Donor saved successfully!"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def organ_request(request):
    return render(request,'organ_request.html')

def save_organ_request(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            organ_request = Recipient(
                user=request.user,  # Assuming recipient is logged in
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone'),
                blood_type=data.get('bloodType'),
                organ_needed=data.get('organNeeded'),
                urgency=data.get('urgency'),
                disease=data.get('disease')
            )
            organ_request.save()
            return JsonResponse({'message': 'Organ request submitted successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def organ_inventory(request):
    if request.method == 'POST':
        organ_type = request.POST['organ_type']
        status = request.POST['status']
        donor_id = request.POST['donor']
        recipient_id = request.POST['recipient']
    
        donor = Donor.objects.get(id=donor_id)
        if recipient_id != "":
            recipient = Recipient.objects.get(id=recipient_id)
        else:
            recipient =None

        # Create or update the organ in the inventory
        Organ.objects.create(
            organ_type=organ_type,
            status=status,
            donor=donor,
            recipient=recipient
        )

        return redirect('organ_inventory')

    # Fetch all donors and facilities for dropdown options
    donors = Donor.objects.all()
    recipients = Recipient.objects.all()

    # Fetch all organs in the inventory
    organs = Organ.objects.all()

    return render(request, 'organ_inventory.html', {'donors': donors, 'recipients': recipients, 'organs': organs})

def organ_matching(request):
    if request.method == "POST":
        recipient_blood_type = request.POST.get('recipient_blood_type')
        organ_type = request.POST.get('organ_type')

        matching_organs = Organ.objects.filter(
            blood_type=recipient_blood_type,
            organ_type=organ_type,
        )

        matching_results = []
        for organ in matching_organs:
            matching_results.append({
                'id': organ.id,  # Send organ ID for request creation
                'donor': organ.donor.name,
                'organ_type': organ.organ_type,
                'blood_type': organ.blood_type,
                'status': 'Yes' if organ.status else 'No',
            })

        return JsonResponse({'matching_organs': matching_results})

    return render(request, 'organ_matching.html')

def create_organ_request(request):
    if request.method == "POST":
        data = json.loads(request.body)
        organ_id = data.get('organ_id')
        recipient_name = data.get("recipient_name")
        print(recipient_name)
        if not organ_id:
            return JsonResponse({'success': False, 'message': 'Organ ID is required'})

        try:
            organ = Organ.objects.get(id=organ_id)
            recipient = Recipient.objects.get(name = recipient_name) 

            allocation = OrganAllocation.objects.create(
                organ=organ,
                recipient=recipient,
                reviewed_by=request.user,  # Assuming an admin will approve later
                status="Pending",
            )

            return JsonResponse({'success': True, 'message': 'Organ request created successfully!'})

        except Organ.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Organ not found'})
        except Recipient.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Recipient not found'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def organ_approval(request):
    return render(request, 'organ_approval.html')

def get_allocations(request):
    """New API to fetch allocation data for the table"""
    allocations = OrganAllocation.objects.all()
    data = [
        {
            "id": alloc.id,
            "recipient_name": alloc.recipient.name,  # Update based on your model field
            "organ_type": alloc.organ.organ_type,
            "blood_type": alloc.recipient.blood_type,
            "status": alloc.status
        }
        for alloc in allocations
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def approve_organ_allocation(request, allocation_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            allocation = get_object_or_404(OrganAllocation, id=allocation_id)

            if data.get("action") == "approve":
                allocation.status = "Approved"
                allocation.organ.status = "Allocated"
                allocation.recipient.status = "Matched"
                
                Notification.objects.create(
                    user=allocation.organ.donor.user,
                    sender=allocation.reviewed_by,  
                    message="Organ allotment approved. Please confirm.",
                    donor_confirmed=False,  
                )
                Notification.objects.create(
                    user=allocation.recipient.user,
                    sender=allocation.reviewed_by,  
                    message="Organ allotment approved. Please confirm.",
                    donor_confirmed=False,  
                )
            elif data.get("action") == "reject":
                allocation.status = "Rejected"
                allocation.recipient.status = "Waiting"

            allocation.save()
            allocation.organ.save()
            allocation.recipient.save()

            return JsonResponse({"message": f"Organ allocation {allocation.status} successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def notification(request):
    notifications = Notification.objects.filter(user=request.user, status='unread')
    return render(request, 'notification.html', {'notifications': notifications})

def confirm_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    
    if notification.user == request.user:
        if 'donor' in request.POST:
            notification.donor_confirmed = True
        elif 'recipient' in request.POST:
            notification.recipient_confirmed = True

        notification.save()

        # Redirect to the dashboard after confirmation
        return redirect('notification')
    return redirect('error')

def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    
    notification.status = 'read'
    notification.save()

    return redirect('notification')

def facility_schedule(request):
    notifications = Notification.objects.all()
    return render(request, 'facility_schedule.html',{'notifications':notifications})

@login_required
def schedule_operation(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    # Only allow facility users to schedule
    if request.user.userinfo.userRole =="facility":  
        if request.method == "POST":
            schedule_time_str = request.POST.get("schedule_time")
            schedule_time = make_aware(datetime.datetime.strptime(schedule_time_str, "%Y-%m-%dT%H:%M"))

            new_notification = Notification(
                user=notification.user,  
                sender=request.user,  
                message=f"Your operation has been scheduled for {schedule_time}",
                status="unread",  
                scheduled_time=schedule_time
            )

            new_notification.save() 
            return redirect("facility_schedule")

    return redirect("error_page")