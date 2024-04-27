from django.db import models
from django.utils import timezone
from user.models import User , Applicant
from django.contrib.postgres.fields import ArrayField
from django_random_id_model import RandomIDModel

# Create your models here.
class Department(RandomIDModel):
    name = models.CharField(max_length=300, null=True)
    icon = models.ImageField(upload_to='department-icon/', blank=True)
    category = models.CharField(max_length=20,null=True)
    description = models.TextField()
    link = models.CharField(max_length=300, null=True)

    def __str__(self):
        return self.name

class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    change_password =  models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    member_type = models.CharField(max_length=10, default="")

    def __str__(self):
        return self.user.email
    
class Job(RandomIDModel):
    header = models.TextField(null=True)
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    # category = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    position = models.CharField(max_length=40, null=True)
    status = models.CharField(max_length=200)
    uploadDate = models.DateField(auto_now_add=True)
    salaryMin = models.IntegerField()
    salaryMax = models.IntegerField()
    minReq = models.CharField(max_length=200)
    yearsExp = models.IntegerField(null=True)
    description = models.TextField()
    contractDur = models.IntegerField(null=True)
    dateClose = models.DateField()
    vacancy = models.IntegerField(null=True)
    # this is for non-academic:
    expGov = models.CharField(max_length=3, null=True)  #previously worked in the government sector , yes or no
    expGovInfo = models.JSONField(null=True) # the position and number of years of experience that candidate should have.
    jobForm = models.CharField(max_length=200)
    btnMsg = models.CharField(max_length=200)


    def __str__(self):
        return self.name
    
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<fullname>/<filename>
    fullname = str(instance.applicant.user.first_name) + '_'+str(instance.applicant.user.last_name)
    return "applicants/{0}/{1}/{2}".format(instance.applicant.job.name ,fullname, filename)
    
class Application(RandomIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    profile = models.ForeignKey(Applicant , on_delete=models.CASCADE)
    fullname = models.CharField(max_length=200, null=True )
    applicant_status = models.CharField(max_length=30 , default="PENDING")
    date_added = models.DateField(default=timezone.now)
    source = models.CharField(max_length=200, null=True)
    prevApplication = models.CharField(max_length=3, null=True) # any prev application yes or no
    datePrev = models.DateField(null=True)
    presentEmployment = models.JSONField(null=True)
    academicRec =  models.JSONField(null=True)
    documents = models.JSONField(null=True)
    consent = models.CharField(max_length=3,null=True, default="Yes")
    applicant_progress = models.CharField(max_length=30 , default="In Progress")
    application_type = models.CharField(max_length=30, null=True)

    #documents = models.FileField(upload_to=user_directory_path, default="")

    def __str__(self):
        return self.user.email

class AcademicApplication(RandomIDModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    postApplied = models.CharField(max_length=20, default="")
    membershipFellowship = models.JSONField(null=True)
    experienceHighEd = models.CharField(max_length=3, null=True) # experience in high edu sector yes or no
    employmentRecHighEd = models.JSONField(null=True)
    experienceInd = models.CharField(max_length=3, null=True) # experience in industry yes or no
    employmentRecInd = models.JSONField(null=True)
    coursesOffering = models.JSONField(null=True)
    teachingSupervision = models.JSONField(null=True)
    scholarlyInfo = models.JSONField(null=True)
    scopusInfo = models.JSONField(null=True)
    languages = models.JSONField(null=True)
    otherLanguages = models.JSONField(null=True)
    family = models.JSONField(null=True)
    referees = models.JSONField(null=True)
    # search_fields = ('application__applicant_id')

class NonAcademicApplication(RandomIDModel):
    application = models.ForeignKey(Application, on_delete = models.CASCADE)
    drivingLicense = models.CharField(max_length=3, null=True) # yes or no
    drivingLicenseType = models.CharField(max_length=20, null=True)
    languages = models.JSONField(null=True)
    highestEducationLevel = models.CharField(max_length=50, null=True)
    expGov = models.CharField(max_length=3, null=True) # yes or no
    workExperience = models.JSONField(null=True)
    

    

class UserFile(models.Model):
    applicant = models.ForeignKey(Application, on_delete=models.CASCADE)
    f_name = models.CharField(max_length=255)
    myfiles = models.FileField(upload_to=user_directory_path, default="", max_length=1000)

    def __str__(self):
        return self.f_name
    
class Bookmarks(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    bookmark = models.JSONField(max_length=250, null=True) #to store the name of dictionary key=id , value = name of dictionary

    def __str__(self):
        return self.recruiter.user.email
    

class Bookmarked(models.Model):
    bookmark = models.ForeignKey(Bookmarks, on_delete=models.CASCADE)
    id_bookmark = models.CharField(max_length=5, null=True)
    name = models.CharField(max_length=200, null=True)
    color = models.CharField(max_length=255, null=True)
    application_list = ArrayField(
        models.BigIntegerField(),
        null=True)

    def __str__(self): 
        return self.bookmark.bookmark
    



    

