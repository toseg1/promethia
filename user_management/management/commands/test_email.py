
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
            required=True
        )

    def handle(self, *args, **options):
        to_email = options['to']
        
        try:
            # Get superuser info
            superusers = User.objects.filter(is_superuser=True)
            if superusers.exists():
                superuser = superusers.first()
                from_name = f"{superuser.first_name} {superuser.last_name}".strip() or superuser.username
            else:
                from_name = "Promethia Admin"
                self.stdout.write(
                    self.style.WARNING('No superuser found. Create one with: python manage.py createsuperuser')
                )

            subject = 'Test Email from Promethia Training Calendar'
            message = f"""
Hello!

This is a test email from your Promethia Training Calendar application.

Email sent from: {from_name}
Django settings configured email: {settings.EMAIL_HOST_USER}
Server time: {settings.TIME_ZONE}

If you receive this email, your email configuration is working correctly!

Best regards,
The Promethia Team
            """

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent test email to {to_email}')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            )

            # Common troubleshooting suggestions
            self.stdout.write(
                self.style.WARNING('\nTroubleshooting tips:')
            )
            self.stdout.write('1. Check your Gmail App Password is correct')
            self.stdout.write('2. Make sure 2-Factor Authentication is enabled on Gmail')
            self.stdout.write('3. Verify the recipient email address is valid')
            self.stdout.write('4. Check your internet connection')
            self.stdout.write('5. Ensure Gmail allows "Less secure app access" or use App Passwords')