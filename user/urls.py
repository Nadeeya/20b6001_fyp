from django.urls import path, include
from . import views
from main.views import home
from mod.views import adminHomePage
from recruiter.views import recruiterHome , changePassword

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('', home , name="home"),
    path('logout/', views.logoutUser ,name="logout"),
    path('profile-page', views.profilePage ,name="profilePage"),
    path('sign-up/', views.signup , name="signup"),
    path('applicant-registration/', views.registration , name='applicant_reg'),
    path('admin-home/', adminHomePage , name="admin-home"),
    path('recruiter-home/', recruiterHome , name="recruiterHome"),
    path('change-password/', changePassword , name="changePassword"),
    path('my-application/<str:pk>', views.myApplication , name="myApplication"),
    path('remove-profile-pic/<str:pk>', views.removeProfilePic , name="removeProfilePic"),
    path('view-submission-pdf/<str:pk>', views.downloadSubmission , name="downloadSubmission"),


]