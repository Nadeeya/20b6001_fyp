from django import template
from mod.models import Application , Recruiter , Job
# import datetime

register = template.Library()


@register.simple_tag
def department_details(department):
    job = Job.objects.filter(department=department).count()
    recruiter = Recruiter.objects.filter(department=department).count()
    applicants = Application.objects.filter(job__department=department).count()

    return job, recruiter, applicants