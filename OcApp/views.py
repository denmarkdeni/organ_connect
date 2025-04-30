from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login,logout , authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import make_aware
from .models import UserInfo, Donor, Recipient ,Organ, OrganMatch, Notification, Staff, Hospital, Doctor, Review
import json, datetime
from .forms import ReplyForm, HospitalVerificationForm

def index(request):
    reviews = Review.objects.all().order_by('-timestamp')
    return render(request, 'index.html', {'reviews': reviews})

@csrf_exempt
def add_review(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        gender = data.get('gender')
        review_text = data.get('reviewText')
        
        if name and gender and review_text:
            Review.objects.create(
                name=name,
                gender=gender,
                review_text=review_text
            )
            return JsonResponse({'status': 'success', 'message': 'Review added successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def login_register(request):
    if request.method == 'POST':

        if request.POST['action']=="register":
            fullname = request.POST['name']
            email = request.POST['email']
            username = request.POST['username']
            password = request.POST['password']
            user_role = request.POST['role']

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('login_register')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('login_register')
            user = User.objects.create_user(username=username, email=email, password=password, last_name=fullname)

            UserInfo.objects.create(user=user, email=email, userRole=user_role)

            messages.success(request, 'Your account has been created successfully!')
            return redirect('login_register')
        
        if request.POST['action']=="login":
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Login at {0}'.format(datetime.datetime.now()))
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
                return redirect('login_register')
            else:
                messages.error(request, 'Invalid username or password')
            
    return render(request,'login_register.html')

def log_out(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('login_register')

def admin_dash(request):
    return render(request,'admin_dash.html')

def doctor_dash(request):
    notification_count = Notification.objects.filter(is_read=False, receiver=request.user).count()
    return render(request,'doctor_dash.html',{'notification_count':notification_count})

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
    user = User.objects.get(id=request.user.id)
    return render(request,'donor_console.html',{"user":user})

def remove_user(request, user_id):
    user = User.objects.get(id=user_id)
    name = user.username
    user.delete()
    messages.success(request,f" User {name} Deleted Successfully!")
    return redirect('manage_users')

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
                fullname=data["name"],
                email=data["email"],
                phone=data["phone"],
                age=data["age"],
                blood_type=data["bloodType"],
                medical_history=data["medical_history"],
                organs=", ".join(data["organs"])
            )

            return JsonResponse({"message": "Donor saved successfully!"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def organ_request(request):
    user = User.objects.get(id=request.user.id)
    return render(request,'organ_request.html',{"user":user})

def save_organ_request(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if Recipient.objects.filter(user=request.user).exists():
                return JsonResponse({'message': 'User Requested Already'})

            organ_request = Recipient(
                user=request.user,  # Assuming recipient is logged in
                fullname=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone'),
                age=data.get('age'),
                blood_type=data.get('bloodType'),
                required_organ=data.get('organNeeded'),
                urgency=data.get('urgency'),
                disease=data.get('disease')
            )
            organ_request.save()
            return JsonResponse({'message': 'Organ request submitted successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def donor_list(request):
    donors = Donor.objects.all()  # Fetch all registered donors
    return render(request, "donor_list.html", {"donors": donors})

def upload_organ(request):
    if request.method == "POST":
        donor_id = request.POST.get("donor_id")
        organ_name = request.POST.get("organ_name")
        status = request.POST.get("status")
        donor = Donor.objects.get(id=donor_id)

        if Organ.objects.filter(donor=donor, organ_type=organ_name).exists():
            return JsonResponse({"error": "Already Uploaded !"}, status=400)
        
        Organ.objects.create(donor=donor, organ_type=organ_name, status=status, blood_type=donor.blood_type, medical_history=donor.medical_history)

        return JsonResponse({"message": "Organ uploaded successfully"})

    return JsonResponse({"error": "Invalid request"}, status=400)

def organ_inventory(request):
    if request.method == 'POST':
        organ_type = request.POST['organ_type']
        status = request.POST['status']
        donor_id = request.POST['donor']
        donor = Donor.objects.get(id=donor_id)

        # Create or update the organ in the inventory
        Organ.objects.create(
            organ_type=organ_type,
            status=status,
            donor=donor,
            blood_type=donor.blood_type
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
            status='Available'
        )

        matching_results = []
        for organ in matching_organs:
            matching_results.append({
                'id': organ.id,  # Send organ ID for request creation
                'donor': organ.donor.fullname,
                'organ_type': organ.organ_type,
                'blood_type': organ.blood_type,
                'status': 'Yes' if organ.status else 'No',
            })

        return JsonResponse({'matching_organs': matching_results})

    recipients = Recipient.objects.all()
    return render(request, 'organ_matching.html',{"recipients":recipients})

def create_organ_request(request):
    if request.method == "POST":
        data = json.loads(request.body)
        organ_id = data.get('organ_id')
        recipient_name = data.get("recipient_name")
         
        if not organ_id:
            return JsonResponse({'success': False, 'message': 'Organ ID is required'})

        try:
            organ = Organ.objects.get(id=organ_id)
            recipient = Recipient.objects.get(fullname = recipient_name) 

            organ_match = OrganMatch.objects.create(
                organ=organ,
                recipient=recipient,
                reviewed_by=request.user,  # Assuming an admin will approve later
                status="Pending",
            )
            organ.status="Pending"
            organ.save()

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
    allocations = OrganMatch.objects.all()
    doctors = Doctor.objects.all()
    data = {
        "allocations":[
            {
                "id": alloc.id,
                "recipient_name": alloc.recipient.fullname,  # Update based on your model field
                "donor_name": alloc.organ.donor.fullname,  
                "organ_type": alloc.organ.organ_type,
                "blood_type": alloc.recipient.blood_type,
                "doctor": alloc.doctor.user.username if alloc.doctor and alloc.doctor.user else None,
                "doctor_id": alloc.doctor.id if alloc.doctor else None,
                "status": alloc.status
            }
            for alloc in allocations
        ],
        "doctors": [
            {
                "id": doctor.id,
                "name": doctor.user.username  # or fullname if you have
            }
            for doctor in doctors
        ]
    }
    return JsonResponse(data, safe=False)

from .models import Doctor  # Import Doctor model if not already

@csrf_exempt
def approve_organ_allocation(request, allocation_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            allocation = get_object_or_404(OrganMatch, id=allocation_id)

            if data.get("action") == "approve":
                allocation.status = "Approved"
                allocation.organ.status = "Allocated"
                allocation.recipient.status = "Matched"

                Notification.objects.create(
                    receiver=allocation.organ.donor.user,
                    sender=allocation.reviewed_by,
                    type='organ match confirmation',
                    organ_match=allocation,
                    message=f"Hello Mr/Mrs.{allocation.organ.donor.user.last_name}, your organ donation is approved. Please confirm."
                )
                Notification.objects.create(
                    receiver=allocation.recipient.user,
                    sender=allocation.reviewed_by,
                    type='organ match confirmation',
                    organ_match=allocation,
                    message=f"Hello Mr/Mrs.{allocation.recipient.user.last_name}, your organ allocation is approved. Please confirm."
                )

            elif data.get("action") == "reject":
                allocation.status = "Rejected"
                allocation.recipient.status = "Waiting"

            elif data.get("action") == "assign_doctor":
                doctor_id = data.get("doctor_id")
                if doctor_id:
                    doctor = get_object_or_404(Doctor, id=doctor_id)
                    allocation.doctor = doctor

                    # Send notification to doctor
                    Notification.objects.create(
                        receiver=doctor.user,
                        sender=allocation.reviewed_by,
                        type='doctor assignment',
                        message=f"You have been assigned to oversee an organ allocation for {allocation.recipient.fullname} and {allocation.organ.donor.fullname}."
                    )
                else:
                    allocation.doctor = None  # Unassign the doctor

            allocation.save()
            allocation.organ.save()
            allocation.recipient.save()

            return JsonResponse({"message": "Operation completed successfully."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def notification(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    print(notifications)
    return render(request, 'notification.html', {'notifications': notifications})

@login_required
def reply_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, receiver=request.user)

    if request.method == "POST":
        reply_text = request.POST.get("reply_text")
        if reply_text:
            notification.reply_message = reply_text
            notification.save()

            return JsonResponse({"success": True, "message": "Reply sent successfully!"})

    return JsonResponse({"success": False, "message": "Invalid request!"})

def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    
    notification.is_read = True
    notification.save()

    return redirect('notification')

def facility_schedule(request):
    notifications = Notification.objects.all().order_by('-created_at')
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
                receiver=notification.receiver,  
                sender=request.user,  
                type = 'schedule message',
                message=f"Mr/Mrs.{notification.receiver.username}, Your operation has been scheduled for {schedule_time}",
                is_read=False,  
                organ_match=notification.organ_match
            )
            organ_match_model=notification.organ_match
            organ_match_model.operation_schedule_date = schedule_time
            organ_match_model.save()
            notification.operation_schedule_date=schedule_time
            notification.save()
            new_notification.save() 
            return redirect("facility_schedule")

    return redirect("error_page")

def request_new_hospital(request):
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        contact = request.POST.get("contact")

        if Hospital.objects.filter(name=name).exists():
            messages.error(request, "Hospital already exists!")
        else:
            Hospital.objects.create(name=name, address=address, contact=contact)
            messages.success(request, "New hospital Uploaded! , Wait until Admin will Review and Verify Hospital ")
            return redirect("new_hospital") 

    return render(request, "new_hospital.html")

def update_staff(request):
    staff = request.user
    hospitals = Hospital.objects.filter(is_verified=True)

    if request.method == "POST":
        hospital_id = request.POST.get("hospital_id")

        if hospital_id:
            staff.hospital = Staff.objects.create(user=staff,hospital_id=hospital_id)

        staff.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("update_staff")  # Redirect to the same page

    return render(request, "staff_profile.html", {"staff": staff, "hospitals": hospitals})

def update_doctor(request):
    doctor = request.user  
    hospitals = Hospital.objects.all()

    if request.method == "POST":
        specialization = request.POST.get("specialization")
        hospital_id = request.POST.get("hospital_id")

        if hospital_id:
            Doctor.objects.create(user=doctor,hospital_id=hospital_id,specialization=specialization)

        doctor.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("update_doctor")  # Redirect to the same page

    return render(request, "doctor_profile.html", {"doctor": doctor, "hospitals": hospitals})

@login_required
def hospital_verification(request):
    hospitals = Hospital.objects.all()
    return render(request, 'hospital_verification.html', {'hospitals': hospitals})

@login_required
def verify_hospital(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    
    if request.method == "POST":
        form = HospitalVerificationForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            return redirect('hospital_verification')  # Redirect back to the list
    
    else:
        form = HospitalVerificationForm(instance=hospital)
    
    return render(request, 'verify_hospital.html', {'form': form, 'hospital': hospital})

def schedule_pdf(request, organ_match_id):
    schedule = OrganMatch.objects.get(id=organ_match_id)
    return render(request, 'schedule_pdf.html',{'schedule':schedule})