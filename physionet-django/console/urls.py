from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.console_home, name='console_home'),
    url(r'^project-list/$', views.project_list, name='project_list'),
    url(r'^storage-requests/$', views.storage_requests,
        name='storage_requests'),
    url(r'^user-list/$', views.user_list, name='user_list'),
]
