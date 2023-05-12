from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.template.defaultfilters import truncatechars
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

User._meta.get_field('email')._unique = True


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar image')

    # date_joined as registration date, username as nickname

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #
    #     if self.avatar:
    #         with Image.open(self.avatar.path) as img:
    #             img.thumbnail((200, 200))
    #             # Save the resized image back to the same location
    #             img.save(self.avatar.path, format=img.format)


class Message(models.Model):
    message = models.TextField(verbose_name="Message text",
                               validators=[
                                   MinLengthValidator(5, 'Message is expected to contain at least 5 characters')
                               ])
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    date_created = models.DateTimeField(verbose_name='Date of creation', default=timezone.now)
    votes = models.IntegerField(verbose_name="Number of votes for the Q", default=0)

    class Meta:
        abstract = True


class Tag(models.Model):
    tag = models.CharField(verbose_name='Tag text', max_length=64, unique=True)
    slug = models.SlugField(default="")

    def save(self, *args, **kwargs):
        """Alter save to create slug, omitting non-ascii symbols, altering with counter to prevent duplicates"""
        self.slug = slugify(self.tag)
        base_slug, n = self.slug, 0
        while Tag.objects.filter(slug=self.slug).exists():
            n += 1
            self.slug = f"{base_slug}{n}"
        return super(Tag, self).save(*args, **kwargs)


class TrendingQuestionManager(models.Manager):
    def get_queryset(self):
        return super(TrendingQuestionManager, self).get_queryset().order_by('-votes')[:20]


class Question(Message):
    title = models.CharField(verbose_name='Title text', max_length=150, blank=False,
                             validators=[
                                 MinLengthValidator(5, 'Title is expected to contain at least 5 characters')
                             ])
    tags = models.ManyToManyField('Tag', blank=True)  # todo: validate max 3 choices, how?
    voted_by = models.ManyToManyField('auth.User', blank=True, related_name='voted_questions',
                                      through='QuestionVotedBy')

    max_tags = 1

    objects = models.Manager()
    trending = TrendingQuestionManager()

    def get_absolute_url(self):
        return reverse("question-detail", kwargs={"pk": self.pk})


# def tags_changed(sender, **kwargs):
#     instance = kwargs['instance']
#     if len(instance.tags.all()) >= instance.max_tags :
#         raise ValidationError(f'Max number of records is {instance.max_tags}')
#
#
# m2m_changed.connect(tags_changed, sender=Question.tags.through)


class QuestionVotedBy(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    vote = models.SmallIntegerField(default=0)


class Answer(Message):
    question = models.ForeignKey('Question', related_name='answers', on_delete=models.CASCADE)
    correct = models.BooleanField(verbose_name='Correct answer flag')
    voted_by = models.ManyToManyField('auth.User', blank=True, related_name='voted_answers', through='AnswerVotedBy')


class AnswerVotedBy(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)
    vote = models.SmallIntegerField(default=0)


@receiver(post_save, sender=Answer)
def notify_question_author_on_answer(**kwargs):
    obj = kwargs['instance']
    domain = Site.objects.get_current().domain
    message = render_to_string(template_name='basesite/answer_email.txt', context={
        'domain': domain,
        'answer': obj
    })
    send_mail(
        f"New answer: {truncatechars(obj.question.title, 15)}",
        message,
        'test@test.com',
        [obj.question.author.email]
    )
