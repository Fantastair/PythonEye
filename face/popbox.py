import re
import pickle
import pygame
import pygame.freetype
import requests
import threading
import webbrowser
from pathlib import Path

import fantas
from fantas import uimanager
import face.debugboard
import prestyle

r = uimanager.r


def open_popbox(box, father, *reset):
	box.join(father)
	box.set_greedy()
	for ui in reset:
		if isinstance(ui, fantas.InputLine):
			ui.clear()
			if ui.inputwidget.inputing:
				pygame.key.set_repeat(300, 50)
		else:
			if ui.bg == ui.colors['hover_bg']:
				ui.mousewidget.mouseout()

def close_popbox(box, *reset):
	box.leave()
	box.unset_greedy()
	for i in reset:
		if i.inputwidget.inputing:
			i.inputwidget.stop_input()
			i.mousewidget.mouseout()
			pygame.key.set_repeat()


hovermessagebox = fantas.HoverMessageBox(3, 30, uimanager.simhei, prestyle.hovermessage_text, bd=1, bg=uimanager.FAKEWHITE, sc=uimanager.DARKGRAY2)


def reopen(encoding):
	reopen_with.reopen_with(encoding)
	close_popbox(reopen_with)

reopen_with = fantas.ChildBox(True, (200,210), bg=uimanager.DARKBLUE1, bd=2, sc=uimanager.DARKBLUE2, center=(uimanager.size[0]/2,uimanager.size[1]/2))
reopen_with.bar = fantas.Label((reopen_with.origin_size[0]-4,40), bg=uimanager.DARKBLUE4, topleft=(2,2))
reopen_with.bar.join(reopen_with)
reopen_with.icon = fantas.Ui(uimanager.pythoneye_icon, center=(20,20))
reopen_with.icon.size = (30,30)
reopen_with.icon.join(reopen_with.bar)
fantas.Text('选择编码方式', uimanager.simhei, prestyle.popbox_text, midleft=(40,20)).join(reopen_with.bar)
reopen_with.close_button = fantas.ColorButton((36,36), prestyle.popbox_closebutton, midright=(reopen_with.origin_size[0]-6,20))
reopen_with.close_button.join(reopen_with.bar)
reopen_with.close_button.bind(close_popbox, reopen_with)
reopen_with.close_button.bind_shortcut('Escape')
fantas.Text('×', uimanager.simhei, prestyle.popbox_text, center=(18,18)).join(reopen_with.close_button)
reopen_with.choose_buttons = (
	fantas.ColorButton((180,30), prestyle.popbox_button, midtop=(100,50)),
	fantas.ColorButton((180,30), prestyle.popbox_button, midtop=(100,90)),
	fantas.ColorButton((180,30), prestyle.popbox_button, midtop=(100,130)),
	fantas.ColorButton((180,30), prestyle.popbox_button, midtop=(100,170)),
	)
for b, t in zip(reopen_with.choose_buttons,('utf-8','gbk','ascii','gb2312')):
	b.join(reopen_with)
	fantas.Text(t, uimanager.simhei, prestyle.popbox_text, center=(90,15)).join(b)
	b.bind(reopen, t)


about_pythoneye = fantas.ChildBox(True, (400,400), bg=uimanager.DARKBLUE1, bd=2, sc=uimanager.DARKBLUE2, center=(uimanager.size[0]/2,uimanager.size[1]/2))
about_pythoneye.bar = fantas.Label((about_pythoneye.origin_size[0]-4,40), bg=uimanager.DARKBLUE4, topleft=(2,2))
about_pythoneye.bar.join(about_pythoneye)
fantas.Text('Python Eye', uimanager.jb_mono, prestyle.popbox_text, midleft=(50,20)).join(about_pythoneye.bar)
about_pythoneye.close_button = fantas.ColorButton((36,36), prestyle.popbox_closebutton, midright=(about_pythoneye.origin_size[0]-6,20))
about_pythoneye.close_button.join(about_pythoneye.bar)
about_pythoneye.close_button.bind(close_popbox, about_pythoneye)
about_pythoneye.close_button.bind_shortcut('Escape')
fantas.Text('×', uimanager.simhei, prestyle.popbox_text, center=(18,18)).join(about_pythoneye.close_button)
about_pythoneye.icon = fantas.Ui(uimanager.pythoneye_icon, center=(20,20))
about_pythoneye.icon.size = (30,30)
about_pythoneye.icon.join(about_pythoneye.bar)
fantas.Label((220,25), bg=uimanager.PURPLE, center=(200,88)).join(about_pythoneye)
prestyle.popbox_text['size'] = 34
prestyle.popbox_text['fgcolor'] = uimanager.FAKEWHITE
fantas.Text('Python Eye', uimanager.jb_mono, prestyle.popbox_text, center=(200,80)).join(about_pythoneye)
prestyle.popbox_text['size'] = 18
prestyle.popbox_text['fgcolor'] = uimanager.DARKBLUE3
link_text_style = dict(prestyle.popbox_text)
link_text_style['style'] = pygame.freetype.STYLE_OBLIQUE
about_pythoneye.blog = fantas.WebURL('·官方博客：CSDN', 'https://blog.csdn.net/2301_79102953/article/details/132386562', uimanager.simhei, link_text_style, center=(200,140))
about_pythoneye.blog.join(about_pythoneye)
fantas.HoverMessage(about_pythoneye.blog, 'https://blog.csdn.net/...', hovermessagebox).apply_event()
about_pythoneye.store = fantas.WebURL('·软件发布：蓝奏云', 'https://fantastair.lanzout.com/b03qfxm6b', uimanager.simhei, link_text_style, center=(200,170))
about_pythoneye.store.join(about_pythoneye)
fantas.HoverMessage(about_pythoneye.store, 'https://fantastair.lanzout.com/...', hovermessagebox).apply_event()
fantas.Text('网盘访问密码：pythoneye', uimanager.simhei, prestyle.popbox_text, center=(200,200)).join(about_pythoneye)
fantas.Text(f'当前版本：{uimanager.version}', uimanager.simhei, prestyle.popbox_text, center=(200,240)).join(about_pythoneye)
fantas.Text('*** ====================== ***', uimanager.jb_mono, prestyle.popbox_text, center=(200,270)).join(about_pythoneye)
fantas.Text('python', uimanager.simhei, prestyle.popbox_text, midright=(190,305)).join(about_pythoneye)
fantas.Text('3.11.5', uimanager.simhei, prestyle.popbox_text, midleft=(210,305)).join(about_pythoneye)
fantas.Text('pygame', uimanager.simhei, prestyle.popbox_text, midright=(190,340)).join(about_pythoneye)
fantas.Text('2.5.2', uimanager.simhei, prestyle.popbox_text, midleft=(210,340)).join(about_pythoneye)
fantas.Text('requests', uimanager.simhei, prestyle.popbox_text, midright=(190,360)).join(about_pythoneye)
fantas.Text('2.31.0', uimanager.simhei, prestyle.popbox_text, midleft=(210,360)).join(about_pythoneye)
link_text_style1 = dict(link_text_style)
link_text_style1['size'] = 12
fantas.Text(f'written by Fantastair @2023', uimanager.jb_mono, link_text_style1, bottomright=(396,396)).join(about_pythoneye)
# fantas.WebURL(f'written by Fantastair @2023', 'https://blog.csdn.net/2301_79102953/article/details/132644935', uimanager.jb_mono, link_text_style1, bottomright=(396,396)).join(about_pythoneye)


class MessageBox(fantas.MessageBox):
	__slots__ = ['alpha_in', 'alpha_out', 'move_in', 'move_out', 'fixed_button', 'fixed', 'autofix']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.alpha_in = fantas.UiKeyFrame(self, 'alpha', 200, 10, uimanager.slower_curve)
		self.alpha_in.bind_endupwith(self.timer.launch)
		self.alpha_out = fantas.UiKeyFrame(self, 'alpha', 0, 20, uimanager.slower_curve)
		self.alpha_out.bind_endupwith(self.leave)
		self.timer.bind_endupwith(self.hide)
		self.move_in = fantas.RectKeyFrame(self, 'top', self.rect.top-30, 10, uimanager.slower_curve)
		self.move_in.bind_endupwith(self.auto_fix)
		self.move_out = fantas.RectKeyFrame(self, 'top', self.rect.top, 20, uimanager.slower_curve)
		self.fixed_button = fantas.ColorButton((self.text.origin_size[1]+self.pad/2,self.text.origin_size[1]+self.pad/2), prestyle.message_button, midleft=(self.origin_size[0]-self.origin_size[1],self.text.rect.height/2+self.pad))
		self.fixed_button.join(self)
		self.fixed_button.bind(self.fix)
		i = fantas.Ui(uimanager.fixed_button, center=(self.fixed_button.origin_size[0]/2,self.fixed_button.origin_size[1]/2))
		i.size = (self.fixed_button.origin_size[0]*0.8,self.fixed_button.origin_size[1]*0.8)
		i.apply_size()
		i.join(self.fixed_button)
		self.set_layout(self.fixed_button, ('fx', 'right', -self.pad*0.75))
		self.fixed = False
		self.autofix = False

	def fix(self):
		if not self.move_out.is_launched() and not self.move_in.is_launched():
			self.fixed = True
			self.fixed_button.colors['origin_bg'] = self.fixed_button.colors['hover_bg'] = self.fixed_button.colors['press_bg'] = self.fixed_button.colors['fixed']
			self.fixed_button.mousewidget.set_color('origin')
			self.fixed_button.bind(self.unfix)

	def unfix(self):
		self.fixed = False
		self.fixed_button.colors['origin_bg'] = self.fixed_button.colors['hover_bg'] = self.fixed_button.colors['press_bg'] = self.fixed_button.colors['unfixed']
		self.fixed_button.mousewidget.set_color('origin')
		self.fixed_button.bind(self.fix)
		self.timer.launch()

	def auto_fix(self):
		if self.autofix:
			self.fix()

	def load_message(self, message, force=False):
		if self.text.text != message or force:
			self.text.text = message
			self.text.update_img()
			self.set_size((self.text.rect.w+self.pad*3+self.fixed_button.size[0], self.text.rect.h+self.pad*2))

	def show(self, target=None):
		self.autofix = False
		if not self.fixed:
			if target is None:
				target = uimanager.root
			self.join(target)
			if self.alpha_out.is_launched():
				self.alpha_out.stop()
				self.move_out.stop()
				self.timer.stop()
			self.alpha_in.launch(flag='continue')
			self.move_in.launch(flag='continue')

	def hide(self):
		if not self.fixed:
			if self.alpha_in.is_launched():
				self.alpha_out.stop()
				self.move_out.stop()
				self.timer.stop()
			else:
				self.alpha_out.launch(flag='continue')
				self.move_out.launch(flag='continue')

messagebox = MessageBox(10, 60, uimanager.deyi, prestyle.message_text, bd=2, bg=uimanager.DARKBLUE3, sc=uimanager.FAKEWHITE, center=(640*r,600*r))


def quit():
	import sys
	import face.debugboard
	if uimanager.user_data['last_file'] is not None:
		uimanager.user_data['last_file'] = str(uimanager.user_data['last_file'])
	if uimanager.user_data['python_interpreter'] is not None:
		uimanager.user_data['python_interpreter'] = str(uimanager.user_data['python_interpreter'])
	pickle.dump(uimanager.user_data, 'user_data')
	for f in Path('temp').iterdir():
		f.unlink()
	if face.debugboard.actionbar.started:
		face.debugboard.actionbar.end_debugger()
	pygame.quit()
	sys.exit()

ensure_quit = fantas.ChildBox(True, (200,100), bg=uimanager.DARKBLUE1, bd=2, sc=uimanager.DARKBLUE2, center=(uimanager.size[0]/2,uimanager.size[1]/2))
ensure_quit.icon = fantas.Ui(uimanager.pythoneye_icon, center=(30,30))
ensure_quit.icon.size = (30,30)
ensure_quit.icon.join(ensure_quit)
prestyle.popbox_text['size'] = 24
fantas.Text('确定要退出？', uimanager.simhei, prestyle.popbox_text, center=(120,30)).join(ensure_quit)
prestyle.popbox_text['size'] = 18
s = dict(prestyle.popbox_button)
s['hover_bg'] = uimanager.RED
s['press_bg'] = uimanager.DARKRED
ensure_quit.ensure_button = fantas.ColorButton((90,30), s, midright=(100,75))
ensure_quit.ensure_button.join(ensure_quit)
ensure_quit.ensure_button.bind(quit)
ensure_quit.ensure_button.bind_shortcut('Return')
fantas.Text('确定', uimanager.simhei, prestyle.popbox_text, center=(45,15)).join(ensure_quit.ensure_button)
ensure_quit.cancel_button = fantas.ColorButton((90,30), prestyle.popbox_button, midleft=(100,75))
ensure_quit.cancel_button.join(ensure_quit)
ensure_quit.cancel_button.bind(close_popbox, ensure_quit)
ensure_quit.cancel_button.bind_shortcut('Escape')
fantas.Text('取消', uimanager.simhei, prestyle.popbox_text, center=(45,15)).join(ensure_quit.cancel_button)


def ensure_run():
	line = run_until.input_linenumber.get_input()
	if line.isdigit():
		close_popbox(run_until)
		run_until.input_linenumber.clear()
		face.debugboard.actionbar.run_until(line)
	else:
		messagebox.load_message('非法行号！')
		messagebox.show()

run_until = fantas.ChildBox(True, (280,104), bg=uimanager.DARKBLUE1, bd=2, sc=uimanager.DARKBLUE2, center=(uimanager.size[0]/2,uimanager.size[1]/2))
run_until.bar = fantas.Label((run_until.origin_size[0]-4,40), bg=uimanager.DARKBLUE4, topleft=(2,2))
run_until.bar.join(run_until)
run_until.icon = fantas.Ui(uimanager.pythoneye_icon, center=(20,20))
run_until.icon.size = (30,30)
run_until.icon.join(run_until.bar)
fantas.Text('运行直到大于等于...', uimanager.simhei, prestyle.popbox_text, topleft=(50,12)).join(run_until.bar)
run_until.close_button = fantas.ColorButton((36,36), prestyle.popbox_closebutton, midright=(run_until.origin_size[0]-6,20))
run_until.close_button.join(run_until.bar)
run_until.close_button.bind_shortcut('Escape')
fantas.Text('×', uimanager.simhei, prestyle.popbox_text, center=(18,18)).join(run_until.close_button)
run_until.input_linenumber = fantas.InputLine((180,40), uimanager.simhei, prestyle.popbox_inputline, prestyle.popbox_text, '输入行号...', maxinput=6, bg=uimanager.DARKBLUE2, bd=2, sc=uimanager.DARKBLUE3, topleft=(10,52))
run_until.input_linenumber.join(run_until)
run_until.ensure_button = fantas.ColorButton((70,40), prestyle.popbox_button, topleft=(200,52))
run_until.ensure_button.bind(ensure_run)
run_until.ensure_button.bind_shortcut('Return')
run_until.ensure_button.join(run_until)
fantas.Text('确定', uimanager.simhei, prestyle.popbox_text, center=(35,20)).join(run_until.ensure_button)
run_until.close_button.bind(close_popbox, run_until, run_until.input_linenumber)


def check_update():
	open_popbox(check_update_box, uimanager.root, check_update_box.close_button)
	if check_update_box.pythoneye.father is check_update_box:
		check_update_box.pythoneye.leave()
		check_update_box.current_version.leave()
		check_update_box.newest_version.leave()
		check_update_box.download_button.leave()
	elif check_update_box.internet_error.father is check_update_box:
		check_update_box.internet_error.leave()
	up_move_up.launch(start=150)
	bottom_move_down.launch(start=130)
	up_alpha_in.launch(start=0)
	bottom_alpha_in.launch(start=0)
	mid_alpha_in.launch(start=0)
	messagebox.load_message('正在获取最新版本信息...')
	messagebox.show()
	t = threading.Thread(target=get_version)
	t.daemon = True
	t.start()

version_url = 'https://blog.csdn.net/2301_79102953/article/details/131678078'
head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42"}
version_obj = re.compile(r'<p>&lt;Windows版本信息&#xff1a;Version (?P<version>.*?)&gt;</p>')

def get_version():
	try:
		resp = requests.get(version_url, headers=head)
		version = version_obj.search(resp.text).group('version')
		check_update_box.newest_version.text = f'最新版本：{version}'
		check_update_box.newest_version.update_img()
		check_update_box.pythoneye.join(check_update_box)
		check_update_box.current_version.join(check_update_box)
		check_update_box.newest_version.join(check_update_box)
		check_update_box.download_button.join(check_update_box)
		if check_update_box.download_button.is_banned:
			check_update_box.download_button.recover()
		if version == uimanager.version:
			messagebox.load_message('你的Python Eye已是最新版本！')
			if not check_update_box.download_button.is_banned:
				check_update_box.download_button.ban()
		else:
			messagebox.load_message('有新版本可以更新！')
		messagebox.show()
	except requests.exceptions.ConnectionError:
		check_update_box.internet_error.join(check_update_box)
	stop_check()

def get_version_in_slience():
	try:
		resp = requests.get(version_url, headers=head)
		version = version_obj.search(resp.text).group('version')
		if version != uimanager.version:
			messagebox.load_message('有新版本可以更新！')
			messagebox.show()
		elif not uimanager.user_data['show_check_result']:
			messagebox.load_message('你的Python Eye已是最新版本！')
			messagebox.show()
	except requests.exceptions.ConnectionError:
		check_update_box.internet_error.join(check_update_box)

def stop_check():
	up_alpha_out.launch('continue')
	mid_alpha_out.launch('continue')
	bottom_alpha_out.launch('continue')
	mid_rotate.stop()
	if up_move_up.is_launched():
		up_move_up.stop()
		bottom_move_down.stop()
		up_alpha_in.stop()
		mid_alpha_in.stop()
		bottom_alpha_in.stop()

check_update_box = fantas.ChildBox(True, (320,240), bg=uimanager.DARKBLUE1, bd=2, sc=uimanager.DARKBLUE2, center=(uimanager.size[0]/2,uimanager.size[1]/2))
check_update_box.bar = fantas.Label((check_update_box.origin_size[0]-4,40), bg=uimanager.DARKBLUE4, topleft=(2,2))
check_update_box.bar.join(check_update_box)
check_update_box.icon = fantas.Ui(uimanager.pythoneye_icon, center=(20,20))
check_update_box.icon.size = (30,30)
check_update_box.icon.join(check_update_box.bar)
fantas.Text('检查更新', uimanager.simhei, prestyle.popbox_text, topleft=(50,12)).join(check_update_box.bar)
check_update_box.close_button = fantas.ColorButton((36,36), prestyle.popbox_closebutton, midright=(check_update_box.origin_size[0]-6,20))
check_update_box.close_button.join(check_update_box.bar)
check_update_box.close_button.bind(close_popbox, check_update_box)
check_update_box.close_button.bind_shortcut('Escape')
fantas.Text('×', uimanager.simhei, prestyle.popbox_text, center=(18,18)).join(check_update_box.close_button)
up = fantas.Ui(uimanager.pythoneye_part_up, center=(160,150))
up.join(check_update_box)
mid = fantas.Ui(uimanager.pythoneye_part_mid, center=(160,140))
mid.join(check_update_box)
bottom = fantas.Ui(uimanager.pythoneye_part_bottom, center=(160,130))
bottom.join(check_update_box)
up_move_up = fantas.RectKeyFrame(up, 'centery', -10, 15, uimanager.slower_curve, absolute=False)
bottom_move_down = fantas.RectKeyFrame(bottom, 'centery', 10, 15, uimanager.slower_curve, absolute=False)
up_alpha_in = fantas.UiKeyFrame(up, 'alpha', 255, 15, uimanager.slower_curve)
bottom_alpha_in = fantas.UiKeyFrame(bottom, 'alpha', 255, 15, uimanager.slower_curve)
mid_alpha_in = fantas.UiKeyFrame(mid, 'alpha', 255, 15, uimanager.slower_curve)
mid_rotate = fantas.UiKeyFrame(mid, 'angle', -360, 40, uimanager.harmonic_curve)
mid_alpha_in.bind_endupwith(mid_rotate.launch, start=0)
mid_rotate.bind_endupwith(mid_rotate.launch, start=0)
up_alpha_out = fantas.UiKeyFrame(up, 'alpha', 0, 20, uimanager.slower_curve)
mid_alpha_out = fantas.UiKeyFrame(mid, 'alpha', 0, 20, uimanager.slower_curve)
bottom_alpha_out = fantas.UiKeyFrame(bottom, 'alpha', 0, 20, uimanager.slower_curve)
prestyle.popbox_text['size'] = 32
check_update_box.pythoneye = fantas.Text('Python Eye', uimanager.jb_mono, prestyle.popbox_text, center=(160,80))
prestyle.popbox_text['size'] = 18
check_update_box.current_version = fantas.Text(f'当前版本：{uimanager.version}', uimanager.simhei, prestyle.popbox_text, center=(160,120))
check_update_box.newest_version = fantas.Text('最新版本：', uimanager.simhei, prestyle.popbox_text, center=(160,150))
check_update_box.internet_error = fantas.Text('无法获取更新，请检查你的网络连接！', uimanager.simhei, prestyle.popbox_text, center=(160,135))
check_update_box.download_button = fantas.ColorButton((280,40), prestyle.popbox_button, center=(160,200))
fantas.Text('前往下载(网盘密码：pythoneye)', uimanager.simhei, prestyle.popbox_text, center=(140,20)).join(check_update_box.download_button)
check_update_box.download_button.bind(webbrowser.open, 'https://fantastair.lanzout.com/b03qfxm6b')


save_eye_box = fantas.ChildBox(True, (320,260), bg=uimanager.DARKBLUE1, bd=2, sc=uimanager.DARKBLUE2, center=(uimanager.size[0]/2,uimanager.size[1]/2))
save_eye_box.bar = fantas.Label((save_eye_box.origin_size[0]-4,40), bg=uimanager.DARKBLUE4, topleft=(2,2))
save_eye_box.bar.join(save_eye_box)
save_eye_box.icon = fantas.Ui(uimanager.pythoneye_icon, center=(20,20))
save_eye_box.icon.size = (30,30)
save_eye_box.icon.join(save_eye_box.bar)
fantas.Text('保存当前调试状态', uimanager.simhei, prestyle.popbox_text, topleft=(50,12)).join(save_eye_box.bar)
save_eye_box.close_button = fantas.ColorButton((36,36), prestyle.popbox_closebutton, midright=(save_eye_box.origin_size[0]-6,20))
save_eye_box.close_button.join(save_eye_box.bar)
save_eye_box.close_button.bind(close_popbox, save_eye_box)
save_eye_box.close_button.bind_shortcut('Escape')
fantas.Text('×', uimanager.simhei, prestyle.popbox_text, center=(18,18)).join(save_eye_box.close_button)
prestyle.popbox_text['size'] = 16
fantas.Text('以.eye为后缀保存为二进制文件，可通过', uimanager.simhei, prestyle.popbox_text, midleft=(16,60)).join(save_eye_box)
fantas.Text('此文件直接回到当前的调试状态。此文件', uimanager.simhei, prestyle.popbox_text, midleft=(16,80)).join(save_eye_box)
fantas.Text('已包含源代码，在发送给他人或自己携带', uimanager.simhei, prestyle.popbox_text, midleft=(16,100)).join(save_eye_box)
fantas.Text('时无需另附代码。源代码也可以从此导出。', uimanager.simhei, prestyle.popbox_text, midleft=(16,120)).join(save_eye_box)
prestyle.popbox_text['fgcolor'] = uimanager.RED
fantas.Text('注意，只会保存主文件的源代码，因此你', uimanager.simhei, prestyle.popbox_text, midleft=(16,140)).join(save_eye_box)
fantas.Text('的代码中不能import其他代码，除非它', uimanager.simhei, prestyle.popbox_text, midleft=(16,160)).join(save_eye_box)
fantas.Text('们在python环境中。(以后可能会支持)', uimanager.simhei, prestyle.popbox_text, midleft=(16,180)).join(save_eye_box)
prestyle.popbox_text['fgcolor'] = uimanager.DARKBLUE3
prestyle.popbox_text['size'] = 18
save_eye_box.ensure_button = fantas.ColorButton((280,40), prestyle.popbox_button, center=(160,220))
save_eye_box.ensure_button.join(save_eye_box)
fantas.Text('我已知晓，开始保存', uimanager.simhei, prestyle.popbox_text, center=(140,20)).join(save_eye_box.ensure_button)


run_code_box = fantas.ChildBox(True, (700*r+100,30), bg=uimanager.DARKBLUE1, bd=2, sc=uimanager.DARKBLUE2, center=(uimanager.size[0]/2,uimanager.size[1]/2))
run_code_box.input_code = fantas.InputLine((700*r,30), uimanager.simhei, prestyle.popbox_inputline, prestyle.popbox_text, '在此处插入代码...', bg=uimanager.DARKBLUE2)
run_code_box.input_code.join(run_code_box)
run_code_box.cancel_button = fantas.ColorButton((46,22), prestyle.popbox_button, midright=(run_code_box.origin_size[0]-4,15))
run_code_box.cancel_button.join(run_code_box)
run_code_box.cancel_button.bind_shortcut('Escape')
fantas.Text('取消', uimanager.simhei, prestyle.popbox_text, center=(23,11)).join(run_code_box.cancel_button)
run_code_box.ensure_button = fantas.ColorButton((46,22), prestyle.popbox_button, midright=(run_code_box.cancel_button.rect.left-2,15))
run_code_box.ensure_button.join(run_code_box)
run_code_box.ensure_button.bind_shortcut('Return')
fantas.Text('插入', uimanager.simhei, prestyle.popbox_text, center=(23,11)).join(run_code_box.ensure_button)
run_code_box.cancel_button.bind(close_popbox, run_code_box, run_code_box.input_code)


def del_tracer():
	del_tracer_box.tracer.leave()
	face.debugboard.actionbar.tracers.remove(del_tracer_box.tracer)
	close_popbox(del_tracer_box)

del_tracer_box = fantas.ChildBox(True, (220,135), bg=uimanager.DARKBLUE1, bd=2, sc=uimanager.DARKBLUE2, center=(uimanager.size[0]/2,uimanager.size[1]/2))
del_tracer_box.bar = fantas.Label((del_tracer_box.origin_size[0]-4,40), bg=uimanager.DARKBLUE4, topleft=(2,2))
del_tracer_box.bar.join(del_tracer_box)
del_tracer_box.icon = fantas.Ui(uimanager.pythoneye_icon, center=(20,20))
del_tracer_box.icon.size = (30,30)
del_tracer_box.icon.join(del_tracer_box.bar)
fantas.Text('确定删除此追踪项？', uimanager.simhei, prestyle.popbox_text, topleft=(50,12)).join(del_tracer_box.bar)
del_tracer_box.ensure_button = fantas.ColorButton((90,30), prestyle.popbox_button, midright=(110,100))
del_tracer_box.ensure_button.join(del_tracer_box)
del_tracer_box.ensure_button.bind(del_tracer)
del_tracer_box.ensure_button.bind_shortcut('Return')
fantas.Text('确定', uimanager.simhei, prestyle.popbox_text, center=(45,15)).join(del_tracer_box.ensure_button)
del_tracer_box.cancel_button = fantas.ColorButton((90,30), prestyle.popbox_button, midleft=(110,100))
del_tracer_box.cancel_button.join(del_tracer_box)
del_tracer_box.cancel_button.bind(close_popbox, del_tracer_box)
del_tracer_box.cancel_button.bind_shortcut('Escape')
fantas.Text('取消', uimanager.simhei, prestyle.popbox_text, center=(45,15)).join(del_tracer_box.cancel_button)
del_tracer_box.arg = fantas.Text('', uimanager.jb_mono, prestyle.popbox_text, center=(110,62))
del_tracer_box.arg.join(del_tracer_box)


class CheckButton(fantas.Label):
	__slots__ = ['key', 'checked', 'mousewidget', 'check_text']

	def __init__(self, key, c, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.key = key
		self.checked = uimanager.user_data[key]
		self.check_text = fantas.Text('√', uimanager.simhei, prestyle.popbox_text, center=c)
		if self.checked:
			self.check_text.join(self)
		self.mousewidget = fantas.AnyButton(self)
		self.mousewidget.bind(self.check)
		self.mousewidget.apply_event()

	def check(self):
		uimanager.user_data[self.key] = self.checked = not self.checked
		if self.checked:
			self.check_text.join(self)
		else:
			self.check_text.leave()

	def update(self):
		if self.checked != uimanager.user_data[self.key]:
			self.check()


def close_set():
	close_popbox(set_board)
	pickle.dump(uimanager.user_data, 'user_data')
	messagebox.load_message('设置已保存')
	messagebox.show()


set_board = fantas.ChildBox(True, (500,370), bg=uimanager.DARKBLUE1, bd=2, sc=uimanager.DARKBLUE2, center=(uimanager.size[0]/2,uimanager.size[1]/2))
set_board.bar = fantas.Label((set_board.origin_size[0]-4,40), bg=uimanager.DARKBLUE4, topleft=(2,2))
set_board.bar.join(set_board)
set_board.icon = fantas.Ui(uimanager.pythoneye_icon, center=(20,20))
set_board.icon.size = (30,30)
set_board.icon.join(set_board.bar)
fantas.Text('设置', uimanager.simhei, prestyle.popbox_text, topleft=(50,12)).join(set_board.bar)
set_board.close_button = fantas.ColorButton((36,36), prestyle.popbox_closebutton, midright=(set_board.origin_size[0]-6,20))
set_board.close_button.join(set_board.bar)
set_board.close_button.bind(close_set)
set_board.close_button.bind_shortcut('Escape')
fantas.Text('×', uimanager.simhei, prestyle.popbox_text, center=(18,18)).join(set_board.close_button)

prestyle.popbox_text['fgcolor'] = uimanager.FAKEWHITE
prestyle.popbox_text['style'] = pygame.freetype.STYLE_STRONG
set_board.check_buttons = [
	CheckButton('auto_open_lastfile', (7,9), (16,16), bd=1, sc=uimanager.FAKEWHITE, center=(50,80)),
	CheckButton('show_recorder_tip', (7,9), (16,16), bd=1, sc=uimanager.FAKEWHITE, center=(50,110)),
	CheckButton('auto_search_python', (7,9), (16,16), bd=1, sc=uimanager.FAKEWHITE, center=(50,140)),
	
	CheckButton('auto_check_update', (7,9), (16,16), bd=1, sc=uimanager.FAKEWHITE, center=(50,180)),
	CheckButton('show_check_result', (7,9), (16,16), bd=1, sc=uimanager.FAKEWHITE, center=(50,210)),
	
	CheckButton('show_render_time', (7,9), (16,16), bd=1, sc=uimanager.FAKEWHITE, center=(50,250)),
	CheckButton('auto_scale', (7,9), (16,16), bd=1, sc=uimanager.FAKEWHITE, center=(50,280)),

	CheckButton('close_direct', (7,9), (16,16), bd=1, sc=uimanager.FAKEWHITE, center=(50,320)),
]
prestyle.popbox_text['fgcolor'] = uimanager.DARKBLUE3
del prestyle.popbox_text['style']
for c in set_board.check_buttons:
	c.join(set_board)

set_board.check_texts = [
	fantas.Text('自动打开上次的py文件', uimanager.simhei, prestyle.popbox_text, midleft=(70,80)),
	fantas.Text('保存调试状态时显示相关提示', uimanager.simhei, prestyle.popbox_text, midleft=(70,110)),
	fantas.Text('自动从系统环境变量中选择第一个可用的解释器', uimanager.simhei, prestyle.popbox_text, midleft=(70,140)),

	fantas.Text('启动时自动检查更新', uimanager.simhei, prestyle.popbox_text, midleft=(70,180)),
	fantas.Text('自动检查更新后如果没有新版本则不显示提示信息', uimanager.simhei, prestyle.popbox_text, midleft=(70,210)),

	fantas.Text('显示渲染代码耗时', uimanager.simhei, prestyle.popbox_text, midleft=(70,250)),
	fantas.Text('自动缩放窗口（适用于小屏幕）', uimanager.simhei, prestyle.popbox_text, midleft=(70,280)),

	fantas.Text('关闭软件前不再提示', uimanager.simhei, prestyle.popbox_text, midleft=(70,320)),
]
for t in range(len(set_board.check_texts)):
	set_board.check_texts[t].join(set_board)
	b = fantas.AnyButton(set_board.check_texts[t])
	b.bind(set_board.check_buttons[t].check)
	b.apply_event()
fantas.HoverMessage(set_board.check_texts[0], '注意不包括eye文件', hovermessagebox).apply_event()
fantas.HoverMessage(set_board.check_texts[2], '仅在开始调试时尝试搜索', hovermessagebox).apply_event()
fantas.HoverMessage(set_board.check_texts[5], '单位：ms', hovermessagebox).apply_event()
fantas.HoverMessage(set_board.check_texts[6], '重启软件生效', hovermessagebox).apply_event()


find_me = fantas.ChildBox(True, (300,200), bg=uimanager.DARKBLUE1, bd=2, sc=uimanager.DARKBLUE2, center=(uimanager.size[0]/2,uimanager.size[1]/2))
find_me.bar = fantas.Label((find_me.origin_size[0]-4,40), bg=uimanager.DARKBLUE4, topleft=(2,2))
find_me.bar.join(find_me)
find_me.icon = fantas.Ui(uimanager.pythoneye_icon, center=(20,20))
find_me.icon.size = (30,30)
find_me.icon.join(find_me.bar)
fantas.Text('Bug反馈 & 功能建议', uimanager.simhei, prestyle.popbox_text, topleft=(50,12)).join(find_me.bar)
find_me.close_button = fantas.ColorButton((36,36), prestyle.popbox_closebutton, midright=(find_me.origin_size[0]-6,20))
find_me.close_button.join(find_me.bar)
find_me.close_button.bind(close_popbox, find_me)
find_me.close_button.bind_shortcut('Escape')
fantas.Text('×', uimanager.simhei, prestyle.popbox_text, center=(18,18)).join(find_me.close_button)
prestyle.popbox_text['size'] = 26
fantas.Text('-> 联系作者 <-', uimanager.simhei, prestyle.popbox_text, center=(150,80)).join(find_me)
prestyle.popbox_text['size'] = 20
fantas.Text('QQ：2364209908', uimanager.simhei, prestyle.popbox_text, center=(150,130)).join(find_me)
fantas.Text('Fantastair@qq.com', uimanager.simhei, prestyle.popbox_text, center=(150,160)).join(find_me)
prestyle.popbox_text['size'] = 18
