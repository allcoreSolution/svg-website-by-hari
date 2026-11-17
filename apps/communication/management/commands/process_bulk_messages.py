from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.communication.models import BulkMessage
from apps.communication.services import check_stale_sending_messages, process_bulk_message_send

class Command(BaseCommand):
    help = "Resumes pending bulk messages and recovers interrupted/stale sending runs."

    def handle(self, *args, **options):
        self.stdout.write("Checking for stale sending runs...")
        interrupted = check_stale_sending_messages()
        if interrupted:
            self.stdout.write(self.style.WARNING(f"Flagged {interrupted} stale sending message(s) as Interrupted."))

        # Find messages that have pending recipients and are in a resumable state
        pending_messages = BulkMessage.objects.filter(
            status__in=['Pending', 'Interrupted', 'Partial', 'Failed']
        ).distinct()

        resumed_count = 0
        for bm in pending_messages:
            has_pending = bm.recipients.filter(delivery_status='Pending').exists()
            if has_pending:
                self.stdout.write(f"Resuming delivery for BulkMessage ID {bm.id} ('{bm.title}')...")
                process_bulk_message_send(bm.id, actor_name="Management Command / Cron")
                resumed_count += 1

        self.stdout.write(self.style.SUCCESS(f"Finished processing. Resumed {resumed_count} bulk message(s)."))
