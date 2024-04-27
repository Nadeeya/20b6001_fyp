from django.core.management.base import BaseCommand
from mod.models import Job , Application

class Command(BaseCommand):
    help = 'Deletes draft'

    def handle(self, *args, **options):
        jobs=Job.objects.filter(status='CLOSED')
        for job in jobs:
                applicants = Application.objects.filter(job=job).filter(applicant_progress='DRAFT')
                applicants.delete()
        # success message
        self.stdout.write('Successfully delete all drafts from closed jobs')