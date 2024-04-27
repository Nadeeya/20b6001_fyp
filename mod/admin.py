from django.contrib import admin
from .models import Recruiter , Job , Application , UserFile , Department , AcademicApplication , NonAcademicApplication

# Register your models here.
admin.site.register(Recruiter)
admin.site.register(Job)
admin.site.register(Application)
admin.site.register(UserFile)
admin.site.register(Department)
admin.site.register(AcademicApplication)
admin.site.register(NonAcademicApplication)
