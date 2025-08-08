# leads/management/commands/fetch_meta_leads.py

import requests
from django.core.management.base import BaseCommand
from leads.models import Lead, UserProfile, Agent  # add Agent, Category if needed
from django.utils.dateparse import parse_datetime

ACCESS_TOKEN="EAASw7mrwjR4BPOlmZCoFjwYbahCfs0381CI7MqfjqUkOpdac6rgQUjhuAbCgejG9SYAOn1GocOY1tdJCiPKWbQTd1h66WmvN0MEElEcPZBlfDdNCI7uG8EtvXNJAZCbIm1pbp5FCM31BC1Hc4AUtM8hYEZBG8whVODZB4ZApM7pUZBSaM2VN5nCZCRWUCMaLHNKCEGxddwHtcd9cEasujS2zZAeSyhXZBMyjcBwFt4pWmWiJ2gxLcZD"
FORM_ID='120227592556850482'
FORM_ID_VIDEO='120227819770820482'

class Command(BaseCommand):
    help = 'Fetch Meta leads and save to Lead model'

    def handle(self, *args, **kwargs):
        url = f'https://graph.facebook.com/v23.0/{FORM_ID}/leads'
        params = {
            'access_token': ACCESS_TOKEN,
            'fields': 'created_time,field_data',
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            self.stderr.write("❌ Error fetching leads")
            self.stderr.write(str(response.json()))
            return

        leads = response.json().get('data', [])
        for lead in leads:
            fb_lead_id = lead['id']
            data = {
                field.get('name'): field.get('values', [None])[0]
                for field in lead.get('field_data', [])
                if field.get('name')
            }
            print(data)
            full_name = data.get('full name', '')
            print(full_name)
            first_name, last_name = '', ''
            if full_name:
                parts = full_name.strip().split()
                first_name = parts[0]
                last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
            print(first_name, last_name)
            email = data.get('email', '')
            if not email:
                print(f"Skipping {first_name} due to missing email.")
                continue  # Skip this lead
            phone_number = data.get('phone_number', '')

            # Prevent duplicates (optional)
            if Lead.objects.filter(emails=email, phone_number=phone_number).exists():
                continue

            # Get default organisation (assuming single org for now)
            organisation = UserProfile.objects.first()
            agent= Agent.objects.first()

            Lead.objects.create(
                first_name=first_name,
                last_name=last_name,
                emails=email,
                phone_number=phone_number,
                age=0,
                description='Lead imported from Meta Lead Ad',
                organisation=organisation,
                agent=agent,  # or assign default agent
                category=None,  # or assign default category
            )

        self.stdout.write(f"✅ {len(leads)} leads processed.")
