import history.serverUtils

import os
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	help = 'Adds save files from a pre-defined directory'

	def handle(self, *args, **options):
		history.serverUtils.get_first_level_pages(11, 10)