import fantas
from fantas import uimanager

# blank_tuple = tuple()


class KeyFrame:
	# 关键帧基类，提供了自动插值方法
	# 由子类定义如何利用自动插值的数据
	# 也可以用作实现定时触发函数(已经封装在Trigger类里)

	__slots__ = ['curve', 'endupwith', 'args', 'kwargs', 'start', 'totalframe', 'offset', 'currentframe']

	def __init__(self, curve):
		self.curve = curve
		self.endupwith = None

	def bind_endupwith(self, func, *args, **kwargs):
		# 绑定结束动作
		self.endupwith = func
		self.args = args
		self.kwargs = kwargs

	def set_keyframe(self, start, value, totalframe, absolute=True):
		# 设置关键帧参数
		self.start = start
		self.totalframe = totalframe
		if absolute:
			if isinstance(value, tuple):
				self.offset = fantas.tuple_operate(value, start, fantas.sub)
			else:
				self.offset = value - start
		else:
			self.offset = value

	def launch(self):
		# 启动关键帧
		self.currentframe = 1
		if self not in uimanager.keyframe_queue:
			uimanager.keyframe_queue.append(self)

	def stop(self):
		# 关闭关键帧（重复关闭是安全的）
		if self in uimanager.keyframe_queue:
			uimanager.keyframe_queue.remove(self)

	def is_launched(self):
		# 判断是否已经启动
		return self in uimanager.keyframe_queue

	def tick(self):
		# 进入下一帧
		self.currentframe += 1
		if self.currentframe == self.totalframe+1:
			uimanager.keyframe_queue.remove(self)
			if self.endupwith is not None:
				self.endupwith(*self.args, **self.kwargs)

	def transform(self):
		# 执行一次变换
		r = self.curve.calc(self.currentframe/self.totalframe)
		if isinstance(self.offset, tuple):
			return fantas.tuple_operate(self.start, fantas.tuple_int_operate(self.offset, r, fantas.mul), fantas.add)
		else:
			return self.start + self.offset * r


class Trigger(KeyFrame):
	# 函数触发器
	# 使用KeyFrame的记帧功能实现
	# 曲线参数不会用到，可以传None

	__slots__ = ['totaltime']

	def set_trigger(self, time):
		# 永久设定触发时间
		self.totaltime = time

	def launch(self, time=None):
		# 启动触发器
		# time参数可临时指定触发时间
		if time is None:
			self.totalframe = self.totaltime
		else:
			self.totalframe = time
		super().launch()


class AttrKeyFrame(KeyFrame):
	# 属性赋值型关键帧
	# 可以自动获取起始值

	__slots__ = ['subject', 'attr', 'value', 'absolute']

	def __init__(self, subject, attr, value, totalframe, curve, absolute=True):
		self.subject = subject
		self.attr = attr
		self.value = value
		self.totalframe = totalframe
		self.absolute = absolute
		super().__init__(curve)

	def tick(self):
		setattr(self.subject, self.attr, self.transform())
		super().tick()

	def launch(self, flag='nothing', start=None):
		# 启动关键帧
		if self.is_launched():
			if flag == 'restart':  # 重新开始
				self.currentframe = 0
			elif flag == 'continue':  # 从此开始
				if start is None:
					start = getattr(self.subject, self.attr)
				self.set_keyframe(start, self.value, self.totalframe, self.absolute)
				self.currentframe = 1
		else:
			self.currentframe = 1
			if start is None:
				start = getattr(self.subject, self.attr)
			self.set_keyframe(start, self.value, self.totalframe, self.absolute)
			uimanager.keyframe_queue.append(self)


class UiKeyFrame(AttrKeyFrame):
	# 控制<Ui>对象的size、angle、alpha属性
	# 特别地，对于<FrameAnimation>对象，可以控制其currentframe属性实现帧动画

	__slots__ = []

	def tick(self):
		super().tick()
		self.subject.mark_update()


class RectKeyFrame(AttrKeyFrame):
	# 控制<Ui>对象的rect的位置

	__slots__ = ['ui']

	def __init__(self, ui, *args, **kwargs):
		self.ui = ui
		super().__init__(ui.rect, *args, **kwargs)

	def tick(self):
		super().tick()
		if not self.ui.is_root():
			self.ui.father.mark_update()


class LabelKeyFrame(AttrKeyFrame):
	# 控制<Label>对象的set系列方法实现动画

	def __init__(self, label, *args, **kwargs):
		self.label = label
		super().__init__(label, *args, **kwargs)

	def tick(self):
		getattr(self.label, f'set_{self.attr}')(self.transform())
		KeyFrame.tick(self)
