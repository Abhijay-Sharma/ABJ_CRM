from django.core.mail import send_mail
from django.shortcuts import render , reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from leads.models import Agent
from agents.forms import AgentModelForm
from .mixins import OrganisorAndRequiredMixin
import random
from django.core.mail import send_mail


# Create your views here.

class AgentListView(OrganisorAndRequiredMixin, generic.ListView):
    template_name = 'agents/agents_list.html'

    def get_queryset(self):
        organisation=self.request.user.userprofile
        return Agent.objects.filter(organisaton=organisation)

class AgentCreateView(OrganisorAndRequiredMixin, generic.CreateView):
    template_name = 'agents/agent_create.html'
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse('agents:agent-list')

    def form_valid(self, form):

        user = form.save(commit=False)
        user.is_agent = True
        user.is_organiser = False
        # user.set_password(random.randint(1, 1000000))
        user.save()
        Agent.objects.create(user=user, organisaton=self.request.user.userprofile)

        send_mail(
            subject="You are invited to be an agent",
            message="You are added as an agent on ABJCRM. You can login to start working",
            from_email="admin@test.com",
            recipient_list=[user.email]
        )

        return super(AgentCreateView, self).form_valid(form)

class AgentDetailView(OrganisorAndRequiredMixin, generic.DetailView):
    template_name = 'agents/agent_detail.html'
    context_object_name = 'agent'

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisaton=organisation)

class AgentUpdateView(OrganisorAndRequiredMixin, generic.UpdateView):
    template_name = 'agents/agent_update.html'
    form_class=AgentModelForm
    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisaton=organisation)

    def get_success_url(self):
        return reverse('agents:agent-list')


class AgentDeleteView(OrganisorAndRequiredMixin, generic.DeleteView):
    template_name = 'agents/agent_delete.html'
    context_object_name = 'agent'

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisaton=organisation)
    def get_success_url(self):
        return reverse('agents:agent-list')