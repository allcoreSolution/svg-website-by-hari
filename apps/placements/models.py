from django.db import models

class Placement(models.Model):
    applicant = models.ForeignKey('candidates.Applicant', on_delete=models.SET_NULL, null=True, blank=True, related_name='placements')
    candidate_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=150)
    position = models.CharField(max_length=150)
    package = models.CharField(max_length=50, blank=True, default="")
    placement_date = models.CharField(max_length=50, blank=True, default="")
    joining_date = models.CharField(max_length=50, blank=True, default="")
    status = models.CharField(max_length=50, default="Placed")
    notes = models.TextField(blank=True, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'placements'
        verbose_name = 'Placement'
        verbose_name_plural = 'Placements'
        ordering = ['-id']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status and self.status in ['Placed', 'Joined', 'Candidate Joined', 'Hired', 'Offered & Joined', 'Completed']:
            try:
                from apps.ledger.services import ensure_commission_for_joined
                ensure_commission_for_joined(placement=self)
            except Exception:
                pass

    def to_dict(self):
        return {
            "id": self.id,
            "applicant_id": self.applicant_id,
            "candidate_name": self.candidate_name,
            "company_name": self.company_name,
            "position": self.position,
            "package": self.package or "",
            "placement_date": self.placement_date or "",
            "joining_date": self.joining_date or "",
            "status": self.status or "Placed",
            "notes": self.notes or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"{self.candidate_name} @ {self.company_name}"


class JobOffer(models.Model):
    applicant = models.ForeignKey('candidates.Applicant', on_delete=models.SET_NULL, null=True, blank=True, related_name='job_offers')
    candidate_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=150)
    designation = models.CharField(max_length=150)
    offered_ctc = models.CharField(max_length=50, blank=True, default="")
    offer_date = models.CharField(max_length=50, blank=True, default="")
    joining_date = models.CharField(max_length=50, blank=True, default="")
    status = models.CharField(max_length=50, default="Offer Sent")
    notes = models.TextField(blank=True, null=True, default="")
    document = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'job_offers'
        verbose_name = 'Job Offer'
        verbose_name_plural = 'Job Offers'
        ordering = ['-id']

    def to_dict(self):
        return {
            "id": self.id,
            "applicant_id": self.applicant_id,
            "candidate_name": self.candidate_name,
            "company_name": self.company_name,
            "designation": self.designation,
            "offered_ctc": self.offered_ctc or "",
            "offer_date": self.offer_date or "",
            "joining_date": self.joining_date or "",
            "status": self.status or "Offer Sent",
            "notes": self.notes or "",
            "document": self.document or "",
            "document_url": f"/api/admin/files/download/{self.document}" if self.document else "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"{self.candidate_name} - {self.company_name}"
