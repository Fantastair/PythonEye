import os
import pickle
import pygame
import pygame.freetype

import fantas

os.environ['SDL_IME_SHOW_UI'] = '1'

class UiManager:
	# 图形管理类，用于实现主循环
	# 兼具变量共享池的作用

	def __init__(self):
		self.fps = 60
		self.root = None
		self.bg = None
		self.greedy_widgets = None
		self.keyframe_queue = []
		pygame.init()
		pygame.freetype.init()
		pygame.key.stop_text_input()
		self.keyboard_events = (pygame.KEYUP, pygame.KEYDOWN)
		self.mods = (
			pygame.K_RSHIFT, pygame.K_LSHIFT,
			pygame.K_RCTRL, pygame.K_LCTRL,
			pygame.K_RALT, pygame.K_LALT
			)
		self.mod = set()
		self.keymap = pickle.load('keymap')
		# self.keymap = pickle.load('fantas/keymap')
		self.cursor_map = {
			'^': pygame.SYSTEM_CURSOR_ARROW,  # 普通箭头
			'I': pygame.SYSTEM_CURSOR_IBEAM,  # 插入
			'o': pygame.SYSTEM_CURSOR_WAIT,  # 加载
			'+': pygame.SYSTEM_CURSOR_CROSSHAIR,  # 十字
			'^o': pygame.SYSTEM_CURSOR_WAITARROW,  # 箭头+等待（不存在的话就是等待）
			'\\': pygame.SYSTEM_CURSOR_SIZENWSE,  # \双向箭头
			'/': pygame.SYSTEM_CURSOR_SIZENESW, # /双向箭头
			'-': pygame.SYSTEM_CURSOR_SIZEWE,  # -双向箭头
			'|': pygame.SYSTEM_CURSOR_SIZENS,  # |双向箭头
			'^+': pygame.SYSTEM_CURSOR_SIZEALL,  # 十字四向箭头
			'no': pygame.SYSTEM_CURSOR_NO,  # 禁止
			'hand': pygame.SYSTEM_CURSOR_HAND,  # 手掌
		}
		self.cursor_stack = [pygame.SYSTEM_CURSOR_ARROW]

	def init(self, size, r=None, flags=None):
		# 初始化（创建窗口等）
		self.clock = pygame.time.Clock()
		if r is None:
			info = pygame.display.Info()
			# if size[0] < info.current_w and size[1] < info.current_h:
			# 	r = 1
			if info.current_w/info.current_h < size[0]/size[1]:
				r = info.current_w*0.8 / size[0]
			else:
				r = info.current_h*0.8 / size[1]
		self.r = r
		self.size = (size[0]*r, size[1]*r)
		if flags is None:
			flags = pygame.HWSURFACE | pygame.SRCALPHA
		self.screen = pygame.display.set_mode(self.size, flags=flags)

	def allow_events(self, events):
		# 设置只开放的事件
		pygame.event.set_blocked(None)
		pygame.event.set_allowed(events)

	def mainloop(self, quit):
		# 主循环
		while True:
			self.clock.tick(self.fps)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quit()
				elif event.type in self.keyboard_events:
					if event.type == pygame.KEYDOWN:
						if event.key in self.mods:
							self.mod.add(self.keymap[event.key])
					elif event.type == pygame.KEYUP:
						if event.key in self.mods:
							self.mod.discard(self.keymap[event.key])
					event.key = self.keymap.get(event.key)
					if event.key is None:
						continue
					event.shortcut = self.join(event.key)
				if self.greedy_handle(event):
					self.root.handle(event)
			self.transform()
			# self.render_times = 0
			if self.render():
				pygame.display.flip()
				# print(self.render_times)
	def join(self, key) -> str:
		# 用'+'将修饰键与key连接为一个字符串
		# 修饰键优先级：Ctrl > Shift > Alt
		# 不区分左右修饰键，注意首字母大写
		if self.mod:
			return '+'.join([c for c in ('Ctrl', 'Shift', 'Alt') if c in [k.split()[1].capitalize() for k in self.mod]]) + ('+' + key.capitalize() if key not in self.mod else '')
		else:
			return key.capitalize()


	def greedy_handle(self, event):
		# 贪婪事件处理，可以让组件独吞事件
		# 组件的 handle 方法返回 True 时将结束事件处理
		if self.greedy_widgets is not None:
			for w in self.greedy_widgets:
				if w.handle(event):
					break
			else:
				return True
		else:
			return True

	def transform(self):
		# 关键帧变换
		for k in self.keyframe_queue:
			k.tick()

	def render(self):
		# 渲染
		if self.root.update_flag:
			if self.bg is not None:
				self.screen.fill(self.bg)
			self.root.render(self.screen)
			return True
		else:
			return False

	def load_color(self, file):
		# 加载预设颜色
		with open(file) as f:
			for color in f.readlines():
				name, value = color.strip().split()
				setattr(self, name, pygame.Color(value))

	def load_font(self, path):
		# 加载字体
		for file in os.listdir(path):
			setattr(self, file.split('.')[0], pygame.freetype.Font(path+'/'+file, 20))

	def load_image(self, path, scale=True):
		# 加载图片
		for file in os.listdir(path):
			img = pygame.image.load(path+'/'+file).convert_alpha()
			if scale and self.r != 1:
				w, h = img.get_size()
				img = pygame.transform.smoothscale(img, (w*self.r,h*self.r))
			setattr(self, file.split('.')[0], img)

	def load_sound(self, path):
		# 加载声音
		for file in os.listdir(path):
			setattr(self, file.split('.')[0], pygame.mixer.Sound(path+'/'+file))

	def set_cursor(self, shape):
		self.cursor_stack.append(self.cursor_map[shape])
		pygame.mouse.set_cursor(self.cursor_map[shape])

	def set_cursor_back(self):
		self.cursor_stack.pop()
		if not self.cursor_stack:
			self.cursor_stack.append(self.cursor_map['^'])
		pygame.mouse.set_cursor(self.cursor_stack[-1])


uimanager = UiManager()

# 预设曲线
# y = x
uimanager.curve = fantas.Curve()
# 渐快(加速)
# uimanager.faster_curve = fantas.FormulaCurve('math.sin(math.pi/2*x)')
# 渐慢(刹车/弹射)
uimanager.slower_curve = fantas.FormulaCurve('1-math.cos(math.pi/2*x)')
# 简谐(平滑/惯性)
uimanager.harmonic_curve = fantas.FormulaCurve('(1-math.cos(math.pi*x))/2')
# 正弦(抖动/原地)
uimanager.sin_curve = fantas.FormulaCurve('math.sin(math.pi*x*2)')

_mouse_events = (
	pygame.MOUSEMOTION,
	pygame.MOUSEBUTTONUP,
	pygame.MOUSEBUTTONDOWN
	)


class Ui(fantas.NodeBase):
	# 图形显示的基本单元

	__slots__ = ['anchor', 'angle', 'alpha', 'origin_alpha', 'update_flag', 'widgetgroup', 'img', 'size', 'origin_size', 'rect', 'temp_img']

	def __init__(self, img, **anchor):
		self.anchor = 'center'
		self.angle = 0
		self.alpha = self.origin_alpha = 255
		self.update_flag = True
		self.widgetgroup = None
		super().__init__()
		self.img = img
		self.size = self.origin_size = img.get_size()
		self.rect = img.get_rect(**anchor)

	def mark_update(self):
		# 标记图像更新
		# 重复标记是安全且节能的
		self.update_flag = True
		while not self.is_root():
			self = self.father
			if self.update_flag:
				break
			self.update_flag = True

	def update_rect(self, anchor=None):
		# 同步rect以匹配temp_img
		if anchor is None:
			anchor = self.anchor
		pos = getattr(self.rect, anchor)
		self.rect.size = self.temp_img.get_size()
		setattr(self.rect, anchor, pos)

	def apply_angle(self):
		# 应用angle变换
		if self.angle != 0:
			self.img = pygame.transform.rotate(self.img, self.apply_angle)
			self.angle = 0

	def apply_size(self):
		# 应用size变换
		if self.size != self.origin_size:
			self.img = self.temp_img = pygame.transform.smoothscale(self.img, self.size)
			self.origin_size = self.size
			self.update_rect()

	def apply_alpha(self):
		# 应用alpha变换
		if self.angle != self.origin_alpha:
			self.img.set_alpha(self.alpha)
			self.origin_alpha = alpha

	def handle(self, event):
		# 事件预加工 + 传递
		if self.widgetgroup:
			if not self.is_root() and event.type in _mouse_events:
				father_pos = event.pos
				my_pos = (event.pos[0]-self.rect.left, event.pos[1]-self.rect.top)
				for w in self.widgetgroup:
					if isinstance(w, Ui):
						if w in self.kidgroup:
							event.pos = my_pos
							w.handle(event)
					else:
						event.pos = father_pos
						w.handle(event)
				event.pos = father_pos
			else:
				for w in self.widgetgroup:
					w.handle(event)

	def apply_event(self, widget):
		# 添加事件申请者
		# 重复添加是安全且节能的
		if self.widgetgroup is None:
			self.widgetgroup = []
		while self is not None and widget not in self.widgetgroup:
			self.widgetgroup.append(widget)
			widget = self
			self = self.father
			if self is not None and self.widgetgroup is None:
				self.widgetgroup = []

	def cancel_event(self, widget):
		# 取消事件申请者
		# 重复取消是安全且节能的
		while self is not None and self.widgetgroup is not None and widget in self.widgetgroup:
			self.widgetgroup.remove(widget)
			if not self.widgetgroup:
				widget = self
				self = self.father
			else:
				break

	def render(self, target=None):
		# 渲染
		if target is not None:
			self.temp_img = target
			self.temp_img.blit(self.img, self.rect)
			if not self.is_leaf():
				for ui in self.kidgroup:
					ui.render()
		elif not self.update_flag:
			self.father.temp_img.blit(self.temp_img, self.rect)
		else:
			size = self.size != self.origin_size
			angle = self.angle != 0
			alpha = self.alpha != self.origin_alpha
			if self.is_leaf():
				self.temp_img = self.img
			else:
				self.temp_img = self.img.copy()
				if not self.is_leaf():
					for ui in self.kidgroup:
						ui.render()
			if any((size, angle, alpha)):
				if size:
					self.temp_img = pygame.transform.smoothscale(self.temp_img, self.size)
				if angle:
					self.temp_img = pygame.transform.rotate(self.temp_img, self.angle)
				if alpha:
					self.temp_img.set_alpha(self.alpha)
				if size or angle:
					self.update_rect()
			self.father.temp_img.blit(self.temp_img, self.rect)
		self.update_flag = False
		# uimanager.render_times += 1

	def get_absolute_pos(self):
		# 获得绝对位置(left, top)
		left = top = 0
		while not self.is_root():
			left += self.rect.left
			top += self.rect.top
			self = self.father
		return (left, top)

	def append(self, node):
		super().append(node)
		self.mark_update()
		if node.widgetgroup:
			self.apply_event(node)

	def insert(self, node, index):
		super().insert(node, index)
		self.mark_update()
		if node.widgetgroup:
			self.apply_event(node)

	def remove(self, node):
		super().remove(node)
		if self.widgetgroup is not None and node in self.widgetgroup:
			self.widgetgroup.remove(node)
		self.mark_update()

	def remove_index(self, index):
		node = self.kidgroup.pop(index)
		node.father = None
		if self.widgetgroup is not None and node in self.widgetgroup:
			self.widgetgroup.remove(node)
		self.mark_update()


class Widget:
	# 组件基类， 接收事件并处理

	__slots__ = ['ui']

	def __init__(self, ui):
		self.ui = ui

	def apply_event(self, greedy=False):
		# 申请事件
		# 重复申请是安全且节能的
		# 将 greedy 设置为 True 可以进入贪婪处理
		if greedy:
			if uimanager.greedy_widgets is None:
				uimanager.greedy_widgets = [self]
			elif self not in uimanager.greedy_widgets:
				uimanager.greedy_widgets.insert(0, self)
		else:
			self.ui.apply_event(self)

	def cancel_event(self, greedy=False):
		# 取消事件
		# 重复取消是安全且节能的
		# 将 greedy 设置为 True 可以退出贪婪处理
		if greedy:
			if uimanager.greedy_widgets is not None and self in uimanager.greedy_widgets:
				uimanager.greedy_widgets.remove(self)
		else:
			self.ui.cancel_event(self)

	def applied(self):
		# 判断事件是否已申请
		return self in self.ui.widgetgroup

	def handle(self, event):
		# 事件处理，由子类定义
		pass


class UiGroup(Ui):
	# Ui组，用于方便地管理多个同级Ui对象
	# 参与位置嵌套

	__slots__ = ['rect_locked', 'widgetgroup', 'rect', 'anchor']

	def __init__(self):
		fantas.NodeBase.__init__(self)
		self.anchor = 'center'
		self.rect_locked = False
		self.widgetgroup = None
		self.rect = pygame.Rect((0,0,0,0))

	def update_rect(self, anchor=None):
		if anchor is None:
			anchor = self.anchor
		pos = getattr(self.rect, anchor)
		length = len(self.kidgroup)
		if length == 1:
			self.rect.size = self.kidgroup[0].rect.size
		elif length != 0:
			self.rect.size = self.kidgroup[0].rect.unionall([ui.rect for ui in self.kidgroup[1:]]).size
		setattr(self.rect, anchor, pos)

	def render(self, target=None):
		if target is None:
			self.temp_img = self.father.temp_img
		else:
			self.temp_img = target
		if not self.rect_locked:
			self.update_rect()
		for ui in self.kidgroup:
			ui.rect.left += self.rect.left
			ui.rect.top += self.rect.top
			ui.render()
			ui.rect.left -= self.rect.left
			ui.rect.top -= self.rect.top
