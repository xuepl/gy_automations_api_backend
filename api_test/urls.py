from django.urls import re_path
from . import views

urlpatterns = [

    re_path(r'^login/?$', views.Login.as_view()),
    re_path(r'^signup/?$', views.SignUp.as_view()),
    re_path(r'^projects/?$', views.Projects.as_view({"get": "list", "post": "create"})),
    re_path(r'^projects/(?P<pk>\d+)/?$',
            views.Projects.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),
    re_path(r'^hosts/?$', views.GlobalHosts.as_view({"get": "list", "post": "create"})),
    re_path(r'^hosts/(?P<pk>\d+)/?$',
            views.GlobalHosts.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),
    re_path(r'^suites/?$', views.TestSuite.as_view({"get": "list", "post": "create"})),
    re_path(r'^suites/?$', views.TestSuite.as_view({"get": "list", "post": "create"})),
    re_path(r'^suites/(?P<pk>\d+)/?$',
            views.TestSuite.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),
    re_path(r'^cases/?$', views.TestCase.as_view({"get": "list", "post": "create"})),
    re_path(r'^cases/(?P<pk>\d+)/?$',
            views.TestCase.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),
    re_path(r'^api/?$', views.API.as_view({"get": "list", "post": "create"})),
    re_path(r'^api/(?P<pk>\d+)/?$',
            views.API.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})),


    re_path(r'^runApi/?$', views.RunAPI.as_view()),
    re_path(r'^getApiResult/(?P<pk>\d+)/?$', views.GetResult.as_view()),
]
