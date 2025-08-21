from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect , reverse
from django.http import HttpResponse, JsonResponse
from .models import Lead , Agent , Category
from .forms import LeadForm , LeadModelForm , CustomUserCreationForm, AssignAgentForm , LeadCategoryUpdateForm, CategoryModelForm
from django.views.generic import TemplateView, ListView, DetailView , CreateView , UpdateView , DeleteView , FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from agents.mixins import OrganisorAndRequiredMixin
from django.db.models import Q


# Create your views here.


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse('login')

class LandingPageView(TemplateView):
    template_name = 'landing.html'


def landing_page(request):
    return render(request, 'landing.html')

class LeadListView(LoginRequiredMixin,ListView):
    template_name = 'leads/lead_list.html'

    def get_queryset(self):
        user = self.request.user
        # initial quetryset of leads for entire organisation
        if user.is_organiser:
            queryset = Lead.objects.filter(
                organisation=user.userprofile,
                agent__isnull=False
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisaton,
                agent__isnull=False
            )
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset.order_by('-created_time')

    def get_context_data(self, **kwargs):
        # now we will grab the already existing context by using the super command
        context=super(LeadListView,self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=True)# this is how we check if a foreign key is null
            context.update({           #here we will pass what we want to update in context
                "unassigned_leads": queryset
            })

        return context


def lead_list(request):
    # Get the client's IP address
    leads=Lead.objects.all()
    context={
        'leads':leads
    }
    return render(request,'leads/lead_list.html',context)

class LeadDetailView(LoginRequiredMixin,DetailView):
    template_name = 'leads/lead_detail.html'
    context_object_name = 'lead'
    def get_queryset(self):
        user=self.request.user
        #initial quetryset of leads for entire organisation
        if user.is_organiser:
            queryset=Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset=Lead.objects.filter(organisation=user.agent.organisaton)
            # filter for the agent that is logged in
            queryset=queryset.filter(agent__user=user)
        return queryset

def lead_detail(request,pk):
    lead=Lead.objects.get(id=pk)
    context={
        'lead':lead
    }
    return render(request, 'leads/lead_detail.html',context)

class LeadCreateView(OrganisorAndRequiredMixin,CreateView):
    template_name = 'leads/lead_create.html'
    form_class = LeadModelForm

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation=self.request.user.userprofile
        lead.save()
        return super(LeadCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('leads:lead-list')

def lead_create(request):

    form=LeadModelForm()
    if request.method == 'POST':
        form=LeadModelForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect("/leads")

    context={
        'form':LeadModelForm()
    }
    # print(request.POST)
    return render(request,"leads/lead_create.html",context)


class LeadUpdateView(OrganisorAndRequiredMixin,UpdateView):
    template_name = 'leads/lead_update.html'
    form_class = LeadModelForm
    def get_queryset(self):
        user=self.request.user
        return Lead.objects.filter(organisation=user.userprofile)

    def get_success_url(self):
        return reverse('leads:lead-list')

def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form=LeadModelForm(instance=lead)
    if request.method == 'POST':
        form = LeadModelForm(request.POST, instance=lead)
        print("Method is Post")
        if form.is_valid():
            form.save()
            print("form is valid")
            return redirect("/leads")
    context = {
            'lead': lead,
            'form': LeadModelForm()
        }
    return render(request, 'leads/lead_update.html',context)

class LeadDeleteView(OrganisorAndRequiredMixin,DeleteView):
    template_name = 'leads/lead_delete.html'    # so we have to create a templates which is a form asking confirmation to delete

    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)

    def get_success_url(self):
        return reverse('leads:lead-list')

def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")


class AssignAgentView(OrganisorAndRequiredMixin,FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)

class CategoryListView(LoginRequiredMixin,ListView):
    template_name = "leads/category_list.html"
    context_object_name = 'category_list'

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisaton
            )
        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count()
        })
        return context


    def get_queryset(self):
        user = self.request.user
        # initial quetryset of leads for entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(
                organisaton=user.userprofile,
            )
        else:
            queryset = Category.objects.filter(
                organisaton=user.agent.organisaton,
            )
        return queryset

class CategoryDetailView(LoginRequiredMixin,DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = 'category'

    def get_queryset(self):
        user = self.request.user

        if user.is_organiser:
            queryset = Category.objects.filter(organisaton=user.userprofile)
        else:
            queryset = Category.objects.filter(organisaton=user.agent.organisaton)
        return queryset

class CategoryCreateView(LoginRequiredMixin,CreateView):
    template_name = "leads/category_create.html"
    form_class = CategoryModelForm

    def form_valid(self, form):
        category = form.save(commit=False)
        category.organisaton=self.request.user.userprofile
        print("Hey did that ,", self.request.user.userprofile)
        category.save()
        return super(CategoryCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('leads:category-list')

class LeadCategoryUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisaton)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().id})


# def lead_update(request, pk):
#     lead = Lead.objects.get(id=pk)
#     form=LeadForm()
#     if request.method == 'POST':
#         form=LeadForm(request.POST)
#         if form.is_valid():
#             print("The form is Valid")
#             first_name=form.cleaned_data['first_name']
#             last_name=form.cleaned_data['last_name']
#             age=form.cleaned_data['age']
#             lead.first_name=first_name
#             lead.last_name=last_name
#             lead.age=age
#             lead.save()
#             return redirect("/leads")
#     context = {
#         'lead': lead,
#         'form': LeadForm()
#     }
#     return render(request, 'leads/lead_update.html',context)


# def lead_create(request):
#     form=LeadModelForm()
#     if request.method == 'POST':
#         form=LeadModelForm(request.POST)
#         if form.is_valid():
#             print("The form is Valid")
#             first_name=form.cleaned_data['first_name']
#             last_name=form.cleaned_data['last_name']
#             age=form.cleaned_data['age']
#             agent=form.cleaned_data['agent']
#             Lead.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 age=age,
#                 agent=agent
#             )
#             print("Lead Created")
#
#             return redirect("/leads")
#
#     context={
#         'form':LeadModelForm()
#     }
#     # print(request.POST)
#     return render(request,"leads/lead_create.html",context)


# Helper function to extract the IP address
def get_client_ip(request):
    # Check if behind a proxy/load balancer
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # First IP in the list
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# /search?lead=

def search_leads(request):
    lead = request.GET.get('lead')
    payload=[]
    if lead:
        lead_objs = Lead.objects.filter(
            Q(first_name__icontains=lead) | Q(last_name__icontains=lead)
        )

        for lead_obj in lead_objs:
            payload.append([lead_obj.first_name + " " + lead_obj.last_name, lead_obj.id])

    return JsonResponse({'status':200,'data':payload})