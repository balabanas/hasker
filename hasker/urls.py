"""hasker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
# from django.views.generic import TemplateView
# from rest_framework import routers
# from rest_framework.schemas import get_schema_view
# from rest_framework import permissions


from basesite import views
# from basesite.views import QuestionListView, QuestionCreateView, HaskerLoginView, QuestionDetailView, \
#     tag_typeahead, SignUpView, SettingsView, QuestionTagListView, QuestionSearchListView, accept_answer, vote

from hasker.settings.base import *


# class AuthRootRouter(routers.DefaultRouter):
#     def get_api_root_view(self, api_urls=None):
#         view = super().get_api_root_view(api_urls=api_urls)
#         view.cls.permission_classes = [permissions.IsAuthenticated]
#         return view
#
#
# router = AuthRootRouter()
# router.register(r'questions', views.QuestionViewSet, basename='api-question')
# router.register(r'questions/(?P<question_id>\d+)/answers', views.AnswerViewSet, basename='api-answer')
# router.register(r'questions/(?P<question_id>\d+)/tags', views.QuestionTagViewSet, basename='api-tag')

urlpatterns = [
    # path('info/', views.infoview, name='diagnostic'),
    path('admin/', admin.site.urls),

    path('', views.QuestionListView.as_view(), name='list'),
    path('tag/<slug:slug>', views.QuestionTagListView.as_view(), name='tag-list'),
    path('search', views.QuestionSearchListView.as_view(), name='search'),
    path('ask', views.QuestionCreateView.as_view(), name='create'),
    path('sign-up', views.SignUpView.as_view(), name='sign-up'),
    path('settings', views.SettingsView.as_view(), name='settings'),
    path('login', views.HaskerLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('question/<int:pk>', views.QuestionDetailView.as_view(), name='question-detail'),
    path('vote/<int:pk>', views.vote, name='vote'),
    path('tag-typeahead', views.tag_typeahead, name='tag-typeahead'),
    path('accept-answer/<int:qpk>/<int:apk>', views.accept_answer, name='accept-answer'),

    path('api/v1/', include('hasker_api.urls')),
    # path('api/v1/openapi', get_schema_view(
    #     title="Hasker",
    #     description="Q&A traversing API",
    #     version="1.0.0"
    # ), name='openapi-schema'),
    # path('api/v1/swagger-ui/', TemplateView.as_view(
    #     template_name='basesite/swagger-ui.html',
    #     extra_context={'schema_url': 'openapi-schema'}
    # ), name='swagger-ui'),
]

if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
