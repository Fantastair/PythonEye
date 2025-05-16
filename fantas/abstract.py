class NodeBase:
	# 这是一个抽象的树节点类，仅实现了对节点间的结构操作(即指针域)
	# 如何定义数据域由继承它的子类决定

	__slots__ = ['kidgroup', 'father']

	def __init__(self):
		self.kidgroup = None  # 存储孩子节点，有序，默认为None以节省空间
		self.father = None  # 存储父节点

	def append(self, node):
		# 添加node节点至最后
		if self.kidgroup is None:
			self.kidgroup = []
		if not node.is_root():
			node.leave()
		node.father = self
		self.kidgroup.append(node)

	def insert(self, node, index):
		# 插入node至index位置
		if self.kidgroup is None:
			self.kidgroup = []
		if not node.is_root():
			node.leave()
		node.father = self
		self.kidgroup.insert(index, node)

	def remove(self, node):
		# 从自己的子节点中移除node
		if self.kidgroup is None:
			self.kidgroup = []
		if node in self.kidgroup:
			self.kidgroup.remove(node)
			node.father = None

	def remove_index(self, index):
		# 移除index位置的node
		self.kidgroup.pop(index).father = None

	def join(self, node):
		# 将自己作为子节点添加至node中
		node.append(self)

	def join_to(self, node, index):
		# 添加至index位置
		node.insert(self, index)

	def leave(self):
		# 从父节点中移除
		self.father.remove(self)

	def move_to(self, n):
		# 移至位置n
		self.father.kidgroup.remove(self)
		self.father.kidgroup.insert(n, self)

	def move_up(self, n=1):
		# 上移n层(默认为1)
		self.move_to(self.get_index() + n)

	def move_down(self):
		# 下移n层(默认为1)
		self.move_to(self.get_index() - n)

	def move_top(self):
		# 移至顶部
		self.move_to(len(self.father.kidgroup))

	def move_bottom(self):
		# 移至底部
		self.move_to(0)

	def exchange(self, node):
		# 与node节点交换位置
		if self.father is not None:
			self.father.kidgroup[self.get_index()] = node
		if node.father is not None:
			node.father.kidgroup[node.get_index()] = self
		self.father, node.father = node.father, self.father
		self.kidgroup, node.kidgroup = node.kidgroup, self.kidgroup

	def get_index(self):
		# 查询自己在父节点中的位置
		return self.father.kidgroup.index(self)

	def get_degree(self):
		# 查询自己的度
		return len(self.kidgroup) if self.kidgroup is not None else 0

	def is_root(self):
		# 是否为根节点
		return self.father is None

	def is_leaf(self):
		# 是否为叶子节点
		return not self.kidgroup

	def is_branch(self):
		# 是否为分支节点(不包括根节点)
		return not self.is_root() and not self.is_leaf()

	def is_top(self):
		# 是否在顶层
		return self.father.kidgroup[-1] is self

	def is_bottom(self):
		# 是否在底层
		return self.father.kidgroup[0] is self

	def is_brother(self, node):
		# node是否为自己的兄弟节点
		return self.father is node.father

	def get_father(self, n):
		# 向上查询父节点，n层
		for s in range(n):
			self = self.father
		return self

	def get_root(self):
		# 查询根节点
		while not self.is_root():
			self = self.father
		return self

	def get_floor(self):
		# 查询当前层数
		floor = 1
		while not self.is_root():
			self = self.father
			floor += 1
		return floor

	def get_distance(self, node):
		# 查询与node的距离(层数之差)
		return abs(self.get_floor()-node.get_floor())

	def is_fathers(self, node):
		# 是否为node的父系节点(node在自己的子树上)
		# 特别的，自己也是自己的父系节点
		while node is not self:
			node = node.father
			if node is None:
				return False
		return True

	def is_kids(self, node):
		# 是否是node的子系节点(即node是否是自己的父系节点)
		return node.is_fathers(self)

	def get_depth(self):
		# 查询自己子树(包含自己)的深度
		# 注意！使用递归算法，可能会消耗较多资源
		if self.is_leaf():
			return 1
		else:
			return max([n.get_depth() for n in self.kidgroup]) + 1


class Curve:
	# 这是一个抽象的曲线基类，提供了预加载方法，也可作为y=x使用

	__slots__ = ['method', 'temp', 'level']

	def __init__(self):
		self.method = (self.calc, self.calc_temp)

	def calc(self, x):
		# 用x求出y
		# 在子类里需要重写此方法以实现不同的曲线
		return x

	def calc_temp(self, x):
		# 从temp里求值
		return self.temp[round(self.level*x)]

	def compile(self, level):
		# 预加载方法，level指定加载位数
		# 加载后的数据保存在temp里，调用use_temp方法以使用预加载的数据
		# 求值时只会得到temp里的数据
		self.temp = [self.calc(x//level) for x in range(level+1)]
		self.level = level

	def use_temp(self):
		# 使用预加载的数据
		self.calc = self.method[1]

	def use_calc(self):
		# 使用实时计算
		self.calc = self.method[0]


import math
class FormulaCurve(Curve):
	# 单公式曲线

	__slots__ = ['formula']

	def __init__(self, formula: str):
		super().__init__()
		self.formula = formula  # formula是包含x的数学表达式，可以使用math库的函数

	def calc(self, x):
		return eval(self.formula)


class BezierCurve(Curve):
	# 贝塞尔曲线，3阶，1段

	__slots__ = ['points']

	factor = (1, 3, 3, 1)
	def __init__(self, points):
		# 该曲线必须预加载才能使用
		super().__init__()
		self.points = points
		self.use_temp()

	def compile(self, level):
		# 这里的level是精细度，越小越精细
		x = 0
		p = [0, 0]
		self.level = int(1//level + 1)
		self.temp = []
		while x <= 1:
			p[0] = p[1] = 0
			for i in range(4):
				r = self.factor[i] * x**i * (1-x)**(3-i)
				p[0] += r * self.points[i][0]
				p[1] += r * self.points[i][1]
			self.temp.append(tuple(p))
			x += level

	def calc_temp(self, x):
		i, j = 0, self.level-1
		while i != j-1:
			m = (i+j)//2
			if x < self.temp[m][0]:
				j = m
			else:
				i = m
		offset = self.temp[j][1] - self.temp[i][1]
		return self.temp[i][1] + offset*(x-self.temp[i][0])/(self.temp[j][0]-self.temp[i][0])


class SuperCurve(Curve):
	# 超级曲线(分段曲线)，可实现一系列曲线的分段整合

	__slots__ = ['curves', 'splits']

	def __init__(self, curves, splits):
		super().__init__()
		self.curves = curves  # 存储曲线
		self.splits = (0,) + splits + (1,)  # 划分定义域

	def calc(self, x):
		# 基于二分查找快速确定定义域并求值
		i, j = 0, len(self.splits)-1
		while i != j-1:
			m = (i+j)//2
			if x < self.splits[m]:
				j = m
			else:
				i = m
		return self.curves[i].calc(x)


# 数字运算函数
add = lambda a,b:a+b
sub = lambda a,b:a-b
mul = lambda a,b:a*b
div = lambda a,b:a/b
mod = lambda a,b:a%b
fld = lambda a,b:a//b

# 元组运算，operation是数字运算的函数
def tuple_operate(t1, t2, operation):
	return tuple(map(operation, t1, t2))

def tuple_int_operate(t, i, operation):
	return tuple([operation(s,i) for s in t])
