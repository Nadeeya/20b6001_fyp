from django.urls import path, include
from . import views
from user.views import loginPage , logoutUser , profilePage , registration , jobApplications


urlpatterns = [
    path('', views.home, name="home"),
    

    #directories for ubd navigation bar:
    path('researchFacilities/', views.researchFacilities ,name="researchFacilities"),
    path('ubdLiving/', views.ubdLiving ,name="ubdLiving"),
    path('ubdBenefit/', views.ubdBenefit ,name="ubdBenefit"),
    path('ubdAbout/', views.ubdAbout ,name="ubdAbout"),

    #to connect to other web page from other apps:
    path('login/', loginPage, name="login"),
    path('logout/', logoutUser, name="logout"),
    path('profile-page/', profilePage , name="profilePage"),
    path('applicant-registration/', registration , name="applicant_reg"),
    path('job-applications/', jobApplications , name="jobApplications"),

    #view each job details
    path('jobDetails/<str:pk>/', views.jobDetails ,name="jobDetails"),
    path('jobForm/<str:pk>/', views.jobForm ,name="jobForm"),
    path('non-academic-job-form/<str:job_id>/', views.nonAcademicJobForm ,name="nonAcademicJobForm"),

    path('scopusVerification/<str:pk>/', views.scopusVerification ,name="scopusVerification"),
    path('scholarlyVerification/<str:pk>/', views.scholarlyVerification ,name="scholarlyVerification"),
    # use previous application:
    path('prev-application-option/<str:job_id>/', views.prevApplicationOption ,name="prevApplicationOption"),
    path('use-prev-application/<str:job_id>/', views.usePrevApplication ,name="usePrevApplication"),
    path('continue-draft/<str:job_id>/<str:draft_id>', views.continueDraft ,name="continueDraft"),


]