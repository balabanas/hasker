from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from basesite import models
from basesite.models import Answer, UserProfile


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = models.Question
        fields = ('title', 'message', 'tags', )

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
        fields = ('message', )


class UserProfileForm(UserCreationForm):
    avatar = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        email_value = self.cleaned_data.get('email')
        if email_value:
            if UserProfile.objects.filter(email=email_value).exists():
                raise forms.ValidationError("User with this email is already registered.")
        return email_value

    def save(self, commit=True):
        user = super().save()
        UserProfile.objects.create(user=user, email=self.cleaned_data['email'], avatar=self.cleaned_data['avatar'])
        return user


class UserProfileChangeForm(UserChangeForm):
    avatar = forms.ImageField(required=False)
    email = forms.EmailField(required=True)
    clear_avatar = forms.BooleanField(required=False)

    class Meta(UserCreationForm.Meta):
        fields = ('email', 'avatar', 'clear_avatar', )

    def clean_email(self):
        email_value = self.cleaned_data.get('email')
        if email_value:
            if UserProfile.objects.filter(email=email_value).exclude(user=self.instance).exists():
                raise forms.ValidationError("The email specified belongs to another user.")
        return email_value

    def save(self, commit=True):
        super().save()
        up, _ = UserProfile.objects.get_or_create(user=self.instance)
        if self.cleaned_data['avatar']:
            up.avatar = self.cleaned_data['avatar']
        if self.cleaned_data['clear_avatar']:
            up.avatar = None
        if self.cleaned_data['email']:
            up.email = self.cleaned_data['email']
        up.save()
        return self.instance
