from django import forms
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

    def save(self, commit=True):
        project = super().save(commit=commit)
        skills_text = self.cleaned_data.get('skills', '')
        if skills_text:
            from .models import Skill
            skill_names = [s.strip(

            ) for s in skills_text.split(',') if s.strip()]
            for name in skill_names:
                skill, _ = Skill.objects.get_or_create(name=name)
                project.skills.add(skill)
        return project
