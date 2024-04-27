from django.shortcuts import render, redirect
from django.contrib import messages
#from .models import Job
from mod.models import Job , Application , UserFile , Department , AcademicApplication , NonAcademicApplication
from user.models import User, Applicant
import os
from django.conf import settings
from datetime import datetime
from pybliometrics.scopus import AuthorRetrieval
from django.core.mail import send_mail , EmailMultiAlternatives
from django.http import HttpResponse
import shutil
from scholarly import scholarly
import json
from django.templatetags.static import static


# Create your views here.
def home(request):
    search = request.GET.get('search') if request.GET.get('search') != None else ''
    department = request.GET.get('department') if request.GET.get('department') != None else ''
    category = request.GET.get('category') if request.GET.get('category') != None else ''
    minReq = request.GET.get('minReq') if request.GET.get('minReq') != None else ''
    order = request.GET.get('uploadDate') if request.GET.get('uploadDate') != None else ''
    status = request.GET.get('jobStatus') if request.GET.get('jobStatus') != None else ''

    jobs = Job.objects.filter(name__icontains=search).filter(department__name__icontains=department).filter(department__category__icontains=category).filter(minReq__icontains=minReq).order_by('-dateClose', '-uploadDate')

    if order == 'latest':
        jobs = jobs.order_by('-uploadDate', '-dateClose')
    
    elif order == 'earliest':
        jobs = jobs.order_by('uploadDate' , '-dateClose')

    elif order == 'close_earliest':
        jobs = jobs.order_by('dateClose').filter(status='OPEN')
    
    elif order == 'close_latest':
        jobs = jobs.order_by('-dateClose').filter(status='OPEN')
    
    now =  datetime.now().date()

    elapsedTimeDict = {}
    for job in jobs:
        if now>job.dateClose:
            job.status = 'CLOSED'
            job.save()
        else:
            job.status = 'OPEN'
            job.save()
        
    if status == 'OPEN':
        jobs = jobs.filter(status='OPEN')
    elif status == 'CLOSED':
        jobs = jobs.filter(status='CLOSED')

    days = ''

    for job in jobs :
        elapsedTime = (now - job.uploadDate).days
        if elapsedTime == 0:
            days = 'Today'
        elif elapsedTime < 7:
            if elapsedTime == 1:
                days = 'A day ago'
            else:
                days = str(elapsedTime) + ' days ago'
        elif elapsedTime == 7:
            days = 'A week ago'
        elif elapsedTime > 7 and elapsedTime < 30:
            week = elapsedTime//7
            if week == 1:
                days = 'A week ago'
            else:
                days =  str(week) + ' weeks ago'
        elif elapsedTime == 30 | elapsedTime == 31:
            days = 'A month ago'
        elif elapsedTime > 31 and elapsedTime < 365:
            month = elapsedTime//30
            if month == 1:
                days = 'A month ago'
            else:
                days = str(month) + ' months ago'
        elif elapsedTime == 365:
            days = 'A year ago'
        elif elapsedTime > 365:
            years = elapsedTime//365
            if years == 1:
                days = 'A year ago'
            else:
                days = str(years) + ' years ago'

        id = job.id
        elapsedTimeDict[id] = days

    department_list= Department.objects.all()

    category_list = ['Academic' , 'Non-Academic' , 'Others']
    
    
    minReq_list = ["O'level",
                   "A'level",
                   'Diploma',
                   'Degree',
                   'Master',
                   'PHD']
    job_count = jobs.count()
    
    
    context = {'jobs':jobs, 'job_count':job_count , 'category':category_list , 'department':department_list ,'minReq':minReq_list , 'elapsedTime':elapsedTimeDict}
    
    
    if department:
        dep_intro = Department.objects.get(name=department)
        context = {'jobs':jobs, 'job_count':job_count , 'category':category_list , 'department':department_list ,'minReq':minReq_list , 'elapsedTime':elapsedTimeDict , 'dep_intro' :dep_intro}


    return render(request, 'main/mainPages/home.html', context)

# directories for ubd navigation bar:

def researchFacilities(request):
    return render(request, 'main/mainPages/researchFacilities.html')

def ubdLiving(request):
    return render(request, 'main/mainPages/ubdLiving.html')

def ubdBenefit(request):
    return render(request, 'main/mainPages/ubdBenefit.html')

def ubdAbout(request):
    return render(request, 'main/mainPages/ubdAbout.html')

# job details page:

def jobDetails(request, pk):
    job = Job.objects.get(id=pk)
    id = request.user.id

    # user id:
    try:
        draft = Application.objects.get(job=job,user_id =id,profile_id=id, applicant_progress='DRAFT')
        context = {'job':job, 'draft':draft}

    except:
        try:
            applied = Application.objects.get(job=job, user_id= id, profile_id=id)
            context = {'job':job , 'applied':applied}
        except:
            context = {'job':job}


    return render(request, 'main/mainPages/jobDetails.html', context)

def getScopusInfo(id):
    try: 
        ret = AuthorRetrieval(id)
        info = {
            'name' :ret.given_name,
            'surname' : ret.surname,
            'h_index' : ret.h_index,
            'link' : ret.self_link,
            'citation' : ret.citation_count,
            'document' : ret.document_count,
        }
    except:
        info = {}

    return info

def getScholarlyInfo(id):
    id = str(id)
    try:
        ret = scholarly.search_author_id(id)
        info = {
            'name' : ret['name'],
            'email' : ret['email_domain'],
            'interests' : ret['interests'],
            'link' : 'https://scholar.google.com/citations?user=' + id,
        }
    except:
        info = {}

    return info

def jobForm(request, pk):

    if not request.user.is_authenticated:
        messages.error(request, 'You are not logged in!')
        return redirect('login')
    
    job = Job.objects.get(id=pk)
    id = request.user.id
    user = User.objects.get(id=id)
    profile = Applicant.objects.get(user=user)

    NATIONALITIES_list = ['Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean', 'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran',  'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech', 'Danish', 'Djibouti', 'Dominican', 'Dutch', 'Dutchman', 'Dutchwoman', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz', 'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan', 'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'Netherlander', 'New Zealander', 'Ni-Vanuatu', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean', 'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese', 'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean']
    gender_list = ['Female', 'Male', 'Others']
    maritalStat_list = ['Single', 'Married', 'Others']
    period_of_notice = ['3 months', '6 months', '1 year']
    course_levels = ['Undergraduate', 'Postgraduate']
    language_levels = ['Fluent', 'Good', 'Fair', 'Low Proficiency']
    post_applied = ['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer']
    source = ['UBD website', 'Jobs.ac.uk', 'Pelita Brunei', 'Other']


    if profile.submission != 0:
        prev_application = Application.objects.filter(profile=profile).last()
        last_submission = prev_application.date_added
        context = {'n': range(13), 'job':job, 'user':user, 'profile':profile, 'nationalities':NATIONALITIES_list , 'gender':gender_list
               , 'maritalStat':maritalStat_list , 'last_submission':last_submission , 'period_of_notice':period_of_notice, 'course_levels':course_levels, 
               'language_levels':language_levels, 'post_applied':post_applied, 'source':source}

    else:
        context = {'n': range(13), 'job':job, 'user':user, 'profile':profile, 'nationalities':NATIONALITIES_list , 'gender':gender_list
               , 'maritalStat':maritalStat_list , 'period_of_notice':period_of_notice, 'course_levels':course_levels, 'language_levels':language_levels,
               'post_applied':post_applied, 'source':source}
    
    # submit the form
    if request.method == "POST" and 'submitForm' in request.POST:

        #FIRST PAGE
        email = request.POST.get('email')
        postApplied = request.POST.get('post_applied')
        prevApplication = request.POST.get('prevApplication')

        #date prev
        if prevApplication == 'Yes' :
            datePrev = request.POST.get('date_prev')

        else:
            datePrev  = 0000-00-00
        

        source = request.POST.get('source')
        fullname = request.POST.get('fullname')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        pob = request.POST.get('pob')
        cod = request.POST.get('cod')
        nationality = request.POST.get('nationality')
        citizenship = request.POST.get('citizenship')
        marital = request.POST.get('marital')
        religion = request.POST.get('religion')
        icPass = request.POST.get('ic_passport') 
        address = request.POST.get('address')
        code = request.POST.get('code')
        phoneNo = request.POST.get('phone')

        #present employment
        presentPost = request.POST.get('present_post')
        presentEmployer = request.POST.get('present_employer')
        currentDuties = request.POST.get('current_duties')
        currentPostAppt = request.POST.get('current_post_appointment')
        basicSalary = request.POST.get('basic_salary')
        otherEmolumentsAllowance = request.POST.get('other_emoluments_allowance')
        incomeTaxDeduction = request.POST.get('income_tax_deduction')
        periodOfNotice = request.POST.get('period_of_notice')
        
        #academic record
        academicRecord = {}

        academicName = request.POST.getlist('academic_name')
        academicInst = request.POST.getlist('institute')
        academicCountry = request.POST.getlist('academic_rec_country')
        academicDate = request.POST.getlist('date_award')
        academicGrade = request.POST.getlist('grade')

        for x in range(len(academicName)):
            academicRecord[x+1] = {
                'Academic_name' : academicName[x],
                'Institute' : academicInst[x],
                'Country' :  academicCountry[x],
                'Award_date' : academicDate[x],
                'Grade' : academicGrade[x],
            }

        #membership and fellowship
        membershipFellowship = request.POST.getlist('membership_fellowship')

        #employment record in higher education
        experienceHighEd = request.POST.get('exp_highEd')
        erhe = {}

        if experienceHighEd == 'Yes':
            academicPosition = request.POST.getlist('academic_position')
            prevInstitute = request.POST.getlist('prev_institute')
            erheCountry = request.POST.getlist('erhe_country')
            erheStart = request.POST.getlist('start_erhe')
            erheEnd = request.POST.getlist('end_erhe')

            for x in range(len(academicPosition)):
                erhe[x+1] = {
                    'Academic_position' : academicPosition[x],
                    'Previous_institute' : prevInstitute[x],
                    'Country' : erheCountry[x],
                    'Start_date' : erheStart[x],
                    'End_date' : erheEnd[x],
                }        

        #employment record in industry
        experienceInd = request.POST.get('exp_ind')
        eri ={}
        if experienceInd == 'Yes':
            industryPosition = request.POST.getlist('industry_position')
            prevIndustry = request.POST.getlist('prev_industry')
            eriCountry = request.POST.getlist('eri_country')
            eriStart = request.POST.getlist('start_eri')
            eriEnd = request.POST.getlist('end_eri')

            for x in range(len(industryPosition)):
                eri[x+1] = {
                    'Industry_position' :  industryPosition[x],
                    'Previous_industry' : prevIndustry[x],
                    'Country' : eriCountry[x],
                    'Start_date' : eriStart[x],
                    'End_date' : eriEnd[x],

            }
        #teaching supervision
        #courses
        courses = {}

        if request.POST.getlist('course')!=None:

            course = request.POST.getlist('course')
            level = request.POST.getlist('course_level')

            for x in range(len(course)):
                courses[x+1] = {
                    'Course' : course[x],
                    'Level' : level[x]
                }
        
        superVisionFile = request.FILES['list_supervision_file']
        areaInterest = request.POST.get('area_interest')
        publications = request.FILES['publications']
        scholarly_id = request.POST.get('scholarly_id')
        scopus_id = request.POST.get('scopus_id')

        # scholarly info

        scholarlyInfo = getScholarlyInfo(scholarly_id)
        scopusInfo = getScopusInfo(scopus_id)

        malay = request.POST.get('Malay')
        english = request.POST.get('English')
        arabic = request.POST.get('Arabic')

        #other languages:

        otherLanguages = {}

        if request.POST.getlist('language') is not None:

            language = request.POST.getlist('language')
            fluency = request.POST.getlist('fluency')

            for x in range(len(language)):
                otherLanguages[x+1] = {
                    'language' : language[x],
                    'fluency' : fluency[x]
                }
        else:
            otherLanguages[0] = 'No other languages'

        #FAMILY PARTICULARS
        noChildren = request.POST.get('no_children')
        if noChildren == '':
            children = 0
        else:
            noChildren = int(noChildren)
        #if applicant have children:
            if noChildren > 0 :        
                children = {}
                childrenName = request.POST.getlist('children_name')
                childrenDob = request.POST.getlist('children_dob')
                childrenGender = request.POST.getlist('children_gender')

                for x in range(noChildren):
                    children[x+1] = {
                        'name' : childrenName[x],
                        'dob' : childrenDob[x],
                        'gender' : childrenGender[x]
                    }
            else:
                children = 0

        #if applicant is married:
        if marital == 'Married':
            spouseName = request.POST.get('spouse_name')
            spouseOccupation = request.POST.get('spouse_occupation')
        else:
            #changing marital stat:
            changeMarital = request.POST.get('changeMarital')
            if changeMarital == 'Yes':
                marital = 'Married'
                spouseName = request.POST.get('spouse_name')
                spouseOccupation = request.POST.get('spouse_occupation')
            else:
                spouseName = 'no spouse'
                spouseOccupation = 'no spouse'

        family = {
            'Children' : children,
            'Spouse' : spouseName,
            'Spouse_occupation' : spouseOccupation
        }

        referees = {}

        #referees
        for x in range(1,4):
           referee_name = request.POST.get('referee_'+str(x)+'_name')
           referee_position = request.POST.get('referee_'+str(x)+'_position')
           referee_compInst = request.POST.get('referee_'+str(x)+'_compInst')
           referee_email = request.POST.get('referee_'+str(x)+'_email')
           referee_phone = request.POST.get('referee_'+str(x)+'_phone')
           referee_contact = request.POST.get('referee_'+str(x)+'_contact')

           referees[x] = {
               'name' : referee_name,
               'position' : referee_position,
               'company_institute' : referee_compInst,
               'email' : referee_email,
               'phone' : referee_phone, 
               'contactability' : referee_contact, 
           }

        icPassFile = request.FILES['passport_ic']
        coverLetter = request.FILES['cover_letter']
        researchStatement = request.FILES['research_statement']
        teachingStatement = request.FILES['teaching_statement']
        cv = request.FILES['CV']
        transcript = request.FILES['transcripts']
        other_docs = request.FILES['other_docs']

        #SAVING

        user.email = email
        user.save()
        profile.dob = dob
        profile.gender = gender
        profile.pob = pob
        profile.nationality = nationality
        profile.citizenship = citizenship
        profile.cod = cod
        profile.maritalStat = marital
        profile.religion = religion
        profile.address = address
        profile.code = code
        profile.phoneNo = phoneNo
        profile.icPass = icPass
        profile.submission = profile.submission + 1
        profile.save()

        applicant_status = 'PENDING'

        application  = Application.objects.create(
            user = user,
            job = job,
            profile = profile)
        
        #file saving

        file_name = "Supervision file"

        myfile = UserFile.objects.create(applicant = application ,f_name=file_name,myfiles=superVisionFile)
        myfile.save()

        publicationsFile = UserFile.objects.create(applicant = application, f_name="Publications", myfiles=publications)
        publicationsFile.save()

        icPassFile1 = UserFile.objects.create(applicant=application, f_name="IC Passport", myfiles=icPassFile)
        icPassFile1.save()
        coverLetterFile = UserFile.objects.create(applicant=application, f_name="Cover Letter", myfiles = coverLetter)
        coverLetterFile.save()
        researchStatementFile = UserFile.objects.create(applicant=application, f_name="Research Statement", myfiles = researchStatement)
        researchStatementFile.save()
        teachingStatementFile = UserFile.objects.create(applicant=application, f_name="Teaching Statement", myfiles = teachingStatement)
        teachingStatementFile.save()
        cvFile = UserFile.objects.create(applicant=application, f_name="CV", myfiles=cv)
        cvFile.save()
        transcriptFile = UserFile.objects.create(applicant=application, f_name="Transcript", myfiles=transcript)
        transcriptFile.save()
        other_docsFile = UserFile.objects.create(applicant=application, f_name="Other Document", myfiles=other_docs)
        other_docsFile.save()
        
        
        presentEmployement = {
            'Present_post' : presentPost,
            'Present_Employer' : presentEmployer,
            'Current_duties' : currentDuties,
            'Current_post_appointment' : currentPostAppt,
            'Basic_salary' : basicSalary,
            'Other_Emoluments_Allowance' : otherEmolumentsAllowance,
            'Income_Tax_Deduction' : incomeTaxDeduction,
            'Period_of_Notice' : periodOfNotice
        }


        teachingSupervision = {
            'Supervision_file_name' : myfile.f_name,
            'Supervision_file' : myfile.myfiles.url,
            'Area_of_interest' :areaInterest,
            'Publications_name' : publicationsFile.f_name,
            'Publications_file' : publicationsFile.myfiles.url,
            'Scholarly_id' : scholarly_id,
            'Scopus_id' : scopus_id,
        }

        languages = {
            'Malay': malay,
            'English' : english,
            'Arabic' : arabic,
        }

        applicant_files = UserFile.objects.filter(applicant_id = application.id)
        
        documents = {}
        key = 1

        for files in applicant_files:
            documents[key] = {
                'name' : files.f_name,
                'file' : files.myfiles.url
            }
            key += 1 
        

        application_cont = Application.objects.get(id = application.id)

        application_cont.applicant_status = applicant_status
        application_cont.prevApplication = prevApplication

        if prevApplication == 'Yes' :
            application_cont.datePrev = datePrev

        application_cont.source = source
        application_cont.fullname = fullname
        application_cont.presentEmployment = presentEmployement
        application_cont.academicRec = academicRecord
        application_cont.documents = documents
        # application_cont.postApplied = postApplied
        application_cont.application_type = 'Academic'

        
        application_cont.save()

        academicApplication = AcademicApplication.objects.create(
            application = application_cont,
            postApplied = postApplied,
            membershipFellowship = membershipFellowship,
            experienceHighEd = experienceHighEd,
            employmentRecHighEd = erhe,
            experienceInd = experienceInd,
            employmentRecInd = eri,
            coursesOffering = courses,
            teachingSupervision = teachingSupervision,
            scholarlyInfo = scholarlyInfo,
            scopusInfo = scopusInfo,
            languages = languages,
            otherLanguages = otherLanguages,
            family = family,
            referees = referees
        )

        academicApplication.save()
       
        #SEND EMAIL:
        subject = 'Confirmation: Job Application Submission for ' + job.name
        from_email = "ubdtesting70@gmail.com"
        to = user.email
        text_content = 'Dear ' + fullname + ', We are pleased to inform you that your job application has been successfully received and processed. We appreciate the time and effort you dedicated to completing the application process.'
        html_content = '<h3>Dear ' + fullname + ',</h3> <p>We are pleased to inform you that your job application has been successfully received and processed.<br> We appreciate the time and effort you dedicated to completing the application process.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        messages.success(request, 'Your application form has been submitted!')


        return redirect('home')
    

    # save as draft
    if request.method == 'POST' and 'addDraft' in request.POST:
        #FIRST PAGE
        email = request.POST.get('email')
        postApplied = request.POST.get('post_applied')
        prevApplication = request.POST.get('prevApplication')

        #date prev
        if prevApplication == 'Yes' :
            datePrev = request.POST.get('date_prev')

        else:
            datePrev  = 0000-00-00
        

        source = request.POST.get('source')
        fullname = request.POST.get('fullname')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        pob = request.POST.get('pob')
        cod = request.POST.get('cod')
        nationality = request.POST.get('nationality')
        citizenship = request.POST.get('citizenship')
        marital = request.POST.get('marital')
        religion = request.POST.get('religion')
        icPass = request.POST.get('ic_passport') 
        address = request.POST.get('address')
        code = request.POST.get('code')
        phoneNo = request.POST.get('phone')

        #present employment
        presentPost = request.POST.get('present_post')
        presentEmployer = request.POST.get('present_employer')
        currentDuties = request.POST.get('current_duties')
        currentPostAppt = request.POST.get('current_post_appointment')
        basicSalary = request.POST.get('basic_salary')
        otherEmolumentsAllowance = request.POST.get('other_emoluments_allowance')
        incomeTaxDeduction = request.POST.get('income_tax_deduction')
        periodOfNotice = request.POST.get('period_of_notice')
        
        #academic record
        academicRecord = {}
        academicName = request.POST.getlist('academic_name')
        academicInst = request.POST.getlist('institute')
        academicCountry = request.POST.getlist('academic_rec_country')
        academicDate = request.POST.getlist('date_award')
        academicGrade = request.POST.getlist('grade')

        if academicName != [] and academicName != None and academicName[0] !='':
            for x in range(len(academicName)):
                academicRecord[x+1] = {
                    'Academic_name' : academicName[x],
                    'Institute' : academicInst[x],
                    'Country' :  academicCountry[x],
                    'Award_date' : academicDate[x],
                    'Grade' : academicGrade[x],
                }

        #membership and fellowship
        membershipFellowship = request.POST.getlist('membership_fellowship')

        #employment record in higher education
        experienceHighEd = request.POST.get('exp_highEd')
        erhe = {}

        if experienceHighEd == 'Yes':
            academicPosition = request.POST.getlist('academic_position')
            prevInstitute = request.POST.getlist('prev_institute')
            erheCountry = request.POST.getlist('erhe_country')
            erheStart = request.POST.getlist('start_erhe')
            erheEnd = request.POST.getlist('end_erhe')

            for x in range(len(academicPosition)):
                erhe[x+1] = {
                    'Academic_position' : academicPosition[x],
                    'Previous_institute' : prevInstitute[x],
                    'Country' : erheCountry[x],
                    'Start_date' : erheStart[x],
                    'End_date' : erheEnd[x],
                }        

        #employment record in industry
        experienceInd = request.POST.get('exp_ind')
        eri ={}
        if experienceInd == 'Yes':
            industryPosition = request.POST.getlist('industry_position')
            prevIndustry = request.POST.getlist('prev_industry')
            eriCountry = request.POST.getlist('eri_country')
            eriStart = request.POST.getlist('start_eri')
            eriEnd = request.POST.getlist('end_eri')

            for x in range(len(industryPosition)):
                eri[x+1] = {
                    'Industry_position' :  industryPosition[x],
                    'Previous_industry' : prevIndustry[x],
                    'Country' : eriCountry[x],
                    'Start_date' : eriStart[x],
                    'End_date' : eriEnd[x],

            }
        #teaching supervision
        #courses
        courses = {}
        course = request.POST.getlist('course')
        level = request.POST.getlist('course_level')

        if course != None and course!= []  and course[0]!='':
            for x in range(len(course)):
                courses[x+1] = {
                    'Course' : course[x],
                    'Level' : level[x],
                }
        
        # superVisionFile = request.FILES['list_supervision_file']
        areaInterest = request.POST.get('area_interest')
        # publications = request.FILES['publications']
        scholarly_id = request.POST.get('scholarly_id')
        scopus_id = request.POST.get('scopus_id')

        malay = request.POST.get('Malay')
        english = request.POST.get('English')
        arabic = request.POST.get('Arabic')

        #other languages:

        otherLanguages = {}

        if request.POST.getlist('language') is not None:

            language = request.POST.getlist('language')
            fluency = request.POST.getlist('fluency')

            for x in range(len(language)):
                otherLanguages[x+1] = {
                    'language' : language[x],
                    'fluency' : fluency[x]
                }
        else:
            otherLanguages[0] = 'No other languages'

        #FAMILY PARTICULARS
        noChildren = request.POST.get('no_children')
        if noChildren == '':
            children = 0
        else:
            noChildren = int(noChildren)
        #if applicant have children:
            if noChildren > 0 :        
                children = {}
                childrenName = request.POST.getlist('children_name')
                childrenDob = request.POST.getlist('children_dob')
                childrenGender = request.POST.getlist('children_gender')

                for x in range(noChildren):
                    children[x+1] = {
                        'name' : childrenName[x],
                        'dob' : childrenDob[x],
                        'gender' : childrenGender[x]
                    }
            else:
                children = 0

        #if applicant is married:
        if marital == 'Married':
            spouseName = request.POST.get('spouse_name')
            spouseOccupation = request.POST.get('spouse_occupation')
        else:
            #changing marital stat:
            changeMarital = request.POST.get('changeMarital')
            if changeMarital == 'Yes':
                marital = 'Married'
                spouseName = request.POST.get('spouse_name')
                spouseOccupation = request.POST.get('spouse_occupation')
            else:
                spouseName = 'no spouse'
                spouseOccupation = 'no spouse'

        family = {
            'Children' : children,
            'Spouse' : spouseName,
            'Spouse_occupation' : spouseOccupation
        }

        referees = {}

        #referees
        for x in range(1,4):
           referee_name = request.POST.get('referee_'+str(x)+'_name')
           referee_position = request.POST.get('referee_'+str(x)+'_position')
           referee_compInst = request.POST.get('referee_'+str(x)+'_compInst')
           referee_email = request.POST.get('referee_'+str(x)+'_email')
           referee_phone = request.POST.get('referee_'+str(x)+'_phone')
           referee_contact = request.POST.get('referee_'+str(x)+'_contact')

           referees[x] = {
               'name' : referee_name,
               'position' : referee_position,
               'company_institute' : referee_compInst,
               'email' : referee_email,
               'phone' : referee_phone, 
               'contactability' : referee_contact, 
           }

        #SAVING

        user.email = email
        user.save()
        profile.dob = dob
        profile.gender = gender
        profile.pob = pob
        profile.nationality = nationality
        profile.citizenship = citizenship
        profile.cod = cod
        profile.maritalStat = marital
        profile.religion = religion
        profile.address = address
        profile.code = code
        profile.phoneNo = phoneNo
        profile.icPass = icPass
        profile.save()

        applicant_status = 'PENDING'

        application  = Application.objects.create(
            user = user,
            job = job,
            profile = profile,
            applicant_progress = 'DRAFT')
        
        # file saving
        # file_name = "Supervision file"

        # myfile = UserFile.objects.create(applicant = application ,f_name=file_name,myfiles=superVisionFile)
        # myfile.save()

        presentEmployement = {
            'Present_post' : presentPost,
            'Present_Employer' : presentEmployer,
            'Current_duties' : currentDuties,
            'Current_post_appointment' : currentPostAppt,
            'Basic_salary' : basicSalary,
            'Other_Emoluments_Allowance' : otherEmolumentsAllowance,
            'Income_Tax_Deduction' : incomeTaxDeduction,
            'Period_of_Notice' : periodOfNotice
        }


        teachingSupervision = {
            # 'Supervision_file_name' : myfile.f_name,
            # 'Supervision_file' : myfile.myfiles.url,
            'Area_of_interest' :areaInterest,
            # 'Publications_name' : publicationsFile.f_name,
            # 'Publications_file' : publicationsFile.myfiles.url,
            'Scholarly_id' : scholarly_id,
            'Scopus_id' : scopus_id,
        }

        languages = {
            'Malay': malay,
            'English' : english,
            'Arabic' : arabic,
        }

        application_cont = Application.objects.get(id = application.id)

        application_cont.applicant_status = applicant_status
        application_cont.prevApplication = prevApplication

        if prevApplication == 'Yes' :
            application_cont.datePrev = datePrev

        application_cont.source = source
        application_cont.fullname = fullname
        application_cont.presentEmployment = presentEmployement
        application_cont.academicRec = academicRecord
        # application_cont.documents = documents
        # application_cont.postApplied = postApplied
        application_cont.application_type = 'Academic'
        application_cont.applicant_progress = 'DRAFT'

        application_cont.save()

        academicApplication = AcademicApplication.objects.create(
            application = application_cont,
            postApplied = postApplied,
            membershipFellowship = membershipFellowship,
            experienceHighEd = experienceHighEd,
            employmentRecHighEd = erhe,
            experienceInd = experienceInd,
            employmentRecInd = eri,
            coursesOffering = courses,
            teachingSupervision = teachingSupervision,
            # scholarlyInfo = scholarlyInfo,
            # scopusInfo = scopusInfo,
            languages = languages,
            otherLanguages = otherLanguages,
            family = family,
            referees = referees
        )

        academicApplication.save()




        messages.success(request, 'Your application form has been saved as draft!')
        return redirect('home')

    return render(request, 'main/mainPages/jobForm.html', context)

def scopusVerification(request, pk):
    try: 
        ret = AuthorRetrieval(pk)
        author = {
            'name' :ret.given_name,
            'surname' : ret.surname,
            'h_index' : ret.h_index,
            'link' : ret.self_link,
            'citation' : ret.citation_count,
            'document' : ret.document_count,
        }
        
        context = {'author':author}
    except:
        context = {'message':'We could not get your scopus profile. Please try again'}
    return render(request, 'main/mainPages/scopusVerification.html', context)

def scholarlyVerification(request, pk):
    id = str(pk)
    try:
        ret = scholarly.search_author_id(id)
        author = {
            'name' : ret['name'],
            'email' : ret['email_domain'],
            'interests' : ret['interests'],
            'link' : 'https://scholar.google.com/citations?user=' + id,
        }
        context= {'author':author}
    except:
        context = {'message':'We could not get your google scholar profile. Please try again'}
    
    return render(request, 'main/mainPages/scholarlyVerification.html', context)


def prevApplicationOption(request, job_id):
    context = {'job_id':job_id}
    return render(request, 'main/mainPages/modal-usePrevApp.html' , context)

def usePrevApplication(request, job_id):
    applicant_id = request.user.id
    job = Job.objects.get(id = job_id)
    profile = Applicant.objects.get(user_id=applicant_id)
    user = User.objects.get(id=applicant_id)
    prev_application = Application.objects.filter(profile_id=applicant_id).exclude(applicant_progress='DRAFT').filter(application_type='Academic').last()
    prev_academic = AcademicApplication.objects.get(application = prev_application)

    last_submission = prev_application.date_added

    NATIONALITIES_list = ['Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean', 'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran',  'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech', 'Danish', 'Djibouti', 'Dominican', 'Dutch', 'Dutchman', 'Dutchwoman', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz', 'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan', 'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'Netherlander', 'New Zealander', 'Ni-Vanuatu', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean', 'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese', 'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean']
    gender_list = ['Female', 'Male', 'Others']
    maritalStat_list = ['Single', 'Married', 'Others']
    period_of_notice = ['3 months', '6 months', '1 year']
    course_levels = ['Undergraduate', 'Postgraduate']
    language_levels = ['Fluent', 'Good', 'Fair', 'Low Proficiency']
    post_applied = ['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer']
    source = ['UBD website', 'Jobs.ac.uk', 'Pelita Brunei', 'Other']


    if request.method == 'POST' and 'submitForm' in request.POST:
        # FIRST PAGE
        postApplied = request.POST.get('post_applied')
        source = request.POST.get('source')

        # PERSONAL
        fullname = request.POST.get('fullname')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        pob = request.POST.get('pob')
        cod = request.POST.get('cod')
        nationality = request.POST.get('nationality')
        citizenship = request.POST.get('citizenship')
        marital = request.POST.get('marital')
        religion = request.POST.get('religion')
        icPass = request.POST.get('ic_passport') 
        address = request.POST.get('address')
        code = request.POST.get('code')
        phoneNo = request.POST.get('phone')

        profile.dob = dob
        profile.gender = gender
        profile.pob = pob
        profile.nationality = nationality
        profile.citizenship = citizenship
        profile.cod = cod
        profile.maritalStat = marital
        profile.religion = religion
        profile.address = address
        profile.code = code
        profile.phoneNo = phoneNo
        profile.icPass = icPass
        profile.submission = profile.submission + 1
        profile.save()

        applicant_status = 'PENDING'

        application  = Application.objects.create(
            user = user,
            job = job,
            profile = profile)

        # PRESENT EMPLOYMENT
        presentPost = request.POST.get('present_post')
        presentEmployer = request.POST.get('present_employer')
        currentDuties = request.POST.get('current_duties')
        currentPostAppt = request.POST.get('current_post_appointment')
        basicSalary = request.POST.get('basic_salary')
        otherEmolumentsAllowance = request.POST.get('other_emoluments_allowance')
        incomeTaxDeduction = request.POST.get('income_tax_deduction')
        periodOfNotice = request.POST.get('period_of_notice')

        # ACADEMIC RECORD
        academicRecord = {}

        academicName = request.POST.getlist('academic_name')
        academicInst = request.POST.getlist('institute')
        academicCountry = request.POST.getlist('academic_rec_country')
        academicDate = request.POST.getlist('date_award')
        academicGrade = request.POST.getlist('grade')

        for x in range(len(academicName)):
            academicRecord[x+1] = {
                'Academic_name' : academicName[x],
                'Institute' : academicInst[x],
                'Country' :  academicCountry[x],
                'Award_date' : academicDate[x],
                'Grade' : academicGrade[x],
            }

        # MEMBERSHIP AND FELLOWSHIP
        
        membershipFellowship = request.POST.getlist('membership_fellowship')

        #employment record in higher education
        experienceHighEd = request.POST.get('exp_highEd')
        erhe = {}

        if experienceHighEd == 'Yes':
            academicPosition = request.POST.getlist('academic_position')
            prevInstitute = request.POST.getlist('prev_institute')
            erheCountry = request.POST.getlist('erhe_country')
            erheStart = request.POST.getlist('start_erhe')
            erheEnd = request.POST.getlist('end_erhe')

            for x in range(len(academicPosition)):
                erhe[x+1] = {
                    'Academic_position' : academicPosition[x],
                    'Previous_institute' : prevInstitute[x],
                    'Country' : erheCountry[x],
                    'Start_date' : erheStart[x],
                    'End_date' : erheEnd[x],
                }        

        #employment record in industry
        experienceInd = request.POST.get('exp_ind')
        eri ={}
        if experienceInd == 'Yes':
            industryPosition = request.POST.getlist('industry_position')
            prevIndustry = request.POST.getlist('prev_industry')
            eriCountry = request.POST.getlist('eri_country')
            eriStart = request.POST.getlist('start_eri')
            eriEnd = request.POST.getlist('end_eri')

            for x in range(len(industryPosition)):
                eri[x+1] = {
                    'Industry_position' :  industryPosition[x],
                    'Previous_industry' : prevIndustry[x],
                    'Country' : eriCountry[x],
                    'Start_date' : eriStart[x],
                    'End_date' : eriEnd[x],

            }
                
        # TEACHING SUPERVISION
        courses = {}

        if request.POST.getlist('course')!=None:

            course = request.POST.getlist('course')
            level = request.POST.getlist('course_level')

            for x in range(len(course)):
                courses[x+1] = {
                    'Course' : course[x],
                    'Level' : level[x]
                }

        # copy file function:
        def copy_file(file_url, file_name):
            source_path = str(os.path.join(settings.BASE_DIR) + str(file_url)).replace('\\','/').replace('%20', ' ')
            fullname = str(user.first_name) + '_'+str(user.last_name)
            new_file_path = os.path.join(settings.MEDIA_ROOT, 'applicants/' + str(job.name) +'/' + fullname + '/')
            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
            file_path = shutil.copy2(source_path, new_file_path)
            f_name = os.path.split(file_path)[1]
            path = "applicants/{0}/{1}/{2}".format(job.name ,fullname, f_name)
            # save to model database
            myfile = UserFile.objects.create(applicant=application, f_name=file_name, myfiles=path)
            return myfile


        documents = {}
        if 'change_list_supervision_file' in request.FILES:
            superVisionFile = request.FILES['change_list_supervision_file']
            file_name = 'List of supervision'
            myfile = UserFile.objects.create(applicant = application , f_name=file_name, myfiles=superVisionFile)
            myfile.save()
            documents[1] = {
                'name' : myfile.f_name,
                'file' : myfile.myfiles.url
            }

        else:
            file_name = 'Supervision file'
            path_url = str(prev_academic.teachingSupervision["Supervision_file"])
            copied_file = copy_file(path_url , file_name)
            
            documents[1] = {
                'name' : file_name,
                'file' : copied_file.myfiles.url
            }

           

        areaInterest = request.POST.get('area_interest')
        # publications = request.FILES['publications']
        

        if 'change_publications' in request.FILES:
            publications = request.FILES['change_publications']
            file_name = 'Publications'
            myfile = UserFile.objects.create(applicant = application ,f_name=file_name,myfiles=publications)
            myfile.save()
            documents[2] = {
                'name' :myfile.f_name,
                'file' : myfile.myfiles.url
            }


        else:
            publications_url = prev_academic.teachingSupervision["Publications_file"]
            publications_name = 'Publications'
            copied_file = copy_file(publications_url, publications_name)
            
            documents[2] = {
                'name' : publications_name,
                'file' : copied_file.myfiles.url
            }
            
        scholarly_id = request.POST.get('scholarly_id')
        scopus_id = request.POST.get('scopus_id')

        scholarlyInfo = getScholarlyInfo(scholarly_id)
        scopusInfo = getScopusInfo(scopus_id)

        # LANGUAGES

        malay = request.POST.get('Malay')
        english = request.POST.get('English')
        arabic = request.POST.get('Arabic')

        #other languages:

        otherLanguages = {}

        if request.POST.getlist('language') is not None:

            language = request.POST.getlist('language')
            fluency = request.POST.getlist('fluency')

            for x in range(len(language)):
                otherLanguages[x+1] = {
                    'language' : language[x],
                    'fluency' : fluency[x]
                }
        else:
            otherLanguages[0] = 'No other languages'

        # FAMILY PARTICULARS
        noChildren = request.POST.get('no_children')
        if noChildren == '':
            children = 0
        else:
            noChildren = int(noChildren)
        #if applicant have children:
            if noChildren > 0 :        
                children = {}
                childrenName = request.POST.getlist('children_name')
                childrenDob = request.POST.getlist('children_dob')
                childrenGender = request.POST.getlist('children_gender')

                for x in range(noChildren):
                    children[x+1] = {
                        'name' : childrenName[x],
                        'dob' : childrenDob[x],
                        'gender' : childrenGender[x]
                    }
            else:
                children = 0
        
        #if applicant is married:
        if marital == 'Married':
            spouseName = request.POST.get('spouse_name')
            spouseOccupation = request.POST.get('spouse_occupation')
        else:
            #changing marital stat:
            changeMarital = request.POST.get('changeMarital')
            if changeMarital == 'Yes':
                marital = 'Married'
                spouseName = request.POST.get('spouse_name')
                spouseOccupation = request.POST.get('spouse_occupation')
            else:
                spouseName = 'no spouse'
                spouseOccupation = 'no spouse'

        family = {
            'Children' : children,
            'Spouse' : spouseName,
            'Spouse_occupation' : spouseOccupation
        }

        # REFEREES
        referees = {}
        for x in range(1,4):
           referee_name = request.POST.get('referee_'+str(x)+'_name')
           referee_position = request.POST.get('referee_'+str(x)+'_position')
           referee_compInst = request.POST.get('referee_'+str(x)+'_compInst')
           referee_email = request.POST.get('referee_'+str(x)+'_email')
           referee_phone = request.POST.get('referee_'+str(x)+'_phone')
           referee_contact = request.POST.get('referee_'+str(x)+'_contact')

           referees[x] = {
               'name' : referee_name,
               'position' : referee_position,
               'company_institute' : referee_compInst,
               'email' : referee_email,
               'phone' : referee_phone, 
               'contactability' : referee_contact, 
           }

        #   OTHER DOCUMENTS
        # passport or ic
        if 'change_passport_ic' in request.FILES:
            passport_ic = request.FILES['change_passport_ic']
            file_name = 'Passport / IC'
            file = UserFile.objects.create(applicant = application, f_name =file_name , myfiles = passport_ic)
            file.save()
            documents[3] = {
                'name' : file_name,
                'file' : file.myfiles.url
            }

        else:
            passport_ic_url = prev_application.documents['3']['file']
            passport_ic_name = 'Passport / IC'
            documents[3] = {
                'name' : passport_ic_name,
                'file' : passport_ic_url
            }

        # cover letter
        if 'change_cover_letter' in request.FILES:
            file = request.FILES['change_cover_letter']
            file_name = 'Cover letter'
            file = UserFile.objects.create(applicant = application, f_name =file_name , myfiles = file)
            file.save()
            documents[4] = {
                'name' : file_name,
                'file' : file.myfiles.url
            }

        else:
            url = prev_application.documents['4']['file']
            name = 'Cover Letter'
            copied_file = copy_file(url, name)
            documents[4] = {
                'name' : name,
                'file' : copied_file.myfiles.url
            }
        # Research Statement
        if 'change_research_statement' in request.FILES:
            file = request.FILES['change_research_statement']
            file_name = 'Research Statement'
            file = UserFile.objects.create(applicant = application, f_name =file_name , myfiles = file)
            file.save()
            documents[5] = {
                'name' : file_name,
                'file' : file.myfiles.url
            }

        else:
            url = prev_application.documents['5']['file']
            name = 'Research Statement'
            copied_file = copy_file(url, name)
            documents[5] = {
                'name' : name,
                'file' : copied_file.myfiles.url
            }

        # Teaching Statement
        if 'change_teaching_statement' in request.FILES:
            file = request.FILES['change_teaching_statement']
            file_name = 'Teaching Statement'
            file = UserFile.objects.create(applicant = application, f_name =file_name , myfiles = file)
            file.save()
            documents[6] = {
                'name' : file_name,
                'file' : file.myfiles.url
            }

        else:
            url = prev_application.documents['6']['file']
            name = 'Teaching Statement'
            copied_file = copy_file(url, name)
            documents[6] = {
                'name' : name,
                'file' : copied_file.myfiles.url
            }
        
        # CV
        if 'change_cv' in request.FILES:
            file = request.FILES['change_cv']
            file_name = 'Curriculum Vitae'
            file = UserFile.objects.create(applicant = application, f_name =file_name , myfiles = file)
            file.save()
            documents[7] = {
                'name' : file_name,
                'file' : file.myfiles.url
            }

        else:
            url = prev_application.documents['7']['file']
            name = 'Curriculum Vitae'
            copied_file = copy_file(url, name)
            documents[7] = {
                'name' : name,
                'file' : copied_file.myfiles.url
            }
        # transcript
        if 'change_transcripts' in request.FILES:
            file = request.FILES['change_transcripts']
            file_name = 'Education Transcripts'
            file = UserFile.objects.create(applicant = application, f_name =file_name , myfiles = file)
            file.save()
            documents[8] = {
                'name' : file_name,
                'file' : file.myfiles.url
            }

        else:
            url = prev_application.documents['8']['file']
            name = 'Education Transcripts'
            copied_file = copy_file(url, name)
            documents[8] = {
                'name' : name,
                'file' : copied_file.myfiles.url
            }

        # Other documents
        if 'change_other_docs' in request.FILES:
            file = request.FILES['change_other_docs']
            file_name = 'Other Documents'
            file = UserFile.objects.create(applicant = application, f_name =file_name , myfiles = file)
            file.save()
            documents[9] = {
                'name' : file_name,
                'file' : file.myfiles.url
            }

        else:
            url = prev_application.documents['9']['file']
            name = 'Other Documents'
            copied_file = copy_file(url, name)
            documents[9] = {
                'name' : name,
                'file' : copied_file.myfiles.url
            }
            

        presentEmployement = {
            'Present_post' : presentPost,
            'Present_Employer' : presentEmployer,
            'Current_duties' : currentDuties,
            'Current_post_appointment' : currentPostAppt,
            'Basic_salary' : basicSalary,
            'Other_Emoluments_Allowance' : otherEmolumentsAllowance,
            'Income_Tax_Deduction' : incomeTaxDeduction,
            'Period_of_Notice' : periodOfNotice
        }


        teachingSupervision = {
            'Supervision_file_name' : documents[1]['name'],
            'Supervision_file' : documents[1]['file'],
            'Area_of_interest' :areaInterest,
            'Publications_name' : documents[2]['name'],
            'Publications_file' : documents[2]['file'],
            'Scholarly_id' : scholarly_id,
            'Scopus_id' : scopus_id,
        }

        languages = {
            'Malay': malay,
            'English' : english,
            'Arabic' : arabic,
        }

        application_cont = Application.objects.get(id = application.id)

        application_cont.applicant_status = applicant_status
        application_cont.prevApplication = 'Yes'

        application_cont.datePrev = last_submission

        application_cont.source = source
        application_cont.fullname = fullname
        application_cont.presentEmployment = presentEmployement
        application_cont.academicRec = academicRecord
        application_cont.documents = documents
        # application_cont.postApplied = postApplied
        application_cont.application_type = 'Academic'

        
        application_cont.save()

        academicApplication = AcademicApplication.objects.create(
            application = application_cont,
            postApplied = postApplied,
            membershipFellowship = membershipFellowship,
            experienceHighEd = experienceHighEd,
            employmentRecHighEd = erhe,
            experienceInd = experienceInd,
            employmentRecInd = eri,
            coursesOffering = courses,
            teachingSupervision = teachingSupervision,
            scholarlyInfo = scholarlyInfo,
            scopusInfo = scopusInfo,
            languages = languages,
            otherLanguages = otherLanguages,
            family = family,
            referees = referees
        )

        academicApplication.save()

        

        #SEND EMAIL:
        subject = 'Confirmation: Job Application Submission for ' + job.name
        from_email = "ubdtesting70@gmail.com"
        to = user.email
        text_content = 'Dear ' + fullname + ', We are pleased to inform you that your job application has been successfully received and processed. We appreciate the time and effort you dedicated to completing the application process.'
        html_content = '<h3>Dear ' + fullname + ',</h3> <p>We are pleased to inform you that your job application has been successfully received and processed.<br> We appreciate the time and effort you dedicated to completing the application process.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        messages.success(request, 'Your application form has been submitted!')
        return redirect('home')



    context = {'n': range(13),'last_submission':last_submission,'prev_application':prev_application, 'nationalities':NATIONALITIES_list , 
               'maritalStat' :maritalStat_list , 'gender':gender_list, 'profile':profile, 'job':job, 
               'period_of_notice' : period_of_notice, 'course_levels':course_levels, 'language_levels':language_levels, 'post_applied':post_applied, 'source':source , 'no_draft':'no_draft',
               'prev_academic':prev_academic} 

    return render(request, 'main/mainPages/jobForm.html' , context)

def continueDraft(request, job_id , draft_id):
    applicant_id = request.user.id
    job = Job.objects.get(id = job_id)
    profile = Applicant.objects.get(user_id=applicant_id)
    user = User.objects.get(id=applicant_id)
    application = Application.objects.get(id=draft_id)
    last_submission = application.date_added
    academicApplication = AcademicApplication.objects.get(application=application)

    NATIONALITIES_list = ['Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean', 'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran',  'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech', 'Danish', 'Djibouti', 'Dominican', 'Dutch', 'Dutchman', 'Dutchwoman', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz', 'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan', 'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'Netherlander', 'New Zealander', 'Ni-Vanuatu', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean', 'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese', 'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean']
    gender_list = ['Female', 'Male', 'Others']
    maritalStat_list = ['Single', 'Married', 'Others']
    period_of_notice = ['3 months', '6 months', '1 year']
    course_levels = ['Undergraduate', 'Postgraduate']
    language_levels = ['Fluent', 'Good', 'Fair', 'Low Proficiency']
    post_applied = ['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer']
    source = ['UBD website', 'Jobs.ac.uk', 'Pelita Brunei', 'Other']

    context = {'n': range(13),'last_submission':last_submission,'prev_application':application, 'nationalities':NATIONALITIES_list , 
               'maritalStat' :maritalStat_list , 'gender':gender_list, 'profile':profile, 'job':job, 'prev_academic':academicApplication , 
               'period_of_notice' : period_of_notice, 'course_levels':course_levels, 'language_levels':language_levels, 'post_applied':post_applied, 'source':source}
    
    if request.method == "POST" and 'submitForm' in request.POST:

        #FIRST PAGE
        email = request.POST.get('email')
        postApplied = request.POST.get('post_applied')
        prevApplication = request.POST.get('prevApplication')

        #date prev
        if prevApplication == 'Yes' :
            datePrev = request.POST.get('date_prev')

        else:
            datePrev  = 0000-00-00
        

        source = request.POST.get('source')
        fullname = request.POST.get('fullname')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        pob = request.POST.get('pob')
        cod = request.POST.get('cod')
        nationality = request.POST.get('nationality')
        citizenship = request.POST.get('citizenship')
        marital = request.POST.get('marital')
        religion = request.POST.get('religion')
        icPass = request.POST.get('ic_passport') 
        address = request.POST.get('address')
        code = request.POST.get('code')
        phoneNo = request.POST.get('phone')

        #present employment
        presentPost = request.POST.get('present_post')
        presentEmployer = request.POST.get('present_employer')
        currentDuties = request.POST.get('current_duties')
        currentPostAppt = request.POST.get('current_post_appointment')
        basicSalary = request.POST.get('basic_salary')
        otherEmolumentsAllowance = request.POST.get('other_emoluments_allowance')
        incomeTaxDeduction = request.POST.get('income_tax_deduction')
        periodOfNotice = request.POST.get('period_of_notice')
        
        #academic record
        academicRecord = {}

        academicName = request.POST.getlist('academic_name')
        academicInst = request.POST.getlist('institute')
        academicCountry = request.POST.getlist('academic_rec_country')
        academicDate = request.POST.getlist('date_award')
        academicGrade = request.POST.getlist('grade')

        for x in range(len(academicName)):
            academicRecord[x+1] = {
                'Academic_name' : academicName[x],
                'Institute' : academicInst[x],
                'Country' :  academicCountry[x],
                'Award_date' : academicDate[x],
                'Grade' : academicGrade[x],
            }

        #membership and fellowship
        membershipFellowship = request.POST.getlist('membership_fellowship')

        #employment record in higher education
        experienceHighEd = request.POST.get('exp_highEd')
        erhe = {}

        if experienceHighEd == 'Yes':
            academicPosition = request.POST.getlist('academic_position')
            prevInstitute = request.POST.getlist('prev_institute')
            erheCountry = request.POST.getlist('erhe_country')
            erheStart = request.POST.getlist('start_erhe')
            erheEnd = request.POST.getlist('end_erhe')

            for x in range(len(academicPosition)):
                erhe[x+1] = {
                    'Academic_position' : academicPosition[x],
                    'Previous_institute' : prevInstitute[x],
                    'Country' : erheCountry[x],
                    'Start_date' : erheStart[x],
                    'End_date' : erheEnd[x],
                }        

        #employment record in industry
        experienceInd = request.POST.get('exp_ind')
        eri ={}
        if experienceInd == 'Yes':
            industryPosition = request.POST.getlist('industry_position')
            prevIndustry = request.POST.getlist('prev_industry')
            eriCountry = request.POST.getlist('eri_country')
            eriStart = request.POST.getlist('start_eri')
            eriEnd = request.POST.getlist('end_eri')

            for x in range(len(industryPosition)):
                eri[x+1] = {
                    'Industry_position' :  industryPosition[x],
                    'Previous_industry' : prevIndustry[x],
                    'Country' : eriCountry[x],
                    'Start_date' : eriStart[x],
                    'End_date' : eriEnd[x],

            }
        #teaching supervision
        #courses
        courses = {}

        if request.POST.getlist('course')!=None:

            course = request.POST.getlist('course')
            level = request.POST.getlist('course_level')

            for x in range(len(course)):
                courses[x+1] = {
                    'Course' : course[x],
                    'Level' : level[x]
                }
        
        superVisionFile = request.FILES['list_supervision_file']
        areaInterest = request.POST.get('area_interest')
        publications = request.FILES['publications']

        scholarly_id = request.POST.get('scholarly_id')
        scopus_id = request.POST.get('scopus_id')

        scholarlyInfo = getScholarlyInfo(scholarly_id)
        scopusInfo = getScopusInfo(scopus_id)

        malay = request.POST.get('Malay')
        english = request.POST.get('English')
        arabic = request.POST.get('Arabic')

        #other languages:

        otherLanguages = {}

        if request.POST.getlist('language') is not None:

            language = request.POST.getlist('language')
            fluency = request.POST.getlist('fluency')

            for x in range(len(language)):
                otherLanguages[x+1] = {
                    'language' : language[x],
                    'fluency' : fluency[x]
                }
        else:
            otherLanguages[0] = 'No other languages'

        #FAMILY PARTICULARS
        noChildren = request.POST.get('no_children')
        if noChildren == '':
            children = 0
        else:
            noChildren = int(noChildren)
        #if applicant have children:
            if noChildren > 0 :        
                children = {}
                childrenName = request.POST.getlist('children_name')
                childrenDob = request.POST.getlist('children_dob')
                childrenGender = request.POST.getlist('children_gender')

                for x in range(noChildren):
                    children[x+1] = {
                        'name' : childrenName[x],
                        'dob' : childrenDob[x],
                        'gender' : childrenGender[x]
                    }
            else:
                children = 0

        #if applicant is married:
        if marital == 'Married':
            spouseName = request.POST.get('spouse_name')
            spouseOccupation = request.POST.get('spouse_occupation')
        else:
            #changing marital stat:
            changeMarital = request.POST.get('changeMarital')
            if changeMarital == 'Yes':
                marital = 'Married'
                spouseName = request.POST.get('spouse_name')
                spouseOccupation = request.POST.get('spouse_occupation')
            else:
                spouseName = 'no spouse'
                spouseOccupation = 'no spouse'

        family = {
            'Children' : children,
            'Spouse' : spouseName,
            'Spouse_occupation' : spouseOccupation
        }

        referees = {}

        #referees
        for x in range(1,4):
           referee_name = request.POST.get('referee_'+str(x)+'_name')
           referee_position = request.POST.get('referee_'+str(x)+'_position')
           referee_compInst = request.POST.get('referee_'+str(x)+'_compInst')
           referee_email = request.POST.get('referee_'+str(x)+'_email')
           referee_phone = request.POST.get('referee_'+str(x)+'_phone')
           referee_contact = request.POST.get('referee_'+str(x)+'_contact')

           referees[x] = {
               'name' : referee_name,
               'position' : referee_position,
               'company_institute' : referee_compInst,
               'email' : referee_email,
               'phone' : referee_phone, 
               'contactability' : referee_contact, 
           }

        icPassFile = request.FILES['passport_ic']
        coverLetter = request.FILES['cover_letter']
        researchStatement = request.FILES['research_statement']
        teachingStatement = request.FILES['teaching_statement']
        cv = request.FILES['CV']
        transcript = request.FILES['transcripts']
        other_docs = request.FILES['other_docs']

        #SAVING

        user.email = email
        user.save()
        profile.dob = dob
        profile.gender = gender
        profile.pob = pob
        profile.nationality = nationality
        profile.citizenship = citizenship
        profile.cod = cod
        profile.maritalStat = marital
        profile.religion = religion
        profile.address = address
        profile.code = code
        profile.phoneNo = phoneNo
        profile.icPass = icPass
        profile.submission = profile.submission + 1
        profile.save()

        applicant_status = 'PENDING'

        # application  = Application.objects.get(id=draft_id)
        
        #file saving

        file_name = "Supervision file"

        myfile = UserFile.objects.create(applicant = application ,f_name=file_name,myfiles=superVisionFile)
        myfile.save()

        publicationsFile = UserFile.objects.create(applicant = application, f_name="Publications", myfiles=publications)
        publicationsFile.save()

        icPassFile1 = UserFile.objects.create(applicant=application, f_name="IC Passport", myfiles=icPassFile)
        icPassFile1.save()
        coverLetterFile = UserFile.objects.create(applicant=application, f_name="Cover Letter", myfiles = coverLetter)
        coverLetterFile.save()
        researchStatementFile = UserFile.objects.create(applicant=application, f_name="Research Statement", myfiles = researchStatement)
        researchStatementFile.save()
        teachingStatementFile = UserFile.objects.create(applicant=application, f_name="Teaching Statement", myfiles = teachingStatement)
        teachingStatementFile.save()
        cvFile = UserFile.objects.create(applicant=application, f_name="CV", myfiles=cv)
        cvFile.save()
        transcriptFile = UserFile.objects.create(applicant=application, f_name="Transcript", myfiles=transcript)
        transcriptFile.save()
        other_docsFile = UserFile.objects.create(applicant=application, f_name="Other Document", myfiles=other_docs)
        other_docsFile.save()
        
        
        presentEmployement = {
            'Present_post' : presentPost,
            'Present_Employer' : presentEmployer,
            'Current_duties' : currentDuties,
            'Current_post_appointment' : currentPostAppt,
            'Basic_salary' : basicSalary,
            'Other_Emoluments_Allowance' : otherEmolumentsAllowance,
            'Income_Tax_Deduction' : incomeTaxDeduction,
            'Period_of_Notice' : periodOfNotice
        }


        teachingSupervision = {
            'Supervision_file_name' : myfile.f_name,
            'Supervision_file' : myfile.myfiles.url,
            'Area_of_interest' :areaInterest,
            'Publications_name' : publicationsFile.f_name,
            'Publications_file' : publicationsFile.myfiles.url,
            'Scholarly_id' : scholarly_id,
            'Scopus_id' : scopus_id,
        }

        languages = {
            'Malay': malay,
            'English' : english,
            'Arabic' : arabic,
        }

        applicant_files = UserFile.objects.filter(applicant_id = application.id)
        
        documents = {}
        key = 1

        for files in applicant_files:
            documents[key] = {
                'name' : files.f_name,
                'file' : files.myfiles.url
            }
            key += 1 
        

        application_cont = Application.objects.get(id = application.id)

        application_cont.applicant_status = applicant_status
        application_cont.prevApplication = prevApplication

        if prevApplication == 'Yes' :
            application_cont.datePrev = datePrev

        application_cont.source = source
        application_cont.fullname = fullname
        application_cont.presentEmployment = presentEmployement
        application_cont.academicRec = academicRecord
        application_cont.documents = documents
        # application_cont.postApplied = postApplied
        application_cont.application_type = 'Academic'
        application_cont.applicant_progress = 'In Progress'

        
        application_cont.save()
        # save in the academic model as well:
        academicApplication.postApplied = postApplied
        academicApplication.membershipFellowhsip = membershipFellowship
        academicApplication.experienceHighEd = experienceHighEd
        academicApplication.employmentRecHighEd = erhe
        academicApplication.experienceInd = experienceInd
        academicApplication.employmentRecInd = eri
        academicApplication.coursesOffering = courses
        academicApplication.teachingSupervision = teachingSupervision
        academicApplication.scholarlyInfo = scholarlyInfo
        academicApplication.scopusInfo = scopusInfo 
        academicApplication.languages = languages
        academicApplication.otherLanguages = otherLanguages
        academicApplication.family = family
        academicApplication.referees = referees

        academicApplication.save()

        
       
        #SEND EMAIL:
        subject = 'Confirmation: Job Application Submission for ' + job.name
        from_email = "ubdtesting70@gmail.com"
        to = user.email
        text_content = 'Dear ' + fullname + ', We are pleased to inform you that your job application has been successfully received and processed. We appreciate the time and effort you dedicated to completing the application process.'
        html_content = '<h3>Dear ' + fullname + ',</h3> <p>We are pleased to inform you that your job application has been successfully received and processed.<br> We appreciate the time and effort you dedicated to completing the application process.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        messages.success(request, 'Your application form has been submitted!')



        return redirect('home')
    # save as draft
    if request.method == "POST" and 'addDraft' in request.POST:
         #FIRST PAGE
        email = request.POST.get('email')
        postApplied = request.POST.get('post_applied')
        prevApplication = request.POST.get('prevApplication')

        #date prev
        if prevApplication == 'Yes' :
            datePrev = request.POST.get('date_prev')

        else:
            datePrev  = 0000-00-00
        

        source = request.POST.get('source')
        fullname = request.POST.get('fullname')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        pob = request.POST.get('pob')
        cod = request.POST.get('cod')
        nationality = request.POST.get('nationality')
        citizenship = request.POST.get('citizenship')
        marital = request.POST.get('marital')
        religion = request.POST.get('religion')
        icPass = request.POST.get('ic_passport') 
        address = request.POST.get('address')
        code = request.POST.get('code')
        phoneNo = request.POST.get('phone')

        #present employment
        presentPost = request.POST.get('present_post')
        presentEmployer = request.POST.get('present_employer')
        currentDuties = request.POST.get('current_duties')
        currentPostAppt = request.POST.get('current_post_appointment')
        basicSalary = request.POST.get('basic_salary')
        otherEmolumentsAllowance = request.POST.get('other_emoluments_allowance')
        incomeTaxDeduction = request.POST.get('income_tax_deduction')
        periodOfNotice = request.POST.get('period_of_notice')
        
        #academic record
        academicRecord = {}
        academicName = request.POST.getlist('academic_name')
        academicInst = request.POST.getlist('institute')
        academicCountry = request.POST.getlist('academic_rec_country')
        academicDate = request.POST.getlist('date_award')
        academicGrade = request.POST.getlist('grade')

        if academicName != []:
            for x in range(len(academicName)):
                academicRecord[x+1] = {
                    'Academic_name' : academicName[x],
                    'Institute' : academicInst[x],
                    'Country' :  academicCountry[x],
                    'Award_date' : academicDate[x],
                    'Grade' : academicGrade[x],
                }

        #membership and fellowship
        membershipFellowship = request.POST.getlist('membership_fellowship')

        #employment record in higher education
        experienceHighEd = request.POST.get('exp_highEd')
        erhe = {}

        if experienceHighEd == 'Yes':
            academicPosition = request.POST.getlist('academic_position')
            prevInstitute = request.POST.getlist('prev_institute')
            erheCountry = request.POST.getlist('erhe_country')
            erheStart = request.POST.getlist('start_erhe')
            erheEnd = request.POST.getlist('end_erhe')

            for x in range(len(academicPosition)):
                erhe[x+1] = {
                    'Academic_position' : academicPosition[x],
                    'Previous_institute' : prevInstitute[x],
                    'Country' : erheCountry[x],
                    'Start_date' : erheStart[x],
                    'End_date' : erheEnd[x],
                }        

        #employment record in industry
        experienceInd = request.POST.get('exp_ind')
        eri ={}
        if experienceInd == 'Yes':
            industryPosition = request.POST.getlist('industry_position')
            prevIndustry = request.POST.getlist('prev_industry')
            eriCountry = request.POST.getlist('eri_country')
            eriStart = request.POST.getlist('start_eri')
            eriEnd = request.POST.getlist('end_eri')

            for x in range(len(industryPosition)):
                eri[x+1] = {
                    'Industry_position' :  industryPosition[x],
                    'Previous_industry' : prevIndustry[x],
                    'Country' : eriCountry[x],
                    'Start_date' : eriStart[x],
                    'End_date' : eriEnd[x],

            }
        #teaching supervision
        #courses
        courses = {}

        if request.POST.getlist('course') != []:

            course = request.POST.getlist('course')
            level = request.POST.getlist('course_level')

            for x in range(len(course)):
                courses[x+1] = {
                    'Course' : course[x],
                    'Level' : level[x]
                }
        
        # superVisionFile = request.FILES['list_supervision_file']
        areaInterest = request.POST.get('area_interest')
        # publications = request.FILES['publications']
        scholarly_id = request.POST.get('scholarly_id')
        scopus_id = request.POST.get('scopus_id')

        # scholarlyInfo = getScholarlyInfo(scholarly_id)
        # scopusInfo = getScopusInfo(scopus_id)

        malay = request.POST.get('Malay')
        english = request.POST.get('English')
        arabic = request.POST.get('Arabic')

        #other languages:

        otherLanguages = {}

        if request.POST.getlist('language') is not None:

            language = request.POST.getlist('language')
            fluency = request.POST.getlist('fluency')

            for x in range(len(language)):
                otherLanguages[x+1] = {
                    'language' : language[x],
                    'fluency' : fluency[x]
                }
        else:
            otherLanguages[0] = 'No other languages'

        #FAMILY PARTICULARS
        noChildren = request.POST.get('no_children')
        if noChildren == '':
            children = 0
        else:
            noChildren = int(noChildren)
        #if applicant have children:
            if noChildren > 0 :        
                children = {}
                childrenName = request.POST.getlist('children_name')
                childrenDob = request.POST.getlist('children_dob')
                childrenGender = request.POST.getlist('children_gender')

                for x in range(noChildren):
                    children[x+1] = {
                        'name' : childrenName[x],
                        'dob' : childrenDob[x],
                        'gender' : childrenGender[x]
                    }
            else:
                children = 0

        #if applicant is married:
        if marital == 'Married':
            spouseName = request.POST.get('spouse_name')
            spouseOccupation = request.POST.get('spouse_occupation')
        else:
            #changing marital stat:
            changeMarital = request.POST.get('changeMarital')
            if changeMarital == 'Yes':
                marital = 'Married'
                spouseName = request.POST.get('spouse_name')
                spouseOccupation = request.POST.get('spouse_occupation')
            else:
                spouseName = 'no spouse'
                spouseOccupation = 'no spouse'

        family = {
            'Children' : children,
            'Spouse' : spouseName,
            'Spouse_occupation' : spouseOccupation
        }

        referees = {}

        #referees
        for x in range(1,4):
           referee_name = request.POST.get('referee_'+str(x)+'_name')
           referee_position = request.POST.get('referee_'+str(x)+'_position')
           referee_compInst = request.POST.get('referee_'+str(x)+'_compInst')
           referee_email = request.POST.get('referee_'+str(x)+'_email')
           referee_phone = request.POST.get('referee_'+str(x)+'_phone')
           referee_contact = request.POST.get('referee_'+str(x)+'_contact')

           referees[x] = {
               'name' : referee_name,
               'position' : referee_position,
               'company_institute' : referee_compInst,
               'email' : referee_email,
               'phone' : referee_phone, 
               'contactability' : referee_contact, 
           }

        #SAVING

        user.email = email
        user.save()
        profile.dob = dob
        profile.gender = gender
        profile.pob = pob
        profile.nationality = nationality
        profile.citizenship = citizenship
        profile.cod = cod
        profile.maritalStat = marital
        profile.religion = religion
        profile.address = address
        profile.code = code
        profile.phoneNo = phoneNo
        profile.icPass = icPass
        # profile.submission = profile.submission + 1
        profile.save()

        applicant_status = 'PENDING'

        presentEmployement = {
            'Present_post' : presentPost,
            'Present_Employer' : presentEmployer,
            'Current_duties' : currentDuties,
            'Current_post_appointment' : currentPostAppt,
            'Basic_salary' : basicSalary,
            'Other_Emoluments_Allowance' : otherEmolumentsAllowance,
            'Income_Tax_Deduction' : incomeTaxDeduction,
            'Period_of_Notice' : periodOfNotice
        }


        teachingSupervision = {
            # 'Supervision_file_name' : myfile.f_name,
            # 'Supervision_file' : myfile.myfiles.url,
            'Area_of_interest' :areaInterest,
            # 'Publications_name' : publicationsFile.f_name,
            # 'Publications_file' : publicationsFile.myfiles.url,
            'Scholarly_id' : scholarly_id,
            'Scopus_id' : scopus_id,
        }

        languages = {
            'Malay': malay,
            'English' : english,
            'Arabic' : arabic,
        }

        application_cont = Application.objects.get(id = application.id)

        application_cont.applicant_status = applicant_status
        application_cont.prevApplication = prevApplication

        if prevApplication == 'Yes' :
            application_cont.datePrev = datePrev

        application_cont.source = source
        application_cont.fullname = fullname
        application_cont.presentEmployment = presentEmployement
        application_cont.academicRec = academicRecord
        # application_cont.documents = documents
        application_cont.postApplied = postApplied
        application_cont.application_type = 'Academic'
        application_cont.applicant_progress = 'DRAFT'

        application_cont.save()

        academicApplication.postApplied = postApplied
        academicApplication.membershipFellowhsip = membershipFellowship
        academicApplication.experienceHighEd = experienceHighEd
        academicApplication.employmentRecHighEd = erhe
        academicApplication.experienceInd = experienceInd
        academicApplication.employmentRecInd = eri
        academicApplication.coursesOffering = courses
        academicApplication.teachingSupervision = teachingSupervision
        # academicApplication.scholarlyInfo = scholarlyInfo
        # academicApplication.scopusInfo = scopusInfo 
        academicApplication.languages = languages
        academicApplication.otherLanguages = otherLanguages
        academicApplication.family = family
        academicApplication.referees = referees


        academicApplication.save()



        messages.success(request, 'Your application form has been saved as draft!')
        return redirect('home')

    return render(request, 'main/mainPages/jobForm.html' , context)

def nonAcademicJobForm(request, job_id):
    if not request.user.is_authenticated:
        messages.error(request, 'You are not logged in!')
        return redirect('login')
    job = Job.objects.get(id=job_id)
    id = request.user.id
    user = User.objects.get(id=id)
    profile = Applicant.objects.get(user=user)

    NATIONALITIES_list = ['Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean', 'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran',  'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech', 'Danish', 'Djibouti', 'Dominican', 'Dutch', 'Dutchman', 'Dutchwoman', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz', 'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan', 'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'Netherlander', 'New Zealander', 'Ni-Vanuatu', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean', 'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese', 'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean']
    gender_list = ['Female', 'Male', 'Others']
    context = {'n': range(5), 'job':job , 'profile' :profile , 'user':user, 'nationalities' : NATIONALITIES_list , 'gender':gender_list}

    if request.method == 'POST' and 'submitForm' in request.POST:
        fullname = request.POST.get('fullname')
        ic_no = request.POST.get('ic_no')
        ic_color = request.POST.get('ic_color')
        dob = request.POST.get('dob')
        address = request.POST.get('address')
        citizenship =  request.POST.get('citizenship')
        gender =  request.POST.get('gender')
        nationality =  request.POST.get('nationality')
        drivingLicense =  request.POST.get('driving_license')
        drivingLicenseType =  request.POST.get('driving_license_type')
        malay =  request.POST.get('Malay')
        english =  request.POST.get('English')

        languages = {
            'Malay' : malay,
            'English' : english
        }

        # 
        highestEducationLevel=  request.POST.get('highest_education_level')
        # academic recoord stored in application model. For non-Academic it is just one record, which is the highest academic record
        
        academicName =  request.POST.get('academic_name')
        institute =  request.POST.get('institute')
        academicCountry =  request.POST.get('academic_rec_country')
        dateAward =  request.POST.get('date_award')
        grade =  request.POST.get('grade')

        academicRecord = {
                'Academic_name' : academicName,
                'Institute' : institute,
                'Country' :  academicCountry,
                'Award_date' : dateAward,
                'Grade' : grade,
            }
        

        expGov =  request.POST.get('expGov')



        # experience Industry
        experienceInd =  request.POST.get('exp_ind')
        if experienceInd == 'Yes':
            industryPosition = request.POST.get('industry_position')
            prevIndustry = request.POST.get('prev_industry')
            eriCountry = request.POST.get('eri_country')
            eriStart = request.POST.get('start_eri')
            eriEnd = request.POST.get('end_eri')

            eri= {
                'Industry_position' :  industryPosition,
                'Previous_industry' : prevIndustry,
                'Country' : eriCountry,
                'Start_date' : eriStart,
                'End_date' : eriEnd,
            }

        # current work
        presentPost = request.POST.get('present_post')
        presentEmployer = request.POST.get('present_employer')
        currentPostAppt = request.POST.get('current_post_appointment')
        basicSalary = request.POST.get('basic_salary')

        presentEmployement = {
            'Present_post' : presentPost,
            'Present_Employer' : presentEmployer,
            'Current_post_appointment' : currentPostAppt,
            'Basic_salary' : basicSalary,
        }


        
        # Documents:
        icPassFile = request.FILES['passport_ic']
        coverLetter = request.FILES['cover_letter']
        cv = request.FILES['CV']
        other_docs = request.FILES['other_docs']

        

        # profile change:
        profile.icPass = ic_no
        profile.icColor = ic_color
        profile.nationality = nationality
        profile.citizenship = citizenship
        profile.dob = dob
        profile.address = address
        profile.gender = gender
        profile.save()


        # saving:
        application = Application.objects.create(
            user = user,
            job = job,
            profile =  profile,
            fullname = fullname,
            presentEmployment = presentEmployement,
            academicRec = academicRecord,
            application_type = 'Non-Academic')
        
        # file saving
        icPassFile1 = UserFile.objects.create(applicant=application, f_name="IC Passport", myfiles=icPassFile)
        icPassFile1.save()
        coverLetterFile = UserFile.objects.create(applicant=application, f_name="Cover Letter", myfiles = coverLetter)
        coverLetterFile.save()
        cvFile = UserFile.objects.create(applicant=application, f_name="CV", myfiles=cv)
        cvFile.save()
        other_docsFile = UserFile.objects.create(applicant=application, f_name="Other Document", myfiles=other_docs)
        other_docsFile.save()

        applicant_files = UserFile.objects.filter(applicant_id = application.id)
        
        documents = {}
        key = 1

        for files in applicant_files:
            documents[key] = {
                'name' : files.f_name,
                'file' : files.myfiles.url
            }
            key += 1 

        application.documents = documents
        application.save()
        
        nonAcademmic = NonAcademicApplication.objects.create(
            application = application,
            drivingLicense = drivingLicense,
            drivingLicenseType = drivingLicenseType,
            languages = languages,
            highestEducationLevel = highestEducationLevel,
            expGov = expGov,
            workExperience = eri
        )

        nonAcademmic.save()
        #SEND EMAIL:
        subject = 'Confirmation: Job Application Submission for ' + job.name
        from_email = "ubdtesting70@gmail.com"
        to = user.email
        text_content = 'Dear ' + fullname + ', We are pleased to inform you that your job application has been successfully received and processed. We appreciate the time and effort you dedicated to completing the application process.'
        html_content = '<h3>Dear ' + fullname + ',</h3> <p>We are pleased to inform you that your job application has been successfully received and processed.<br> We appreciate the time and effort you dedicated to completing the application process.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        messages.success(request, 'Your application form has been submitted!')
        return redirect('home')




    return render(request, 'main/mainPages/nonAcademicJobForm.html', context)






