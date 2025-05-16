import os
import gc
import time
import pickle
import pygame
import pygame.freetype
import webbrowser
import subprocess
from pathlib import Path
from threading import Thread
from tkinter.filedialog import askopenfilename, asksaveasfilename

import fantas
from fantas import uimanager
import prestyle
import debugger
import highlight
import face.dropfile
import face.popbox


def delete_codeboard():
	if actionbar.started:
		actionbar.end_debugger()
	global codeboard
	codeboard.leave()
	gc.collect()
	del codeboard
	codeboard = None


def open_newfile():
	file = askopenfilename(title='Python Eye 选择文件', filetypes=(('Python code', '*.py'),), multiple=False)
	if file:
		delete_codeboard()
		face.dropfile.dropboxwidget.dropfile(Path(file.lower()))


def closefile():
	for t in actionbar.tracers:
		t.leave()
	actionbar.tracers = []
	delete_codeboard()
	uimanager.user_data['last_file'] = None
	pygame.display.set_caption('Python Eye')
	uimanager.root = face.dropfile.icon
	uimanager.root.mark_update()
	face.dropfile.dropboxwidget.apply_event()


def reopen(encoding=None):
	if encoding is None:
		encoding = uimanager.user_data['encoding']
	else:
		uimanager.user_data['encoding'] = encoding
	delete_codeboard()
	face.dropfile.dropboxwidget.dropfile()
	e = uimanager.user_data['encoding']
	if uimanager.user_data['show_render_time']:
		face.popbox.messagebox.load_message(f'重载成功 | 编码：{e} | 耗时：{codeboard.render_time} ms')
	else:
		face.popbox.messagebox.load_message(f'重载成功 | 编码：{e}')
	face.popbox.messagebox.show()
face.popbox.reopen_with.reopen_with = reopen


def export_code():
	file = asksaveasfilename(title='Python Eye 导出源代码', filetypes=(('python code', '*.py'),), defaultextension='.py')
	if file:
		with open(file, 'w', encoding=uimanager.user_data['encoding']) as f:
			f.write(codeboard.highlight.original_code)
		face.popbox.messagebox.load_message(f'导出成功：{file}')
		face.popbox.messagebox.show()
	else:
		face.popbox.messagebox.load_message('未指定导出地址！')
		face.popbox.messagebox.show()


r = uimanager.r
codeboard = None

menubar = fantas.MenuBar((1280*r,20), 70, uimanager.simhei, (prestyle.menubar_menu,prestyle.menubar_item,prestyle.menubar_text), topleft=(0,0))

menubar.item_style['boxwidth'] = 246
menubar.item_style['width'] = 240
menubar.add_menu('文件', alt='F')
menubar.menus['文件'].add_item('打开文件', open_newfile)
menubar.menus['文件'].add_item('关闭文件', closefile)
menubar.menus['文件'].add_item('重载文件', reopen)
menubar.menus['文件'].add_item('重新用...编码打开', face.popbox.open_popbox, face.popbox.reopen_with, menubar, face.popbox.reopen_with.close_button, *face.popbox.reopen_with.choose_buttons)
menubar.menus['文件'].add_item('导出源代码', export_code)
menubar.menus['文件'].add_splitline()
menubar.menus['文件'].add_item('退出', pygame.event.post, pygame.event.Event(pygame.QUIT))

menubar.menus['文件'].bind_shortcut('打开文件', 'Ctrl+O')
menubar.menus['文件'].bind_shortcut('关闭文件', 'Ctrl+W')
menubar.menus['文件'].bind_shortcut('重载文件', 'F5')
menubar.menus['文件'].bind_shortcut('重新用...编码打开', 'E', False)
menubar.menus['文件'].bind_shortcut('导出源代码', 'Ctrl+Shift+S')
menubar.menus['文件'].bind_shortcut('退出', 'Alt+F4')


def recover_debugger(info):
	uimanager.set_cursor('^o')
	file_name = info['file'].name
	file_path = Path(str(Path(f'temp\\{file_name}').absolute()).lower())
	uimanager.user_data['last_file'] = file_path	
	uimanager.user_data['encoding'] = info['encoding']	
	with open(file_path, 'w', encoding=uimanager.user_data['encoding']) as f:
		f.write(info['original_code'])
	if codeboard is not None:
		delete_codeboard()
	openfile(file_path)
	actionbar.start_debugger()
	for c in info['com_record']:
		print(c if c[:2] != 'b ' and c[:7] != 'tbreak ' else c.replace(str(info['file']), str(file_path)))
		if actionbar.py_debugger.do_command(c if c[:2] != 'b ' and c[:7] != 'tbreak ' else c.replace(str(info['file']), str(file_path))) == '<|PythonEye Flag Debugger Over|>':
			break
	else:
		line_number = info['line_number']
		actionbar.set_line(f'{file_path}({line_number})')
		if info['lastline'] is not None:
			actionbar.set_line(info['lastline'])
		for b in info['breakpoints'][1:]:
			if 'breakpoint already hit ' not in b and ' time' not in b:
				line = int(b[b.find(str(info['file']))+len(str(info['file']))+1:])
				p = fantas.Ui(uimanager.breakpoint if b[17:21]=='keep' else uimanager.tbreakpoint, center=(codeboard.maxlinewidth+(codeboard.linewidth-codeboard.maxlinewidth)/2,(line-0.5)*codeboard.lineheight))
				p.join(codeboard.linenumberwidget.ui)
				codeboard.linenumberwidget.lines.append(line)
				codeboard.linenumberwidget.breakpoints.append((int(b[:4].strip()), p))
		if actionbar.tracers:
			for t in actionbar.tracers:
				t.leave()
			actionbar.tracers = []
		for t in info['tracers']:
			actionbar.trace_arg(t)
		face.popbox.messagebox.load_message('还原成功！')
		face.popbox.messagebox.show()
		menubar.menus['调试'].recover_item('开始调试')
		uimanager.set_cursor_back()
		return
	actionbar.end_debugger()
	face.popbox.messagebox.load_message('还原失败')	
	face.popbox.messagebox.show()
	menubar.menus['调试'].recover_item('开始调试')
	uimanager.set_cursor_back()

def export_eye(file=None):
	if file is None:
		file = Path(askopenfilename(title='Python Eye 还原调试', filetypes=(('PythonEye Recoder', '*.eye'),), multiple=False))
	if file.suffix == '.eye':
		try:
			face.popbox.messagebox.load_message('正在还原调试')
			face.popbox.messagebox.show()
			info = pickle.load(file)
			t = Thread(target=recover_debugger, args=(info,))
			t.daemon = True
			menubar.menus['调试'].ban_item('开始调试')
			t.start()
			pygame.display.set_caption(f'{file} - Python Eye')
			uimanager.user_data['last_eye'] = file
		except pickle.UnpicklingError:
			face.popbox.messagebox.load_message('文件失效')
		except:
			import traceback
			traceback.print_exc()
			face.popbox.messagebox.load_message('未知错误导致无法还原调试')
	else:
		face.popbox.messagebox.load_message('此文件不可用！')
	face.popbox.messagebox.show()

def start_save_eye():
	if uimanager.user_data['show_recorder_tip']:
		face.popbox.open_popbox(face.popbox.save_eye_box, menubar, face.popbox.save_eye_box.close_button, face.popbox.save_eye_box.ensure_button)
	else:
		actionbar.save_eye()

menubar.add_menu('调试', alt='D')
menubar.menus['调试'].add_item('开始调试')
menubar.menus['调试'].add_splitline()
menubar.menus['调试'].add_item('步过')
menubar.menus['调试'].add_item('步进')
# menubar.menus['调试'].add_item('配置断点')
menubar.menus['调试'].add_item('运行至...')
menubar.menus['调试'].add_item('清除所有断点')
menubar.menus['调试'].add_item('插入临时代码')
# menubar.menus['调试'].add_item('获取堆栈跟踪')
# menubar.menus['调试'].add_item('变量追踪')
menubar.menus['调试'].add_splitline()
menubar.menus['调试'].add_item('从.eye文件还原调试', export_eye)
menubar.menus['调试'].add_item('保存当前调试状态')

menubar.menus['调试'].recover_item('开始调试')
# menubar.menus['调试'].items['配置断点'].bind(face.popbox.open_popbox, face.popbox.add_breakpoint, menubar, face.popbox.add_breakpoint.close_button)
menubar.menus['调试'].items['运行至...'].bind(face.popbox.open_popbox, face.popbox.run_until, menubar, face.popbox.run_until.close_button, face.popbox.run_until.ensure_button, face.popbox.run_until.input_linenumber)
menubar.menus['调试'].items['插入临时代码'].bind(face.popbox.open_popbox, face.popbox.run_code_box, menubar, face.popbox.run_code_box.input_code, face.popbox.run_code_box.ensure_button, face.popbox.run_code_box.cancel_button)
menubar.menus['调试'].items['保存当前调试状态'].bind(start_save_eye)
menubar.menus['调试'].bind_shortcut('开始调试', 'Ctrl+D')
menubar.menus['调试'].bind_shortcut('步过', 'Ctrl+Down')
menubar.menus['调试'].bind_shortcut('步进', 'Ctrl+Right')
# menubar.menus['调试'].bind_shortcut('配置断点', 'B', False)
menubar.menus['调试'].bind_shortcut('运行至...', 'Ctrl+U')
menubar.menus['调试'].bind_shortcut('插入临时代码', 'Ctrl+I')
menubar.menus['调试'].bind_shortcut('清除所有断点', 'C', False)
# menubar.menus['调试'].bind_shortcut('获取堆栈跟踪', 'W', False)
menubar.menus['调试'].bind_shortcut('从.eye文件还原调试', 'Ctrl+R')
menubar.menus['调试'].bind_shortcut('保存当前调试状态', 'Ctrl+S')


def open_pythonshell():
	if uimanager.user_data['python_interpreter'] is None:
		face.popbox.messagebox.load_message('Python解释器地址已失效，请重新选择！')
		face.popbox.messagebox.show()
	else:
		subprocess.Popen([uimanager.user_data['python_interpreter'], '-m', 'idlelib.idle.pyw'])
		face.popbox.messagebox.load_message('正在启动 IDLE Shell')
		face.popbox.messagebox.show()


def easy_edit():
	if uimanager.user_data['python_interpreter'] is None:
		face.popbox.messagebox.load_message('Python解释器地址已失效，请重新选择！')
		face.popbox.messagebox.show()
	else:
		subprocess.Popen([uimanager.user_data['python_interpreter'], '-m', 'idlelib.idle.pyw', uimanager.user_data['last_file']])
		face.popbox.messagebox.load_message('将使用 IDLE 进行编辑，需要在编辑完成后重载文件(F5)')
		face.popbox.messagebox.show()


def show_fix():
	menubar.menus['工具'].items['固定提示'].text.text = '固定提示'
	menubar.menus['工具'].items['固定提示'].text.update_img()
	menubar.menus['工具'].items['固定提示'].bind(fix_message)

def show_unfix():
	menubar.menus['工具'].items['固定提示'].text.text = '解除固定'
	menubar.menus['工具'].items['固定提示'].text.update_img()
	menubar.menus['工具'].items['固定提示'].bind(unfix_message)	

def fix_message():
	show_unfix()
	face.popbox.messagebox.show()
	face.popbox.messagebox.autofix = True

def unfix_message():
	show_fix()
	face.popbox.messagebox.unfix()

def click_fix():
	if face.popbox.messagebox.fixed:
		show_unfix()
	else:
		show_fix()

s = fantas.AnyButton(face.popbox.messagebox.fixed_button)
s.apply_event()
s.bind(click_fix)

menubar.item_style['boxwidth'] = 256
menubar.item_style['width'] = 250
menubar.add_menu('工具', alt='T')
menubar.menus['工具'].add_item('查看上一条提示', face.popbox.messagebox.show)
menubar.menus['工具'].add_item('固定提示', fix_message)
menubar.menus['工具'].add_splitline()
menubar.menus['工具'].add_item('简易编辑', easy_edit)
menubar.menus['工具'].add_item('IDLE Shell', open_pythonshell)
# menubar.menus['工具'].add_splitline()
# menubar.menus['工具'].add_item('函数追踪')
# menubar.menus['工具'].add_item('热点代码追踪')

menubar.menus['工具'].bind_shortcut('查看上一条提示', 'Ctrl+Alt+T')
menubar.menus['工具'].bind_shortcut('固定提示', 'Ctrl+Alt+F')
menubar.menus['工具'].bind_shortcut('简易编辑', 'Ctrl+Alt+E')
menubar.menus['工具'].bind_shortcut('IDLE Shell', 'Ctrl+Alt+S')
# menubar.menus['工具'].bind_shortcut('函数追踪', 'F', False)
# menubar.menus['工具'].bind_shortcut('热点代码追踪', 'H', False)


def set_python():
	python = Path(askopenfilename(title='Python Eye 选择解释器', filetypes=(('pythonw.exe', '*.exe'),), multiple=False).lower())
	if python.name == 'pythonw.exe' or python.name == 'python.exe':
		uimanager.user_data['python_interpreter'] = python
		face.popbox.messagebox.load_message(f'成功设置解释器：{python}')
	else:
		face.popbox.messagebox.load_message('你没有选择正确的python解释器！')
	face.popbox.messagebox.show()


menubar.item_style['boxwidth'] = 286
menubar.item_style['width'] = 280
menubar.add_menu('首选项', alt='N', menu_width=85)
menubar.menus['首选项'].add_item('设置', face.popbox.open_popbox, face.popbox.set_board, menubar, face.popbox.set_board.close_button)
menubar.menus['首选项'].add_item('选择Python解释器', set_python)
# menubar.menus['首选项'].add_splitline()
# menubar.menus['首选项'].add_item('高级显示')

menubar.menus['首选项'].bind_shortcut('设置', 'S', False)
menubar.menus['首选项'].bind_shortcut('选择Python解释器', 'Ctrl+Shift+P')
menubar.item_style['boxwidth'] = 206
menubar.item_style['width'] = 200

menubar.add_menu('帮助', alt='H')
menubar.menus['帮助'].add_item('使用文档', webbrowser.open, 'Python Eye 使用文档.html')
menubar.menus['帮助'].add_item('CSDN博客', webbrowser.open, 'https://blog.csdn.net/2301_79102953/article/details/132386562')
menubar.menus['帮助'].add_item('软件发布', webbrowser.open, 'https://fantastair.lanzout.com/b03qfxm6b')
menubar.menus['帮助'].add_splitline()
menubar.menus['帮助'].add_item('检查更新', face.popbox.check_update)
# menubar.menus['帮助'].add_item('更新日志')
menubar.menus['帮助'].add_item('关于Python Eye', face.popbox.open_popbox, face.popbox.about_pythoneye, menubar, face.popbox.about_pythoneye.close_button)
menubar.menus['帮助'].add_splitline()
menubar.menus['帮助'].add_item('Bug反馈 & 功能建议',  face.popbox.open_popbox, face.popbox.find_me, menubar, face.popbox.find_me.close_button)

menubar.menus['帮助'].bind_shortcut('使用文档', 'F1')
menubar.menus['帮助'].bind_shortcut('检查更新', 'U', False)


class TraceArg(fantas.ColorButton):
	pad = 10

	def __init__(self, arg_name, **kwargs):
		super().__init__((0,0), prestyle.trace_button, bd=5, **kwargs)
		self.defined = False
		self.arg_name = arg_name
		self.name = fantas.Text(self.arg_name, uimanager.jb_mono, prestyle.arg_name, topleft=(self.pad,self.pad))
		self.name.join(self)
		self.arg = fantas.Text('', uimanager.simhei, prestyle.arg_text, midleft=(self.name.rect.width+self.pad*3,self.name.rect.height/2+self.pad))
		self.arg.join(self)
		self.arg.anchor = 'midleft'
		self.anchor = 'topleft'
		self.size_keyframe = fantas.LabelKeyFrame(self, 'size', (0,0), 15, uimanager.slower_curve)
		self.move_keyframe = None
		self.alpha_keyframe = fantas.UiKeyFrame(self, 'alpha', 60, 15, uimanager.slower_curve)
		self.widget = TraceArgMouseWidget(self, 2)
		self.widget.r_pos = None
		self.widget.apply_event()
		self.bind(self.del_self)
		self.refresh()
		self.last_time = 0

	def adjust(self):
		value = (self.pad*4+self.arg.rect.width+self.name.rect.width,self.pad*2+self.name.rect.height)
		if value != self.size_keyframe.value:
			self.size_keyframe.value = value
			self.size_keyframe.launch('continue')
			if self.size_keyframe.value[0] + self.rect.left > codeboard.rect.width - (codeboard.scrollbar_y.rect.width if codeboard.scrollbar_y is not None else 0):
				if self.move_keyframe is None:
					self.move_keyframe = fantas.RectKeyFrame(self, 'left', codeboard.rect.width - (codeboard.scrollbar_y.rect.width if codeboard.scrollbar_y is not None else 0)-self.size_keyframe.value[0], 15, uimanager.slower_curve)
				else:
					self.move_keyframe.value = codeboard.rect.width - (codeboard.scrollbar_y.rect.width if codeboard.scrollbar_y is not None else 0)-self.size_keyframe.value[0]
				self.move_keyframe.launch('continue')

	def del_self(self):
		time = pygame.time.get_ticks()
		if time - self.last_time <= 200:
			face.popbox.del_tracer_box.ensure_button.mousewidget.mouseon = False
			face.popbox.del_tracer_box.cancel_button.mousewidget.mouseon = False
			face.popbox.del_tracer_box.tracer = self
			face.popbox.del_tracer_box.arg.text = self.arg_name
			face.popbox.del_tracer_box.arg.update_img()
			face.popbox.open_popbox(face.popbox.del_tracer_box, menubar, face.popbox.del_tracer_box.ensure_button, face.popbox.del_tracer_box.cancel_button)
		self.last_time = time

	def move(self, pos, no_bound=False):
		self.mark_update()
		self.rect.left += pos[0]
		self.rect.top += pos[1]
		for s in actionbar.tracers:
			if s is not self and self.rect.colliderect(s.rect):
				x = y = 0
				if pos[0] != 0 and abs(self.rect.centerx-pos[0]-s.rect.centerx) >= (self.rect.width+s.rect.width)/2:
					x += (self.rect.right - s.rect.left) if pos[0] > 0 else (self.rect.left - s.rect.right)
				if pos[1] != 0 and abs(self.rect.centery-pos[1]-s.rect.centery) >= (self.rect.height+s.rect.height)/2:
					y += (self.rect.bottom - s.rect.top) if pos[1] > 0 else (self.rect.top - s.rect.bottom)
				if x != 0 or y != 0:
					s.move((x,y))
		if not no_bound:
			x = y = 0
			if self.rect.right > codeboard.rect.width - (codeboard.scrollbar_y.rect.width if codeboard.scrollbar_y is not None else 0):
				x += codeboard.rect.width - self.rect.right - (codeboard.scrollbar_y.rect.width if codeboard.scrollbar_y is not None else 0)
			if self.rect.left < codeboard.linewidth:
				x += codeboard.linewidth - self.rect.left
			if self.rect.bottom > codeboard.rect.height - (codeboard.scrollbar_x.rect.height if codeboard.scrollbar_x is not None else 0):
				y += codeboard.rect.height - self.rect.bottom - (codeboard.scrollbar_x.rect.height if codeboard.scrollbar_x is not None else 0)
			if self.rect.top < 0:
				y -= self.rect.top
			if x != 0 or y != 0:
				self.move((x,y), True)

	def refresh(self):
		if actionbar.started:
			value = actionbar.py_debugger.do_command('!' + self.arg_name)[-1]
			if 'NameError: name ' in value and ' is not defined' in value:
				if self.defined:
					value = '无法追踪'
				else:
					value = '未定义'
				self.alpha_keyframe.value = 60
			elif 'SyntaxError' in value:
				value = '语法错误'
				self.alpha_keyframe.value = 60
			else:
				self.defined = True
				self.alpha_keyframe.value = 255
		else:
			value = '等待调试'
			self.defined = False
			self.alpha_keyframe.value = 255
		self.alpha_keyframe.launch('continue')
		if value != self.arg.text:
			self.arg.text = value
			self.arg.update_img()
			self.adjust()
			self.mousewidget.set_color('hover')
		else:
			self.mousewidget.set_color('origin')

class TraceArgMouseWidget(fantas.MouseBase):
	__slots__ = ['r_pos']

	def mousepress(self, pos):
		if self.mousedown == 1:
			self.r_pos = (pos[0]-self.ui.rect.left, pos[1]-self.ui.rect.top)
		else:
			self.r_pos = None

	def mouserelease(self, pos):
		self.r_pos = None

	def mousemove(self, pos):
		if self.r_pos is not None:
			self.ui.move((pos[0]-self.r_pos[0]-self.ui.rect.left, pos[1]-self.r_pos[1]-self.ui.rect.top))


def search_python():
	for s in os.environ['PATH'].split(';'):
		if 'Python' in s and 'Scripts' in s:
			p = Path(s).parent / 'pythonw.exe'
			if p.exists():
				break
	else:
		p = None
	return p


class ActionBar(fantas.Label):
	__slots__ = ['started', 'py_debugger', 'buttons', 'startend_button', 'start_icon', 'end_icon', 'path', 'com_record', 'line_number', 'lastline', 'startend_hovermsg', 'input_tracer','trace_button', 'tracers']

	def __init__(self):
		super().__init__((1280*r, 40), bg=uimanager.DARKGRAY2, top=menubar.rect.bottom)
		self.tracers = []
		self.started = False
		self.py_debugger = None
		self.buttons = [
			fantas.ColorButton((36,36), prestyle.action_button, topright=(self.rect.width-2,2)),
			fantas.ColorButton((36,36), prestyle.action_button, topright=(self.rect.width-52,2)),
			fantas.ColorButton((36,36), prestyle.action_button, topright=(self.rect.width-102,2)),
			fantas.ColorButton((36,36), prestyle.action_button, topright=(self.rect.width-152,2)),
			]			
		self.startend_button = fantas.ColorButton((36,36), prestyle.action_button, topright=(self.rect.width-202,2))
		self.startend_button.bind(self.start_debugger)
		self.start_icon = fantas.Ui(uimanager.startdebug_button, center=(18,18))
		self.end_icon = fantas.Ui(uimanager.enddebug_button, center=(18,18))
		self.start_icon.join(self.startend_button)
		self.buttons[3].bind(self.step_across)
		self.buttons[2].bind(self.step_in)
		self.buttons[1].bind(self.until_bp)
		self.buttons[0].bind(self.until_func)
		face.popbox.save_eye_box.ensure_button.bind(self.save_eye)
		face.popbox.run_code_box.ensure_button.bind(self.insert_code)
		menubar.menus['调试'].items['开始调试'].bind(self.start_debugger)
		menubar.menus['调试'].items['步过'].bind(self.step_across)
		menubar.menus['调试'].items['步进'].bind(self.step_in)
		menubar.menus['调试'].items['开始调试'].bind(self.start_debugger)
		menubar.menus['调试'].items['清除所有断点'].bind(self.clear_breakpoint)
		self.input_tracer = fantas.InputLine((240,36), uimanager.simhei, prestyle.popbox_inputline, prestyle.popbox_text, '变量追踪...', bg=uimanager.DARKBLUE2, bd=2, sc=uimanager.DARKBLUE3, midleft=(10,20))
		self.input_tracer.join(self)
		self.trace_button = fantas.ColorButton((36,36), prestyle.action_button, topleft=(260,2))
		fantas.HoverMessage(self.trace_button, '追踪变量', face.popbox.hovermessagebox).apply_event()
		self.trace_button.join(self)
		self.trace_button.bind(self.trace_arg)
		self.trace_button.bind_shortcut('Return')
		fantas.Ui(uimanager.trace_button, center=(18,18)).join(self.trace_button)

	def trace_arg(self, arg=None):
		if arg is None:
			arg = self.input_tracer.get_input()
		if arg:
			if '(' not in arg:
				if '=' in arg and '==' not in arg:
					face.popbox.messagebox.load_message('不允许使用赋值语句')
				else:
					t = TraceArg(arg, topleft=(self.tracers[-1].rect.left,self.tracers[-1].rect.top+self.tracers[-1].size_keyframe.value[1]+10) if self.tracers and self.tracers[-1].rect.bottom+10+self.tracers[-1].rect.height < codeboard.rect.height else (codeboard.rect.centerx,10))
					self.input_tracer.clear()
					t.join(codeboard)
					self.tracers.append(t)
					face.popbox.messagebox.load_message(f'追踪变量：{arg}')
			else:
				face.popbox.messagebox.load_message('不允许追踪函数调用')
		else:
			face.popbox.messagebox.load_message('追踪项为空')
		face.popbox.messagebox.show()

	def start_debugger(self):
		uimanager.set_cursor('^o')
		if uimanager.user_data['python_interpreter'] is None:
			if uimanager.user_data['auto_search_python']:
				uimanager.user_data['python_interpreter'] = search_python()
				if uimanager.user_data['python_interpreter'] is None:
					face.popbox.messagebox.load_message('Python解释器地址已失效，请手动选择！')
					face.popbox.messagebox.show()
			else:
				face.popbox.messagebox.load_message('Python解释器地址已失效，请手动选择！')
				face.popbox.messagebox.show()
		elif codeboard is not None:
			self.started = True
			self.line_number = 1
			self.startend_hovermsg.text = '结束调试'
			self.path = str(uimanager.user_data['last_file'])
			self.py_debugger = debugger.Debugger(str(uimanager.user_data['last_file']), str(uimanager.user_data['python_interpreter']), self.stdout, self.stdin, self.stderr)
			self.py_debugger.open_eye()
			self.set_line(self.py_debugger.output_queue.get())
			self.start_icon.leave()
			self.end_icon.join(self.startend_button)
			self.startend_button.bind(self.end_debugger)
			for b in self.buttons:
				b.recover()
			menubar.menus['调试'].items['开始调试'].bind(self.end_debugger)
			menubar.menus['调试'].items['开始调试'].text.text = '停止调试'
			menubar.menus['调试'].items['开始调试'].text.update_img()
			menubar.menus['调试'].recover_item('步过')
			menubar.menus['调试'].recover_item('步进')
			# menubar.menus['调试'].recover_item('配置断点')
			menubar.menus['调试'].recover_item('运行至...')
			menubar.menus['调试'].recover_item('插入临时代码')
			menubar.menus['调试'].recover_item('清除所有断点')
			menubar.menus['调试'].recover_item('保存当前调试状态')
			menubar.menus['调试'].ban_item('从.eye文件还原调试')
			codeboard.linenumberwidget.apply_event()
			face.popbox.messagebox.load_message('PythonEye：开始调试')
			face.popbox.messagebox.show()
			for t in self.tracers:
				t.refresh()
		uimanager.set_cursor_back()

	def end_debugger(self, no_msg=False):
		uimanager.set_cursor('^o')
		if codeboard is not None:
			self.started = False
			self.startend_hovermsg.text = '开始调试'
			if not self.py_debugger.finished:
				self.py_debugger.close_eye()
			for t in self.tracers:
				t.refresh()
			codeboard.line_pointer.rect.bottom = 0
			codeboard.linenumber_pointer.rect.bottom = 0
			if codeboard.move_linepointer.is_launched():
				codeboard.move_linepointer.stop()
				codeboard.move_linenumberpointer.stop()
			codeboard.code.mark_update()
			codeboard.linenumber.mark_update()
			self.end_icon.leave()
			self.start_icon.join(self.startend_button)
			self.startend_button.bind(self.start_debugger)
			for b in self.buttons:
				b.ban()
			menubar.menus['调试'].items['开始调试'].bind(self.start_debugger)
			menubar.menus['调试'].items['开始调试'].text.text = '开始调试'
			menubar.menus['调试'].items['开始调试'].text.update_img()
			menubar.menus['调试'].ban_item('步过')
			menubar.menus['调试'].ban_item('步进')
			# menubar.menus['调试'].ban_item('配置断点')
			menubar.menus['调试'].ban_item('运行至...')
			menubar.menus['调试'].ban_item('插入临时代码')
			menubar.menus['调试'].ban_item('清除所有断点')
			menubar.menus['调试'].ban_item('保存当前调试状态')
			menubar.menus['调试'].recover_item('从.eye文件还原调试')
			codeboard.linenumberwidget.cancel_event()
			codeboard.linenumberwidget.clear_breakpoint(only_ui=True)
			if not no_msg:
				face.popbox.messagebox.load_message('PythonEye：调试结束')
				face.popbox.messagebox.show()
		uimanager.set_cursor_back()

	def step_across(self):
		self.do_command('n')

	def step_in(self):
		self.do_command('s')

	def until_bp(self):
		self.do_command('c')

	def until_func(self):
		self.do_command('r')

	def run_until(self, line):
		face.popbox.messagebox.load_message(f'运行直到大于等于 {line} 行')
		face.popbox.messagebox.show()
		self.do_command(f'until {line}')

	def do_command(self, com):
		info = self.py_debugger.do_command(com)
		while '<|PythonEye Flag Stdout|>' in info:
			i = info.find('<|PythonEye Flag Stdout|>')
			info.remove('<|PythonEye Flag Stdout|>')
			print(info.pop(i))
		if info[0] == '--Call--' or info[0] == '--Return--':
			self.step_across()
		elif info[0] == '<|PythonEye Flag Code Error|>':
			self.end_debugger(no_msg=True)
		else:
			flag = True
			if info[0] == '<|PythonEye Flag Debugger Over|>':
				self.end_debugger()
				flag = False
			elif info[0] == '<|PythonEye Flag Delete Breakpoint|>':
				while info[1][:19] == 'Deleted breakpoint ':
					del_info = info.pop(1)[19:]
					index = del_info.find(' ')
					bp_num = int(del_info[:index])
					codeboard.linenumberwidget.del_breakpoint_bynum(bp_num, only_ui=True)
			elif info[0] == '<|PythonEye Flag Debugger SystemExit|>':
				face.popbox.messagebox.load_message('调试程序通过sys.exit()退出')
				face.popbox.messagebox.show()
				self.end_debugger(no_msg=True)
				flag = False
			elif info[0] == '<|PythonEye Flag Debugger SyntaxError|>':
				face.popbox.messagebox.load_message('PythonEye调试程序异常')
				face.popbox.messagebox.show()
				self.end_debugger(no_msg=True)
				flag = False
			elif info[0] == '<|PythonEye Flag Error|>':
				if info[1] == '"until" line number is smaller than current line number':
					face.popbox.messagebox.load_message('命令异常：指定行号小于等于当前行号')
				else:
					face.popbox.messagebox.load_message('命令异常：' + info[1])
				face.popbox.messagebox.show()
				flag = False
			elif info[0] == '<|PythonEye Flag Empty Info|>':
				face.popbox.messagebox.load_message('返回值为空')
				face.popbox.messagebox.show()
			elif info[0] == '<|PythonEye Flag Insert Code|>':
				if len(info) == 1:
					face.popbox.messagebox.load_message('返回值为空')
				else:
					face.popbox.messagebox.load_message('返回：' + info[-1])
				face.popbox.messagebox.show()
			elif info[0][:2] != '> ':
				face.popbox.messagebox.load_message('代码异常：' + info[0])
				face.popbox.messagebox.show()
				self.step_across()
				flag = False
			if flag:
				for s in range(len(info)):
					if info[s][:2] == '> ':
						self.set_line(info[s])
						break
		for t in self.tracers:
			t.refresh()

	def set_line(self, lineinfo):
		file_index = lineinfo.find(self.path)
		if file_index != -1:
			self.lastline = None
			lineinfo = lineinfo[len(self.path)+file_index+1:]
			self.line_number = int(lineinfo[:lineinfo.find(')')])
			if codeboard.line_pointer.bg == uimanager.DARKBLUE2:
				codeboard.line_pointer.set_bg(uimanager.DARKBLUE5)
				codeboard.linenumber_pointer.set_bg(uimanager.DARKBLUE5)
			codeboard.move_linepointer.value = codeboard.lineheight * (self.line_number-1)
			codeboard.move_linepointer.launch(flag='continue')
			codeboard.move_linenumberpointer.value = codeboard.lineheight * (self.line_number-1)
			codeboard.move_linenumberpointer.launch(flag='continue')
			codeboard.linenumber_text.text = '-' * codeboard.maxline
			codeboard.linenumber_text.update_img()
			codeboard.linenumber_text.text = str(self.line_number).rjust(codeboard.maxline, ' ')
			pos = self.line_number + codeboard.code.rect.top//codeboard.lineheight
			visibleline = codeboard.rect.height // codeboard.lineheight
			if visibleline <= 6 or pos < 3 or pos >= visibleline-3:
				codeboard.scrollbar_y.scroll_to([0,(self.line_number-1)/(codeboard.highlight.line_number+codeboard.rect.height/codeboard.lineheight)*(codeboard.scrollbar_y.rect.height-codeboard.scrollbar_y.scrollbutton.rect.height)+codeboard.scrollbar_y.scrollbutton.rect.height/2])
			if face.popbox.messagebox.text.text[:6] == '进入其他文件':
				face.popbox.messagebox.load_message('返回本文件')
				face.popbox.messagebox.show()
		else:
			self.lastline = lineinfo
			if codeboard.line_pointer.bg == uimanager.DARKBLUE5:
				codeboard.line_pointer.set_bg(uimanager.DARKBLUE2)
				codeboard.linenumber_pointer.set_bg(uimanager.DARKBLUE2)
			file_path = lineinfo[2:lineinfo.find(')')+1]
			face.popbox.messagebox.load_message(f'进入其他文件{file_path}')
			face.popbox.messagebox.show()
		codeboard.linenumber.mark_update()

	def add_breakpoint(self, line, form):
		return self.py_debugger.do_command(f'{form} {self.path}:{line}')

	def del_breakpoint(self, num):
		return self.py_debugger.do_command(f'clear {num}')

	def clear_breakpoint(self):
		return self.py_debugger.do_command('clear')

	def save_eye(self):
		uimanager.set_cursor('^o')
		if face.popbox.save_eye_box.father is uimanager.root:
			face.popbox.close_popbox(face.popbox.save_eye_box)
		file = asksaveasfilename(title = 'Python Eye 保存调试状态', filetypes=(('PythonEye Recoder', '*.eye'),), defaultextension='.eye', initialfile=uimanager.user_data['last_file'].stem)
		if file:
			data = {
				'file': uimanager.user_data['last_file'],
				'original_code': codeboard.highlight.original_code,
				'com_record': self.py_debugger.com_record,
				'line_number': self.line_number,
				'lastline': self.lastline,
				'breakpoints': self.py_debugger.do_command('b'),
				'encoding': uimanager.user_data['encoding'],
				'tracers': [t.arg_name for t in self.tracers],
			}
			pickle.dump(data, file)
			face.popbox.messagebox.load_message('保存成功！')
		else:
			face.popbox.messagebox.load_message('未指定保存地址！')
		face.popbox.messagebox.show()
		uimanager.set_cursor_back()

	def insert_code(self):
		code = '!' + face.popbox.run_code_box.input_code.get_input().strip()
		if code:
			self.do_command(code)
			face.popbox.run_code_box.input_code.clear()
			face.popbox.close_popbox(face.popbox.run_code_box, face.popbox.run_code_box.input_code)
		else:
			face.popbox.messagebox.load_message('无法插入空代码')
			face.popbox.messagebox.show()

	def stdout(self, data):
		# face.popbox.messagebox.load_message(data)
		# face.popbox.messagebox.show()
		# pass
		print(data, end='')
		# time.sleep(0.1)

	def stdin(self):
		return '抱歉。。。Input函数功能暂不支持'

	def stderr(self, data):
		print('eye', data)
		# self.end_debugger()


actionbar = ActionBar()
actionbar.join(menubar)
actionicon = (uimanager.untilfunc_button, uimanager.untilbp_button, uimanager.stepin_button, uimanager.stepacross_button)
actiontip = ('运行直到函数结束', '运行至下一断点', '步进', '步过')
for b in range(4):
	actionbar.buttons[b].join(actionbar)
	actionbar.buttons[b].ban()
	fantas.Ui(actionicon[b], center=(18,18)).join(actionbar.buttons[b])
	fantas.HoverMessage(actionbar.buttons[b], actiontip[b], face.popbox.hovermessagebox).apply_event()
actionbar.startend_button.join(actionbar)
actionbar.startend_hovermsg = fantas.HoverMessage(actionbar.startend_button, '开始调试', face.popbox.hovermessagebox)
actionbar.startend_hovermsg.apply_event()
actionbar.buttons[2].kidgroup[0].rect.centerx = 20
actionbar.buttons[2].mark_update()


class CodeGroup(fantas.UiGroup):
	__slots__ = []

	def update_rect(self, anchor=None):
		if anchor is None:
			anchor = self.anchor
		pos = getattr(self.rect, anchor)
		length = len(self.kidgroup)
		if length == 1:
			self.rect.size = self.kidgroup[0].rect.size
		elif length != 0:
			self.rect.size = self.kidgroup[0].rect.unionall([ui.rect for ui in self.kidgroup[1:] if ui is not None]).size
		setattr(self.rect, anchor, pos)

	def render(self):
		self.temp_img = self.father.temp_img
		self.kidgroup[0].rect.left += self.rect.left
		self.kidgroup[0].rect.top += self.rect.top
		self.kidgroup[0].render()
		self.kidgroup[0].rect.left -= self.rect.left
		self.kidgroup[0].rect.top -= self.rect.top
		for ui in self.kidgroup[max(1,-self.rect.top//self.father.lineheight):min(2-self.rect.top//self.father.lineheight+self.father.rect.h//self.father.lineheight,self.father.highlight.line_number+1)]:
			if ui is not None:
				ui.rect.left += self.rect.left
				ui.rect.top += self.rect.top
				ui.render()
				ui.rect.left -= self.rect.left
				ui.rect.top -= self.rect.top
		for ui in self.kidgroup[self.father.highlight.line_number+1:]:
			if ui is not None:
				ui.rect.left += self.rect.left
				ui.rect.top += self.rect.top
				ui.render()
				ui.rect.left -= self.rect.left
				ui.rect.top -= self.rect.top


class CodeBoard(fantas.Label):
	def __init__(self, file):
		self.font = uimanager.jb_mono
		super().__init__((1280*r, 720*r-actionbar.rect.h-menubar.rect.h), bg=uimanager.DARKGRAY1, top=actionbar.rect.bottom)
		self.file = file
		self.highlight = highlight.Highlight(file, uimanager.jb_mono, uimanager.simhei, prestyle.code_text, uimanager.user_data['encoding'])
		self.lineheight = self.font.get_sized_height(prestyle.code_text['size'])
		height = self.lineheight * self.highlight.line_number
		uimanager.breakpoint = pygame.transform.smoothscale(uimanager.breakpoint, (self.lineheight*0.6,)*2)
		uimanager.tbreakpoint = pygame.transform.smoothscale(uimanager.tbreakpoint, (self.lineheight*0.6,)*2)
		self.maxline = len(str(self.highlight.line_number))
		self.maxlinewidth = self.font.get_rect('0'*self.maxline, size=prestyle.code_text['size']).width
		self.linewidth = 50 + self.maxline*prestyle.code_text['size']//2
		self.linenumber = fantas.Label((self.linewidth,height), bg=uimanager.DARKGRAY1)
		self.linenumberwidget = LinenumberWidget(self.linenumber)
		self.code = CodeGroup()
		self.code.rect.height = height
		self.code.rect_locked = True
		shade = pygame.Surface((10,self.rect.height-18), flags=pygame.HWSURFACE | pygame.SRCALPHA)
		with pygame.PixelArray(shade) as pixarray:
			for s in range(10):
				pixarray[s] = getattr(uimanager, f'SHADEBLACK{s}')
		self.shade = fantas.Ui(shade, left=self.linewidth)
		self.code.rect.left = self.linewidth
		self.code.join(self)
		self.linenumber.join(self)
		self.widget = CodeBoardWidget(self)
		visibleline = min(self.rect.height // self.lineheight + 1, self.highlight.line_number)
		pos = self.lineheight-prestyle.code_text['size']
		if uimanager.user_data['show_render_time']:
			t = time.time()
		uimanager.set_cursor('^o')
		self.render_lines()
		self.render_tabtip()
		uimanager.set_cursor_back()
		if uimanager.user_data['show_render_time']:
			self.render_time = round((time.time() - t) * 1000)
		if self.lineheight < self.code.rect.height:
			self.scrollbar_y = ScrollBar(self, prestyle.code_scroll, 1, size=(18,self.rect.height), bd=5, sc=self.bg, right=self.rect.width)
			self.scrollbar_y.join(self)
			self.apply_event(self.scrollbar_y)
		else:
			self.scrollbar_y = None
		if self.code.rect.width > self.rect.width-self.linewidth*2:
			self.scrollbar_x = ScrollBar(self, prestyle.code_scroll, 0, size=(self.rect.width-18,18), bd=5, sc=self.bg, bottom=self.rect.height)
			self.scrollbar_x.join(self)
			self.apply_event(self.scrollbar_x)
		else:
			self.scrollbar_x = None
		self.line_pointer = fantas.Label((self.code.rect.width+self.linewidth,self.lineheight), bg=uimanager.DARKBLUE5, top=-self.lineheight)
		self.linenumber_pointer = fantas.Label((self.linewidth,self.lineheight), bg=uimanager.DARKBLUE5, top=-self.lineheight)
		self.linenumber_text = fantas.Text('', self.font, prestyle.linenumber_hl, left=10)
		self.linenumber_text.anchor = 'midleft'
		self.line_pointer.join_to(self.code, 0)
		self.linenumber_text.join(self.linenumber_pointer)
		self.linenumber_pointer.join(self.linenumber)
		self.widget.apply_event()
		self.move_linepointer = fantas.RectKeyFrame(self.line_pointer, 'top', 0, 20, uimanager.harmonic_curve)
		self.move_linenumberpointer = fantas.RectKeyFrame(self.linenumber_pointer, 'top', 0, 20, uimanager.harmonic_curve)
		self.move_linenumberpointer.bind_endupwith(self.linenumber_text.update_img)

	def render_lines(self):
		line = 1
		pos = 0
		line_renderor = fantas.Text('', self.font, prestyle.linenumber)
		for s in range(self.highlight.line_number):
			t,l = self.highlight.render_line(line)
			if t is not None:
				fantas.Ui(t, topleft=(l,pos)).join(self.code)
			else:
				self.code.kidgroup.append(None)
			line_renderor.text = str(line).rjust(self.maxline,' ')
			self.linenumber.img.blit(line_renderor.draw_text(), (10,pos))
			pos += self.lineheight
			line += 1
		self.linenumber.mark_update()
		self.code.mark_update()
		self.code.update_rect('topleft')
		self.code.rect.height = pos

	def render_tabtip(self):
		tabtemp = []
		line_number = self.highlight.line_number
		for line in self.highlight.lexical_code[::-1]:
			length = len(tabtemp)
			lenline = len(line)
			if lenline == 0 or lenline == 1 and line[0][0] == '空格':
				for s in range(length):
					tabtemp[s] += 1
			else:
				if lenline == 0 or line[0][0] != '空格':
					start = 0
				else:
					start = line[0][2]
					for s in range(start):
						if s < length:
							tabtemp[s] += 1
						else:
							tabtemp.append(1)
							length += 1
				first_line = line_number == 1
				if start <= length or first_line:
					if first_line:
						start = line = 0
					for s in range(start, length):
						height = tabtemp.pop(start) * self.lineheight
						img = pygame.Surface((1,height), flags=pygame.HWSURFACE | pygame.SRCALPHA)
						with pygame.PixelArray(img) as pixarray:
							pixarray[:,::2] = uimanager.DARKGRAY2
						fantas.Ui(img, topleft=(s*self.highlight.tabwidth,line_number*self.lineheight)).join(self.code)
			line_number -= 1


class CodeBoardWidget(fantas.MouseBase):
	__slots__ = ['smoothroll1', 'smoothroll2', 'smoothroll3']

	def __init__(self, ui):
		super().__init__(ui, 3)
		self.smoothroll1 = fantas.RectKeyFrame(self.ui.code, 'top', 0, 8, uimanager.curve)
		self.smoothroll2 = fantas.RectKeyFrame(self.ui.linenumber, 'top', 0, 8, uimanager.curve)
		self.smoothroll3 = fantas.RectKeyFrame(self.ui.code, 'left', self.ui.linewidth, 8, uimanager.curve)

	def mousescroll(self, x, y):
		if uimanager.join('left shift') == 'Shift':
			x, y = -y, 0
		if y and self.ui.scrollbar_y is not None:
			self.smoothroll1.value += y * 5 * self.ui.lineheight
			self.smoothroll1.value = round(self.smoothroll1.value/self.ui.lineheight)*self.ui.lineheight
			if self.smoothroll1.value > 0:
				self.smoothroll1.value = 0
			elif self.ui.code.rect.height + self.smoothroll1.value < self.ui.lineheight:
				self.smoothroll1.value = self.ui.lineheight - self.ui.code.rect.height
			self.smoothroll2.value = self.smoothroll1.value
			self.smoothroll1.launch(flag='continue')
			self.smoothroll2.launch(flag='continue')
			s = self.ui.scrollbar_y
			s.smoothscroll.value = - self.smoothroll1.value / (s.codeboard.code.rect.height-s.codeboard.lineheight) * (s.rect.height-s.bd*2-s.scrollbutton.rect.height) + s.bd + s.scrollbutton.rect.height/2
			s.smoothscroll.launch(flag='continue')
		elif x and self.ui.scrollbar_x is not None:
			self.smoothroll3.value -= x * 2 * self.ui.lineheight
			if self.smoothroll3.value > self.ui.linewidth:
				self.smoothroll3.value = self.ui.linewidth
			elif self.smoothroll3.value+self.ui.code.rect.width < self.ui.rect.width-self.ui.linewidth:
				self.smoothroll3.value = self.ui.rect.width-self.ui.linewidth-self.ui.code.rect.width
			if self.ui is not self.ui.shade.father and self.smoothroll3.value < self.ui.linewidth:
				self.ui.shade.join(self.ui)
			elif self.ui is self.ui.shade.father and self.smoothroll3.value == self.ui.linewidth:
				self.ui.shade.leave()
			self.smoothroll3.launch(flag='continue')
			s = self.ui.scrollbar_x
			s.smoothscroll.value = (s.codeboard.linewidth-self.smoothroll3.value) / (s.codeboard.code.rect.width+2*s.codeboard.linewidth-s.codeboard.rect.width) * (s.rect.width-s.bd*2-s.scrollbutton.rect.width) + s.bd + s.scrollbutton.rect.width/2
			s.smoothscroll.launch(flag='continue')


class ScrollButtonWidget(fantas.ColorButtonMouseWidget):
	__slots__ = []

	def mousepress(self, pos):
		self_ = self
		self = self.ui.father
		if 0 <= pos[0] <= self.rect.width and 0 <= pos[1] <= self.rect.height:
			if not self_.mouseon:
				self.scroll_to(list(pos))
			self_.mousedown = 1 if pygame.mouse.get_pressed()[0] else None

	def mouserelease(self, pos):
		self_ = self
		self = self.ui.father
		if not(0 <= pos[0] <= self.rect.width and 0 <= pos[1] <= self.rect.height) and self_.mousedown == 1 and self.mouseonbar:
			self_.set_color('origin')
			self.mouseonbar = False

	def mousemove(self, pos):
		self_ = self
		self = self.ui.father
		if 0 <= pos[0] <= self.rect.width and 0 <= pos[1] <= self.rect.height:
			if not self.mouseonbar:
				self_.set_color('hover')
				self.mouseonbar = True
		elif self.mouseonbar and self_.mousedown != 1:
			self_.set_color('origin')
			self.mouseonbar = False
		if self_.mousedown == 1:
			self.scroll_to(list(pos))

	def handle(self, event):
		if event.type == pygame.WINDOWLEAVE:
			if self.ui.father.mouseonbar:
				self.ui.father.mouseonbar = False
				self.set_color('origin')
		else:
			super().handle(event)

	def mousein(self):
		pass

	def mouseout(self):
		pass


class ScrollBar(fantas.Label):
	__slots__ = ['mouseonbar', 'axis', 'codeboard', 'style', 'scrollbutton', 'smoothscroll', 'top', 'bottom']

	min_length = 40

	def __init__(self, codeboard, style, axis, **kwargs):
		super().__init__(bg=style['barbg'], **kwargs)
		self.mouseonbar = False
		self.axis = axis
		self.codeboard = codeboard
		self.style = style
		if axis:
			height = codeboard.rect.height/(codeboard.rect.height+codeboard.code.rect.height) * self.rect.height
			self.scrollbutton = fantas.ColorButton((8,max(height,self.min_length)), style, mousewidget=ScrollButtonWidget, topleft=(5,5))
		else:
			width = (codeboard.rect.width-codeboard.linewidth)/(codeboard.rect.width/2+codeboard.code.rect.width) * self.rect.width
			self.scrollbutton = fantas.ColorButton((max(width,self.min_length),8), style, mousewidget=ScrollButtonWidget, topleft=(5,5))
		self.scrollbutton.join(self)
		self.scrollbutton.bind(self.none)
		self.smoothscroll = fantas.RectKeyFrame(self.scrollbutton, 'centery' if axis else 'centerx', 0, 8, uimanager.curve)
		self.top = self.bd + self.scrollbutton.rect.size[axis]/2
		self.bottom = self.rect.size[axis] - self.scrollbutton.rect.size[axis]/2 - self.bd

	def none(self):
		pass

	def scroll_to(self, pos):
		if pos[self.axis] < self.top:
			pos[self.axis] = self.top
		elif pos[self.axis] > self.bottom:
			pos[self.axis] = self.bottom
		self.smoothscroll.value = pos[self.axis]
		self.smoothscroll.launch(flag='continue')
		w = self.codeboard.widget
		if self.axis:
			w.smoothroll1.value = - round(self.smoothscroll.value-self.bd-self.scrollbutton.rect.height/2) / (self.rect.height-self.bd*2-self.scrollbutton.rect.height) * (self.codeboard.code.rect.height-self.codeboard.lineheight)
			w.smoothroll2.value = w.smoothroll1.value
			w.smoothroll1.launch(flag='continue')
			w.smoothroll2.launch(flag='continue')
		else:
			w.smoothroll3.value = - round(self.smoothscroll.value-self.bd-self.scrollbutton.rect.width/2) / (self.rect.width-self.bd*2-self.scrollbutton.rect.width) * (self.codeboard.code.rect.width+2*self.codeboard.linewidth-self.codeboard.rect.width) + self.codeboard.linewidth
			w.smoothroll3.launch(flag='continue')
			if w.ui is not w.ui.shade.father and w.smoothroll3.value < w.ui.linewidth:
				w.ui.shade.join(w.ui)
			elif w.ui is w.ui.shade.father and w.smoothroll3.value == w.ui.linewidth:
				w.ui.shade.leave()


class LinenumberWidget(fantas.MouseBase):
	__slots__ = ['lines', 'breakpoints']

	def __init__(self, ui):
		super().__init__(ui, 1)
		self.lines = []
		self.breakpoints = []
		menubar.menus['调试'].items['清除所有断点'].bind(self.clear_breakpoint)

	def mousepress(self, pos):
		if self.mousedown == 1:
			if pos[0] < self.ui.rect.width:
				line = (pos[1]-self.ui.rect.top)//codeboard.lineheight+1
				if line in self.lines:
					self.del_breakpoint(line)
				else:
					self.add_breakpoint(line)
		elif self.mousedown == 3:
			if pos[0] < self.ui.rect.width:
				line = (pos[1]-self.ui.rect.top)//codeboard.lineheight+1
				if line in self.lines:
					self.del_breakpoint(line)
				else:
					self.add_breakpoint(line, form='tbreak')

	def add_breakpoint(self, line, form='b'):
		info = actionbar.add_breakpoint(line, form)
		if info[0] == '<|PythonEye Flag Error|>':
			if info[1] == 'Blank or comment':
				face.popbox.messagebox.load_message('空行或注释不支持添加断点')
				face.popbox.messagebox.show()
			elif info[1] == 'End of file':
				face.popbox.messagebox.load_message('超出文件最大行数！')
				face.popbox.messagebox.show()
		else:
			p = fantas.Ui(uimanager.breakpoint if form=='b' else uimanager.tbreakpoint, center=(codeboard.maxlinewidth+(codeboard.linewidth-codeboard.maxlinewidth)/2,(line-0.5)*codeboard.lineheight))
			p.join(self.ui)
			self.lines.append(line)
			self.breakpoints.append((int(info[0][11:11+info[0][11:].find(' ')]), p))
			if form == 'b':
				face.popbox.messagebox.load_message(f'已在第 {line} 行添加断点')
			else:
				face.popbox.messagebox.load_message(f'已在第 {line} 行添加临时断点')
			face.popbox.messagebox.show()

	def del_breakpoint(self, line, only_ui=False):
		index = self.lines.index(line)
		self.lines.pop(index)
		bp = self.breakpoints.pop(index)
		if not only_ui:
			actionbar.del_breakpoint(bp[0])
		bp[1].leave()
		face.popbox.messagebox.load_message(f'已删除第 {line} 行的断点')
		face.popbox.messagebox.show()

	def clear_breakpoint(self, only_ui=False):
		for b in self.breakpoints:
			b[1].leave()
		self.lines = []
		self.breakpoints = []
		if not only_ui:
			actionbar.clear_breakpoint()
			face.popbox.messagebox.load_message('已清除所有断点')
			face.popbox.messagebox.show()

	def del_breakpoint_bynum(self, num, only_ui=False):
		for s in range(len(self.breakpoints)):
			if self.breakpoints[s][0] == num:
				self.del_breakpoint(self.lines[s], only_ui)
				return


def openfile(file):
	global codeboard
	codeboard = CodeBoard(file)
	codeboard.join_to(menubar, 0)
	if uimanager.user_data['python_interpreter'] is None or not uimanager.user_data['python_interpreter'].is_file():
		uimanager.user_data['python_interpreter'] = None
		face.popbox.messagebox.load_message('Python解释器地址已失效，请重新选择！')
		face.popbox.messagebox.show()
	if uimanager.user_data['show_render_time']:
		face.popbox.messagebox.load_message(f'打开文件：{file.name} | 耗时：{codeboard.render_time} ms')
	else:
		face.popbox.messagebox.load_message(f'打开文件：{file.name}')
	face.popbox.messagebox.show()
	# actionbar.input_tracer.text.text = 'random'
	# actionbar.trace_arg()
	# actionbar.input_tracer.text.text = 'redo'
	# menubar.keywidget.keyboardpress('d', 'Ctrl+D')
	# menubar.keywidget.keyboardpress('s', 'Ctrl+S')
