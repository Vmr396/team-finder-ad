from django import forms

from django.core.validators import URLValidator

from django.core.exceptions import ValidationError

from .models import Project


class ProjectForm(forms.ModelForm):
    skills = forms.CharField(
        required=False,
        label='Навыки (через запятую)',
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Python, Django, React'})
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']

    def clean_github_url(self):
        """Валидация GitHub URL"""
        github_url = self.cleaned_data.get('github_url', '').strip()
        if not github_url:
            return github_url
        url_validator = URLValidator()
        try:
            url_validator(github_url)
        except ValidationError:
            raise ValidationError('Введите корректный URL')
        
        if not ('github.com' in github_url or 'www.github.com' in github_url):
            raise ValidationError('Ссылка должна вести на GitHub (github.com)')
        
        return github_url

    def save(self, commit=True):
        project = super().save(commit=commit)
        skills_text = self.cleaned_data.get('skills', '')
        if skills_text:
            from .models import Skill
            skill_names = [s.strip() for s in skills_text.split(
                ',') if s.strip()]
            for name in skill_names:
                skill, _ = Skill.objects.get_or_create(name=name)
                project.skills.add(skill)
        return project
