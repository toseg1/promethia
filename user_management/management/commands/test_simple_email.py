# Create: user_management/management/commands/test_simple_email.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import time
import threading

class Command(BaseCommand):
    help = 'Test simple email sending'

    def add_arguments(self, parser):
        parser.add_argument('--to', type=str, required=True, help='Email to send to')
        parser.add_argument('--async', action='store_true', help='Send asynchronously')

    def handle(self, *args, **options):
        email = options['to']
        
        # Simple message
        message = f"""Hello!

This is a test email from your Promethia Training Calendar.

The simple email system is working correctly!

Best regards,
Promethia Team

Sent at: {time.strftime('%Y-%m-%d %H:%M:%S')}"""

        def send_email():
            try:
                start_time = time.time()
                
                send_mail(
                    subject="Test Email - Promethia",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                duration = time.time() - start_time
                self.stdout.write(f"✅ Email sent to {email} in {duration:.2f} seconds")
                
            except Exception as e:
                self.stdout.write(f"❌ Failed to send email: {e}")

        if options['async']:
            # Send asynchronously
            self.stdout.write(f"📧 Sending email to {email} asynchronously...")
            thread = threading.Thread(target=send_email)
            thread.daemon = True
            thread.start()
            self.stdout.write("✅ Email sending started in background")
        else:
            # Send synchronously
            self.stdout.write(f"📧 Sending email to {email} synchronously...")
            send_email()