from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from hasker_api import views


class AuthRootRouter(routers.DefaultRouter):
    def get_api_root_view(self, api_urls=None):
        view = super().get_api_root_view(api_urls=api_urls)
        view.cls.permission_classes = [permissions.IsAuthenticated]
        return view


router = AuthRootRouter()
router.register(r'questions', views.QuestionViewSet, basename='api-question')
router.register(r'questions/(?P<question_id>\d+)/answers', views.AnswerViewSet, basename='api-answer')
router.register(r'questions/(?P<question_id>\d+)/tags', views.QuestionTagViewSet, basename='api-tag')

urlpatterns = [
    path('', include(router.urls)),
    path('openapi/', get_schema_view(
        title="Hasker",
        description="Q&A traversing API",
        version="1.0.0"
    ), name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='hasker_api/swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
]
