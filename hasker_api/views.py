import json

from django.http import HttpResponse
from rest_framework import permissions, mixins, viewsets, filters, pagination
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from basesite.models import Question, Answer
from hasker_api.serializers import TagSerializer, AnswerSerializer, QuestionSerializer


class PageNumberPaginationWithCount(pagination.PageNumberPagination):
    page_size = 20

    def get_paginated_response(self, *args, **kwargs):
        response = super().get_paginated_response(*args, **kwargs)
        response.data['page_count'] = self.page.paginator.num_pages
        return response

    def get_paginated_response_schema(self, *args, **kwargs):
        schema = super().get_paginated_response_schema(*args, **kwargs)
        schema['properties']['page_count'] = {
            'type': 'integer',
            'example': 123,
        }
        return schema


class QuestionViewSet(viewsets.ModelViewSet):
    """
    View set that returns a list of all or filtered questions, trending questions, or detailed question.
    Default filter: off. Enable it by including ?search query to url
    Default sorting: date of creaton, reversed. Alter it by ?ordering query:-date_created, votes, -votes. Searches
    in title and message in Question, and in message of Answer objects to that Questions
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPaginationWithCount
    http_method_names = ['get']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'message', 'answers__message']
    ordering_fields = ['date_created', 'votes']
    ordering = ['-date_created']

    @action(detail=False, methods=['get'], url_path='trending-questions', url_name='trending-list')
    def trending_questions(self, request):
        queryset = Question.trending.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AnswerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Returns a list of answers associated with a specific question id
    """
    serializer_class = AnswerSerializer
    pagination_class = PageNumberPaginationWithCount
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date_created', 'votes']
    ordering = ['-date_created']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paginator.page_size = 30

    def get_queryset(self):
        question_id = self.kwargs.get('question_id')
        try:
            q = Question.objects.get(pk=question_id)
            return Answer.objects.filter(question=q)
        except Question.DoesNotExist as exc:
            raise NotFound("Question not found.") from exc


def infoview(request):
    info = {
        'host': request.get_host(),
        'port': request.get_port(),
        'path': request.build_absolute_uri()
    }
    info = json.dumps(info)
    return HttpResponse(info, content_type='application/json')


class QuestionTagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Returns a list of tags associated with a specific question id
    """
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']

    def get_queryset(self):
        question_id = self.kwargs.get('question_id')
        try:
            return Question.objects.get(pk=question_id).tags.all()
        except Question.DoesNotExist:
            raise NotFound("Question not found.")
