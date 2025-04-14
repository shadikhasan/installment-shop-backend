from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Creates a superuser'

    def handle(self, *args, **kwargs):
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin'

        User = get_user_model()

        # Check if a superuser with this username or email already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'\nSuperuser with username "{username}" already exists.\n'))
            return
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'\nSuperuser with email "{email}" already exists.\n'))
            return

        try:
            # Create the superuser
            user = User.objects.create_superuser(username=username, email=email, password=password)

            self.stdout.write(self.style.SUCCESS('\n' + '*' * 40))
            self.stdout.write(self.style.SUCCESS(' Superuser created successfully '))
            self.stdout.write(self.style.SUCCESS('*' * 40 + '\n'))
            self.stdout.write(self.style.SUCCESS(f' {self.style.HTTP_INFO("Username:")}   {username}'))
            self.stdout.write(self.style.SUCCESS(f' {self.style.HTTP_INFO("Email:")}      {email}'))
            self.stdout.write(self.style.SUCCESS(f' {self.style.HTTP_INFO("Password:")}   {password}\n'))
            self.stdout.write(self.style.SUCCESS('*' * 40 + '\n'))
        
        except IntegrityError:
            self.stdout.write(self.style.ERROR(f'\nFailed to create superuser due to a database error.\n'))
