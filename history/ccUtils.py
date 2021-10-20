from .models import SaveFile, Level, LevelRecord, HistoryUser

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

def test():
	game_manager = load_game_manager_plist()
	glm_03 = game_manager['GLM_03']

	records = []
	for level, data in glm_03.items():
		try:
			level_object = Level.objects.get(online_id=level)
		except:
			level_object = Level(online_id=level)
			level_object.save()
		record = LevelRecord(level=level_object, unprocessed_data=data)
		records.append(record)

	LevelRecord.objects.bulk_create(records, ignore_conflicts=True, batch_size=1000)

		#print(f"{level} - {data['k2']}")
		#print(data)

	print(game_manager['GJA_002'])
	game_manager['GJA_002'] = ''
	print(game_manager['GJA_002'])

	save_file = SaveFile(author=HistoryUser.objects.get(user__username='Cvolton'))
	save_file.save()

	f = open(os.path.expanduser('~/testdata/gdhistory/CCGameManager_decodetest2.dat'), "wb")
	plistlib.dump(game_manager, f)
	f.close()