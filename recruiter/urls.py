from django.urls import path
from . import views
from user.views import loginPage , logoutUser

urlpatterns = [
    path('recruiter-home', views.recruiterHome, name='recruiterHome'),
    path('login/', loginPage , name="login"),
    path('logout/', logoutUser, name="logout"),
    path('view-jobs/', views.viewJobs , name="viewJobs"),
    path('view-applicants/<str:pk>/', views.viewApplicantsJob , name="viewApplicantsJob"),
    path('view-applicant-details/<str:pk>/', views.viewApplicantDet , name="viewApplicantDet"),
    path('generate-pdf/<str:pk>/', views.generate_pdf_file , name="generatePdf"),
    path('generate-pdf-seminar-review-report/<str:pk>/', views.generate_pdf_seminar_report , name="generateSeminarReport"),
    path('recommend-applicant/<str:pk>/', views.recommendApplicant , name="recommendApplicant"),
    path('pending-applicant/<str:pk>/', views.pendingApplicant , name="pendingApplicant"),
    path('not-recommend-applicant/<str:pk>/', views.notRecommendApplicant , name="notRecommendApplicant"),
    path('download-excel/<str:pk>/', views.get_excel , name="getExcel"),
    path('download-folder/<str:pk>/', views.downloadAllApplicantFolder , name="downloadFolder"),
    path('view-all-applicants', views.viewApplicants , name="viewApplicants"),
    path('view-next-applicant/<str:job_id>/<str:current_applicant_id>', views.viewNextApplicant , name="viewNextApplicants"),
    path('view-previous-applicant/<str:job_id>/<str:current_applicant_id>', views.viewPreviousApplicant , name="viewPreviousApplicants"),
    path('view-job-details/<str:pk>', views.viewJobDet , name="viewJobDet"),
    path('change-password', views.changePassword , name="changePassword"),
    path('bookmark/<str:applicant_id>/<str:old_bookmark_id>/<str:bookmarkList_id>', views.bookmarkPopUp , name="bookmark"),
    path('advanceFilter/<str:pk>', views.advanceFilter , name="advanceFilter"),
    path('view-members', views.viewMembers , name="viewMembers"),
    path('view-applicant-details-all/<str:pk>', views.viewApplicantDetAll , name="viewApplicantDetAll"),
    path('view-next-applicant-all/<str:current_applicant_id>', views.viewNextApplicantAll , name="viewNextApplicantsAll"),
    path('view-previous-applicant-all/<str:current_applicant_id>', views.viewPreviousApplicantAll , name="viewPreviousApplicantsAll"),
    path('add-justification/<str:application_id>', views.addJustification , name="addJustification"),
    path('add-seminar-review-report/<str:application_id>', views.addSeminarReviewReport , name="addSeminarReviewReport"),

]