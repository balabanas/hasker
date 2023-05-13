from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin, FormView, CreateView, UpdateView
from django.views.generic.list import ListView, MultipleObjectMixin

from basesite.forms import QuestionCreateForm, AnswerForm, UserProfileForm, UserProfileChangeForm, QCF
from basesite.models import Question, Answer, QuestionVotedBy, AnswerVotedBy, Tag, UserProfile


class QCV(CreateView):
    model = Question
    form_class = QCF
    template_name = 'basesite/qcv.html'


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
        queryset = super(QuestionTagListView, self).get_queryset()
        queryset = queryset.filter(tags__slug=self.kwargs['slug'])
        return queryset

    # def __init__(self, *args, **kwargs):
    #     super(QuestionTagListView, self).__init__(*args, **kwargs)
    #     self.queryset = Question.objects.filter(tags=self.kwargs['pk'])
    # def get_ordering(self):
    #     ordering = self.request.GET.get('ordering', '-date_created')
    #     if ordering in ['-date_created', '-votes']:
    #         return ordering
    #     return '-date_created'

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
    # fields = ['title', 'message', 'tags']
    form_class = QuestionCreateForm
    # success_url = reverse_lazy('question-detail', self.object.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trending_object_list'] = Question.trending.all()
        return context

    # def form_invalid(self, form):
    #     print(form.data)
    #     return super().form_invalid(form)
    #
    def form_valid(self, form):
        form.instance.author = self.request.user
    #     print('here')
    #     print(form.data)
    #     print(self.request.POST['tags'])
    #     # for row in form.fields.values():
    #     #     print(row.value())
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

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
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
            answers = Answer.objects.filter(question__id=qpk, question__author=user)
            # accepted_answer = answers.get(id=apk)
            answers.exclude(id=apk).update(correct=False)
            answers.filter(id=apk).update(correct=True)
        except Answer.DoesNotExist:
            return JsonResponse({'result': 'Not found'})
    return JsonResponse({'result': 'Success'})


def question_vote(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'result': 'Login required'})
    if request.POST:
        user = request.user
        try:
            increment = int(request.POST['increment'])
            instance_type = str(request.POST['instance_type'])
            instance_id = int(request.POST['instance_id'])
            if increment not in (-1, 1) or instance_type not in ('a', 'q'):
                return JsonResponse({'result': 'Wrong request data'})
            q = Question.objects.get(pk=pk)
            if instance_type == 'a':
                a = Answer.objects.get(pk=instance_id)
        except (ValueError, ObjectDoesNotExist):
            #todo: log?
            return JsonResponse({'result': 'Wrong request data'})
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
            instance.save()
            return JsonResponse({'result': 'Success'})
        return JsonResponse({'result': 'Already voted'})


@require_GET
def tag_typeahead(request):
    value = request.GET['query']
    tag_candidates = Tag.objects.filter(tag__icontains=value).values('id', 'tag')[:7]
    result = [{"value": tc['tag'], "label": tc['tag']} for tc in tag_candidates]
    print(result)

    return JsonResponse(result, safe=False)


class HaskerLoginView(LoginView):
    # success_url = reverse_lazy('list')
    def get_context_data(self, **kwargs):
        context = super(HaskerLoginView, self).get_context_data(**kwargs)
        context['trending_object_list'] = Question.trending.all()
        return context


class SignUpView(CreateView):
    model = User
    # model = UserProfile
    # form_class = UserCreationForm
    form_class = UserProfileForm
    # fields = ['avatar']
    success_url = reverse_lazy('list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trending_object_list'] = Question.trending.all()
        return context

    # def form_valid(self, form):
    #     obj = form.save(commit=False)
    #     user = User.objects.create_user('john', 'test@test.com', 'pwd')
    #     obj.user = user
    #     obj.save()
    #     return super().form_valid(self, form)


class SettingsView(UpdateView):
    model = User
    # fields = ('email', )
    form_class = UserProfileChangeForm
    template_name = 'auth/user_edit_form.html'
    success_url = reverse_lazy('list')

    def get_object(self, queryset=None):
        current_user = self.request.user
        print('user: ', current_user)
        return current_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trending_object_list'] = Question.trending.all()
        return context

    # def form_valid(self, form):
    #     print('form valid')
    #     return super().form_valid(form)
    #
    # def form_invalid(self, form):
    #     print(form.errors)
    #     return super().form_invalid(form)


def search(request):
    return render(request, template_name='basesite/search_results.html', context={})


class QuestionSearchListView(ListView):
    model = Question
    paginate_by = 20
    template_name = 'basesite/search_results.html'
    query: str = ""

    def render_to_response(self, context, **response_kwargs):
        self.query: str = self.request.GET['q']
        print('query' + self.query)
        if self.query.strip().startswith('tag:'):
            tag = self.query.strip().split(':', maxsplit=1)[1]
            try:
                tag_slug = Tag.objects.get(tag__iexact=tag).slug
            except Tag.DoesNotExist:
                tag_slug = tag
            print('tag_slug: ', tag_slug)
            return redirect(reverse('tag-list', args=(tag_slug, )))
        return super(QuestionSearchListView, self).render_to_response(context, **response_kwargs)

    def get_ordering(self):
        ordering = self.request.GET.get('ordering', '-date_created')
        if ordering in ['-date_created', '-votes']:
            return ordering
        return '-date_created'

    def get_queryset(self):
        queryset = super(QuestionSearchListView, self).get_queryset()
        # query: str = self.request.GET['q']
        # print('query' + query)
        # if query.strip().startswith('tag:'):
        #     tag = query.strip().split(':', maxsplit=1)[1]
        #     try:
        #         tag_slug = Tag.objects.get(tag__iexact=tag).slug
        #     except Tag.DoesNotExist:
        #         tag_slug = tag
        #     print('tag_slug: ', tag_slug)
        #     return redirect(reverse('tag-list', kwargs={'slug': tag_slug}))
        queryset = queryset.filter(Q(title__icontains=self.query) | Q(message__icontains=self.query) | Q(answers__message__icontains=self.query))
        # queryset = queryset.filter(title__icontains=self.request.GET['q'])
        # queryset = queryset.filter(answers__message__icontains=self.request.GET['q'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trending_object_list'] = Question.trending.all()
        return context
