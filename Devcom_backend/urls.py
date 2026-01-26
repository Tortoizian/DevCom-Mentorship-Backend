"""
URL configuration for Devcom_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from roomalloc.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
	path("api-auth/", include("rest_framework.urls")),
	path("register/", SignupView.as_view()),
	path("csrf_cookie/", GetCSRFToken.as_view()),
	path("authenticated/", CheckAuthenticatedView.as_view()),
	path("login/", LoginView.as_view()),
	path("logout/", LogoutView.as_view()),
	# path("delete/", DeleteUserView.as_view()), # see if this is required or not
	path("get_users/", GetUsersView.as_view()),

	path('', StudentView.as_view(), name='test'), # is not to be present in final version
	path('bookings/<str:rollno>/', StudentBookings.as_view(), name='student_bookings'),
	path('bookings/', StudentBookings.as_view(), name='student_bookings'),
	path('room/', RoomView.as_view(), name='room'),
	path('slot/', SlotView.as_view(), name='slot'),
]

urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))] # catchall for react router. index.html is in build folder