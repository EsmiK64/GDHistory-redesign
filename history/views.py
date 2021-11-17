from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Min, Max, Q
from django.db.models.functions import Coalesce

from datetime import datetime

from .models import Level, LevelRecord, Song, SaveFile, ServerResponse, LevelString
from .forms import UploadFileForm, SearchForm
from . import ccUtils, serverUtils, tasks

def index(request):
	recently_added = LevelRecord.objects.all().prefetch_related('level').order_by('-level__pk')[:5]
	recently_updated = LevelRecord.objects.all().prefetch_related('level').order_by('-pk')[:5]

	context = {
		'recently_added': recently_added,
		'recently_updated': recently_updated,
		'level_count': Level.objects.count(),
		'song_count': Song.objects.count(),
		'save_count': SaveFile.objects.count(),
		'request_count': ServerResponse.objects.count(),
		'level_string_count': LevelString.objects.count(),
	}

	return render(request, 'index.html', context)

def view_level(request, online_id=None):
	level_records = LevelRecord.objects.filter(level__online_id=online_id).prefetch_related('level').prefetch_related('level_string').annotate(oldest_created=Min('save_file__created'), real_date=Coalesce('oldest_created', 'server_response__created')).order_by('-real_date')

	tasks.download_level_task.delay(online_id)

	if len(level_records) == 0:
		return render(request, 'error.html', {'error': 'Level not found in our database'})

	records = {}
	for record in level_records:
		if record.real_date is None:
			continue
		if record.real_date.year not in records:
			records[record.real_date.year] = []
		records[record.real_date.year].append(record)

	years = []
	for i in range(min(records), max(records)+1):
		years.append(i)

	context = {'level_records': records, 'first_record': level_records[0], 'online_id': online_id, 'years': years, 'records_count': level_records.count()}

	return render(request, 'level.html', context)

@login_required
def upload(request):
	form = UploadFileForm(request.POST or None, request.FILES or None)
	if request.method == 'POST' and form.is_valid():
		ccUtils.upload_save_file(request.FILES['file'], datetime.strptime(form.cleaned_data['time'], '%Y-%m-%d'))
		return HttpResponse("good")
	else:
		return render(request, 'upload.html')

def search(request):
	form = SearchForm(request.GET or None)

	if request.method == 'GET' and form.is_valid():
		query = form.cleaned_data['q']

		query_filter = Q(levelrecord__level_name__icontains=query) | Q(online_id=query) if query.isnumeric() else Q(levelrecord__level_name__icontains=query)

		levels = Level.objects.filter(query_filter).annotate(
			oldest_created=Max('levelrecord__save_file__created'),
			downloads=Max('levelrecord__downloads'),
			likes=Max('levelrecord__likes'),
			rating_sum=Max('levelrecord__rating_sum'),
			rating=Max('levelrecord__rating'),
			stars=Max('levelrecord__stars'),
			demon=Max('levelrecord__demon'),
			auto=Max('levelrecord__auto'),
			level_string=Max('levelrecord__level_string__pk'),
			).order_by('-oldest_created').order_by('-downloads').distinct().prefetch_related('levelrecord_set__save_file').prefetch_related('levelrecord_set__level_string')
		#level_records = LevelRecord.objects.filter(level__online_id=query).prefetch_related('level').prefetch_related('level_string').annotate(oldest_created=Min('save_file__created')).order_by('-oldest_created')

		if len(levels) < 1:
			return render(request, 'error.html', {'error': 'No results found'})

		context = {
			'query': query,
			'level_records': levels,
		}
		return render(request, 'search.html', context)
	else:
		return render(request, 'error.html', {'error': 'Invalid search query'})

def login_page_placeholder(request):
		return render(request, 'error.html', {'error': 'This feature is not available yet.'})