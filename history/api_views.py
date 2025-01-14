from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Min, Max, Q
from django.db.models.functions import Coalesce
from django.core.cache import cache

from datetime import datetime

from .models import LevelRecord, LevelDateEstimation
from . import ccUtils, serverUtils, tasks, utils, constants

import math
import plistlib

def index_counts(request):
	counts = cache.get('counts')
	if counts is None:
		counts = utils.recalculate_counts()

	return JsonResponse(counts)

def save_level(request, online_id=None):
	level = utils.get_level_object(online_id)
	if level.needs_priority_download: return JsonResponse({'success': False, 'fail_reason': constants.SaveFailReasons.ALREADY_QUEUED})

	level.needs_priority_download = True
	level.save()

	return JsonResponse({'success': True})

def level_info(request, online_id=None):
	all_levels = LevelRecord.objects.filter(level__is_public=True)
	#TODO: improve this
	if request.user.is_authenticated and request.user.is_superuser:
		all_levels = LevelRecord.objects.all()

	level_records = all_levels.filter(level__online_id=online_id).exclude(level_version=None).prefetch_related('level').prefetch_related('level_string').prefetch_related('real_user_record__user').prefetch_related('song').annotate(oldest_created=Min('save_file__created'), real_date=Coalesce('oldest_created', 'server_response__created', 'manual_submission__created')).order_by('-real_date')
	level = level_records[0].level

	response = level.get_serialized_base()

	level_strings = {}
	response['level_string_count'] = 0
	response['records'] = []
	for record in level_records:
		response['records'].append(record.get_serialized_full())

		if record.level_string is not None and record.level_string.pk not in level_strings:
			response['level_string_count'] += 1
			level_strings[record.level_string.pk] = True

	if len(response['records']) == 0:
		utils.get_level_object(online_id)
		return render(request, 'error.html', {'error': 'Level not found in our database'})

	return JsonResponse(response)

def level_date_estimation(request, online_id):
	low = LevelDateEstimation.objects.prefetch_related('level').filter(cache_online_id__lte=online_id).order_by('-cache_online_id', 'estimation')[:1]
	high = LevelDateEstimation.objects.prefetch_related('level').filter(cache_online_id__gte=online_id).order_by('cache_online_id', 'estimation')[:1]

	response = {
		'low': low[0].get_serialized_base() if len(low) > 0 else None,
		'high': high[0].get_serialized_base()  if len(high) > 0 else None
	}
	
	return JsonResponse(response)