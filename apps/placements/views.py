import json
import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Placement, JobOffer
from apps.accounts.auth_helpers import admin_required
from apps.enquiries.models import log_activity
from apps.candidates.models import Applicant
from apps.candidates.status_helpers import set_applicant_status

@admin_required
def placements_api(request):
    if request.method == "GET":
        q = request.GET.get("q", "").strip().lower()
        status_filter = request.GET.get("status", "").strip()

        queryset = Placement.objects.all().order_by('-id')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        results = []
        for p in queryset:
            if q:
                match = (
                    q in p.candidate_name.lower() or
                    q in p.company_name.lower() or
                    q in p.position.lower()
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

        candidate_name = data.get("candidate_name")
        company_name = data.get("company_name")
        position = data.get("position")

        if not (candidate_name and company_name and position):
            return JsonResponse({"status": "error", "message": "Candidate name, company and position are required."}, status=400)

        applicant_id = data.get("applicant_id") or data.get("candidate_id")
        applicant = None
        if applicant_id:
            try:
                applicant = Applicant.objects.filter(id=int(applicant_id)).first()
            except (ValueError, TypeError):
                applicant = None
        if not applicant and candidate_name:
            applicant = Applicant.objects.filter(full_name__iexact=candidate_name).first()

        placement = Placement.objects.create(
            applicant=applicant,
            candidate_name=candidate_name,
            company_name=company_name,
            position=position,
            package=data.get("package", ""),
            placement_date=data.get("placement_date", datetime.datetime.now().strftime("%d %b %Y")),
            joining_date=data.get("joining_date", ""),
            status=data.get("status", "Placed"),
            notes=data.get("notes", "")
        )

        if applicant:
            set_applicant_status(applicant, 'Joined', changed_by='admin', force_override=True)
            JobOffer.objects.filter(applicant=applicant).update(status='Accepted')

        log_activity(
            "placement",
            "New placement updated",
            f"{candidate_name} placed at {company_name} ({position} - {placement.package})"
        )

        return JsonResponse({"status": "success", "message": "Placement record added successfully!", "placement": placement.to_dict()})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

@admin_required
def placement_detail(request, id):
    try:
        p = Placement.objects.get(id=id)
    except Placement.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Placement record not found."}, status=404)

    if request.method == "GET":
        return JsonResponse({"status": "success", "placement": p.to_dict()})

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if "candidate_name" in data: p.candidate_name = data["candidate_name"]
        elif "full_name" in data: p.candidate_name = data["full_name"]
        elif "name" in data: p.candidate_name = data["name"]

        if "company_name" in data: p.company_name = data["company_name"]
        if "position" in data: p.position = data["position"]
        elif "job_title" in data: p.position = data["job_title"]
        elif "category" in data: p.position = data["category"]

        if "package" in data: p.package = data["package"]
        if "placement_date" in data: p.placement_date = data["placement_date"]
        if "joining_date" in data: p.joining_date = data["joining_date"]
        if "status" in data: p.status = data["status"]
        if "notes" in data: p.notes = data["notes"]

        p.save()
        return JsonResponse({"status": "success", "message": "Placement record updated.", "placement": p.to_dict()})

    elif request.method == "DELETE":
        candidate_name = p.candidate_name
        app = p.applicant
        p.delete()
        if app and app.status in ['Joined', 'Placed']:
            from apps.candidates.status_helpers import set_applicant_status
            set_applicant_status(app, 'Selected', changed_by='admin', notes='Placement record deleted by admin.', force_override=True)
        log_activity("placement", "Placement record deleted", f"Placement for {candidate_name} deleted")
        return JsonResponse({"status": "success", "message": "Placement record deleted successfully."})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

@admin_required
def job_offers_api(request):
    if request.method == "GET":
        offers = JobOffer.objects.all().order_by('-id')
        return JsonResponse([o.to_dict() for o in offers], safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        if not (data.get("candidate_name") and data.get("company_name") and data.get("designation")):
            return JsonResponse({"status": "error", "message": "Candidate name, company name and designation required."}, status=400)

        applicant_id = data.get("applicant_id") or data.get("candidate_id")
        applicant = None
        if applicant_id:
            try:
                applicant = Applicant.objects.filter(id=int(applicant_id)).first()
            except (ValueError, TypeError):
                applicant = None
        if not applicant and data.get("candidate_name"):
            applicant = Applicant.objects.filter(full_name__iexact=data.get("candidate_name")).first()

        offer = JobOffer.objects.create(
            applicant=applicant,
            candidate_name=data.get("candidate_name"),
            company_name=data.get("company_name"),
            designation=data.get("designation"),
            offered_ctc=data.get("offered_ctc", ""),
            offer_date=data.get("offer_date", datetime.datetime.now().strftime("%d %b %Y")),
            joining_date=data.get("joining_date", ""),
            status=data.get("status", "Offer Sent"),
            notes=data.get("notes", "")
        )

        if applicant:
            set_applicant_status(applicant, 'Offer Released', changed_by='admin', force_override=True)
        return JsonResponse({"status": "success", "message": "Job offer recorded.", "offer": offer.to_dict()})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

@admin_required
def delete_job_offer(request, id):
    try:
        offer = JobOffer.objects.get(id=id)
    except JobOffer.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Job offer not found."}, status=404)

    if request.method == "GET":
        return JsonResponse({"status": "success", "offer": offer.to_dict()})

    elif request.method == "PUT":
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST
        if "candidate_name" in data: offer.candidate_name = data["candidate_name"]
        elif "full_name" in data: offer.candidate_name = data["full_name"]
        if "company_name" in data: offer.company_name = data["company_name"]
        if "designation" in data: offer.designation = data["designation"]
        elif "category" in data: offer.designation = data["category"]
        if "offered_ctc" in data: offer.offered_ctc = data["offered_ctc"]
        if "joining_date" in data: offer.joining_date = data["joining_date"]
        if "status" in data: offer.status = data["status"]
        if "notes" in data: offer.notes = data["notes"]
        offer.save()
        return JsonResponse({"status": "success", "message": "Job offer updated.", "offer": offer.to_dict()})

    elif request.method == "DELETE":
        app = offer.applicant
        offer.delete()
        if app and app.status in ['Offer Released', 'Offer Sent']:
            set_applicant_status(app, 'Selected', changed_by='admin', notes='Job offer deleted by admin.', force_override=True)
        return JsonResponse({"status": "success", "message": "Job offer deleted successfully."})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
