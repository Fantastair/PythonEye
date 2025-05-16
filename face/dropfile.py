import pygame
from tkinter.filedialog import askopenfilename
from pathlib import Path

import fantas
from fantas import uimanager
import prestyle
import face.debugboard
import face.popbox


class DropBoxWidget(fantas.AnyButton):
	__slots__ = []

	def handle(self, event):
		if event.type == pygame.DROPFILE:
			if self.dropfile(Path(event.file.lower())):
				self.cancel_event()
		else:
			super().handle(event)

	def dropfile(self, file=None):
		if file is None and uimanager.user_data['last_file'] is not None and uimanager.user_data['last_file'].is_file():
			return self.dropfile(uimanager.user_data['last_file'])
		elif file.suffix == '.py':
			uimanager.user_data['last_file'] = file
			pygame.display.set_caption(f'{file} - Python Eye')
			uimanager.root = face.debugboard.menubar
			face.debugboard.openfile(file)
			return True
		elif file.suffix == '.eye':
			uimanager.root = face.debugboard.menubar
			face.debugboard.export_eye(file)
		else:
			return False

	def openfile(self):
		file = askopenfilename(title='Python Eye 选择文件', filetypes=(('Python Eye', '*.py *.eye'),), multiple=False)
		if file:
			self.dropfile(Path(file.lower()))


class ShortCutKey(fantas.KeyboardBase):
	__slots__ = []

	def keyboardpress(self, key, shortcut):
		if shortcut == 'Ctrl+O':
			dropboxwidget.openfile()


r = uimanager.r

icon = pygame.transform.smoothscale(uimanager.pythoneye_icon, (150*r,150*r))
icon = fantas.Ui(icon, center=(640*r,250*r))

img = pygame.Surface((800*r, 500*r), flags=pygame.HWSURFACE | pygame.SRCALPHA)
w, h = img.get_size()
w //= 2
h //= 2
with pygame.PixelArray(img) as pixarray:
	pixarray[int(w-10*r):int(w+10*r), h:int(h+100*r)] = uimanager.FAKEWHITE
	pixarray[int(w-50*r):int(w+50*r), int(h+40*r):int(h+60*r)] = uimanager.FAKEWHITE
	pixarray[:3] = uimanager.FAKEWHITE
	pixarray[-3:] = uimanager.FAKEWHITE
	pixarray[:, :3] = uimanager.FAKEWHITE
	pixarray[:, -3:] = uimanager.FAKEWHITE
dropbox = fantas.Ui(img, center=(640*r,360*r))
dropbox.join(icon)
dropboxwidget = DropBoxWidget(dropbox)
dropboxwidget.apply_event()
dropboxwidget.bind(dropboxwidget.openfile)
shortcutkey = ShortCutKey(dropbox)
shortcutkey.apply_event()

fantas.Text('拖入你的代码或选择文件', uimanager.simhei, prestyle.dropfile, center=(400*r,400*r)).join(dropbox)
