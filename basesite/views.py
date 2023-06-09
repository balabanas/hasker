from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_GET
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin, CreateView, UpdateView
from django.views.generic.list import ListView, MultipleObjectMixin

from basesite.forms import QuestionCreateForm, AnswerForm, UserProfileForm, UserProfileChangeForm
from basesite.models import Question, Answer, QuestionVotedBy, AnswerVotedBy, Tag


class QuestionListView(ListView):
    model = Question
    paginate_by = 20
    ordering = '-date_created'

    def get_ordering(self):
        ordering = self.request.GET.get('ordering', '-date_created')
        if ordering in ['-date_created', '-votes']:
            self.ordering = ordering
        return self.ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trending_object_list'] = Question.trending.all()
        context['ordering'] = self.ordering
        return context


class QuestionTagListView(ListView):
    model = Question
    paginate_by = 20
    ordering = ('-votes', '-date_created')
    template_name = 'basesite/question_tag_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(tags__slug=self.kwargs['slug'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['trending_object_list'] = Question.trending.all()
        try:
            tag = Tag.objects.get(slug=self.kwargs['slug'])
        except Tag.DoesNotExist:
            tag = None
        context['tag'] = tag
        return context


class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trending_object_list'] = Question.trending.all()
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class QuestionDetailView(FormMixin, MultipleObjectMixin, DetailView):
    model = Question
    form_class = AnswerForm
    paginate_by = 30
    object: Question

    def get_context_data(self, **kwargs):
        object_list = Answer.objects.filter(question_id=self.object.id).order_by('-correct', '-votes', '-date_created')
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['trending_object_list'] = Question.trending.all()
        form = kwargs.get('form', None) or AnswerForm()
        context['form'] = form
        return context

    def post(self, request, pk):  # pk is not used here, but view passes it anyway
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.question = self.object
        obj.author = self.request.user
        obj.correct = False
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("question-detail", kwargs={"pk": self.object.pk})


def accept_answer(request, qpk: int, apk: int):
    if not request.user.is_authenticated:
        return JsonResponse({'result': 'Login required'})
    if request.POST:
        user = request.user
        try:
            Answer.objects.get(id=apk, question__id=qpk, question__author=user)  # just check if answer exists
            answers = Answer.objects.filter(question__id=qpk, question__author=user)
            answers.exclude(id=apk).update(correct=False)
            answers.filter(id=apk).update(correct=True)  # using update to avoid .save() and sending email as a result
        except Answer.DoesNotExist:
            return JsonResponse({'result': 'Not found'})
    return JsonResponse({'result': 'Success'})


def vote(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'result': 'Login required'})
    if request.POST:
        user = request.user
        try:
            increment = int(request.POST['increment'])
            instance_type = str(request.POST['instance_type'])
            instance_id = int(request.POST['instance_id'])
            if increment not in (-1, 1) or instance_type not in ('a', 'q'):
                return JsonResponse({'result': 'Wrong request data (increment or instance_type)'})
            q = Question.objects.get(pk=pk)
            if instance_type == 'a':
                a = Answer.objects.get(pk=instance_id)
        except (ValueError, Question.DoesNotExist, Answer.DoesNotExist) as exc:
            return JsonResponse({'result': 'Wrong request data: ' + str(exc)})
        if instance_type == 'a':
            voted_by = AnswerVotedBy.objects.get_or_create(user=user, answer=a)[0]
            instance = a
        else:
            voted_by = QuestionVotedBy.objects.get_or_create(user=user, question=q)[0]
            instance = q
        if voted_by.vote != increment:
            instance.votes += increment
            voted_by.vote += increment
            voted_by.save()
            instance.save()  # todo: change in order to not sending email on every vote (bulk update?)!
            return JsonResponse({'result': 'Success'})
        return JsonResponse({'result': 'Already voted'})


@require_GET
def tag_typeahead(request):
    value = request.GET['query']
    tag_candidates = Tag.objects.filter(tag__icontains=value).values('id', 'tag')[:7]
    result = [{"value": tc['tag'], "label": tc['tag']} for tc in tag_candidates]
    return JsonResponse(result, safe=False)


class HaskerLoginView(LoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trending_object_list'] = Question.trending.all()
        return context


class SignUpView(CreateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trending_object_list'] = Question.trending.all()
        return context


class SettingsView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileChangeForm
    template_name = 'auth/user_edit_form.html'
    success_url = reverse_lazy('list')

    def get_object(self, queryset=None):
        current_user = self.request.user
        return current_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trending_object_list'] = Question.trending.all()
        return context


class QuestionSearchListView(ListView):
    model = Question
    paginate_by = 20
    template_name = 'basesite/search_results.html'
    query: str = ""

    def get(self, *args, **kwargs):
        self.query: str = self.request.GET['q']
        return super().get(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        if self.query.strip().startswith('tag:'):
            tag = self.query.strip().split(':', maxsplit=1)[1].strip()
            try:
                tag_slug = Tag.objects.get(tag__iexact=tag).slug
            except Tag.DoesNotExist:
                tag_slug = tag
            return redirect(reverse('tag-list', args=(tag_slug,)))
        return super().render_to_response(context, **response_kwargs)

    def get_ordering(self):
        ordering = self.request.GET.get('ordering', '-date_created')
        if ordering in ['-votes', '-date_created']:
            return ordering
        return '-date_created'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(Q(title__icontains=self.query) | Q(message__icontains=self.query) |
                                   Q(answers__message__icontains=self.query)).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trending_object_list'] = Question.trending.all()
        return context
