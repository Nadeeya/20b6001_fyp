from django.db import models
from mod.models import Recruiter , Job , Application




class Justification(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    justification = models.TextField()

class SeminarReviewReport(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    title = models.TextField()
    seminar_date = models.DateField()
    review_date = models.DateField()
    content_score = models.JSONField(null=True)
    content_remarks = models.TextField(null=True)
    quality_score = models.JSONField(null=True)
    quality_remarks = models.TextField(null=True)
    communication_score = models.JSONField(null=True)
    communication_remarks = models.TextField(null=True)
    overall_score = models.JSONField(null=True)
    overall_remarks = models.TextField(null=True)

    
    

    