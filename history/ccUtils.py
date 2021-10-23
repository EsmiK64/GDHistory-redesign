from .models import SaveFile, Level, LevelRecord, HistoryUser
from .utils import assign_key, get_data_path

import plistlib
import os
import base64
import gzip

def get_game_manager_bytes():
	game_manager_file = open(os.path.expanduser('~/testdata/gdhistory/CCGameManager_decodetest.dat'), "rb")
	game_manager_bytes = game_manager_file.read()
	game_manager_file.close()
	return bytearray(game_manager_bytes)

def xor_game_manager_if_needed(game_manager_bytes):
	game_manager_bytes = get_game_manager_bytes()
	if game_manager_bytes[:5] == b'C?xBJ':
		i = 0
		for byte in game_manager_bytes:
			game_manager_bytes[i] = byte ^ 11
			i+=1
	return game_manager_bytes

def ungzip_if_needed(game_manager_bytes):
	if game_manager_bytes[:5] == b'H4sIA':
		game_manager_bytes = base64.b64decode(game_manager_bytes, altchars='-_')
		game_manager_bytes = gzip.decompress(game_manager_bytes)

	return game_manager_bytes

def robtop_plist_to_plist(game_manager_bytes):
	game_manager_bytes = game_manager_bytes.replace(b'</d>',b'</dict>')
	game_manager_bytes = game_manager_bytes.replace(b'</k>',b'</key>')
	game_manager_bytes = game_manager_bytes.replace(b'<d>',b'<dict>')
	game_manager_bytes = game_manager_bytes.replace(b'<d />',b'<dict />')
	game_manager_bytes = game_manager_bytes.replace(b'<k>',b'<key>')
	game_manager_bytes = game_manager_bytes.replace(b'<s>',b'<string>')
	game_manager_bytes = game_manager_bytes.replace(b'</s>',b'</string>')
	game_manager_bytes = game_manager_bytes.replace(b'<i>',b'<integer>')
	game_manager_bytes = game_manager_bytes.replace(b'</i>',b'</integer>')
	game_manager_bytes = game_manager_bytes.replace(b'<t />',b'<true />')
	game_manager_bytes = game_manager_bytes.replace(b'<r>',b'<real>')
	game_manager_bytes = game_manager_bytes.replace(b'</r>',b'</real>')
	return game_manager_bytes

def remove_invalid_characters(game_manager_bytes):
	game_manager_bytes = game_manager_bytes.replace(b'&',b'@@amp@@')
	game_manager_bytes = game_manager_bytes.replace(b'#',b'@@hash@@')
	return game_manager_bytes

def load_game_manager_plist():
	gmb = get_game_manager_bytes()
	gmb = xor_game_manager_if_needed(gmb)
	gmb = ungzip_if_needed(gmb)
	gmb = robtop_plist_to_plist(gmb)
	gmb = remove_invalid_characters(gmb)
	return plistlib.loads(gmb)

def create_level_record_from_data(data, level_object, save_file):
	return LevelRecord(level=level_object, save_file=save_file,
		level_name = assign_key(data, 'k2'),
		description = assign_key(data, 'k3'),
		username = assign_key(data, 'k5'),
		user_id = assign_key(data, 'k6'),
		official_song = assign_key(data, 'k8'),
		rating = assign_key(data, 'k9'),
		rating_sum = assign_key(data, 'k10'),
		downloads = assign_key(data, 'k11'),
		level_version = assign_key(data, 'k16'),
		game_version = assign_key(data, 'k17'),
		likes = assign_key(data, 'k22'),
		length = assign_key(data, 'k23'),
		dislikes = assign_key(data, 'k24'),
		demon = assign_key(data, 'k25'),
		stars = assign_key(data, 'k26'),
		feature_score = assign_key(data, 'k27'),
		auto = assign_key(data, 'k33'),
		password = assign_key(data, 'k41'),
		two_player = assign_key(data, 'k43'),
		custom_song = assign_key(data, 'k41'),
		objects_count = assign_key(data, 'k48'),
		account_id = assign_key(data, 'k60'),
		coins = assign_key(data, 'k64'),
		coins_verified = assign_key(data, 'k65'),
		requested_stars = assign_key(data, 'k66'),
		extra_string = assign_key(data, 'k67'),
		daily_id = assign_key(data, 'k74'),
		epic = assign_key(data, 'k75'),
		demon_type = assign_key(data, 'k76'),
		seconds_spent_editing = assign_key(data, 'k80'),
		seconds_spent_editing_copies = assign_key(data, 'k81'),
		record_type = LevelRecord.RecordType.GLM
	)

def test():
	data_path = get_data_path()

	game_manager = load_game_manager_plist()
	glm_03 = game_manager['GLM_03']

	#stripping password
	game_manager['GJA_002'] = ''

	save_file = SaveFile(author=HistoryUser.objects.get(user__username='Cvolton'))
	save_file.save()

	f = open(f"{data_path}/SaveFile/{save_file.pk}", "wb")
	plistlib.dump(game_manager, f)
	f.close()

	records = []
	for level, data in glm_03.items():
		try:
			level_object = Level.objects.get(online_id=level)
		except:
			level_object = Level(online_id=level)
			level_object.save()

		record = create_level_record_from_data(data, level_object, save_file)


		if 'k4' in data:
			levelString = data['k4']
			data.pop('k4')
			record.unprocessed_data = data
			record.level_string_available = True
			record.save()
			f = open(f"{data_path}/LevelRecord/{record.pk}", "w")
			f.write(levelString)
			f.close()


		else:
			record.unprocessed_data = data
			records.append(record)

	LevelRecord.objects.bulk_create(records, ignore_conflicts=True, batch_size=1000)