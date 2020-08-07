from django.urls import path
from . import views
app_name='whitetube'
urlpatterns = [
    path('',views.HomeView.as_view(),name="home"),
    path('login/', views.LoginView.as_view(),name="login"),
    path('register', views.RegisterView.as_view(),name="register"),
    path('new_video/', views.NewVideo.as_view(),name="new_video"),
    path('video/<int:id>', views.VideoView.as_view(),name="video"),
    path('comment', views.CommentView.as_view(),name="comment"),
    path('get_video/<file_name>', views.VideoFileView.as_view(),name="file"),
    path('logout/', views.LogoutView.as_view(),name="logout"),
    path('createchannel', views.CreateChannelView.as_view(),name="create"),
    path('<user>/channel/', views.ChannelView.as_view(),name="channel")
]
