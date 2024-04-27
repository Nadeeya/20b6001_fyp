from django.shortcuts import render , redirect
from user.models import User
from mod.models import Recruiter , Application , Job , Bookmarks , Bookmarked , AcademicApplication , NonAcademicApplication
from django.http import FileResponse
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from django.http import HttpResponse , Http404 , HttpResponseRedirect
import os
from django.conf import settings
from django.template import loader
from xhtml2pdf import pisa
from shutil import make_archive
from wsgiref.util import FileWrapper
from django.contrib import messages
from django.contrib.auth import authenticate, login , logout
from .models import Justification , SeminarReviewReport
import io
import json
from django.template.loader import get_template
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from django.db.models import Count
import numpy as np
from scipy.stats import norm
import plotly.figure_factory as ff
import math



# from datetime import datetime


# from django.contrib.auth.models import User

#department's home page (dashboard)
def recruiterHome(request):
    pk = request.user.id
    user = User.objects.get(id=pk)
    recruiter = Recruiter.objects.get(user=user)

    department = recruiter.department
    jobs = Job.objects.filter(department=department)
    applicants = Application.objects.filter(job__department=department).exclude(applicant_progress='DRAFT')
    totalJob = jobs.count()
    totalApplicants = applicants.count()

    summary = {}
    i = 1
    for job in jobs:
        job_name = job.name
        total_applicants = Application.objects.filter(job=job).count()
        closing_date = job.dateClose
        status = job.status
        job_id = job.id
        # recommended_applicants = Application.objects.filter(job=job, applicant_status='RECOMMENDED').count()
        # pending_applicants = Application.objects.filter(job=job, applicant_status='PENDING').count()

        summary[i] = {
            'job_name' : job_name,
            'total_applicants' : total_applicants,
            'status' : status,
            'closing_date' : closing_date,
            'job_id': job_id
        }
        i+=1

    try: 

        query_result =  Application.objects.values('job__name').filter(job__department=department).exclude(applicant_progress='DRAFT').annotate(application_count=Count('job__name')).order_by('-application_count')[:10]
        df = pd.DataFrame(
            query_result
        )
        fig = px.bar(
            df,
            orientation='h',
            x = 'application_count',
            y = 'job__name',
            labels = {
                'application_count' : 'No. of Applicants',
                'job__name' : 'Job names',
            },
            color = 'job__name',
            # width=800,
            height=300
            
        ).update_traces(width=0.6)
            
        fig.update_layout(
            title={
                'text' : 'Top 5 jobs',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            font=dict(
            size=12,  # Set the font size here
        ),
        showlegend = False
        )

        chart = fig.to_html()

        # recommended / not recommended / pending

        applicants_status = Application.objects.values('applicant_status').filter(job__department=department).exclude(applicant_progress='DRAFT').annotate(application_count=Count('applicant_status'))
        df = pd.DataFrame(applicants_status)

        fig = px.pie(df, values='application_count', names='applicant_status', color='applicant_status', color_discrete_map={'PENDING':'#fcce79',
                                                                                                                            'RECOMMENDED':'#32CD32',
                                                                                                                            'NOT RECOMMENDED':'#FF6347'})
        fig.update_layout(
            title={
                'text':"Applicants' status",
                'xanchor':'center',
                'x':0.45,
            }
        )
        pie_chart = fig.to_html()

        # applicants nationality :

        applicants_nationality = Application.objects.values('profile__nationality').exclude(applicant_progress='DRAFT').filter(job__department=department).exclude(applicant_progress='DRAFT').annotate(application_count=Count('profile__nationality'))
        df = pd.DataFrame(applicants_nationality)
        df = df.rename(columns={'profile__nationality':'nationality'})

        fig2 = px.pie(df, values='application_count', names='nationality')
        fig2.update_layout(
            title={
                'text':"Applicants' nationality",
                'xanchor':'center',
                'x':0.45,
            }
        )
        pie_chart2 = fig2.to_html() 

        # number of applicants that apply each day:

        applicants_applicationDate =  Application.objects.values('date_added').exclude(applicant_progress='DRAFT').filter(job__department=department).exclude(applicant_progress='DRAFT').annotate(application_count=Count('date_added'))
        df = pd.DataFrame(applicants_applicationDate)

        fig3 = px.line(df, x='date_added', y='application_count')
        plot_line = fig3.to_html()

        if department.category == 'Academic':
            # scopus citations and h-index scatter plot:
            applicants_h_index = AcademicApplication.objects.values('scopusInfo__h_index' , 'scopusInfo__citation').filter(application__job__department=department).exclude(application__applicant_progress='DRAFT').order_by('scopusInfo__h_index').annotate(application_count=Count('scopusInfo__h_index'))
            df = pd.DataFrame(applicants_h_index)
            df = df.rename(columns={'scopusInfo__h_index':'h-index', 'scopusInfo__citation':'citation'})
            fig = px.scatter(df, x='h-index' , y='citation' , size='application_count' , color_discrete_sequence=['rgb(145, 201, 145)'])
            fig.update_layout(title={
                'text':"Overall applicants' Scopus citation and h-index",
                'x':0.5,
                'xanchor':'center', 
            },
            font=dict(size=10),)
            citation_hindex = fig.to_html()


            

            applicants_h_index = AcademicApplication.objects.values('scopusInfo__h_index').exclude(application__applicant_progress='DRAFT').filter(application__job__department=department).order_by('scopusInfo__h_index').annotate(application_count=Count('scopusInfo__h_index'))

            df = pd.DataFrame(applicants_h_index)
            df = df.rename(columns={'scopusInfo__h_index':'h-index'})
            bin_width = 1
            nbins = math.ceil((df["h-index"].max() - df["h-index"].min()) / bin_width)
            fig = px.histogram(df, x='h-index' , y='application_count' , nbins=nbins, color_discrete_sequence=['#fcb247']  )
            fig.update_layout(title={
                'text':'Distribution of Scopus h-index Scores for <br> all academic jobs in the department',
                'x':0.5,
                'xanchor':'center',
                },
                font=dict(size=10),
                xaxis_title='Scopus h-index',
                yaxis_title='No. of applicants',
                bargap = 0.1)
            
            hindex2 = fig.to_html()
            context = {"user":user, "recruiter":recruiter, 'totalJob':totalJob , 'totalApplicants':totalApplicants, 'summary':summary, 'chart':chart, 'pie_chart':pie_chart, 'pie_chart2':pie_chart2, 'scopus':citation_hindex , 'scopus2':hindex2}
        else:
            context = {"user":user, "recruiter":recruiter, 'totalJob':totalJob , 'totalApplicants':totalApplicants, 'summary':summary, 'chart':chart, 'pie_chart':pie_chart, 'pie_chart2':pie_chart2 }

    
    except:
        context = {"user":user, "recruiter":recruiter, 'totalJob':totalJob , 'totalApplicants':totalApplicants, 'summary':summary }



    

    
    return render(request, 'recruiter/recruiterHome.html', context)

#page of list of opening jobs in the department
def viewJobs(request):
    pk = request.user.id
    user = User.objects.get(id=pk)
    recruiter  = Recruiter.objects.get(user=user)

    department = recruiter.department

    try:
        jobs = Job.objects.filter(department=department)
        totalJobs = jobs.count()
        openJobs = jobs.filter(status='OPEN').count()
        closedJobs = jobs.filter(status='CLOSED').count()

        search = request.GET.get('search') if request.GET.get('search') != None else ''
        sort = request.GET.get('sort') if request.GET.get('sort') != None else ''
        status = request.GET.get('status') if request.GET.get('status') != None else ''
        jobs = jobs.filter(name__icontains=search).filter(status__icontains=status)
        if sort == 'earliest':
            jobs = jobs.order_by('uploadDate')
        elif sort == 'latest':
            jobs = jobs.order_by('-uploadDate')
        result = jobs.count()
        context = {'job' : jobs, 'result':result, 'totalJobs':totalJobs , 'openJobs':openJobs , 'closedJobs':closedJobs}


    except Job.DoesNotExist:
        message = "There is no job available"
        context = {'message' : message}

    
    return render(request, 'recruiter/viewJobs.html', context)

#viewApplicants.html -> view each job's applicants
def viewApplicantsJob(request , pk):
    recruiter_id = request.user.id
    recruiter = Recruiter.objects.get(user_id = recruiter_id)
    job = Job.objects.get(id=pk)
    NATIONALITIES_list = ['Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean', 'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran',  'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech', 'Danish', 'Djibouti', 'Dominican', 'Dutch', 'Dutchman', 'Dutchwoman', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz', 'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan', 'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'Netherlander', 'New Zealander', 'Ni-Vanuatu', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean', 'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese', 'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean']


    try:
        # recommended / not recommended / pending

        applicants_status = Application.objects.values('applicant_status').filter(job=job).exclude(applicant_progress='DRAFT').annotate(application_count=Count('applicant_status'))
        df = pd.DataFrame(applicants_status)

        fig = px.pie(df, values='application_count', names='applicant_status', color='applicant_status', color_discrete_map={'PENDING':'#fcce79',
                                                                                                                            'RECOMMENDED':'#32CD32',
                                                                                                                            'NOT RECOMMENDED':'#FF6347'}, width=300, height=300)
        fig.update_layout(
            title={
                'text':"Applicants' status",
                'xanchor':'center',
                'x':0.5,
            },
            font=dict(size=10),
            showlegend=False,

        )
        pie_chart = fig.to_html()

        # scopus info for each job:
        applicants_h_index = AcademicApplication.objects.values('scopusInfo__h_index' , 'scopusInfo__citation').filter(application__job=job).exclude(application__applicant_progress='DRAFT').order_by('scopusInfo__h_index').annotate(application_count=Count('scopusInfo__h_index'))
        df = pd.DataFrame(applicants_h_index)
        df = df.rename(columns={'scopusInfo__h_index':'h-index', 'scopusInfo__citation':'citation'})
        fig = px.scatter(df, x='h-index' , y='citation' , color_discrete_sequence=['rgb(145, 201, 145)'], width=400, height=300)
        fig.update_layout(title={
            'text':"Applicants' Scopus citation and h-index",
            'x':0.5,
            'xanchor':'center', 
        },
        font=dict(size=10),)
        citation_hindex = fig.to_html()


        

        applicants_h_index = AcademicApplication.objects.values('scopusInfo__h_index').exclude(application__applicant_progress='DRAFT').filter(application__job=job).order_by('scopusInfo__h_index').annotate(application_count=Count('scopusInfo__h_index'))

        df = pd.DataFrame(applicants_h_index)
        df = df.rename(columns={'scopusInfo__h_index':'h-index'})
        bin_width = 2
        nbins = math.ceil((df["h-index"].max() - df["h-index"].min()) / bin_width)
        fig = px.histogram(df, x='h-index' , nbins=nbins, color_discrete_sequence=['#fcb247']  , width=400, height=300)
        fig.update_layout(title={
            'text':'Distribution of Scopus h-index Scores',
            'x':0.5,
            'xanchor':'center',
            },
            font=dict(size=10),
            xaxis_title='Scopus h-index',
            yaxis_title='No. of applicants',
            bargap = 0.1)
        
        hindex2 = fig.to_html()


        if job.department.category == 'Academic':
            applicants = AcademicApplication.objects.filter(application__job=job).exclude(application__applicant_progress='DRAFT')
        else:
            applicants = NonAcademicApplication.objects.filter(application__job=job).exclude(application__applicant_progress='DRAFT')
        
        recommended_applicants = applicants.filter(application__applicant_status='RECOMMENDED').count()
        pending_applicants = applicants.filter(application__applicant_status='PENDING').count()
        rejected_applicants = applicants.filter(application__applicant_status='NOT RECOMMENDED').count()

        if Bookmarks.objects.filter(recruiter=request.user.recruiter).filter(job=job).exists():
            bookmarks = Bookmarks.objects.filter(recruiter=request.user.recruiter).filter(job=job).first()

        
        else:
            bookmarks = Bookmarks.objects.create(recruiter = request.user.recruiter , job= job)
            bookmark_name_list  =  ['Good Match', 'Likely Match', 'Likely Reject', 'Definite Reject']
            bookmark_color_list = ['rgb(102, 167, 102)', 'rgb(241, 238, 65)' , 'orange', 'rgb(231, 100, 100)'  ]
            bookmark_list = {}
            for x in range(4):
                bookmark_list[x+1] = {
                    'name' : bookmark_name_list[x],
                    'color' : bookmark_color_list[x]
                }

            bookmarks.bookmark = bookmark_list
            bookmarks.save()
        
        #basic filtering 
        if request.method == 'POST' and 'simple-search' in request.POST:
            search = request.POST.get('search') if request.POST.get('search') != None else ''
            status = request.POST.get('status') if request.POST.get('status') != None else ''
            filter_bookmark_id = request.POST.get('bookmark') if request.POST.get('bookmark') != None else ''

            applicants = applicants.filter(application__fullname__icontains=search).filter(application__applicant_status__icontains=status)
            if filter_bookmark_id != '':
                try:
                    list_of_applicants_bm = Bookmarked.objects.get(id_bookmark=filter_bookmark_id, bookmark=bookmarks).application_list
                except:
                    list_of_applicants_bm=[]
                applicants = applicants.filter(id__in=list_of_applicants_bm)
                # applicants = applicants.application.filter(id__in=list_of_applicants_bm)


        order = request.POST.get('order') if request.POST.get('order') != None else ''
        if order == 'ne':
            applicants = applicants.order_by('-application__date_added')
        elif order == 'od':
            applicants = applicants.order_by('application__date_added')

        #advance filtering
        if request.method == 'POST' and 'advanceFilter' in request.POST:
            if request.POST.get('nationality') != "":
                nationality = request.POST.get('nationality')
                applicants = applicants.filter(application__profile__nationality__icontains=nationality)

            if request.POST.get('citizenship') != "":
                citizenship = request.POST.get('citizenship')
                applicants = applicants.filter(application__profile__citizenship__icontains=citizenship)

            if request.POST.get('cod') != "":
                cod = request.POST.get('cod') 
                applicants = applicants.filter(application__profile__cod__icontains=cod)

            if request.POST.get('period_of_notice') != "":
                pod = request.POST.get('period_of_notice') 
                applicants = applicants.filter(application__presentEmployment__Period_of_Notice__icontains=pod)

            if request.POST.get('erhe') != None:
                erhe = request.POST.get('erhe')
                applicants = applicants.filter(experienceHighEd=erhe)

            if request.POST.get('eri') != None:
                eri = request.POST.get('eri')
                applicants = applicants.filter(experienceHighEd=eri)

            if request.POST.getlist('post_applied'):
                post_applied = request.POST.getlist('post_applied')
                applicants = applicants.filter(postApplied__in=post_applied)

            # age filtering
            # find year born for min age and max age:
            today = datetime.date.today()
            year = today.year

            if request.POST.get('min_age') != '':
                min_age = request.POST.get('min_age')
                min_year = datetime.date(int(year) - int(min_age), 1, 1)
                applicants = applicants.filter(application__profile__dob__lte=min_year)

            if request.POST.get('max_age') != '':
                max_age = request.POST.get('max_age')
                max_year = datetime.date(int(year) - int(max_age), 12, 31)
                applicants = applicants.filter(application__profile__dob__gte=max_year)

        # no of applicants, pending and recommended
        count_applicants = len(applicants)

        context = {'applicants':applicants, 'job':job , 'count_applicants':count_applicants ,
                   'nationality':NATIONALITIES_list, 
                   'recommend_applicants':recommended_applicants,
                   'pending_applicants' : pending_applicants,
                   'rejected_applicants' : rejected_applicants,
                   'bookmarks':bookmarks,
                   'recruiter':recruiter,
                   'status':pie_chart,
                   'citation_hindex':citation_hindex,
                   'hindex':hindex2,
                #    'min':min_year,
                #    'max':max_year
                   }

    except Job.DoesNotExist:
        message = "There is no applicants"
        context = {'message' : message , 'nationality':NATIONALITIES_list}
        
    
    return render(request, 'recruiter/viewApplicants.html', context)


def generate_pdf_file(request,pk):
    applicant = Application.objects.get(id=pk)
    academic = AcademicApplication.objects.get(application=applicant)
    justification = Justification.objects.filter(application=applicant)

    context = {'applicant':applicant , 'justification':justification, 'academic':academic}
    template = get_template('recruiter/applicationDetPdf.html')
    html = template.render(context)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)

    if pdf.err:
        return HttpResponse("Invalid PDF", status_code=400, content_type='text/plain')
    return HttpResponse(result.getvalue(), content_type='application/pdf')

#view details of each of application
def viewApplicantDet(request, pk):
    applicant = Application.objects.get(id=pk)
    recruiter = Recruiter.objects.get(user__id=request.user.id)
    if applicant.application_type == 'Academic':
        academic = AcademicApplication.objects.get(application=applicant)
        justification = Justification.objects.filter(application=applicant)
        
        recruiter = Recruiter.objects.get(user_id=request.user.id)
        if recruiter.member_type == 'lead':
            seminar_reports = SeminarReviewReport.objects.filter(application=applicant)
            no_reports = len(seminar_reports)
            context =  {'applicant':applicant, 'justification':justification, 'seminar_reports':seminar_reports ,'academic':academic , 'recruiter':recruiter}
            if no_reports > 0:
                content = 0
                quality = 0
                communication = 0
                overall = 0
                for seminar_report in seminar_reports:
                    content += int(seminar_report.content_score['total'])
                    quality += int(seminar_report.quality_score['total'])
                    communication += int(seminar_report.communication_score['total'])
                    overall += int(seminar_report.overall_score['total'])

                average = {
                    'content' : round(content / no_reports , 2),
                    'quality' : round(quality / no_reports, 2),
                    'communication' : round(communication / no_reports,2),
                    'overall' : round(overall / no_reports, 2)
                }
                context =  {'applicant':applicant, 'justification':justification, 'seminar_reports':seminar_reports, 'average':average, 'academic':academic, 'recruiter':recruiter}
            
        else:
            try:
                seminar_report = SeminarReviewReport.objects.get(application=applicant, recruiter=recruiter)
                context =  {'applicant':applicant, 'justification':justification, 'seminar_report':seminar_report, 'academic':academic, 'recruiter':recruiter}

            except:
                context =  {'applicant':applicant, 'justification':justification, 'academic':academic, 'recruiter':recruiter}

                
        
    else:
        nonAcademic = NonAcademicApplication.objects.get(application=applicant)
        context = {'applicant':applicant, 'nonAcademic':nonAcademic, 'application':applicant}





    return render(request, 'recruiter/viewApplicantDet.html', context)

#button to recommendApplicant
def recommendApplicant(request, pk):
    applicant = Application.objects.get(id=pk)
    applicant.applicant_status = 'RECOMMENDED'
    id = applicant.job_id
    applicant.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # return redirect('viewApplicantsJob', pk=id)

#button to not recommend applicant
def notRecommendApplicant(request, pk):
    applicant = Application.objects.get(id=pk)
    applicant.applicant_status = 'NOT RECOMMENDED'
    id = applicant.job_id
    applicant.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


    # return redirect('viewApplicantsJob', pk=id)

#button to change back to pending
def pendingApplicant(request, pk):
    applicant = Application.objects.get(id=pk)
    applicant.applicant_status = 'PENDING'
    id = applicant.job_id
    applicant.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

#excel sheet containing list of application for each job


def get_excel(request , pk):
    applicants  = AcademicApplication.objects.filter(application__job_id = pk)
    response = HttpResponse(content_type='application/ms-excel')
    job = Job.objects.get(id=pk)
    response['Content-Disposition'] = f'attachment; filename="{job.name}.xlsx"'



    wb = Workbook()
    ws = wb.active
    ws.title = f"Applicants for {job.name}"

    # Add headers
    headers = ["ID" ,
               "Post Applied", 
                "Full name",
                "Email",
                "DOB",
                "Gender", 
                "POB",
                "Nationality",
                "Citizenhsip",
                "COD",
                "Marital Status",
                "Religion",
                "Home Address",
                "Phone No.",
                "IC / Passport No.",
                "Date applied",
                "Source",
                "Present Post",
                "Present Employer",
                "Current Duties",
                "Current Post Appointment",
                "Basic Salary",
                "Other Emoluments Allowance",
                "Income Tax Deduction",
                "Period of Notice",
                "Academic Record",
                "Membership and Fellowship",
                "Experience in Higher Education",
                "Employment Record Higher Education",
                "Experience in Industry",
                "Employment Record Industry",
                "Courses Offering",
                "Teaching Supervision",
                "Languages",
                "Other Languages",
                "Children",
                "Spouse",
                "Spouse Occupation",
                "Referee 1",
                "Referee 2",
                "Referee 3",
                "Status",
                ]
    ws.append(headers)

    # Add data from the model
    for applicant in applicants:
        ws.append([applicant.application.id,
                    applicant.postApplied,
                    applicant.application.fullname,
                    applicant.application.user.email,
                    applicant.application.profile.dob,
                    applicant.application.profile.gender, 
                    applicant.application.profile.pob , 
                    applicant.application.profile.nationality , 
                    applicant.application.profile.citizenship , 
                    applicant.application.profile.cod , 
                    applicant.application.profile.maritalStat , 
                    applicant.application.profile.religion , 
                    applicant.application.profile.address , 
                    applicant.application.profile.phoneNo , 
                    applicant.application.profile.icPass , 
                    applicant.application.date_added , 
                    applicant.application.source, 
                    applicant.application.presentEmployment.get('Present_post') , 
                    applicant.application.presentEmployment.get('Present_Employer') , 
                    applicant.application.presentEmployment.get('Current_duties') , 
                    applicant.application.presentEmployment.get('Current_post_appointment') , 
                    applicant.application.presentEmployment.get('Basic_salary') , 
                    applicant.application.presentEmployment.get('Other_Emoluments_Allowance') , 
                    applicant.application.presentEmployment.get('Income_Tax_Deduction') , 
                    applicant.application.presentEmployment.get('Period_of_Notice') ,
                    json.dumps(applicant.application.academicRec, indent=2) ,
                    json.dumps(applicant.membershipFellowship , indent=2) ,
                    applicant.experienceHighEd,
                    json.dumps(applicant.employmentRecHighEd  ), 
                    applicant.experienceInd,
                    json.dumps(applicant.employmentRecInd), 
                    json.dumps(applicant.coursesOffering), 
                    json.dumps(applicant.teachingSupervision), 
                    json.dumps(applicant.languages), 
                    json.dumps(applicant.otherLanguages), 
                    json.dumps(applicant.family.get('Children')) , 
                    applicant.family.get('Spouse') , 
                    applicant.family.get('Spouse_occupation') , 
                    json.dumps(applicant.referees.get('1')) , 
                    json.dumps(applicant.referees.get('2')) , 
                    json.dumps(applicant.referees.get('3')) , 
                    applicant.application.applicant_status , 
                    ])

    # Save the workbook to the HttpResponse
    wb.save(response)
    return response
    

# def get_excel(request,pk):
#     output = io.BytesIO()
#     job = Job.objects.get(id=pk)
#     applicants = Application.objects.filter(job_id=pk).values()
#     df = pd.DataFrame(applicants)
#     writer = pd.ExcelWriter(output,engine='xlsxwriter')
#     df.to_excel(writer,sheet_name='Application')
#     writer.close()
#     output_name = job.name
#     output.seek(0)
#     response = HttpResponse(output, 
#     content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = f'attachment; filename={output_name}.xlsx'

#     return response


#button to download all files submited by applicants for each job
def downloadAllApplicantFolder(request, pk):
    job = Job.objects.get(id=pk)
    path = f'applicants/{job.name}'
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    path_to_zip = make_archive(file_path, "zip", file_path)
    response = HttpResponse(FileWrapper(open(path_to_zip,'rb')), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{job.name}.zip"'
    return response

#view all applicants in each department
def viewApplicants(request):
    department = request.user.recruiter.department
    NATIONALITIES_list = ['Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean', 'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran',  'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech', 'Danish', 'Djibouti', 'Dominican', 'Dutch', 'Dutchman', 'Dutchwoman', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz', 'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan', 'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'Netherlander', 'New Zealander', 'Ni-Vanuatu', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean', 'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese', 'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean']
    
    # filter applicants:
    applicants = Application.objects.filter(job__department=department)

    totalApplicants = len(applicants)
    recommended = len(applicants.filter(applicant_status='RECOMMENDED'))
    pending = len(applicants.filter(applicant_status='PENDING'))
    rejected = len(applicants.filter(applicant_status='NOT RECOMMENDED'))
    
    if request.method == 'POST' and 'filter' in request.POST:
        search = request.POST.get('search') if request.POST.get('search') != None else ''
        job_name = request.POST.get('jobs') if request.POST.get('jobs') != None else ''
        status = request.POST.get('status') if request.POST.get('status') != None else ''

        applicants = applicants.filter(fullname__icontains=search).filter(job__name__icontains=job_name).filter(applicant_status__icontains=status)


    order = request.GET.get('order') if request.GET.get('order') != None else ''

    if order == 'ne':
        applicants = applicants.order_by('-date_added')
    elif order == 'od':
        applicants = applicants.order_by('date_added')

    count_applicants = len(applicants)
    jobs = Job.objects.filter(department=department)

    context = {'applicants':applicants, 'count_applicants':count_applicants ,'nationality':NATIONALITIES_list , 'jobs':jobs , 
               'rejected':rejected , 'recommended':recommended, 'pending':pending}
    return render(request, 'recruiter/viewAllApplicants.html', context )

#view the next applicant
def viewNextApplicant(request , job_id , current_applicant_id):
    job = Job.objects.get(id=job_id)
    applicants = Application.objects.filter(job=job)
    for applicant in applicants:
        if applicant.id > int(current_applicant_id):
            return redirect('viewApplicantDet' , pk=applicant.id)
    #if there is no result go to the first applicant?

    first_applicant = Application.objects.filter(job=job).first()

    return redirect ('viewApplicantDet', pk=first_applicant.id)

#view previous applicant
def viewPreviousApplicant(request, job_id, current_applicant_id):
    job = Job.objects.get(id=job_id)
    applicants = Application.objects.filter(job=job)
    for applicant in reversed(applicants):
        if applicant.id < int(current_applicant_id):
            return redirect('viewApplicantDet' , pk=applicant.id)
    #if there is no result go to the first applicant?

    last_applicant = Application.objects.filter(job=job).last()

    return redirect ('viewApplicantDet', pk=last_applicant.id)

#view job details
def viewJobDet(request, pk):
    job = Job.objects.get(id=pk)
    context = {'job':job}
    return render(request, 'recruiter/viewJobDet.html', context)

#change password for first timers
def changePassword(request):
    id = request.user.id
    user = User.objects.get(id=id)
    recruiter = Recruiter.objects.get(user=user)
    context = {'user':user}

    if request.method == 'POST':
        new_pass = request.POST.get('new_pass')
        confirm_pass = request.POST.get('confirm_pass')
        
        if user.check_password(new_pass):
            messages.error(request, 'The new password should not be the same as the old password')
            return redirect('changePassword')
        else:
            if new_pass != confirm_pass:
                messages.error(request, 'The passwords are not a match')
                return redirect('changePassword')
            else:
                user.set_password(new_pass)
                user.save()
                recruiter.change_password = True
                recruiter.save()
                messages.success(request, 'Password change successful!')
                login(request, user)
                return redirect('recruiterHome')
            
    return render(request, 'recruiter/changePassword.html', context)


def bookmarkPopUp(request, applicant_id, old_bookmark_id, bookmarkList_id):
    bookmarks = Bookmarks.objects.get(id=bookmarkList_id)
    bookmarkList = bookmarks.bookmark

    if request.method == 'POST' and 'bookmarking' in request.POST:
        application_id = int(request.POST.get('application_id'))
        bookmark_id = request.POST.get('bookmark_id')

        if old_bookmark_id != '0':
            #remove the application number from old bookmark
            bookmarked = Bookmarked.objects.get(id_bookmark=old_bookmark_id, bookmark=bookmarks)
            bookmark_list = bookmarked.application_list
            bookmark_list.remove(application_id)
            bookmarked.application_list = bookmark_list
            bookmarked.save()

        if bookmark_id != '0':
            try:
                bookmarked = Bookmarked.objects.get(id_bookmark=bookmark_id, bookmark = bookmarks)
                bookmarked.application_list.append(application_id)
                bookmarked.save()

            except Bookmarked.DoesNotExist:

                for key, value in  bookmarks.bookmark.items():
                    if key == bookmark_id:
                        bookmark_name = value['name']
                        bookmark_color = value['color']

                bookmarked = Bookmarked.objects.create(id_bookmark=bookmark_id, bookmark=bookmarks, application_list = [application_id], name=bookmark_name, color=bookmark_color)
                bookmarked.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        
    # if request.method == 'POST' and 'createNewBookmark' in request.POST:
        # bookmarkName = request.POST.get('newBookmark')

        # bookmark = Bookmarks.objects.create(recruiter=request.user.recruiter , job=job , bookmark = bookmarkName)
        # bookmark.save()
    
    context={'bookmarkList':bookmarkList, 'applicant_id':applicant_id, 'old_bookmark_id':old_bookmark_id, 'bookmarkList_id':bookmarkList_id}
    return render(request,'recruiter/bookmarkPopUp-modal.html',context)

def advanceFilter(request, pk):

    job_id = pk
    NATIONALITIES_list = ['Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean', 'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran',  'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech', 'Danish', 'Djibouti', 'Dominican', 'Dutch', 'Dutchman', 'Dutchwoman', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz', 'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan', 'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'Netherlander', 'New Zealander', 'Ni-Vanuatu', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean', 'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese', 'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean']
    post_applied = ['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer']
    qualification = ["O'Levels", "A'Levels" , "HND" , "Degree" , "Masters", "PHD" ]


    context = {'nationality': NATIONALITIES_list, 'post_applied':post_applied, 'job_id':job_id, 'qualification':qualification}
    return render(request, 'recruiter/advanceFilter-modal.html', context)

def viewMembers(request):
    pk = request.user.id
    recruiter = Recruiter.objects.get(user_id=pk)
    department = recruiter.department
    members = Recruiter.objects.filter(department=department)
    context = {'members':members}
    return render(request, 'recruiter/viewMembers.html', context)

# from view all applicants:
def viewApplicantDetAll(request,pk):
    applicant = Application.objects.get(id=pk)
    if applicant.application_type == 'Academic':
        academic = AcademicApplication.objects.get(application=applicant)
        justification = Justification.objects.filter(application=applicant)
        
        recruiter = Recruiter.objects.get(user_id=request.user.id)
        if recruiter.member_type == 'lead':
            seminar_reports = SeminarReviewReport.objects.filter(application=applicant)
            no_reports = seminar_reports.count()
            context =  {'applicant':applicant, 'justification':justification, 'seminar_reports':seminar_reports , 'academic':academic, }
            if no_reports > 0 :
                content = 0
                quality = 0
                communication = 0
                overall = 0
                for seminar_report in seminar_reports:
                    content += int(seminar_report.content_score['total'])
                    quality += int(seminar_report.quality_score['total'])
                    communication += int(seminar_report.communication_score['total'])
                    overall += int(seminar_report.overall_score['total'])

                average = {
                    'content' : content / no_reports,
                    'quality' : quality / no_reports,
                    'communication' : communication / no_reports,
                    'overall' : overall / no_reports
                }

                context =  {'applicant':applicant, 'justification':justification, 'seminar_reports':seminar_reports, 'average':average, 'academic':academic}
            
        else:
            try:
                seminar_report = SeminarReviewReport.objects.get(application=applicant, recruiter=recruiter)
                context =  {'applicant':applicant, 'justification':justification, 'seminar_report':seminar_report , 'academic':academic}
            except:
                context =  {'applicant':applicant, 'justification':justification,'academic':academic }
    
    else:
        nonAcademic = NonAcademicApplication.objects.get(application=applicant)
        context = {'nonAcademic':nonAcademic, 'application':applicant, 'applicant':applicant}


    return render(request, 'recruiter/viewApplicantDet-all.html', context)

#view next applicant in all applicants from the department list:
def viewNextApplicantAll(request, current_applicant_id):
    pk = request.user.id
    department = Recruiter.objects.get(user_id=pk).department
    applicants = Application.objects.filter(job__department=department)
    for applicant in applicants:
        if applicant.id > int(current_applicant_id):
            return redirect('viewApplicantDetAll' , pk=applicant.id)
    #if there is no result go to the first applicant?

    first_applicant = Application.objects.filter(job__department=department).first()

    return redirect ('viewApplicantDetAll', pk=first_applicant.id)

# view prev applicant in all list of applicants from the department
def viewPreviousApplicantAll(request, current_applicant_id):
    pk = request.user.id
    department = Recruiter.objects.get(user_id=pk).department
    applicants = Application.objects.filter(job__department=department)
    for applicant in reversed(applicants):
        if applicant.id < int(current_applicant_id):
            return redirect('viewApplicantDetAll' , pk=applicant.id)
    #if there is no result go to the first applicant?

    last_applicant = Application.objects.filter(job__department=department).last()

    return redirect ('viewApplicantDetAll', pk=last_applicant.id)

def addJustification(request, application_id):
    application = Application.objects.get(id = application_id)
    recruiter_id = request.user.id
    recruiter = Recruiter.objects.get(user_id=recruiter_id)

    if request.method == 'POST':
        justification = request.POST.get('justification')
        report = Justification.objects.create(recruiter=recruiter, application=application, justification=justification)
        report.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


    context  = {'application':application}
    return render(request, 'recruiter/addJustification-modal.html', context)

def addSeminarReviewReport(request, application_id):
    application = Application.objects.get(id = application_id)
    academic = AcademicApplication.objects.get(application=application)
    recruiter_id = request.user.id
    recruiter = Recruiter.objects.get(user_id=recruiter_id)


    try: 
        report = SeminarReviewReport.objects.get(recruiter=recruiter, application=application)
        context = {'application':application, 'recruiter':recruiter,  'academic':academic, 'report':report}

    except:
        context = {'application':application, 'recruiter':recruiter,  'academic':academic}


        if request.method == 'POST':
            title = request.POST.get('seminar_title')
            seminar_date = request.POST.get('seminar_date')
            review_date = request.POST.get('review_date')
            

            # seminar content score
            a_q1 = request.POST.get('a_q1')
            a_q2 = request.POST.get('a_q2')
            a_q3 = request.POST.get('a_q3')
            a_q4 = request.POST.get('a_q4')
            a_total = request.POST.get('a_total')
            # seminar content remarks
            content_remarks = request.POST.get('remarks_1')

            # quality of management score
            b_q1 = request.POST.get('b_q1')
            b_q2 = request.POST.get('b_q2')
            b_q3 = request.POST.get('b_q3')
            b_q4 = request.POST.get('b_q4')
            b_total = request.POST.get('b_total')
            # quality of management remarks
            remarks_2 = request.POST.get('remarks_2')

            # communication score
            c_q1 = request.POST.get('c_q1')
            c_q2 = request.POST.get('c_q2')
            c_q3 = request.POST.get('c_q3')
            c_total = request.POST.get('c_total')

            # communication remarks
            remarks_3 = request.POST.get('remarks_3')

            # overall assesment score
            d_q1 = request.POST.get('d_q1')
            d_q2 = request.POST.get('d_q2')
            d_total = request.POST.get('d_total')

            # overall remarks
            remarks_4 = request.POST.get('remarks_4')

            content_score = {
                'q1' : a_q1,
                'q2' : a_q2,
                'q3' : a_q3,
                'q4' : a_q4,
                'total' : a_total
            }

            quality_score = {
                'q1' : b_q1,
                'q2' : b_q2,
                'q3' : b_q3,
                'q4' : b_q4,
                'total' : b_total
            }

            communication_score = {
                'q1' : c_q1,
                'q2' : c_q2,
                'q3' : c_q3,
                'total' : c_total
            }

            overall_score = {
                'q1' : d_q1,
                'q2' : d_q2,
                'total' : d_total

            }

            report = SeminarReviewReport.objects.create(recruiter=recruiter, application=application,
                                                        title=title, seminar_date=seminar_date,
                                                        review_date=review_date, content_score=content_score,
                                                        content_remarks=content_remarks,
                                                        quality_score=quality_score, quality_remarks=remarks_2,
                                                        communication_score=communication_score, communication_remarks=remarks_3,
                                                        overall_score=overall_score, overall_remarks=remarks_4)
            
            report.save()
            messages.success(request, 'Your seminar review report have been successfully submited.')

            return redirect('viewApplicantsJob', application.job.id )
        
    
    return render(request, 'recruiter/addSeminarReviewReport.html', context)

def generate_pdf_seminar_report(request,pk):
    applicant = Application.objects.get(id=pk)
    seminar_reports = SeminarReviewReport.objects.filter(application=applicant)
    no_reports = seminar_reports.count()
    context =  {'seminar_reports':seminar_reports }
    if no_reports > 0 :
        content = 0
        quality = 0
        communication = 0
        overall = 0
        for seminar_report in seminar_reports:
            content += int(seminar_report.content_score['total'])
            quality += int(seminar_report.quality_score['total'])
            communication += int(seminar_report.communication_score['total'])
            overall += int(seminar_report.overall_score['total'])

        average = {
            'content' : content / no_reports,
            'quality' : quality / no_reports,
            'communication' : communication / no_reports,
            'overall' : overall / no_reports
        }

        context =  {'applicant':applicant, 'seminar_reports':seminar_reports, 'average':average}

    template = get_template('mod/constant/seminarReviewReport.html')
    html = template.render(context)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)

    if pdf.err:
        return HttpResponse("Invalid PDF", status_code=400, content_type='text/plain')
    return HttpResponse(result.getvalue(), content_type='application/pdf')