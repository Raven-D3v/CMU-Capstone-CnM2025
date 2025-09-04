from django.apps import AppConfig
from django.core.management import call_command
import threading
import time


class OnetapsosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'onetapsos'

    def ready(self):
        """Run cleanup tasks daily in the background"""
        from django.conf import settings

        def scheduler():
            while True:
                # Run your existing report cleanup
                call_command("cleanup_report")

                # Run your notification cleanup
                call_command("cleanup_notifications")

                # Wait 24 hours (86400 seconds)
                time.sleep(86400)

        # Run scheduler in a background thread (so Django can still serve requests)
        thread = threading.Thread(target=scheduler, daemon=True)
        thread.start()
