from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from veri_yonetimi.models import UserProfile

class Command(BaseCommand):
    help = 'Populate user roles based on existing permissions'

    def handle(self, *args, **options):
        # Get all users
        users = User.objects.all()
        
        updated_count = 0
        
        for user in users:
            # Get or create profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Set role based on existing permissions
            if user.is_superuser:
                profile.role = 'super_user'
            elif user.is_staff:
                # Check if user has province assignments to determine role
                if profile.sorumlu_iller:
                    profile.role = 'province_manager'
                else:
                    profile.role = 'province_admin'
            else:
                profile.role = 'viewer'
            
            profile.save()
            updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ {user.username} - {profile.get_role_display()}')
            )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'🎉 Toplam {updated_count} kullanıcıya rol ataması yapıldı!')
        )