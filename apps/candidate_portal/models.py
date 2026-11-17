from django.db import models


class ApplicationStatusHistory(models.Model):
    applicant = models.ForeignKey('candidates.Applicant', on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=50, blank=True, default="")
    new_status = models.CharField(max_length=50)
    changed_by = models.CharField(max_length=100, default='system')
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'application_status_history'
        verbose_name = 'Application Status History'
        verbose_name_plural = 'Application Status Histories'
        ordering = ['-created_at']

    def to_dict(self):
        return {
            "id": self.id,
            "applicant_id": self.applicant_id,
            "old_status": self.old_status or "",
            "new_status": self.new_status,
            "changed_by": self.changed_by,
            "notes": self.notes or "",
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"Applicant #{self.applicant_id}: {self.old_status} -> {self.new_status}"


class CandidateSavedJob(models.Model):
    candidate_account = models.ForeignKey('accounts.CandidateAccount', on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='saved_by_candidates')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'candidate_saved_jobs'
        verbose_name = 'Candidate Saved Job'
        verbose_name_plural = 'Candidate Saved Jobs'
        unique_together = ('candidate_account', 'job')
        ordering = ['-created_at']

    def to_dict(self):
        return {
            "id": self.id,
            "candidate_account_id": self.candidate_account_id,
            "job_id": self.job_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }

    def __str__(self):
        return f"Candidate #{self.candidate_account_id} saved Job #{self.job_id}"
