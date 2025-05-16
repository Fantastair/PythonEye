import pygame
import pygame.freetype
import fantas
from fantas import uimanager


def split_img(img, size):
	# 将原始图像分隔为size大小的连续帧
	result = []
	r = pygame.Rect((0,0),size)
	w, h = img.get_size()
	w, h = w//size[0], h//size[1]
	for y in range(h):
		r.top = y*size[1]
		for x in range(w):
			r.left = x*size[0]
			result.append(img.subsurface(r))
	return result


class FrameAnimation(fantas.Ui):
	# 帧动画，使用关键帧控制播放

	__slots__ = ['currentframe', 'length', 'img_list', 'img']

	def __init__(self, img_list, **kwargs):
		super().__init__(img_list[0], **kwargs)
		self.currentframe = 0
		self.length = len(img_list)
		self.img_list = img_list

	def set_frame(self, frame):
		# 设置当前帧
		self.currentframe = frame
		self.img = self.img_list[frame]
		self.mark_update()

	def next_frame(self, n=1):
		# 向后切换帧，默认为1帧
		self.currentframe += n
		self.currentframe %= self.length
		self.set_frame(self.currentframe)


class Label(fantas.Ui):
	# 标签，提供了纯色背景和矩形边框
	# 可以自定义内部元素并控制其相对位置

	__slots__ = ['bd', 'bg', 'sc', 'layout_data', 'side', 'hbar', 'vbar']


	def __init__(self, size, bd=0, bg=None, sc=None, **kwargs):
		self.bd = 0
		self.bg = self.sc = self.layout_data = self.side =None
		img = pygame.Surface(size, flags=pygame.HWSURFACE | pygame.SRCALPHA)
		if bg is not None:
			self.bg = bg
			img.fill(bg)
		super().__init__(img, **kwargs)
		if bd > 0:
			self.bd = bd
			self.sc = sc
			self.create_side()

	def create_side(self):
		# 创建边框，样式需要更新时也使用此方法
		self.hbar = pygame.Surface((self.origin_size[0], self.bd), flags=pygame.HWSURFACE | pygame.SRCALPHA)
		self.vbar = pygame.Surface((self.bd, self.origin_size[1]), flags=pygame.HWSURFACE | pygame.SRCALPHA)
		if self.sc is not None:
			self.hbar.fill(self.sc)
			self.vbar.fill(self.sc)
		if self.side:
			for s in self.side:
				s.leave()
		self.side = [
			fantas.Ui(self.hbar), fantas.Ui(self.vbar),
			fantas.Ui(self.hbar, bottomleft=(0,self.origin_size[1])),
			fantas.Ui(self.vbar, topright=(self.origin_size[0],0))
			]
		for s in self.side:
			s.join(self)
		self.mark_update()

	def set_size(self, size):
		# 设置大小
		self.origin_size = self.size = size
		self.img = pygame.Surface(size, flags=pygame.HWSURFACE | pygame.SRCALPHA)
		pos = getattr(self.rect, self.anchor)
		self.rect.size = size
		setattr(self.rect, self.anchor, pos)
		if self.bg is not None:
			self.img.fill(self.bg)
		if self.bd > 0:
			self.create_side()
		self.layout()
		self.mark_update()

	def set_bg(self, bg):
		# 设置背景色
		self.bg = bg
		if bg is not None:
			self.img.fill(bg)
		else:
			self.img = pygame.Surface(self.origin_size, flags=pygame.HWSURFACE | pygame.SRCALPHA)
		self.mark_update()

	def set_sc(self, sc):
		# 设置边框色
		self.sc = sc
		if self.bd > 0:
			self.hbar.fill(sc)
			self.vbar.fill(sc)
			for s in self.side:
				s.mark_update()

	def set_bd(self, bd):
		# 设置边框粗细
		self.bd = bd
		self.create_side()

	def set_layout(self, ui, data):
		# 设置布局参数
		if self.layout_data is None:
			self.layout_data = {}
		if ui in self.layout_data:
			self.layout_data[ui].append(data)
		else:
			self.layout_data[ui] = [data]

	def layout(self):
		# 重新布局
		# 参数示例：('rect', 'center', (100,100))
		#           模式     属性        数据
		if self.layout_data is not None:
			for ui in self.layout_data:
				for data in self.layout_data[ui]:
					if data[0] == 'pos':  # 固定坐标
						setattr(ui.rect, data[1], data[2])
					elif data[0] == 'fx':  # 相对右端坐标
						setattr(ui.rect, data[1], self.rect.width+data[2])
					elif data[0] == 'fy':  # 相对底端坐标
						setattr(ui.rect, data[1], self.rect.height+data[2])
					elif data[0] == 'x':  # 固定x轴比例
						setattr(ui.rect, data[1], self.rect.width*data[2])
					elif data[0] == 'y':  # 固定y轴比例
						setattr(ui.rect, data[1], self.rect.height*data[2])
					elif data[0] == 'xy':  # 二维比例
						setattr(ui.rect, data[1], fantas.tuple_operate(self.size, data[2], fantas.mul))


class Text(fantas.Ui):
	# 单行文本，统一样式

	__slots__ = ['text', 'font', 'style']

	def __init__(self, text, font, style, **kwargs):
		# style = {'fgcolor', 'bgcolor', 'style', 'size', 'rotation'}
		# 可省略但不能多
		self.text = text
		self.font = font
		self.style = style
		super().__init__(self.draw_text(), **kwargs)

	def update_img(self):
		# 更新图像
		self.img = self.temp_img = self.draw_text()
		self.update_rect()
		self.mark_update()

	def draw_text(self):
		bounds = self.font.get_rect(self.text, size=self.style['size'], style=pygame.freetype.STYLE_DEFAULT if 'style' not in self.style else self.style['style'])
		img = pygame.Surface((bounds.width, self.font.get_sized_height(self.style['size'])), flags=pygame.HWSURFACE | pygame.SRCALPHA)
		self.font.render_to(img, (0, self.font.get_sized_ascender(self.style['size'])-bounds.top), None, **self.style)
		return img


class ChildBox(Label):
	# 内部子窗口

	def __init__(self, greedy=False, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.greedy = greedy

	def handle(self, event):
		super().handle(event)
		return self.greedy

	def set_greedy(self):
		# 独享事件
		# 可用于弹出式窗口，阻止用户进行其他操作
		fantas.Widget.apply_event(self, True)

	def unset_greedy(self):
		# 取消独享事件
		fantas.Widget.cancel_event(self, True)


class MessageBox(Label):
	# 消息提示弹窗
	__slots__ = ['pad', 'text', 'timer']

	def __init__(self, pad, lasttime, font, textstyle, *args, **kwargs):
		super().__init__((0,0), *args, **kwargs)
		self.pad = pad
		self.text = Text('', font, textstyle, topleft=(pad,pad))
		self.text.join(self)
		self.text.anchor = 'topleft'
		self.timer = fantas.Trigger(None)
		self.timer.bind_endupwith(self.leave)
		self.timer.set_trigger(lasttime)

	def load_message(self, message, force=False):
		# 加载消息
		if self.text.text != message or force:
			self.text.text = message
			self.text.update_img()
			self.set_size((self.text.rect.w+self.pad*2, self.text.rect.h+self.pad*2))

	def show(self, target=None):
		# 显示弹窗
		if target is None:
			target = uimanager.root
		self.join(target)
		self.timer.launch()


class HoverMessageBox(MessageBox):
	# 悬浮提示弹窗
	__slots__ = ['alpha_in', 'alpha_out']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.timer.bind_endupwith(self.show)
		self.alpha_in = fantas.UiKeyFrame(self, 'alpha', 255, 5, uimanager.slower_curve)
		self.alpha_out = fantas.UiKeyFrame(self, 'alpha', 0, 10, uimanager.slower_curve)
		self.alpha_out.bind_endupwith(self.leave)
		self.alpha = 0

	def show(self, target=None):
		if self.father is None:
			if target is None:
				target = uimanager.root
			self.join(target)
		self.alpha_in.launch('continue')

	def hide(self):
		if self.alpha_in.is_launched():
			self.alpha_in.stop()
		self.alpha_out.launch('continue')

	def set_pos(self, pos):
		self.rect.topleft = pos
		if self.rect.right > uimanager.size[0]:
			self.rect.right = uimanager.size[0]
		elif self.rect.bottom > uimanager.size[1]:
			self.rect.bottom = uimanager.size[1]
