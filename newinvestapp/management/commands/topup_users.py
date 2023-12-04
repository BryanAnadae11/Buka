from django.core.management.base import BaseCommand

from newinvestapp.models import Client

from django.conf import settings

import requests

import json

import random

from django.db.models import Count, F, Value

class Command(BaseCommand):
	help = 'Top users balance automatically'

	def handle(self, *args, **kwargs):
		print('Script to top up clients automatically')
		for client in Client.objects.annotate(pro= F('deposit') * F('roi') + F('profit')):
			client.profit= client.pro or 0
			client.save()
		client= Client.objects.all()
		for i in client:
			print(i.profit)
		print('Top up successful')

