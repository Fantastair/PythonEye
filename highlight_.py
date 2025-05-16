import re
import pickle
import pygame.freetype

import fantas
from fantas import uimanager


tab = 4
'''
token_map = (
	('字符串', string),
	('标识符', identifier),
	('虚数', imagnumber),
	('浮点数', floatnumber),
	('整数', integer),
	('运算符', operator),
	('分隔符', separator),
	('注释', r'#'),
	('换行', r'\n'),
	('空格', spacetab),
	('其他', r'.'),
	)
'''
token_main_obj = re.compile('|'.join('(?P<%s>%s)' % item for item in token_map))
space_obj = re.compile(spacetab)



# 关键字
keyword = r'\A' + r'\Z|\A'.join(python_args.keyword) + r'\Z'
# 定义词
definition = r'\Adef\Z|\Aclass\Z|\Alambda\Z'
# 常量
constant = r'\A' + r'\Z|\A'.join(python_args.constant) + r'\Z'
# 错误和警告
error_warning = r'\A' + r'\Z|\A'.join(python_args.error_warning) + r'\Z'
# 内建函数
builtin_function = r'\A' + r'\Z|\A'.join(python_args.builtin_function) + r'\Z'
# 内置数据类型
builtin_type = r'\A' + r'\Z|\A'.join(python_args.builtin_type) + r'\Z'
# 魔法方法
magic_method = r'\A' + r'\Z|\A'.join(python_args.magic_method) + r'\Z'

identifier_map = (
	('错误警告', error_warning),
	('魔法方法', magic_method),
	('内建函数', builtin_function),
	('内置类型', builtin_type),
	('常量', constant),
	('关键字', keyword),
	('定义', definition),
	('SELF', r'\Aself\Z'),
	)

identifier_obj = re.compile('|'.join('(?P<%s>%s)' % item for item in identifier_map))

color_map = {
	'字符串': uimanager.STRING,
	'魔法方法': uimanager.MAGCIMETHOD,
	'内建函数': uimanager.BUILTINFUNC,
	'常量': uimanager.CONSTANT,
	'关键字': uimanager.KEYWORD,
	'定义': uimanager.DEFINITION,
	'标识符': uimanager.CODE,
	'浮点数': uimanager.NUMBER,
	'整数': uimanager.NUMBER,
	'运算符': uimanager.OPERATOR,
	'分隔符': uimanager.SPLITCHAR,
	'其他': uimanager.CODE,
}

def lexical_analysis(code):
	# 词法分析
	for m in token_main_obj.finditer(code):
		form = m.lastgroup
		text = m.group()
		if form == '标识符':
			i = identifier_obj.match(text)
			if i is not None:
				form = i.lastgroup
				yield Token(form, text)
			else:
				yield Token('标识符', text)
		elif form == '空格':
			text = text.expandtabs(tab)
			yield Token(form, text)
		elif form == '字符串':
			text = text.expandtabs(tab)
			text = text.split('\n')
			length = len(text)
			for l in range(length):
				s = space_obj.match(text[l])
				if s is not None:
					yield Token('空格', s.group())
					yield Token(form, text[l][s.end():])
				else:
					yield Token(form, text[l])
				if l < length - 1:
					yield Token('换行', '\n')
		elif form == '整数':
			print(text)
		else:
			yield Token(form, text)


widths = (
	(126,    1), (159,    0), (687,     1), (710,   0), (711,   1),
	(727,    0), (733,    1), (879,     0), (1154,  1), (1161,  0),
	(4347,   1), (4447,   2), (7467,    1), (7521,  0), (8369,  1),
	(8426,   0), (9000,   1), (9002,    2), (11021, 1), (12350, 2),
	(12351,  1), (12438,  2), (12442,   0), (19893, 2), (19967, 1),
	(55203,  2), (63743,  1), (64106,   2), (65039, 1), (65059, 0),
	(65131,  2), (65279,  1), (65376,   2), (65500, 1), (65510, 2),
	(120831, 1), (262141, 2), (1114109, 1))

def get_width(s):
	# 计算单个字符宽度
	s = ord(s)
	if s == 0xe or s == 0xf:
		return 0
	for num, wid in widths:
		if s <= num:
			return wid
	return 1

jb_mono_chars = pickle.load('jb_mono_chars')


render_cache = {}
class TextRenderor():
	__slots__ = ['text', 'font','style', 'fonts', 'font_characters', 'lineheight', 'spacewidth', 'font_ascender']

	def __init__(self, text, font, default_font, lineheight, spacewidth, style):
		self.text = text
		self.font = font
		self.style = style
		self.fonts = (self.font, default_font)
		self.lineheight = lineheight
		self.spacewidth = spacewidth
		self.font_characters = jb_mono_chars
		self.font_ascender = self.font.get_sized_ascender(self.style['size'])

	def draw_text(self):
		draft = [['',0]]
		flag = True
		w = 0
		for s in self.text:
			l = get_width(s)
			if (ord(s) in self.font_characters) == flag:
				draft[-1][0] += s
				if flag:
					draft[-1][1] += l * self.spacewidth
			else:
				flag = not flag
				draft.append([s,l * self.spacewidth if flag else 0])
		if draft[0][0]:
			self.font = self.fonts[0]
		else:
			draft.pop(0)
			self.font = self.fonts[1]
		width = 0
		for s in range(len(draft)):
			i, r = self.font.render(draft[s][0], **self.style)
			self.font = self.fonts[1] if self.font == self.fonts[0] else self.fonts[0]
			draft[s].append(i)
			draft[s].append(r)
			width += draft[s][1] if draft[s][1] else r.width
		if len(draft) == 1 and draft[0][1] == 0:
			img = draft[0][2]
		else:
			img = pygame.Surface((width,self.lineheight), flags=pygame.HWSURFACE | pygame.SRCALPHA)
			pos = 0
			for s in draft:
				if s[1]:
					img.blit(s[2], (pos+(s[1]-s[3].width)/2, self.font_ascender-s[3].top))
					pos += s[1]
				else:
					img.blit(s[2], (pos, self.lineheight-s[3].height/4-s[3].top))
					pos += s[3].width
		return img


class Highlight:
	def __init__(self, file, font, default_font, style, encoding):
		self.file = file
		self.font = font
		self.default_font = default_font
		self.tabwidth = self.font.get_rect(' ' * tab, size=style['size']).width
		self.spacewidth = self.font.get_rect(' ', size=style['size']).width
		self.lineheight = max(self.font.get_sized_height(style['size']), self.default_font.get_sized_height(style['size']))
		self.style = style
		self.encoding = encoding
		with self.file.open('r', errors='ignore', encoding=self.encoding) as f:
			self.original_code = f.read()
		self.renderor = TextRenderor('', self.font, self.default_font, self.lineheight, self.spacewidth, style)
		if self.font not in render_cache:
			render_cache[self.font] = {
			pygame.freetype.STYLE_NORMAL: {},
			pygame.freetype.STYLE_OBLIQUE: {}
			}
		if self.default_font not in render_cache:
			render_cache[self.default_font] = {
			pygame.freetype.STYLE_NORMAL: {},
			pygame.freetype.STYLE_OBLIQUE: {}			
			}
		self.grammar_analysis()

	def grammar_analysis(self):
		# 语法分析
		self.lexical_code = [[]]
		state_stack = []
		line = 0
		for t in lexical_analysis(self.original_code):
			flag = True
			if t.form == '换行':
				flag = False
				line += 1
				self.lexical_code.append([])
				if state_stack and state_stack[-1]!='"""' and state_stack[-1]!="'''":
					state_stack = []
			elif t.form == '空格':
				flag = False
				self.lexical_code[line].append([t.form, t.text])
			elif t.form == '注释':
				state_stack.append('comment')
				flag = False
				self.lexical_code[line].append([t.form, '#', pygame.freetype.STYLE_NORMAL, uimanager.COMMENT])
			elif not state_stack or state_stack[-1] != 'comment':
				if t.form == '标识符':
					if not state_stack:
						state_stack.append('name')
					elif state_stack[-1] == 'class' or state_stack[-1] == 'def':
						flag = False
						self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_NORMAL, uimanager.DEFINITIONNAME])
					elif state_stack[-1] == 'class(':
						flag = False
						self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_OBLIQUE, uimanager.DEFINITIONNAME])
						state_stack[-1] = 'class(arg'
					elif state_stack[-1] == 'def(':
						flag = False
						self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_OBLIQUE, uimanager.FORMALARG])
						state_stack[-1] = 'def(arg'
					elif state_stack[-1] == 'call(':
						state_stack[-1] = 'call(arg'
					elif state_stack[-1] == 'lambda':
						flag = False
						state_stack[-1] = 'def(arg'
						self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_OBLIQUE, uimanager.FORMALARG])
				elif t.form == '分隔符':
					if state_stack:
						if t.text == '(':
							if state_stack[-1] == 'class' or state_stack[-1] == 'def':
								state_stack[-1] += '('
							elif state_stack[-1] == 'name':
								state_stack[-1] = 'call('
								if self.lexical_code[line][-1][0] == '空格':
									last = self.lexical_code[line][-2]
								else:
									last = self.lexical_code[line][-1]
								if last[0] == '标识符':
									last[3] = uimanager.CALL
							else:
								state_stack.append('(')
						elif t.text == ')':
							if '(' in state_stack[-1]:
								state_stack.pop(-1)
						elif t.text == ',':
							if state_stack[-1] in ('def(arg','call(arg'):
								state_stack[-1] = state_stack[-1][:-3]
							elif state_stack[-1] in ('def(arg=','call(arg='):
								state_stack[-1] = state_stack[-1][:-4]
							elif 'arg:' in state_stack[-1]:
								state_stack.pop(-1)
								state_stack[-1] = 'def('
						elif t.text == '.':
							if state_stack[-1] == 'class(name':
								if self.lexical_code[line][-1][0] == '空格':
									last = self.lexical_code[line][-2]
								else:
									last = self.lexical_code[line][-1]
								last[2] = pygame.freetype.STYLE_NORMAL
								last[3] = uimanager.CODE
								state_stack[-1] = 'class('
							elif state_stack[-1] == 'arg:type':
								if self.lexical_code[line][-1][0] == '空格':
									last = self.lexical_code[line][-2]
								else:
									last = self.lexical_code[line][-1]
								last[2] = pygame.freetype.STYLE_NORMAL
								last[3] = uimanager.CODE
								state_stack[-1] = 'arg:'
						elif t.text == ':':
							if 'def(' in state_stack[-1]:
								state_stack.append('arg:')
				elif t.form == '运算符':
					if state_stack and t.text == '=' and state_stack[-1] == 'call(arg':
						if self.lexical_code[line][-1][0] == '空格':
							last = self.lexical_code[line][-2]
						else:
							last = self.lexical_code[line][-1]
						last[3] = uimanager.FORMALARG
						last[2] = pygame.freetype.STYLE_OBLIQUE						
						state_stack[-1] = 'call(arg='
					elif t.text == '@' and not state_stack:
						state_stack.append('@')
				elif t.form == '定义':
					state_stack.append(t.text)
					flag = False
					self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_OBLIQUE, uimanager.DEFINITION])
				elif t.form == '字符串':
					if t.text and t.text[0] in 'rRfFbB':
						prefix = t.text[0]
						t = t._replace(text=t.text[1:])
						if t.text[0] in 'rRfFbB':
							prefix += t.text[0]
							t = t._replace(text=t.text[1:])
						if t.text[0] == '"' or t.text[0] == "'":
							self.lexical_code[line].append(['字符串前缀', prefix, pygame.freetype.STYLE_OBLIQUE, uimanager.PRESUFFIX])
						else:
							t = t._replace(text=prefix+t.text)
					else:
						prefix = None
					if state_stack:
						if state_stack[-1] == 'def(arg=' or state_stack[-1] == 'call(arg=':
							state_stack[-1] = state_stack[-1][:-1]
						elif state_stack[-1] == '"""' or state_stack[-1] == "'''":
							flag = False
							self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_NORMAL, uimanager.COMMENT])
							if t.text[-3:] == state_stack[-1]:
								state_stack.pop(-1)
					elif prefix is None and (t.text[:3] == "'''" or t.text[:3] == '"""') and (not self.lexical_code[line] or len(self.lexical_code[line])==1 and self.lexical_code[line][0][0]=='空格'):
						flag = False
						state_stack.append(t.text[:3])
						self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_NORMAL, uimanager.COMMENT])
				elif t.form == 'SELF':
					flag = False
					if self.lexical_code[line] and self.lexical_code[line][-1][1] == '.':
						self.lexical_code[line].append(['标识符', t.text, pygame.freetype.STYLE_NORMAL, uimanager.CODE])
					else:
						self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_OBLIQUE, uimanager.SELF])
				elif t.form in ('整数', '浮点数', '常量'):
					if state_stack and (state_stack[-1] == 'def(arg=' or state_stack[-1] == 'call(arg='):
						state_stack[-1] = state_stack[-1][:-1]
				elif t.form == '内置类型':
					flag = False
					if self.lexical_code[line] and self.lexical_code[line][-1][1] == '.':
						self.lexical_code[line].append(['标识符', t.text, pygame.freetype.STYLE_NORMAL, uimanager.CODE])
					else:
						self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_OBLIQUE, uimanager.BUILTINTYPE])
				elif t.form == '内建函数':
					flag = False
					if self.lexical_code[line] and self.lexical_code[line][-1][1] == '.':
						self.lexical_code[line].append(['标识符', t.text, pygame.freetype.STYLE_NORMAL, uimanager.CODE])
					else:
						self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_NORMAL, uimanager.BUILTINTYPE])
				elif t.form == '错误警告':
					flag = False
					if self.lexical_code[line] and self.lexical_code[line][-1][1] == '.':
						self.lexical_code[line].append(['标识符', t.text, pygame.freetype.STYLE_NORMAL, uimanager.CODE])
					else:
						self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_OBLIQUE, uimanager.ERRORWARNING])
				elif t.form == '虚数':
					flag = False
					self.lexical_code[line].append([t.form, t.text[:-1], pygame.freetype.STYLE_NORMAL, uimanager.NUMBER])
					self.lexical_code[line].append([t.form, t.text[-1], pygame.freetype.STYLE_OBLIQUE, uimanager.PRESUFFIX])
					if state_stack and state_stack[-1] == 'def(arg=' or state_stack[-1] == 'call(arg=':
						state_stack[-1] = state_stack[-1][:-1]
			else:
				flag = False
				self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_NORMAL, uimanager.COMMENT])
			if flag:
				self.lexical_code[line].append([t.form, t.text, pygame.freetype.STYLE_NORMAL, color_map[t.form]])
		self.line_number = len(self.lexical_code)

	def render_line(self, line):
		index = line - 1
		if self.lexical_code[index]:
			draft = []
			pos = 0
			left = 0
			for item in self.lexical_code[index]:
				if item[0] == '空格':
					if pos == 0:
						left += len(item[1]) * self.spacewidth
					else:
						pos += len(item[1]) * self.spacewidth
					item.append(left//self.tabwidth)
				else:
					color = item[3].normalize()
					if color in render_cache[self.font][item[2]]:
						if item[1] in render_cache[self.font][item[2]][color]:
							img, w, h = render_cache[self.font][item[2]][color][item[1]]
						else:
							self.renderor.text = item[1]
							self.renderor.style['style'] = item[2]
							self.renderor.style['fgcolor'] = item[3]
							img = self.renderor.draw_text()
							w, h = img.get_size()
							render_cache[self.font][item[2]][color][item[1]] = (img, w, h)
					else:
						self.renderor.text = item[1]
						self.renderor.style['style'] = item[2]
						self.renderor.style['fgcolor'] = item[3]
						img = self.renderor.draw_text()
						w, h = img.get_size()
						render_cache[self.font][item[2]][color] = {item[1]: (img, w, h)}
					draft.append((img, pos, h))
					pos += w
			img = pygame.Surface((pos,self.lineheight), flags=pygame.HWSURFACE | pygame.SRCALPHA)
			for i in draft:
				img.blit(i[0], (i[1],(self.lineheight-i[2])/2))
			return img, left
		else:
			return None, None
