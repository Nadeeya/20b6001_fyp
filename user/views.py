from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User , Applicant
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from mod.models import Application , AcademicApplication , NonAcademicApplication
from django.http import HttpResponseRedirect , HttpResponse
from PIL import Image
from django.core.mail import send_mail , EmailMultiAlternatives
import io
from django.template.loader import get_template
from xhtml2pdf import pisa

# Create your views here.

def loginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email , password = password)

        if user is not None:
            login(request, user)

            message = "Successfully logged in"
            
            context = {'message':message}

            if user.is_superuser:
                return redirect('adminHome')
            
            if request.user.type == 'APPLICANT':   
                return redirect('home')
            
            if request.user.type == 'RECRUITER':
                if request.user.recruiter.change_password == False:
                    return redirect('changePassword')
                else:
                    return redirect('recruiterHome')
        else:
            messages.error(request, 'Email or Password does not exist')
    
        

    context = {}
    return render(request, 'user/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def profilePage(request):
    id = request.user.id
    user = User.objects.get(id=id)
    profile = Applicant.objects.get(user=user)
    NATIONALITIES_list = ['Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean', 'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran',  'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech', 'Danish', 'Djibouti', 'Dominican', 'Dutch', 'Dutchman', 'Dutchwoman', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz', 'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan', 'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'Netherlander', 'New Zealander', 'Ni-Vanuatu', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean', 'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese', 'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean']
    gender_list = ['Female', 'Male', 'Others']
    maritalStat_list = ['Single', 'Married', 'Others']
    context = {'user': user , 'profile':profile, 
               'nationalities': NATIONALITIES_list,
               'gender': gender_list,
               'maritalStat':maritalStat_list}
    

    if request.method == 'POST' and 'profileDetails' in request.POST:
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        # email = request.POST.get('email')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        pob = request.POST.get('pob')
        nationality = request.POST.get('nationality')
        citizenship = request.POST.get('citizenship')
        cod = request.POST.get('cod')
        maritalStat = request.POST.get('maritalStat')
        religion = request.POST.get('religion')
        address = request.POST.get('address')
        code = request.POST.get('code')
        phoneNo = request.POST.get('phoneNo')
        icPass = request.POST.get('icPass')
        highQual = request.POST.get('highQual')
        yearsExp = request.POST.get('yearsExp')

        user.first_name = fname
        user.last_name = lname
        user.save()
        profile.dob = dob
        profile.gender = gender
        profile.pob = pob
        profile.nationality = nationality
        profile.citizenship = citizenship
        profile.cod = cod
        profile.maritalStat = maritalStat
        profile.religion = religion
        profile.address = address
        profile.code = code
        profile.phoneNo = phoneNo
        profile.icPass = icPass
        profile.highQual = highQual
        profile.yearsExp = yearsExp
        profile.save()

        messages.success(request, 'Your profile details has been updated!')

        return render(request, 'user/profilePage.html' , context)
    
    if request.method == 'POST' and 'uploadProfilePic' in request.POST:
        pic = request.FILES
        pic = pic['p']

        try:
            Image.open(pic)
            profile.profilePic = pic
            profile.save()  
            messages.success(request, 'Your profile picture has been updated.')
        except:
            messages.warning(request, 'Sorry , your image is invalid')
        return render(request, 'user/profilePage.html', context)
    
    if request.method == 'POST' and 'changeProfilePic' in request.POST:
        pic = request.FILES
        pic = pic['p']

        try:
            Image.open(pic)
            profile.profilePic.delete(save=True)
            profile.profilePic = pic
            profile.save()  
            messages.success(request, 'Your profile picture has been updated.')
        except:
            messages.warning(request, 'Sorry , your image is invalid')
        return render(request, 'user/profilePage.html', context)



    return render(request, 'user/profilePage.html', context)

def signup(request):
    return render(request, 'user/signup.html')



def registration(request):
     NATIONALITIES_list = ['Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean', 'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran',  'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech', 'Danish', 'Djibouti', 'Dominican', 'Dutch', 'Dutchman', 'Dutchwoman', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz', 'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan', 'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'Netherlander', 'New Zealander', 'Ni-Vanuatu', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean', 'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese', 'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean']
     
     
     if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        pob = request.POST.get('pob')
        nationality = request.POST.get('nationality')
        citizenship = request.POST.get('citizenship')
        cod = request.POST.get('cod')
        maritalStat = request.POST.get('maritalStat')
        religion = request.POST.get('religion')
        address = request.POST.get('address')
        code = request.POST.get('code')
        phoneNo = request.POST.get('phoneNo')
        icPass = request.POST.get('icPass')
        
        

        check_user = User.objects.filter(email=email).first()

        if password != password1:
            messages.error(request, 'Password mismatch.')
            return redirect(request.META.get('HTTP_REFERER'))
        
        if check_user:
            messages.error(request, 'User Email already exists.')
            return redirect(request.META.get('HTTP_REFERER'))
        
        user = User.objects.create_user(username= email, email=  email, password=password, first_name = fname, last_name = lname , type = 'APPLICANT')
        user.save()

        applicant_profile = Applicant.objects.create(
            user=user,
            dob=dob,
            gender = gender,
            pob = pob,
            nationality=nationality,
            citizenship = citizenship,
            cod = cod,
            maritalStat = maritalStat,
            religion = religion,
            address = address,
            code = code,
            phoneNo = phoneNo,
            icPass = icPass,
        )
        applicant_profile.save()

        login(request, user)
        messages.success(request, 'Successfully registered.')

        # send email
        subject = 'Confirmation: Successful UBD Applicant Registration Complete'
        from_email = "ubdtesting70@gmail.com"
        to = email
        text_content = "Dear " + fname + ", We are pleased to inform you that your registration to our system has been successfull. You can now apply for the job openings through the UBD portal."
        html_content = "<h3>Dear " + fname + ", <h3> <p>We are pleased to inform you that your registration to our system has been successfull.<br> You can now apply for the job openings through the UBD portal.</p>"
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return redirect('home')
     
    
     context = {'nationalities': NATIONALITIES_list } 

     return render(request, 'user/signup.html', context)
         

def jobApplications(request):
    id = request.user.id
    user = User.objects.get(id=id)
    applications = Application.objects.filter(user=user)

    context = {'applications':applications}
    return render(request, 'user/jobApplications.html', context)

def myApplication(request, pk):
    applicant = Application.objects.get(id = pk)
    if applicant.application_type == 'Academic':
        academic = AcademicApplication.objects.get(application=applicant)
        context = {'academic':academic}
        return render(request, 'user/myApplication.html', context)
    elif applicant.application_type == 'Non-Academic':
        nonAcademic = NonAcademicApplication.objects.get(application=applicant)
        context = {'application':applicant, 'nonAcademic':nonAcademic}
        return render(request, 'user/myNonAcademicApplication.html', context)

    


    


def removeProfilePic(request, pk):
    applicant = Applicant.objects.get(user_id = pk)

    applicant.profilePic.delete(save=True)
    messages.success(request, 'Your profile picture has been successfully removed.')
    return redirect('profilePage')

def downloadSubmission(request , pk):
    applicant = Application.objects.get(id=pk)
    if applicant.application_type == 'Academic':
        academic = AcademicApplication.objects.get(application=applicant)
        context = {'applicant':applicant, 'academic':academic}
        template = get_template('user/myApplicationPdf.html')
        html = template.render(context)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    elif applicant.application_type == 'Non-Academic':
        nonAcademic = NonAcademicApplication.objects.get(application=applicant)
        context = {'nonAcademic':nonAcademic, 'application':applicant}
        template = get_template('user/myNonAcademicApplicationPDF.html')
        html = template.render(context)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)


    if pdf.err:
        return HttpResponse("Invalid PDF", status_code=400, content_type='text/plain')
    
    return HttpResponse(result.getvalue(), content_type='application/pdf')




         