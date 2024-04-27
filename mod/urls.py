from django.urls import path, include
from . import views
from user.views import loginPage , logoutUser

urlpatterns = [
    path('admin-home/', views.adminHomePage , name='adminHome'),
    path('add-recruiter/', views.addRecruiter, name='addRecruiter'),
    path('add-job/', views.addJob, name='addJob'),
    path('add-non-academic-job/', views.addNonAcademicJob, name='nonAcademicJob'),
    path('login/', loginPage , name="login"),
    path('logout/', logoutUser, name="logout"),
    path('manage-recuiters/', views.manageRecruiters, name="manageRecruiters"),
    path('manage-jobs/', views.manageJobs, name="manageJobs"),
    path('edit-recruiter/<str:pk>/', views.editRecruiter, name="editRecruiter"),
    path('delete-recruiter/<str:pk>/', views.deleteRecruiter, name="deleteRecruiter"),
    path('edit-job/<str:pk>/', views.editJob, name="editJob"),
    path('recreate-job/<str:pk>/', views.recreateJob, name="recreateJob"),
    path('viewAllApplicants/', views.viewAllApplicants, name="viewAllApplicants"),
    path('viewApplicantDet-all/<str:pk>/', views.viewApplicationDetAll, name="viewApplicantDetAllMod"),
    path('view-application-detail/<str:pk>/', views.viewApplicationDet, name="viewApplicationDet"),
    path('view-department/', views.viewDepartments, name="viewDepartments"),
    path('add-department/', views.addDepartment, name="addDepartment"),
    path('department-details/<str:pk>', views.departmentDetails, name="departmentDetails"),
    path('edit-department/<str:pk>', views.editDepartment, name="editDepartment"),
    path('view-next-applicant-all/<str:current_applicant_id>', views.viewNextApplicantAll , name="viewNextApplicantsAllMod"),
    path('view-next-application/<str:current_applicant_id>/<str:job_id>/', views.viewNextApplication , name="viewNextApplication"),
    path('view-prev-application/<str:current_applicant_id>/<str:job_id>/', views.viewPreviousApplication , name="viewPreviousApplication"),
    path('view-previous-applicant-all/<str:current_applicant_id>', views.viewPreviousApplicantAll , name="viewPreviousApplicantsAllMod"),
    path('view-job-details/<str:pk>', views.viewJobDetails , name="viewJobDetails"),
    path('view-job-applications/<str:pk>', views.viewJobApplications , name="viewJobApplications"),
    path('advance-filtering/<str:pk>', views.advanceFiltering , name="advanceFiltering"),
    path('remove-icon/<str:pk>', views.removeIcon , name="removeIcon"),
    path('tinymce/', include('tinymce.urls')),
    path('send-reminders/<str:pk>', views.sendEmailReminder , name="sendEmailReminder"),
    path('view-confirmation/<str:pk>/', views.viewConfirmation ,name="viewConfirmation"),
    path('create-job-option/', views.createJobOption ,name="createJobOption"),




]