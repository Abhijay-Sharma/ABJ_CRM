from django.db import models
from django.contrib.auth.models import AbstractUser     # not using the default user this time
from django.db.models.signals import post_save

class User(AbstractUser):       # to add our custom fields later on without problem
    is_organiser=models.BooleanField(default=True)
    is_agent=models.BooleanField(default=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Lead(models.Model):
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    age=models.IntegerField(default=0)
    organisation=models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agent=models.ForeignKey('Agent',null=True,blank=True,on_delete=models.SET_NULL)   # connected to agent so each lead has 1 agent
    category=models.ForeignKey('Category',related_name='leads',null=True,blank=True,on_delete=models.SET_NULL)
    description=models.TextField()
    date_added=models.DateTimeField(auto_now_add=True)
    phone_number=models.CharField(max_length=200)
    emails=models.EmailField(max_length=254)
    # New field to store FB lead creation time
    created_time = models.DateTimeField(null=True, blank=True)
    class Meta:
        unique_together = ('emails', 'phone_number')

    def __str__(self):
        return f"{self.first_name}{self.last_name}"

class Agent(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)  # One on One Field and not Foreign Key becasue we want every user to only have one agent
    organisaton=models.ForeignKey(UserProfile,on_delete=models.CASCADE)  # if organisation profile is deleted so all agents relaated to org also deleted

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name=models.CharField(max_length=30)
    organisaton=models.ForeignKey(UserProfile,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

def post_user_created_signal(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(post_user_created_signal, sender=User)