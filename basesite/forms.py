from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.text import slugify

from basesite import models
from basesite.models import Tag, Answer, UserProfile


class QCF(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ['title', 'message', 'tags']

    def clean_tags(self):
        data = self.data.getlist('tags')
        if len(data) > self.Meta.model.max_tags:
            print('validation error')
            raise forms.ValidationError({'tags': f"Maximum number of tags: {self.Meta.model.max_tags}"})
        print('Data in clean_tags: ', data)
        cleaned_tags = []
        for tag in data:
            tag_object, _ = self.Meta.model.tags.field.related_model.objects.get_or_create(tag=tag.strip())
            print(tag_object)
            cleaned_tags.append(tag_object)
        return cleaned_tags

    def clean(self):
        print('in clean...')
        cleaned_data = super(QCF, self).clean()
        if 'tags' in self.errors:
            del self.errors['tags']
        cleaned_tags = self.clean_tags()
        cleaned_data['tags'] = cleaned_tags
        # print('tags', tags)
        print('errors', self.errors)
        return cleaned_data


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = models.Question
        # fields = '__all__'
        fields = ['title', 'message', 'tags']

    # def clean_tags(self):
    #     print('here')
    #     data = self.data.getlist('tags')
    #     tag_objects_new = [Tag(tag=tag) for tag in data]
    #     Tag.objects.bulk_create(tag_objects_new, ignore_conflicts=True)
    #     tag_objects_db = Tag.objects.filter(tag__in=data)
    #     return tag_objects_db

    def clean_tags(self):
        data = self.data.getlist('tags')
        if len(data) > self.Meta.model.max_tags:
            raise forms.ValidationError({'tags': f"Maximum number of tags: {self.Meta.model.max_tags}"})
        cleaned_tags = []
        for tag in data:
            tag_object, _ = self.Meta.model.tags.field.related_model.objects.get_or_create(tag=tag.strip())
            cleaned_tags.append(tag_object)
        return cleaned_tags

    def clean(self):
        cleaned_data = super(QuestionCreateForm, self).clean()
        if 'tags' in self.errors:
            del self.errors['tags']
        cleaned_tags = self.clean_tags()
        cleaned_data['tags'] = cleaned_tags
        return cleaned_data



class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['message']  # todo: lists to tuples


# class UserProfileForm(forms.ModelForm):
#     email = forms.EmailField()
#     username = forms.CharField()
#     password = forms.PasswordInput()
#     repeat_password = forms.PasswordInput()
#
#     class Meta:
#         model = UserProfile
#         fields = ['avatar']

class UserProfileForm(UserCreationForm):
    # email = forms.EmailField()
    # username = forms.CharField()
    # password = forms.PasswordInput()
    # repeat_password = forms.PasswordInput()
    avatar = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        # model = UserProfile
        fields = UserCreationForm.Meta.fields + ('email', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def save(self, commit=True):
        user = super().save()
        print('avatar', self.fields['avatar'])
        user_profile = UserProfile.objects.create(user=user, avatar=self.cleaned_data['avatar'])
        return user


class UserProfileChangeForm(UserChangeForm):
    avatar = forms.ImageField(required=False)
    clear_avatar = forms.BooleanField(required=False)

    class Meta(UserCreationForm.Meta):
        fields = ('email', 'avatar', 'clear_avatar')

    # def __init__(self, *args, **kwargs):
    #     super(UserProfileChangeForm, self).__init__(*args, **kwargs)
        # user_profile = self.initial['username']

        # self.initial['avatar'] = UserProfile.objects.get(user=self.instance).avatar
        # print(self.initial['avatar'])
    def save(self, commit=True):
        super().save()
        if self.cleaned_data['avatar']:
            up, _ = UserProfile.objects.get_or_create(user=self.instance)
            up.avatar = self.cleaned_data['avatar']
            up.save()
        if self.cleaned_data['clear_avatar']:
            up = UserProfile.objects.get(user=self.instance)
            up.avatar = None
            up.save()
        return self.instance

