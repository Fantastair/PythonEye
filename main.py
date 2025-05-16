import sys
import pygame
import pygame.freetype
import pickle
from pathlib import Path

def dump(data, file):
	data = b'1' + pickle.dumps(data)[::-1] + b'1'
	with open(file, 'wb') as f:
		f.write(data)
pickle.dump = dump

def load(file):
	with open(file, 'rb') as f:
		data = f.read()[-2:0:-1]
	return pickle.loads(data)
pickle.load = load

import fantas
from fantas import uimanager

uimanager.version = '1.0.3(公测版)'
uimanager.user_data = pickle.load('user_data')
if uimanager.user_data['last_file'] is not None:
	uimanager.user_data['last_file'] = Path(uimanager.user_data['last_file'])
if uimanager.user_data['python_interpreter'] is not None:
	uimanager.user_data['python_interpreter'] = Path(uimanager.user_data['python_interpreter'])

if uimanager.user_data['auto_scale']:
	uimanager.init((1280,720))
else:
	uimanager.init((1280,720), r=1)
uimanager.load_color('res/color_table')
uimanager.load_color('res/highlight')
uimanager.load_image('res/image', False)
uimanager.load_font('res/font')
uimanager.bg = uimanager.DARKGRAY1
pygame.display.set_caption('Python Eye')
pygame.display.set_icon(uimanager.pythoneye_icon)

import face.dropfile
uimanager.root = face.dropfile.icon
if len(sys.argv) > 1:
	face.dropfile.dropboxwidget.dropfile(Path(sys.argv[1].lower()))
elif uimanager.user_data['auto_open_lastfile']:
	if uimanager.user_data['last_file'] is not None and uimanager.user_data['last_file'].is_file():
		face.dropfile.dropboxwidget.dropfile(uimanager.user_data['last_file'])
	else:
		uimanager.user_data['last_file'] = None

def quit():
	import face.popbox
	if uimanager.user_data['close_direct']:
		face.popbox.quit()
	else:
		face.popbox.open_popbox(face.popbox.ensure_quit, uimanager.root, face.popbox.ensure_quit.cancel_button)


if uimanager.user_data['auto_check_update']:
	import face.popbox
	import threading
	t = threading.Thread(target=face.popbox.get_version_in_slience)
	t.daemon = True
	t.start()

uimanager.mainloop(quit=quit)
