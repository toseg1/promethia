from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Create superuser from environment variables'

    def handle(self, *args, **options):
        # Get credentials from environment variables
        username = os.environ.get('ADMIN_USERNAME')
        email = os.environ.get('ADMIN_EMAIL') 
        password = os.environ.get('ADMIN_PASSWORD')
        
        # Only create if all environment variables are set
        if not all([username, email, password]):
            self.stdout.write('Admin credentials not found in environment variables')
            return
            
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(f'Superuser {username} created successfully')
        else:
            self.stdout.write(f'Superuser {username} already exists')
