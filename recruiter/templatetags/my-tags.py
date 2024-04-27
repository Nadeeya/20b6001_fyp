from django import template
from mod.models import Bookmarked , Application , Recruiter , Job
# import datetime

register = template.Library()


@register.simple_tag
def bookmarkOptions(bookmark_id , applicant_id):
    # bookmark_id is bookmarkList_id
    # get all bookmarks using bookmark_id
    bookmarked = Bookmarked.objects.filter(bookmark_id=bookmark_id)

    for b in bookmarked:
        if applicant_id in b.application_list:
            old_bookmark_id = b.id_bookmark
            return b.name , b.color , old_bookmark_id
      
    #if applicant id is not in list at all:
    default = 'Bookmark'
    default_color = ''
    old_bookmark_id = 0
    return default , default_color , old_bookmark_id


@register.simple_tag
def department_details(department):
    job = Job.objects.filter(department=department).count()
    recruiter = Recruiter.objects.filter(department=department).count()
    applicants = Application.objects.filter(job__department=department).count()

    # if job == 1 or job == 0:
    #     job = str(job) + ' job opening'
    # else:
    #     job = str(job) + ' job openings'
    # if recruiter == 1 or recruiter == 0:
    #     recruiter = str(recruiter) + ' staff member'
    # else:
    #     recruiter = str(recruiter) + ' staff members'
    # if applicants == 1 or applicants == 0:
    #     applicants = str(applicants) + ' applicant'
    # else:
    #     applicants = str(applicants) + ' applicants'

    return job, recruiter, applicants

        


