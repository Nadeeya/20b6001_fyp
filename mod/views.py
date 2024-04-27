from django.shortcuts import render , redirect
from user.models import User , Applicant
from django.contrib.auth.decorators import login_required
from .models import Recruiter , Job , Application , Department , AcademicApplication , NonAcademicApplication
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.contrib import messages
from recruiter.models import Justification , SeminarReviewReport
from django.core.mail import send_mail , EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from django.db.models import Count
import plotly.figure_factory as ff
from sklearn import preprocessing
import numpy as np
from scipy.stats import norm
import math




# Create your views here.
from datetime import datetime


@login_required(login_url='login')
@permission_required("mod.view_post")
def adminHomePage(request):
    jobs = Job.objects.all()
    recruiters = Recruiter.objects.all()
    applicants = Application.objects.all().exclude(applicant_progress='DRAFT')

    totalJobs = jobs.count()
    totalRecruiters = recruiters.count()
    totalApplicants = applicants.count()

    jobs = Job.objects.all()

    # get top 10 jobs
    # try:
    query_result =  Application.objects.values('job__name').annotate(application_count=Count('job__name')).order_by('-application_count')[:10]
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
        color = 'job__name'
        
    ).update_traces(width=0.7)
        
    fig.update_layout(
        title={
            'text' : 'Top 10 jobs',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font=dict(
        size=11,  # Set the font size here
    ),
    showlegend = False
    )

    chart = fig.to_html()

    # no. of applicants in each department.
    applicants_dep = Application.objects.values('job__department__name').annotate(application_count=Count('job__department__name')).order_by('-application_count')

    df = pd.DataFrame(applicants_dep)
    df = df.rename(columns={'job__department__name':'department'})
    fig2 = px.pie(df , values='application_count', names='department')
    fig2.update_layout(title={
                'text':'Applicants in each department',
                'x':0.4,
                'xanchor':'center',
                },
                font=dict(size=10),
                )
    pie_chart = fig2.to_html()

    # no of applicants from each race.

    applicants_race = Application.objects.values('profile__nationality').filter(application_type='Academic').annotate(application_count=Count('profile__nationality')).order_by('-application_count')
    df = pd.DataFrame(applicants_race)
    df = df.rename(columns={'profile__nationality':'nationality'})
    fig3 = px.pie(df, values='application_count', names='nationality')
    fig3.update_layout(title={
                'text':"Academic Applicants' nationality",
                'x':0.45,
                'xanchor':'center',
                },
                font=dict(size=10),
                )
    
    pie_chart2 = fig3.to_html()

    applicants_applicationDate =  Application.objects.values('date_added').order_by('-date_added').annotate(application_count=Count('applicant_status'))
    df = pd.DataFrame(applicants_applicationDate)

    fig3 = px.line(df, x='date_added', y='application_count')
    fig3.update_layout(title={
                'text':"No.of Applications receive <br> each day",
                'x':0.5,
                'xanchor':'center',
                },
                font=dict(size=10),
                xaxis_title='Date',
                yaxis_title='No. of Application')
    plot_line = fig3.to_html()

    applicants_h_index = AcademicApplication.objects.values('scopusInfo__h_index' , 'scopusInfo__citation').order_by('scopusInfo__h_index').annotate(application_count=Count('scopusInfo__h_index'))
    df = pd.DataFrame(applicants_h_index)
    df = df.rename(columns={'scopusInfo__h_index':'h-index', 'scopusInfo__citation':'citation'})
    fig = px.scatter(df, x='h-index' , y='citation' , size='application_count' , color_discrete_sequence=['rgb(145, 201, 145)'])
    fig.update_layout(title={
        'text':"Overall applicants' scopus citation and h-index",
        'x':0.5,
        'xanchor':'center', 
    },
    font=dict(size=10),)
    citation_hindex = fig.to_html()


    nbins = math.ceil((df["h-index"].max() - df["h-index"].min()) / 2)
    fig = px.histogram(df, x='h-index' , y='application_count' ,nbins=nbins ,color_discrete_sequence=['#fcb247'] )
    fig.update_layout(title={
        'text':'Distribution of Scopus h-index Scores for <br> all academic jobs',
        'x':0.5,
        'xanchor':'center',
        },
        font=dict(size=10),
        xaxis_title='Scopus h-index',
        yaxis_title='No. of applicants',
        bargap = 0.1)
    
    hindex = fig.to_html()

    context = {'totalJobs':totalJobs, 'totalApplicants':totalApplicants , 'totalRecruiters':totalRecruiters , 'jobs':jobs, 'chart':chart, 'pie_chart':pie_chart, 'pie_chart2':pie_chart2 , 'plot_line':plot_line, 'citation_hindex':citation_hindex, 'hindex':hindex }


    # no of applicants applying 
    # except:
    #     context = {'totalJobs':totalJobs, 'totalApplicants':totalApplicants , 'totalRecruiters':totalRecruiters , 'jobs':jobs, 
    #             #    'chart':chart, 'pie_chart':pie_chart, 'pie_chart2':pie_chart2
    #                }

    return render(request, 'mod/adminHome.html' , context)

@login_required(login_url='login')
@permission_required("mod.view_post")
def addRecruiter(request):
    department = Department.objects.all()
    
    context = {'department':department}
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        department_id = request.POST.get('department')
        member_type = request.POST.get('member_type')

        check_user = User.objects.filter(email=email).first()

        if password != password1:
            messages.error(request, 'Passwords does not match')
            return render(request, 'mod/addRecruiter.html' , context)
        
        if check_user:
            messages.error(request, 'User email already exist.')
            return render(request, 'mod/addRecruiter.html', context)
        
        user = User.objects.create_user(username= email, email=email, password=password, first_name = fname, last_name = lname , type = 'RECRUITER')
        user.save()

        department = Department.objects.get(id=department_id)

        recruiter_details = Recruiter.objects.create(
            user = user,
            department = department,
            member_type = member_type
        )

        recruiter_details.save()

        messages.success(request, 'Recruiting staff member has been successfully added')
        return redirect('manageRecruiters')
    
    return render(request, 'mod/addRecruiter.html', context)

@login_required(login_url='login')
@permission_required("mod.view_post")
def addJob(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        department_id = request.POST.get('department')
        type = request.POST.get('type')
        salaryMin = request.POST.get('salaryMin')
        salaryMax = request.POST.get('salaryMax')
        dateClose = request.POST.get('dateClose')
        status = request.POST.get('status')
        contractDur = request.POST.get('contractDur')
        minReq = request.POST.get('minReq')
        yearsExp = request.POST.get('yearsExp')
        description = request.POST.get('description')
        jobForm = request.POST.get('form')

        if jobForm == 'ACADEMIC':
            btnMsg = 'Default'
        else:
            btnMsg = request.POST.get('btnMsg')


        department = Department.objects.get(id=department_id)
    
        job = Job.objects.create(
            name = name,
            department = department,
            type = type,
            salaryMin = salaryMin,
            salaryMax = salaryMax,
            dateClose = dateClose,
            status = status,
            contractDur = contractDur,
            minReq = minReq,
            yearsExp = yearsExp,
            description = description,
            jobForm = jobForm,
            btnMsg = btnMsg
        )

        job.save()
        messages.success(request, 'Job advertisment successfully added!')
        return redirect('manageJobs')
    
    category = ['Academic' , 'Non-Academic' , 'Others']
    department = Department.objects.all()
    
    context = {'category':category, 'department':department}

    return render(request, 'mod/addJob.html', context)

@login_required(login_url='login')
@permission_required("mod.view_post")
def manageRecruiters(request):
    recruiter = Recruiter.objects.all()
    #filter recruiters:
    search = request.GET.get('search') if request.GET.get('search') != None else ''
    category = request.GET.get('category') if request.GET.get('category') != None else ''
    department = request.GET.get('department') if request.GET.get('department') != None else ''

    

    recruiter = recruiter.filter(user__first_name__icontains=search)
    recruiter = recruiter.filter(department__category__icontains=category).filter(department__name__icontains=department).filter(user__email__icontains=search)
    department = Department.objects.values_list('name', flat=True)
    category = Department.objects.order_by().values_list('category',flat=True).distinct()
    
    
    result = recruiter.count()
    context = {'recruiter':recruiter, 'department':department , 'result':result , 'category':category}
    return render(request, 'mod/manageRecruiter.html', context)

@login_required(login_url='login')
@permission_required("mod.view_post")
def manageJobs(request):
    job = Job.objects.all().order_by('-status')
    openJobs = Job.objects.filter(status='OPEN').count()
    closedJobs = Job.objects.filter(status='CLOSED').count()

    # category = ['Academic' , 'Non-Academic' , 'Others']
    department = Department.objects.values_list('name', flat=True)
    category = Department.objects.values_list('category',  flat=True).distinct()
    
    search = request.GET.get('search') if request.GET.get('search') != None else ''
    category_search = request.GET.get('category') if request.GET.get('category') != None else ''
    department_search = request.GET.get('department') if request.GET.get('department') != None else ''
    
    job = job.filter(name__icontains=search).filter(department__category__icontains=category_search).filter(department__name__icontains=department_search)
    totalJobs = job.count()
    totalApplicants_list = []

    for j in job:
        n = Application.objects.filter(job=j).count()
        totalApplicants_list.append(n)

    context = {'job' : job,  'totalJobs':totalJobs , 'openJobs':openJobs , 'closedJobs':closedJobs, 'category':category, 'department':department , 'totalApplicantsList':totalApplicants_list}

    return render(request, 'mod/manageJob.html', context)

@login_required(login_url='login')
@permission_required("mod.view_post")
def editRecruiter(request, pk):
    
    recruiter = Recruiter.objects.get(user_id=pk)
    user = User.objects.get(id=pk)
    
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        department_id = request.POST.get('department')
        # category = request.POST.get('category')
        member_type = request.POST.get('member_type')

        department = Department.objects.get(id=department_id)

        user.first_name = fname
        user.last_name = lname
        user.email = email
        user.save()
        recruiter.department = department
        # recruiter.category = category
        recruiter.member_type = member_type

        recruiter.save()

        messages.success(request, 'Successfully edited!')

        return redirect('editRecruiter', recruiter.user_id)
    
    category = Department.objects.values_list('category', flat=True).distinct()
    department = Department.objects.all()

    context = {'category':category, 'department':department , 'recruiter':recruiter}

    return render(request, 'mod/editRecruiter.html' , context)

@login_required(login_url='login')
def deleteRecruiter(request, pk):
    recruiter = Recruiter.objects.get(user_id=pk)
    user = User.objects.get(id=pk)
    recruiter.delete()
    user.delete()
    return HttpResponse("Deleted!")

def sendChangeNotification(job_id):
    job = Job.objects.get(id=job_id)
    applications = Application.objects.filter(job=job)

    for applicant in applications:
        subject = 'Important Update: Changes to Job Details for ' + job.name
        from_email = "ubdtesting70@gmail.com"
        to = applicant.user.email

        plain_text = get_template('mod/email/changesNotification.html')
        htmly = get_template('mod/email/changesNotification.html')

        context = {
            'fullname' : applicant.fullname,
            'due_date' : job.dateClose,
            'job_name' : job.name
        }

        d = {'context':context}
        text_content = plain_text.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

@login_required(login_url='login')
def editJob(request, pk):
    job = Job.objects.get(id=pk)
    category = ['Academic' , 'Non-Academic' , 'Others']
    department = Department.objects.all()
    type = ['Full-time', 'Part-time']
    minReq = ["O'levels", "A'levels", 'HND' , 'Degree', 'Master', 'PHD']

    if job.department.category == 'Academic':
        status = ['OPEN', 'CLOSED']

        if request.method == 'POST':
            name = request.POST.get('name')
            department_id = request.POST.get('department')
            salaryMin = request.POST.get('salaryMin')
            salaryMax = request.POST.get('salaryMax')
            dateClose = request.POST.get('dateClose')
            status1 = request.POST.get('status')
            contractDur = request.POST.get('contractDur')
            minReq1 = request.POST.get('minReq')
            yearsExp = request.POST.get('yearsExp')
            description = request.POST.get('description')

            department = Department.objects.get(id=department_id)

            job.name = name
            job.department = department
            job.salaryMax = salaryMax
            job.salaryMin = salaryMin
            job.dateClose = dateClose
            job.status = status1
            job.contractDur = contractDur
            job.minReq = minReq1
            job.yearsExp = yearsExp
            job.description = description

            job.save()

            sendChangeNotification(job.id)

            messages.success(request, 'The job details have been successfully updated!')

            return redirect('viewJobDetails' , pk=pk)
        context = {'job':job, 'category':category, 'department':department, 'type':type ,'status':status, 'minReq':minReq}

        return render(request, 'mod/editJob.html', context)

    else:
        context = {'department':department, 'job':job , 'type':type, 'minReq':minReq}

        if request.method == 'POST' and 'changeDetails' in request.POST:
            header = request.POST.get('header')
            name = request.POST.get('name')
            department_id = request.POST.get('department')
            salaryMin = request.POST.get('salaryMin')
            salaryMax = request.POST.get('salaryMax')
            dateClose = request.POST.get('dateClose')
            vacancy = request.POST.get('vacancy')
            minReq = request.POST.get('minReq')
            type = request.POST.get('type')
            description = request.POST.get('description')
            jobForm = request.POST.get('form')



            # experience in government
            pengalaman_berkhidmat = request.POST.get('pengalaman_berkhidmat')
            if pengalaman_berkhidmat == 'Yes' : 
                prev_jawatan = request.POST.get('prev_jawatan')
                pengalaman_tahun = request.POST.get('pengalaman_tahun')

                expGovInfo = {
                    'prev_jawatan' :prev_jawatan,
                    'pengalaman_tahun' :  pengalaman_tahun,
                }
            else:
                prev_jawatan = ''
                pengalaman_tahun = 0

            # job form:
            if jobForm == 'NON-ACADEMIC':
                btnMsg = 'Non-Academic'
            else:
                btnMsg = request.POST.get('btnMsg')
            

            department = Department.objects.get(id=department_id)
            # job creation:

            job.header = header
            job.name = name
            job.department = department
            job.type = type
            job.status = 'OPEN'
            job.salaryMin = salaryMin
            job.salaryMax = salaryMax
            job.dateClose = dateClose
            job.description = description
            job.vacancy = vacancy
            job.minReq = minReq
            job.expGov = pengalaman_berkhidmat
            job.expGovInfo = expGovInfo
            job.jobForm = jobForm
            job.btnMsg = btnMsg
            
            job.save()

            messages.success(request, 'Successfully edited the job!')
            return redirect('manageJobs')
        return render(request, 'mod/editNonAcademicJob.html', context)


@login_required(login_url='login')
def recreateJob(request, pk):
    job = Job.objects.get(id=pk)
    category = ['Academic' , 'Non-Academic' , 'Others']
    department = Department.objects.all()
    
    type = ['Full-time', 'Part-time']
    status = ['OPEN', 'CLOSED']
    minReq = ['Olevels', 'Alevels', 'HND' , 'Degree', 'Master', 'PHD']

    if request.method == 'POST':
        name = request.POST.get('name')
        department_id = request.POST.get('department')
        type = request.POST.get('type')
        salaryMin = request.POST.get('salaryMin')
        salaryMax = request.POST.get('salaryMax')
        dateClose = request.POST.get('dateClose')
        status1 = request.POST.get('status')
        contractDur = request.POST.get('contractDur')
        minReq1 = request.POST.get('minReq')
        yearsExp = request.POST.get('yearsExp')
        description = request.POST.get('description')
        jobForm = request.POST.get('form')
        if jobForm == 'ACADEMIC':
            btnMsg = 'Default'
        else:
            btnMsg = request.POST.get('btnMsg')

        department = Department.objects.get(id=department_id)

        new_job = Job.objects.create(
            name = name,
            department = department,
            type = type,
            salaryMin = salaryMin,
            salaryMax = salaryMax,
            dateClose = dateClose,
            status = status1,
            contractDur = contractDur,
            minReq = minReq1,
            yearsExp = yearsExp,
            description = description,
            jobForm = jobForm,
            btnMsg = btnMsg

        )
        new_job.save()

        messages.success(request, 'A new job position has been successfully created! ')
        return redirect('viewJobDetails' , pk=new_job.id)


    
    context = {'job':job, 'category':category, 'department':department, 'type':type ,'status':status, 'minReq':minReq, 'recreate':'recreate'}

    return render(request, 'mod/editJob.html', context)

@login_required(login_url='login')
def viewAllApplicants(request):
    applicants = Application.objects.all().exclude(applicant_progress='DRAFT')
    recommended = applicants.filter(applicant_status='RECOMMENDED').count
    pending = len(applicants.filter(applicant_status='PENDING'))
    rejected = len(applicants.filter(applicant_status='NOT RECOMMENDED'))
    jobs = Job.objects.all()

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
    
    context = {'applicants':applicants, 'count_applicants':count_applicants, 'jobs':jobs , 'rejected':rejected , 'recommended':recommended, 'pending':pending}

    return render(request, 'mod/viewAllApplicants.html', context)

@login_required(login_url='login')
def viewDepartments(request):
    departments = Department.objects.all()

    context = {'departments':departments}

    return render(request, 'mod/departments.html', context)

@login_required(login_url='login')
def addDepartment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        link = request.POST.get('link')

        if 'icon' in request.FILES:
            icon = request.FILES['icon']
        else:
            icon = ''
    
        department = Department.objects.create(
            name = name,
            description = description,
            category = category,
            link = link,
            icon = icon
        )
        department.save()

        messages.success(request, 'Department successfully added.')
        return redirect('viewDepartments')
        
    return render(request, 'mod/addDepartment.html')


@login_required(login_url='login')
def departmentDetails(request , pk):
    department = Department.objects.get(id=pk)
    recruiters = Recruiter.objects.filter(department = department)
    jobs = Job.objects.filter(department = department)


    context = {'department':department , 'recruiters' : recruiters, 'jobs':jobs}
    return render(request, 'mod/departmentDetails.html', context)


@login_required(login_url='login')
def editDepartment(request, pk):
    department = Department.objects.get(id=pk)
    category = ['Academic', 'Non-Academic' , 'Others']

    if request.method == 'POST' and 'change_icon'  in request.POST:
        if department.icon != '':
            department.icon.delete(save=True)
        
        icon = request.FILES['icon']
        department.icon = icon
        department.save()

        messages.success(request, 'Icon have succesfully changed')
        return redirect(request.META.get('HTTP_REFERER'))

    if request.method == 'POST' and 'edit_details' in request.POST:
        name = request.POST.get('name')
        description = request.POST.get('description')
        category  = request.POST.get('category')
        link = request.POST.get('link')

        department.name = name
        department.description = description
        department.category = category
        department.link = link
        department.save()
        messages.success(request, 'Changes have been successfully made.')
        return redirect(request.META.get('HTTP_REFERER'))


    context ={'department':department , 'category':category}

    return render(request, 'mod/editDepartment.html', context)


@login_required(login_url='login')
def removeIcon(request , pk):
    department = Department.objects.get(id=pk)
    department.icon.delete(save=True)

    messages.success(request, 'Icon successfully removed.')
    return redirect(request.META.get('HTTP_REFERER'))



def viewApplicationDetAll(request,pk):
    applicant = Application.objects.get(id=pk)
    if applicant.application_type == 'Academic':
        academic = AcademicApplication.objects.get(application=applicant)
        justification = Justification.objects.filter(application=applicant)
        seminar_reports = SeminarReviewReport.objects.filter(application=applicant)
        no_reports = seminar_reports.count()
        context =  {'applicant':applicant, 'justification':justification, 'seminar_reports':seminar_reports, 'academic':academic }
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

        return render(request, 'mod/viewApplicantDet-all.html', context)
    elif applicant.application_type == 'Non-Academic':
        nonAcademic = NonAcademicApplication.objects.get(application_id = applicant.id)
        context = {'application':applicant, 'nonAcademic':nonAcademic, 'applicant':applicant}

        return render(request, 'mod/viewApplicantDet-all.html', context)

def viewNextApplicantAll(request, current_applicant_id):
    applicants = Application.objects.all()
    for applicant in applicants:
        if applicant.id > int(current_applicant_id):
            return redirect('viewApplicantDetAllMod' , pk=applicant.id)
    #if there is no result go to the first applicant?

    first_applicant = Application.objects.first()

    return redirect('viewApplicantDetAllMod', pk=first_applicant.id)

def viewPreviousApplicantAll(request, current_applicant_id):
    applicants = Application.objects.all()
    for applicant in reversed(applicants):
        if applicant.id < int(current_applicant_id):
            return redirect('viewApplicantDetAllMod' , pk=applicant.id)
    #if there is no result go to the first applicant?

    last_applicant = Application.objects.last()
    return redirect ('viewApplicantDetAllMod', pk=last_applicant.id)

def viewJobDetails(request,pk):
    job = Job.objects.get(id=pk)
    context = {'job':job}

    return render(request, 'mod/viewJob.html' , context)

def viewJobApplications(request, pk):
    job = Job.objects.get(id=pk)
    NATIONALITIES_list = ['Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean', 'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran',  'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech', 'Danish', 'Djibouti', 'Dominican', 'Dutch', 'Dutchman', 'Dutchwoman', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz', 'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan', 'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'Netherlander', 'New Zealander', 'Ni-Vanuatu', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean', 'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese', 'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean']


    try:
        # applicants = Application.objects.filter(job=job).exclude(applicant_progress='DRAFT')
        if job.department.category == 'Academic':
            applicants = AcademicApplication.objects.filter(application__job=job).exclude(application__applicant_progress='DRAFT')
        else:
            applicants = NonAcademicApplication.objects.filter(application__job=job).exclude(application__applicant_progress='DRAFT')

        recommended_applicants = applicants.filter(application__applicant_status='RECOMMENDED').count()
        pending_applicants = applicants.filter(application__applicant_status='PENDING').count()
        rejected_applicants = applicants.filter(application__applicant_status='NOT RECOMMENDED').count()

        
        #basic filtering 
        if request.method == 'POST' and 'simple-search' in request.POST:
            search = request.POST.get('search') if request.POST.get('search') != None else ''
            status = request.POST.get('status') if request.POST.get('status') != None else ''

            applicants = applicants.filter(application__fullname__icontains=search).filter(application__applicant_status__icontains=status)
            


        order = request.POST.get('order') if request.POST.get('order') != None else ''
        if order == 'ne':
            applicants = applicants.order_by('application__-date_added')
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

        # no of applicants, pending and recommended
        count_applicants = len(applicants)

        context = {'applicants':applicants, 'job':job , 'count_applicants':count_applicants ,
                   'nationality':NATIONALITIES_list, 
                   'recommend_applicants':recommended_applicants,
                   'pending_applicants' : pending_applicants,
                   'rejected_applicants' : rejected_applicants,
                   
                   }

    except Job.DoesNotExist:
        message = "There is no applicants"
        context = {'message' : message , 'nationality':NATIONALITIES_list}

    return render(request, 'mod/viewJobApplications.html' , context)

def advanceFiltering(request, pk):

    job_id = pk
    NATIONALITIES_list = ['Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean', 'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran',  'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech', 'Danish', 'Djibouti', 'Dominican', 'Dutch', 'Dutchman', 'Dutchwoman', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz', 'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan', 'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'Netherlander', 'New Zealander', 'Ni-Vanuatu', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean', 'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese', 'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese', 'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean', 'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese', 'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean']
    post_applied = ['Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer']


    context = {'nationality': NATIONALITIES_list, 'post_applied':post_applied, 'job_id':job_id}
    return render(request, 'mod/advanceFilter.html', context)

def viewApplicationDet(request, pk):
    applicant = Application.objects.get(id=pk)

    if  applicant.application_type == 'Academic':
        academic = AcademicApplication.objects.get(application=applicant)
        justification = Justification.objects.filter(application=applicant)
        seminar_reports = SeminarReviewReport.objects.filter(application=applicant)
        no_reports = seminar_reports.count()
        context =  {'applicant':applicant, 'justification':justification, 'seminar_reports':seminar_reports,'academic':academic }
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

            context =  {'applicant':applicant, 'justification':justification, 'seminar_reports':seminar_reports,
                         'average':average, 'academic':academic}
    else:
        nonAcademic = NonAcademicApplication.objects.get(application=applicant)

        context = {'application':applicant, 'nonAcademic':nonAcademic, 'applicant':applicant}
    return render(request, 'mod/viewApplicationDet.html', context)

def viewNextApplication(request, current_applicant_id, job_id):
    job = Job.objects.get(id=job_id)
    applicants = Application.objects.filter(job=job)
    for applicant in applicants:
        if applicant.id > int(current_applicant_id):
            return redirect('viewApplicationDet' , pk=applicant.id)
    #if there is no result go to the first applicant?

    first_applicant = applicants.first()

    return redirect ('viewApplicationDet', pk=first_applicant.id)

def viewPreviousApplication(request, job_id, current_applicant_id):
    job = Job.objects.get(id=job_id)
    applicants = Application.objects.filter(job=job)
    for applicant in reversed(applicants):
        if applicant.id < int(current_applicant_id):
            return redirect('viewApplicantDet' , pk=applicant.id)
    #if there is no result go to the first applicant?

    last_applicant = Application.objects.filter(job=job).last()

    return redirect ('viewApplicationDet', pk=last_applicant.id)

def sendEmailReminder(request, pk):
    job = Job.objects.get(id=pk)
    applications = Application.objects.filter(job=job).filter(applicant_progress='DRAFT')

    for applicant in applications:
        # send email
        subject = 'Reminder: Submit Your Drafted Job Application (' + job.name + ')'
        from_email = "ubdtesting70@gmail.com"
        to = applicant.user.email

        plain_text = get_template('mod/email/reminderEmail.txt')
        htmly = get_template('mod/email/reminderEmail.html')
        context = {
            'fullname' : applicant.fullname,
            'due_date' : job.dateClose,
        } 
        d = {'context':context}
        text_content = plain_text.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


    
    messages.success(request, 'Successfully sent reminders!')
    return redirect('manageJobs')

def viewConfirmation(request , pk):
    context = {'job_id':pk}
    return render(request, 'mod/viewConfirmation.html' , context)

def createJobOption(request):
    return render(request, 'mod/createJobOption.html')

def addNonAcademicJob(request):
    department_list = Department.objects.filter(category='Non-Academic')
    context = {'department':department_list}

    if request.method == 'POST':
        header = request.POST.get('header')
        name = request.POST.get('name')
        # category = request.POST.get('category')
        department_id = request.POST.get('department')
        salaryMin = request.POST.get('salaryMin')
        salaryMax = request.POST.get('salaryMax')
        dateClose = request.POST.get('dateClose')
        vacancy = request.POST.get('vacancy')
        minReq = request.POST.get('minReq')
        type = request.POST.get('type')
        description = request.POST.get('description')
        jobForm = request.POST.get('form')



        # experience in government
        pengalaman_berkhidmat = request.POST.get('pengalaman_berkhidmat')
        if pengalaman_berkhidmat == 'Yes' : 
            prev_jawatan = request.POST.get('prev_jawatan')
            pengalaman_tahun = request.POST.get('pengalaman_tahun')

            expGovInfo = {
                'prev_jawatan' :prev_jawatan,
                'pengalaman_tahun' :  pengalaman_tahun,
            }
        else:
            prev_jawatan = ''
            pengalaman_tahun = 0

        # job form:
        if jobForm == 'NON-ACADEMIC':
            btnMsg = 'Non-Academic'
        else:
            btnMsg = request.POST.get('btnMsg')
        

        department = Department.objects.get(id=department_id)
        # job creation:
        job = Job.objects.create(
            header = header,
            name = name,
            department = department,
            type = type,
            status = 'OPEN',
            salaryMin = salaryMin,
            salaryMax = salaryMax,
            dateClose = dateClose,
            description = description,
            vacancy = vacancy,
            minReq = minReq,
            expGov = pengalaman_berkhidmat,
            expGovInfo = expGovInfo,
            jobForm = jobForm,
            btnMsg = btnMsg,
        )
        job.save()

        messages.success(request, 'Successfully uploaded new non-academic job opening!')
        return redirect('manageJobs')
        

    return render(request, 'mod/addNon-academicJob.html', context)





    