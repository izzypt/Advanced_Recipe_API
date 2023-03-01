import time
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2OperationalError
from django.db.utils import OperationalError as DjangoOperationalError


class Command(BaseCommand):
    """Django command to wait for teh database to be ready"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                # BaseCommand class includes a check() method.
                # check() verifies that required settings are set, that database connections are available, and that any other dependencies required by the command are available and correctly configured.
                # If any issues are found during the checks, the check() method raises an exception with a descriptive message explaining the issue. 
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OperationalError, DjangoOperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
