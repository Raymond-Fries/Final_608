from django.core.management.base import BaseCommand, CommandError
import  subprocess

class Command(BaseCommand):
    help = 'Concurrently runs alpaca data scripts'
    def handle(self, *args, **options):

        subprocess.Popen(args=['python3', 'manage.py', 'alpaca_data','intraday_data'])
        subprocess.Popen(args=['python3', 'manage.py', 'trade_data','transactions_data'])
        subprocess.Popen(args=['python3', 'manage.py', 'positions_data','positions_data'])
        subprocess.Popen(args=['python3', 'manage.py', 'runserver'])
