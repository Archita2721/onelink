from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse ,FileResponse
from .forms import * 
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes, force_str  
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
from .token import account_activation_token  
from django.contrib.auth.models import User  
from django.core.mail import EmailMessage  
from django.contrib.auth import get_user_model,authenticate,logout,login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm,PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.db.models.query_utils import Q
from .forms import linkform
import qrcode,requests,os,uuid,platform, string, random,shortuuid
from PIL import Image
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from qrcode import QRCode,constants
from .models import *


# Create your views here.
from mixpanel import Mixpanel
mp = Mixpanel("e6d21e6a11f7525155300e960d895a23")

def register(request):  
    if request.method == 'POST':  
        form = NewUserForm(request.POST)  
        if form.is_valid():  
            user = form.save(commit=False)  
            user.is_active = False  
            mp.people_set(request.user.id, {
                '$email': request.user.email,
                '$created': '2013-04-01T13:20:00',
                '$last_login': datetime.datetime.now()
            })
            mp.track(request.user.id, 'Signed Up')
            user.save()  
            current_site = get_current_site(request)  
            mail_subject = 'Activation link has been sent to your email id'  
            message = render_to_string('acc_active_email.html', {  
                'user': user,  
                'domain': current_site.domain,  
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':account_activation_token.make_token(user),  
            })  
            
            to_email = form.cleaned_data.get('email')  
            email = EmailMessage(  
                        mail_subject, message, to=[to_email]  
            )  
            email.send() 
            messages.success(request,'Please confirm your email address to complete the registration')  
        else:
            messages.error(request,"Something went wrong")
    else:  
        form = NewUserForm()  
    return render(request, 'register.html', {'form': form})  

def activate(request, uidb64, token):  
    User = get_user_model()  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()  
        messages.success(request,'Thank you for your email confirmation. Now you can login your account.')  
        return redirect('/login')
    else:  
        messages.error(request,'Activation link is invalid!')  
        return redirect('/login')
    
def login_request(request):
        if request.method == "POST":
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username') 
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                
                if user is not None:
                    login(request, user)
                    mp.people_set(request.user.id, {
                        '$name': request.user.get_full_name(),
                        '$email':request.user.email,
                        '$last_login': datetime.datetime.now()
                    })
                    login(request, user)
                    messages.info(request, f"You are now logged in as {username}.")
                    return redirect("homepage")
                else:
                    messages.error(request,"Invalid username or password.")
            else:
                messages.error(request,"Invalid username or password.")
                            
        form = AuthenticationForm()
        return render(request=request, template_name="login.html", context={"login_form":form})




def url(request,id):
     if request.method == "GET":
        mydata = linkModel.objects.get(id=id)
     return render(request=request,template_name="urls.html",context={'mydata':mydata})

def url(request):
     if request.method == "GET":
        mydata = linkModel.objects.all()
        print(request.user.id)
     return render(request=request,template_name="url.html",context={'mydata':mydata})

def urls(request,id):
     #mp.track(request.user.id, 'Redirected')
     operating_system = platform.system()
     mp.track(request.user.id,"Page redirected", {
        "url": request.path,
        "operating_system": operating_system
     })
     if request.method == "GET":
        mydata = linkModel.objects.get(id=id)
        android_link = mydata.android_link #request.GET.get('android_link')
        ios_link = mydata.ios_link #request.GET.get('ios_link')
        fallback_url = mydata.fallback_link
        
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        print(user_agent)
        if 'iphone' in user_agent or 'ipad' in user_agent :
             #print("apple")
            return redirect(ios_link)
        elif 'android' in user_agent:
              #print("android")
            return redirect(android_link)
        else:
            return redirect(fallback_url)
     return render(request=request,template_name="urls.html",context={'mydata':mydata})

def homepage(request):
    #slug= shortuuid.ShortUUID().random(length=6)
    mp.track(request.user.id, 'Viewed HomePage')
    mydata = linkModel.objects.all()
    if request.method == 'POST':
        form = linkform(request.POST)
        
        if form.is_valid():
            f=form.save()
            ios_link = form.cleaned_data['ios_link']
            # android_link = form.cleaned_data['android_link']
            #combined_link = f"{request.scheme}://{request.get_host()}/redirect?android_link={android_link}&ios_link={ios_link}"
            f.appname = ios_link.split("/")[-2].split("?")[0]
            #print(combined_link)
            ##url = request.build_absolute_uri(reverse('urls',args=[f.id])) #,args=[f.id]
            f.slug = shortuuid.ShortUUID().random(length=6)
            url = request.build_absolute_uri(reverse('short_url', args=[f.slug]))

            qr = QRCode(version=1, error_correction=constants.ERROR_CORRECT_L)
            qr.add_data(url)
            img = qr.make_image()
            #image_filename = f"qr_{str(uuid.uuid4())}.png"
            #image_path = os.path.join(settings.MEDIA_ROOT, image_filename)
            #img.save(image_path)
            img.save("media/qr_code_{}.png".format(f.id))
            #f.qr_code = os.path.join(settings.MEDIA_ROOT, image_filename)
            f.qr_code="media/qr_code_{}.png".format(f.id)
            f.save()
           
           
            # context = {
            #     'addform': form,
            #     #'image_path': f"{settings.MEDIA_URL}{image_filename}"
            # }
            
           
            messages.success(request, 'Saved Successfully!')
            return redirect("url")
        else:
            messages.error(request, 'Something went wong')
    else:
        form = linkform()
    return render (request=request, template_name="homepage.html",context={"addform":form,"mydata":mydata})




def redirect_short_url(request, short_code):
    operating_system = platform.system()
    mp.track(request.user.id,"Page redirected", {
        "url": request.path,
        "operating_system": operating_system
    })
    if request.method == "GET":
        link = linkModel.objects.get(slug=short_code)
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'iphone' in user_agent or 'ipad' in user_agent :
                #print("apple")
            return redirect(link.ios_link)
        elif 'android' in user_agent:
                #print("android")
            return redirect(link.android_link)
        else:
            return redirect(link.fallback_link)
    return render(request=request,template_name="urls.html",context={'mydata':link})
    


# def redirect(request):
#     android_link = request.GET.get('android_link')
#     ios_link = request.GET.get('ios_link')
#     user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
#     print(user_agent)
#     if 'iphone' in user_agent or 'ipad' in user_agent:
#         return redirect(ios_link)
#     elif 'android' in user_agent:
#         return redirect(android_link)
#     else:
#         return redirect(ios_link)


def logout_request(request):
        logout(request)
        messages.info(request, "You have successfully logged out.") 
        return redirect("login")

def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
                                
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "password/password_reset_email.txt"
					c = {
                    
                    'user': user.email,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https' if request.is_secure() else 'http',
                    
					}
					email = render_to_string(email_template_name, c)
                    
					try:
						send_mail(subject, email, 'architashah27@gmail.com' , [user.email], fail_silently=False)
					except BadHeaderError:

						return HttpResponse('Invalid header found.')
						
					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					return redirect ("login")
			messages.error(request, 'An invalid email has been entered.')
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="password/password_reset.html", context={"password_reset_form":password_reset_form})

