import json
import re
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import InternshipEnquiry, InternshipProvider, Internship, InternshipApplication
from apps.accounts.auth_helpers import admin_required, save_resume_file, delete_resume_file, allowed_file
from apps.enquiries.models import log_activity

# ==========================================
# EXISTING INTERNSHIP ENQUIRY VIEWS (UNTOUCHED)
# ==========================================

@require_http_methods(["POST"])
def create_internship_enquiry(request):
    resume_file = request.FILES.get("resume")
    stored_filename = ""
    if resume_file:
        try:
            stored_filename = save_resume_file(resume_file) or ""
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    try:
        data = request.POST if request.POST else (json.loads(request.body) if request.body else {})
    except Exception:
        data = request.POST

    full_name = (data.get("full_name") or data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or data.get("mobile") or "").strip()
    course_stream = data.get("course_stream") or data.get("course") or data.get("qualification") or "Internship"

    if not (full_name and email and phone):
        return JsonResponse({"status": "error", "message": "Name, email and phone are required."}, status=400)

    enquiry = InternshipEnquiry.objects.filter(email__iexact=email, phone=phone, status__in=["New", "Pending"]).order_by('-id').first()
    if enquiry:
        enquiry.full_name = full_name
        enquiry.course_stream = course_stream
        if stored_filename:
            enquiry.resume = stored_filename
        enquiry.save()
    else:
        enquiry = InternshipEnquiry.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            college=data.get("college", ""),
            course_stream=course_stream,
            duration=data.get("duration", "3 Months"),
            skills=data.get("skills", ""),
            message=data.get("message", ""),
            resume=stored_filename,
            status="New",
            notes=""
        )

    log_activity(
        "internship",
        "Internship enquiry received",
        f"{full_name} applied for {course_stream} internship ({enquiry.duration})"
    )

    return JsonResponse({
        "status": "success",
        "success": True,
        "message": "Thank you! Your internship application has been received successfully."
    })

@require_http_methods(["GET"])
@admin_required
def get_internship_enquiries(request):
    q = request.GET.get("q", "").strip().lower()
    status_filter = request.GET.get("status", "").strip()

    queryset = InternshipEnquiry.objects.all().order_by('-id')
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    results = []
    for e in queryset:
        if q:
            match = (
                q in e.full_name.lower() or
                q in e.email.lower() or
                q in e.phone.lower() or
                q in (e.course_stream or "").lower()
            )
            if not match:
                continue
        results.append(e.to_dict())

    return JsonResponse(results, safe=False)

@admin_required
def internship_enquiry_detail(request, id):
    try:
        enquiry = InternshipEnquiry.objects.get(id=id)
    except InternshipEnquiry.DoesNotExist:
        return JsonResponse({"status": "error", "success": False, "message": "Internship enquiry not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(enquiry.to_dict())

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if "full_name" in data: enquiry.full_name = data["full_name"]
        if "email" in data: enquiry.email = data["email"]
        if "phone" in data: enquiry.phone = data["phone"]
        if "college" in data: enquiry.college = data["college"]
        if "course_stream" in data: enquiry.course_stream = data["course_stream"]
        if "duration" in data: enquiry.duration = data["duration"]
        if "skills" in data: enquiry.skills = data["skills"]
        if "message" in data: enquiry.message = data["message"]
        if "status" in data: enquiry.status = data["status"]
        if "notes" in data: enquiry.notes = data["notes"]

        enquiry.save()
        return JsonResponse({"status": "success", "success": True, "message": "Internship enquiry updated.", "enquiry": enquiry.to_dict(), "data": enquiry.to_dict()})

    elif request.method == "DELETE":
        if enquiry.resume:
            delete_resume_file(enquiry.resume)
        enquiry.delete()
        return JsonResponse({"status": "success", "success": True, "message": "Internship enquiry deleted successfully."})

    return JsonResponse({"status": "error", "success": False, "message": "Method not allowed."}, status=405)


# ==========================================
# TASK 2: NEW REST-STYLE JSON APIS
# ==========================================

# 1. INTERNSHIP PROVIDERS API
@admin_required
def internship_providers_api(request):
    if request.method == "GET":
        q = request.GET.get("q", "").strip().lower()
        queryset = InternshipProvider.objects.all().order_by('-id')
        results = []
        for p in queryset:
            if q:
                match = (
                    q in p.name.lower() or
                    q in p.contact_person.lower() or
                    q in p.email.lower() or
                    q in p.phone.lower() or
                    q in p.industry.lower()
                )
                if not match:
                    continue
            results.append(p.to_dict())
        return JsonResponse(results, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        name = (data.get("name") or "").strip()
        if not name:
            return JsonResponse({"status": "error", "success": False, "message": "Provider name is required."}, status=400)

        email = (data.get("email") or "").strip()
        if email and ("@" not in email or "." not in email):
            return JsonResponse({"status": "error", "success": False, "message": "Please enter a valid email address."}, status=400)

        provider = InternshipProvider.objects.create(
            name=name,
            contact_person=data.get("contact_person", "").strip(),
            email=email,
            phone=data.get("phone", "").strip(),
            industry=data.get("industry", "").strip(),
            address=data.get("address", "").strip(),
            notes=data.get("notes", "").strip(),
            is_active=bool(data.get("is_active", True))
        )

        log_activity("internship", "Internship Provider Created", f"Provider '{provider.name}' created by admin")
        return JsonResponse({
            "status": "success",
            "success": True,
            "message": "Internship provider created successfully.",
            "data": provider.to_dict(),
            "provider": provider.to_dict()
        }, status=201)

    return JsonResponse({"status": "error", "success": False, "message": "Method not allowed."}, status=405)


@admin_required
def internship_provider_detail_api(request, id):
    try:
        provider = InternshipProvider.objects.get(id=id)
    except InternshipProvider.DoesNotExist:
        return JsonResponse({"status": "error", "success": False, "message": "Internship provider not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(provider.to_dict())

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if "name" in data:
            name = str(data["name"]).strip()
            if not name:
                return JsonResponse({"status": "error", "success": False, "message": "Provider name cannot be empty."}, status=400)
            provider.name = name
        if "contact_person" in data: provider.contact_person = data["contact_person"]
        if "email" in data: provider.email = data["email"]
        if "phone" in data: provider.phone = data["phone"]
        if "industry" in data: provider.industry = data["industry"]
        if "address" in data: provider.address = data["address"]
        if "notes" in data: provider.notes = data["notes"]
        if "is_active" in data: provider.is_active = bool(data["is_active"])

        provider.save()
        log_activity("internship", "Internship Provider Updated", f"Provider '{provider.name}' updated")
        return JsonResponse({"status": "success", "success": True, "message": "Provider updated successfully.", "data": provider.to_dict()})

    elif request.method == "DELETE":
        name = provider.name
        provider.delete()
        log_activity("internship", "Internship Provider Deleted", f"Provider '{name}' deleted")
        return JsonResponse({"status": "success", "success": True, "message": "Provider deleted successfully."})

    return JsonResponse({"status": "error", "success": False, "message": "Method not allowed."}, status=405)


# 2. INTERNSHIPS API
@admin_required
def internships_api(request):
    if request.method == "GET":
        status_filter = request.GET.get("status", "").strip()
        q = request.GET.get("q", "").strip().lower()

        queryset = Internship.objects.all().order_by('-id')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        results = []
        for i in queryset:
            if q:
                match = (
                    q in i.title.lower() or
                    q in (i.location or "").lower() or
                    q in (i.skills_required or "").lower() or
                    q in (i.description or "").lower() or
                    q in (i.provider.name.lower() if i.provider else "")
                )
                if not match:
                    continue
            results.append(i.to_dict())
        return JsonResponse(results, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        title = (data.get("title") or "").strip()
        if not title:
            return JsonResponse({"status": "error", "success": False, "message": "Internship title is required."}, status=400)

        try:
            seats = int(data.get("seats") or 1)
        except (ValueError, TypeError):
            seats = 1

        if seats < 1:
            return JsonResponse({"status": "error", "success": False, "message": "Seats must be at least 1."}, status=400)

        start_date = None
        end_date = None
        if data.get("start_date"):
            try:
                start_date = datetime.strptime(str(data["start_date"]).strip(), "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"status": "error", "success": False, "message": "Invalid start date format (expected YYYY-MM-DD)."}, status=400)

        if data.get("end_date"):
            try:
                end_date = datetime.strptime(str(data["end_date"]).strip(), "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({"status": "error", "success": False, "message": "Invalid end date format (expected YYYY-MM-DD)."}, status=400)

        if start_date and end_date and end_date < start_date:
            return JsonResponse({"status": "error", "success": False, "message": "End date cannot be earlier than start date."}, status=400)

        provider_obj = None
        provider_id = data.get("provider_id") or data.get("provider")
        if provider_id:
            try:
                provider_obj = InternshipProvider.objects.get(id=provider_id)
            except (InternshipProvider.DoesNotExist, ValueError):
                pass

        internship = Internship.objects.create(
            title=title,
            provider=provider_obj,
            description=data.get("description", "").strip(),
            location=data.get("location", "").strip(),
            mode=data.get("mode", "Onsite").strip(),
            duration=data.get("duration", "3 Months").strip(),
            stipend=data.get("stipend", "").strip(),
            seats=seats,
            skills_required=data.get("skills_required", "").strip(),
            start_date=start_date,
            end_date=end_date,
            status=data.get("status", "Open").strip()
        )

        log_activity("internship", "New Internship Posted", f"Internship '{title}' posted with {seats} seats")
        return JsonResponse({
            "status": "success",
            "success": True,
            "message": "Internship created successfully.",
            "data": internship.to_dict(),
            "internship": internship.to_dict()
        }, status=201)

    return JsonResponse({"status": "error", "success": False, "message": "Method not allowed."}, status=405)


@admin_required
def internship_detail_api(request, id):
    try:
        internship = Internship.objects.get(id=id)
    except Internship.DoesNotExist:
        return JsonResponse({"status": "error", "success": False, "message": "Internship not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(internship.to_dict())

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if "title" in data:
            title = str(data["title"]).strip()
            if not title:
                return JsonResponse({"status": "error", "success": False, "message": "Title cannot be empty."}, status=400)
            internship.title = title

        if "seats" in data:
            try:
                seats = int(data["seats"])
                if seats < 1:
                    return JsonResponse({"status": "error", "success": False, "message": "Seats must be at least 1."}, status=400)
                internship.seats = seats
            except (ValueError, TypeError):
                return JsonResponse({"status": "error", "success": False, "message": "Invalid seats number."}, status=400)

        if "provider_id" in data or "provider" in data:
            p_id = data.get("provider_id") or data.get("provider")
            if p_id:
                try:
                    internship.provider = InternshipProvider.objects.get(id=p_id)
                except InternshipProvider.DoesNotExist:
                    internship.provider = None
            else:
                internship.provider = None

        if "description" in data: internship.description = data["description"]
        if "location" in data: internship.location = data["location"]
        if "mode" in data: internship.mode = data["mode"]
        if "duration" in data: internship.duration = data["duration"]
        if "stipend" in data: internship.stipend = data["stipend"]
        if "skills_required" in data: internship.skills_required = data["skills_required"]
        if "status" in data: internship.status = data["status"]

        start_date = internship.start_date
        end_date = internship.end_date

        if "start_date" in data:
            if data["start_date"]:
                try: start_date = datetime.strptime(str(data["start_date"]).strip(), "%Y-%m-%d").date()
                except ValueError: return JsonResponse({"status": "error", "success": False, "message": "Invalid start date."}, status=400)
            else: start_date = None

        if "end_date" in data:
            if data["end_date"]:
                try: end_date = datetime.strptime(str(data["end_date"]).strip(), "%Y-%m-%d").date()
                except ValueError: return JsonResponse({"status": "error", "success": False, "message": "Invalid end date."}, status=400)
            else: end_date = None

        if start_date and end_date and end_date < start_date:
            return JsonResponse({"status": "error", "success": False, "message": "End date cannot be earlier than start date."}, status=400)

        internship.start_date = start_date
        internship.end_date = end_date
        internship.save()

        log_activity("internship", "Internship Updated", f"Internship '{internship.title}' updated")
        return JsonResponse({"status": "success", "success": True, "message": "Internship updated successfully.", "data": internship.to_dict()})

    elif request.method == "DELETE":
        title = internship.title
        internship.delete()
        log_activity("internship", "Internship Deleted", f"Internship '{title}' deleted")
        return JsonResponse({"status": "success", "success": True, "message": "Internship deleted successfully."})

    return JsonResponse({"status": "error", "success": False, "message": "Method not allowed."}, status=405)


@admin_required
@require_http_methods(["POST"])
def internship_change_status_api(request, id):
    try:
        internship = Internship.objects.get(id=id)
    except Internship.DoesNotExist:
        return JsonResponse({"status": "error", "success": False, "message": "Internship not found."}, status=404)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    new_status = (data.get("status") or "").strip()
    valid_statuses = ["Open", "Active", "Completed", "Closed"]
    if not new_status or new_status not in valid_statuses:
        return JsonResponse({"status": "error", "success": False, "message": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}, status=400)

    old_status = internship.status
    internship.status = new_status
    internship.save()

    log_activity("internship", "Internship Status Changed", f"'{internship.title}' status changed from {old_status} to {new_status}")
    return JsonResponse({
        "status": "success",
        "success": True,
        "message": f"Internship status changed to {new_status}.",
        "data": internship.to_dict()
    })


# 3. INTERNSHIP APPLICATIONS API
@admin_required
def internship_applications_api(request):
    if request.method != "GET":
        return JsonResponse({"status": "error", "success": False, "message": "Method not allowed."}, status=405)

    status_filter = request.GET.get("status", "").strip()
    internship_id = request.GET.get("internship", "").strip()
    q = request.GET.get("q", "").strip().lower()

    queryset = InternshipApplication.objects.all().order_by('-id')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if internship_id:
        try:
            queryset = queryset.filter(internship_id=int(internship_id))
        except ValueError:
            pass

    results = []
    for a in queryset:
        if q:
            match = (
                q in a.full_name.lower() or
                q in a.email.lower() or
                q in a.phone.lower() or
                q in (a.college or "").lower() or
                q in (a.course_stream or "").lower() or
                q in (a.internship.title.lower() if a.internship else "")
            )
            if not match:
                continue
        results.append(a.to_dict())

    return JsonResponse(results, safe=False)


@admin_required
def internship_application_detail_api(request, id):
    try:
        app_obj = InternshipApplication.objects.get(id=id)
    except InternshipApplication.DoesNotExist:
        return JsonResponse({"status": "error", "success": False, "message": "Internship application not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(app_obj.to_dict())

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        old_status = app_obj.status
        if "status" in data: app_obj.status = data["status"]
        if "notes" in data: app_obj.notes = data["notes"]
        if "full_name" in data: app_obj.full_name = data["full_name"]
        if "email" in data: app_obj.email = data["email"]
        if "phone" in data: app_obj.phone = data["phone"]
        if "college" in data: app_obj.college = data["college"]
        if "course_stream" in data: app_obj.course_stream = data["course_stream"]

        app_obj.save()

        if "status" in data and old_status != app_obj.status:
            log_activity("internship", "Application Status Updated", f"{app_obj.full_name} status updated to {app_obj.status}")

        return JsonResponse({"status": "success", "success": True, "message": "Application updated successfully.", "data": app_obj.to_dict()})

    elif request.method == "DELETE":
        if app_obj.resume:
            delete_resume_file(app_obj.resume)
        name = app_obj.full_name
        app_obj.delete()
        log_activity("internship", "Application Deleted", f"Application for {name} deleted")
        return JsonResponse({"status": "success", "success": True, "message": "Application deleted successfully."})

    return JsonResponse({"status": "error", "success": False, "message": "Method not allowed."}, status=405)


# 4. PUBLIC APIs
@require_http_methods(["GET"])
def public_internships_api(request):
    open_internships = Internship.objects.filter(status="Open").order_by('-id')
    results = [i.to_dict() for i in open_internships]
    return JsonResponse({"status": "success", "success": True, "data": results, "internships": results})


@require_http_methods(["POST"])
def public_internship_apply_api(request):
    resume_file = request.FILES.get("resume")
    stored_filename = ""
    if resume_file:
        if resume_file.size > 5 * 1024 * 1024:
            return JsonResponse({"status": "error", "success": False, "message": "Resume file size must not exceed 5 MB."}, status=400)
        try:
            stored_filename = save_resume_file(resume_file) or ""
        except ValueError as e:
            return JsonResponse({"status": "error", "success": False, "message": str(e)}, status=400)

    try:
        data = request.POST if request.POST else (json.loads(request.body) if request.body else {})
    except Exception:
        data = request.POST

    full_name = (data.get("full_name") or data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or data.get("mobile") or "").strip()

    if not full_name:
        return JsonResponse({"status": "error", "success": False, "message": "Full name is required."}, status=400)
    if not email or "@" not in email or "." not in email:
        return JsonResponse({"status": "error", "success": False, "message": "A valid email address is required."}, status=400)
    if not phone or len(re.sub(r'\D', '', phone)) < 7:
        return JsonResponse({"status": "error", "success": False, "message": "A valid phone number (at least 7 digits) is required."}, status=400)

    # Determine target internship
    internship_id = data.get("internship_id") or data.get("internship")
    internship_domain = str(data.get("internship_domain") or data.get("internship_title") or data.get("domain") or "").strip()
    duration = str(data.get("duration") or "3 Months").strip()
    mode = str(data.get("mode") or "Work From Home / Remote").strip()

    internship_obj = None
    if internship_id:
        try:
            internship_obj = Internship.objects.get(id=internship_id)
        except Internship.DoesNotExist:
            pass

    if not internship_obj and internship_domain:
        internship_obj = Internship.objects.filter(title__iexact=internship_domain).first()
        if not internship_obj:
            clean_term = internship_domain.replace("Internship", "").replace("(", "").replace(")", "").strip()
            if clean_term:
                internship_obj = Internship.objects.filter(title__icontains=clean_term).first()
        if not internship_obj:
            internship_obj = Internship.objects.create(
                title=internship_domain if "intern" in internship_domain.lower() else f"{internship_domain} Internship",
                description=f"{internship_domain} Programme at Sky Vision",
                mode=mode,
                duration=duration,
                seats=10,
                status="Open"
            )

    if not internship_obj:
        internship_obj, _ = Internship.objects.get_or_create(
            title="General Internship Programme",
            defaults={
                "description": "General Internship Application",
                "mode": mode or "Onsite",
                "duration": duration or "3 Months",
                "seats": 10,
                "status": "Open"
            }
        )

    notes_info = f"Track: {internship_domain or internship_obj.title} | Duration: {duration} | Mode: {mode}"

    # Check existing pending application for deduplication
    app_obj = InternshipApplication.objects.filter(
        internship=internship_obj,
        email__iexact=email,
        phone=phone,
        status__in=["Pending", "New"]
    ).first()

    if app_obj:
        app_obj.full_name = full_name
        app_obj.college = data.get("college", app_obj.college)
        app_obj.course_stream = data.get("course_stream") or data.get("qualification") or app_obj.course_stream
        app_obj.skills = data.get("skills", app_obj.skills)
        app_obj.message = data.get("message", app_obj.message)
        app_obj.notes = notes_info
        if stored_filename:
            app_obj.resume = stored_filename
        app_obj.save()
    else:
        app_obj = InternshipApplication.objects.create(
            internship=internship_obj,
            full_name=full_name,
            email=email,
            phone=phone,
            college=data.get("college", "").strip(),
            course_stream=(data.get("course_stream") or data.get("qualification") or "").strip(),
            skills=data.get("skills", "").strip(),
            message=data.get("message", "").strip(),
            resume=stored_filename,
            notes=notes_info,
            status="Pending"
        )

    log_activity("internship", "Public Internship Application Submitted", f"{full_name} applied for '{internship_obj.title}'")
    return JsonResponse({
        "status": "success",
        "success": True,
        "message": "Your application has been submitted successfully! Our team will contact you soon.",
        "data": app_obj.to_dict()
    })


# 5. CONVERT ENQUIRY TO APPLICATION
@admin_required
@require_http_methods(["POST"])
def convert_enquiry_to_application_api(request, id):
    try:
        enquiry = InternshipEnquiry.objects.get(id=id)
    except InternshipEnquiry.DoesNotExist:
        return JsonResponse({"status": "error", "success": False, "message": "Internship enquiry not found."}, status=404)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except Exception:
        data = request.POST

    internship_id = data.get("internship_id") or data.get("internship")
    internship_obj = None
    if internship_id:
        try:
            internship_obj = Internship.objects.get(id=internship_id)
        except Internship.DoesNotExist:
            pass

    if not internship_obj:
        internship_obj = Internship.objects.filter(status="Open").order_by('-id').first()

    if not internship_obj:
        internship_obj = Internship.objects.create(
            title=f"Internship ({enquiry.course_stream or 'General'})",
            duration=enquiry.duration or "3 Months",
            status="Open"
        )

    app_obj = InternshipApplication.objects.create(
        internship=internship_obj,
        full_name=enquiry.full_name,
        email=enquiry.email,
        phone=enquiry.phone,
        college=enquiry.college,
        course_stream=enquiry.course_stream,
        skills=enquiry.skills,
        message=enquiry.message,
        resume=enquiry.resume or "",
        status="Pending",
        notes=f"Converted from enquiry #{enquiry.id}. {enquiry.notes or ''}".strip()
    )

    enquiry.status = "Converted"
    enquiry.save()

    log_activity("internship", "Enquiry Converted to Application", f"Enquiry #{enquiry.id} ({enquiry.full_name}) converted to application #{app_obj.id}")
    return JsonResponse({
        "status": "success",
        "success": True,
        "message": f"Internship enquiry converted to application successfully for {app_obj.full_name}!",
        "data": app_obj.to_dict(),
        "application": app_obj.to_dict()
    })
