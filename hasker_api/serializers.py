from rest_framework import serializers

from basesite.models import Question, Answer, Tag


class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    url = serializers.SerializerMethodField()
    tags_url = serializers.SerializerMethodField()
    answers_url = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('author', 'title', 'message', 'date_created', 'votes', 'url', 'has_tags', 'tags_url', 'has_answers',
                  'answers_url')

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.api_url)

    def get_tags_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.api_tags_url)

    def get_answers_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.api_answers_url)


class AnswerSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Answer
        fields = ('id', 'author', 'message', 'date_created', 'votes', 'correct')

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.api_url)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
