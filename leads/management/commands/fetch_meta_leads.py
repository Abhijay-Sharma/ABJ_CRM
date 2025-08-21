# leads/management/commands/fetch_meta_leads.py

import requests
from django.core.management.base import BaseCommand
from leads.models import Lead, UserProfile, Agent  # add Agent, Category if needed
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

ACCESS_TOKEN="EAASw7mrwjR4BPN2zsHPjBYAsYhobGFO0LbHKr8THC0mfAptGcMlLQblxmYet07QSFcpPC7nQLD3It44ax46CFv9VbKPbXXukjU2grVt4Ksutpr2FDhzCaIiXSwHtQ3UH0SVFOLtnvJ2W0ZCJLpgNk3k4tJgmKx5Yy9I24fqOic6LtjGZBZA0U6VpoV3MFsk90ulv5nBAuquo8LSAfbwsAl6jlclKREHDOkIG1ahY2OuBQZDZD"
FORM_ID='120227592556850482'
FORM_ID_VIDEO='120227819770820482'

class Command(BaseCommand):
    help = 'Fetch Meta leads and save to Lead model'

    def handle(self, *args, **kwargs):
        url = f'https://graph.facebook.com/v23.0/{FORM_ID}/leads'
        params = {
            'access_token': ACCESS_TOKEN,
            'fields': 'created_time,field_data',
            'limit': 1000,
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            self.stderr.write("❌ Error fetching leads")
            self.stderr.write(str(response.json()))
            return

        leads = response.json().get('data', [])
        for lead in leads:
            fb_lead_id = lead['id']

            # Parse created_time
            fb_created_time = lead.get('created_time')
            created_time = None
            if fb_created_time:
                created_time = parse_datetime(fb_created_time)
                if created_time and created_time.tzinfo is None:
                    created_time = make_aware(created_time)

            # Flatten field_data
            data = {
                field.get('name'): field.get('values', [None])[0]
                for field in lead.get('field_data', [])
                if field.get('name')
            }

            full_name = data.get('full name', '')
            first_name, last_name = '', ''
            if full_name:
                parts = full_name.strip().split()
                first_name = parts[0]
                last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

            email = data.get('email', '')
            if not email:
                print(f"Skipping {first_name} due to missing email.")
                continue

            phone_number = data.get('phone_number', '')

            # Prevent duplicates (update created_time if missing)
            existing = Lead.objects.filter(emails=email, phone_number=phone_number).first()
            if existing:
                if not existing.created_time and created_time:
                    existing.created_time = created_time
                    existing.save(update_fields=['created_time'])
                continue

            organisation = UserProfile.objects.first()
            agent = Agent.objects.first()

            Lead.objects.create(
                first_name=first_name,
                last_name=last_name,
                emails=email,
                phone_number=phone_number,
                age=0,
                description='Lead imported from Meta Lead Ad',
                organisation=organisation,
                agent=agent,
                category=None,
                created_time=created_time,  # ✅ Save FB lead time
            )

        self.stdout.write(f"✅ {len(leads)} leads processed.")
