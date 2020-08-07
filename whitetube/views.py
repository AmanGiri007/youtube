from django.shortcuts import render,reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.views.generic import View
from .models import Channel,Video,Comment
from .forms import ChannelForm,CommentForm,LoginForm,RegisterForm,NewVideoForm
from django.contrib.auth import logout,login,authenticate
import os
from wsgiref.util import FileWrapper
from django.core.files.storage import FileSystemStorage
import random,string
from django.contrib.auth.models import User
# Create your views here.
class HomeView(View):
    def get(self,request):
        most_recent_videos= Video.objects.order_by('-datetime')[:8]
        most_recent_channels= Channel.objects.filter()
        channel=False
        if request.user.is_authenticated:
            try:
                channel=Channel.objects.filter(user__username=request.user).get()
            except Channel.DoesNotExist:
                channel=False
        content={
            'most_recent_videos':most_recent_videos,
            'most_recent_channels':most_recent_channels,
            'channel':channel,
            'menu_active_item':'home'
        }
        return render(request,'whitetube/home.html',content)
class ChannelView(View):    
    def get(self,request,user):
        if request.user.is_authenticated:
            videos=Video.objects.filter(user__username=user).order_by('-datetime')
            channel=Channel.objects.filter(user__username=user).get()
            content={
                'videos':videos,
                'channel':channel
            }
            return render(request,'whitetube/channel.html',content)
        return HttpResponseRedirect('/')
class CreateChannelView(View):
    def get(self,request):
        if request.user.is_authenticated:
            try:
                if Channel.objects.filter(user__username=request.user).get().channel_name!='':
                    return HttpResponseRedirect('/')
            except Channel.DoesNotExist:
                form=ChannelForm()
                channel=False
                content={
                    'form':form,
                    'channel':channel,
                }
                return render(request,'whitetube/createchannel.html',content)
        else:
            return HttpResponseRedirect('login/')
    def post(self,request):
        form=ChannelForm(request.POST)
        if form.is_valid():
            channel_name=form.cleaned_data['channel_name']
            user=request.user
            subscribers=0
            new_channel=Channel(channel_name=channel_name,user=user,subscribers=subscribers)
            new_channel.save()
            return HttpResponseRedirect('/')
        return HttpResponse('This is Resgister view. POST request.')
class LoginView(View):
    def get(self,request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        form=LoginForm()
        content={
            'form':form,
        }
        return render(request,'whitetube/login.html',content)
    def post(self,request):
        form=LoginForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            user=authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('login/')
        return HttpResponse('This is Login view.POST request.')
class LogoutView(View):
    def get(self,request):
        logout(request)
        return HttpResponseRedirect('/')
class VideoFileView(View):
    def get(self,request,file_name):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file=FileWrapper(open(BASE_DIR+'/whitetube/static/whitetube/videos/'+file_name,'rb'))
        response=HttpResponse(file,content_type='video.mp4')
        response['Content-Disposition']='attachment;filename={}'.format(file_name)
        return response
class VideoView(View):
    def get(self,request,id):
        video_by_id=Video.objects.get(id=id)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        video_by_id.path='http://localhost:8000/get_video/'+video_by_id.path
        content={
            'video':video_by_id
        }
        if request.user.is_authenticated:
            comment_form=CommentForm()
            content['form']=comment_form
        comments=Comment.objects.filter(video__id=id).order_by('-datetime')[:5]
        content['comments']=comments
        try:
            if Channel.objects.filter(user__username = request.user).get().channel_name!='':
                channel = Channel.objects.filter(user__username = request.user).get()
                content['channel'] = channel
        except Channel.DoesNotExist:
            channel = False

        return render(request,'whitetube/video.html', content)
class CommentView(View):
    def post(self, request):
        # pass filled out HTML-Form from View to CommentForm()
        form = CommentForm(request.POST)
        if form.is_valid():
            # create a Comment DB Entry
            text = form.cleaned_data['text']
            video_id = request.POST['video']
            video = Video.objects.get(id=video_id)
            
            new_comment = Comment(text=text, user=request.user, video=video)
            new_comment.save()
            return HttpResponseRedirect('/video/{}'.format(str(video_id)))
        return HttpResponse('This is Register view. POST Request.')
class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            print('already logged in. Redirecting.')
            print(request.user)
            return HttpResponseRedirect('/')
        form = RegisterForm()
        return render(request,'whitetube/register.html', {'form': form})

    def post(self, request):
        # pass filled out HTML-Form from View to RegisterForm()
        form = RegisterForm(request.POST)
        if form.is_valid():
            # create a User account
            print(form.cleaned_data['username'])
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            new_user.save()
            return HttpResponseRedirect('login/')
        return HttpResponse('This is Register view. POST Request.')
class NewVideo(View):
    template_name = 'whitetube/new_video.html'

    def get(self, request):
        if request.user.is_authenticated == False:
            return HttpResponseRedirect('register')
        try:
            if Channel.objects.filter(user__username = request.user).get().channel_name != "" :
                form = NewVideoForm() 
                channel=Channel.objects.filter(user__username = request.user).get()
                return render(request, self.template_name, {'form':form, 'channel':channel})
        except Channel.DoesNotExist:
            return HttpResponseRedirect('/')

    def post(self, request):
        form = NewVideoForm(request.POST, request.FILES)       

        if form.is_valid():
            # create a new Video Entry
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            file = form.cleaned_data['file']

            random_char = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            path = random_char+file.name
            fs = FileSystemStorage(location = os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            filename = fs.save("whitetube/static/whitetube/videos/"+path, file)
            file_url = fs.url(filename)

            print(fs)
            print(filename)
            print(file_url)

            new_video = Video(title=title, 
                            description=description,
                            user=request.user,
                            path=path)
            new_video.save()
            
            # redirect to detail view template of a Video
            return HttpResponseRedirect('/video/{}'.format(new_video.id))
        else:
            return HttpResponse('Your form is not valid. Go back and try again.')