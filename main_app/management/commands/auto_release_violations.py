from django.core.management.base import BaseCommand
from django.utils import timezone
from main_app import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Command(BaseCommand):
    help = 'Automatically release moderate violations after 3 days'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find all moderate violations that should be auto-released
        violations_to_release = models.Violation.objects.filter(
            level='moderate',
            status='suspended',
            suspension_end_date__lte=now,
            resolved=False
        )
        
        released_count = 0
        for violation in violations_to_release:
            # Update violation status
            violation.status = 'active'
            violation.resolved = True
            violation.save(update_fields=['status', 'resolved'])
            
            # Send notification to user
            try:
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f'booking_updates_{violation.user.id}',
                        {
                            'type': 'violation_notification',
                            'violation_id': violation.id,
                            'level': violation.level,
                            'reason': violation.reason,
                            'message': f"✅ Your suspension has been automatically lifted. Your account is now active again.",
                            'status': 'active',
                            'suspension_end_date': None,
                        }
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Released violation {violation.id} for user {violation.user.username}'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️ Error sending notification for violation {violation.id}: {e}'
                    )
                )
            
            released_count += 1
        
        if released_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully released {released_count} violation(s)'
                )
            )
        else:
            self.stdout.write('No violations to release at this time.')

