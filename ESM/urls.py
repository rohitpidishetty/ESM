from django.contrib import admin
from django.urls import path
from auth.views import App

application = App()

try:
  urlpatterns = [
    path('admin/', admin.site.urls),
    path('/', application.login, name='login'),
    path('', application.login, name='login'),
    path('log-in', application.login, name='login'),
    path('sign-up', application.signup, name='signup'),
    path('home', application.home, name='home'),
    path('user-not-found-error', application._404unf, name='_404unf'),
    path('swap', application.swapAccept, name='swapAccept'),
    path('request-accepted', application.reqAccepted, name='reqAccepted'),
    path('link-configuration-ended', application.linkUnavail, name='linkUnavail')
  ]
except Exception as e:
  print('Err')
