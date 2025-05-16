'''
print_ = print
def myprint(*value, file=None, sep=' ', end='\n', flush=False):
	print_('劫持print>>>', *value)

input_ = input
def myinput(prompt):
	return input_('劫持input>>>'+prompt)

# __builtins__.print = myprint
# __builtins__.input = myinput
print(type(__builtins__))

import pdb
pdb.run('a=1\nb=2\nc=3')

import pickle

with open('fantas/keymap', 'rb') as f:
	data = pickle.load(f)

for s in data:
	if 'arrow' in data[s]:
		data[s] = data[s].split()[0]
		print(s, ':', data[s])
print('abc')
with open('fantas/keymap', 'wb') as f:
	data = pickle.dump(data, f)

from fontTools.ttLib import TTFont
chars = TTFont('res/font/jb_mono.ttf')['cmap'].tables[0].ttFont.getBestCmap()

for s in chars:
	print(s, chars[s], chr(s))
import pickle
import pygame

with open('fantas/keymap_info.txt') as f:
	origin_data = f.readlines()

result = {}
for line in origin_data:
	key = line[:14].strip()
	exec(f'result[pygame.{key}] = line[22:].strip()')

print(result)

with open('fantas/keymap', 'wb') as f:
	pickle.dump(result, f)

# with open('fantas/keymap', 'rb') as f:
	# data = pickle.load(f)

# print(data)

# for s in data:
	# print(s, data[s])

import re
import requests

url = 'https://blog.csdn.net/2301_79102953/article/details/131678078'
head = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42"
}

resp = requests.get(url, headers=head)

version_obj = re.compile(r'<p>&lt;版本信息&#xff1a;Version (?P<version>.*?)&gt;</p>')

print(version_obj.search(resp.text).group('version'))
# print(resp.text)
'''
# import pickle

# with open('test/123.eye', 'rb') as f:
# 	a = pickle.load(f)

# print(a['file'])
# print()
# print(a['breakpoints'])
# print(a['line_number'])
# print()
# for s in a['com_record']:
# 	print(s[0])
# 	print(s[1])
# print(a['original_code'])


# import pickle
# with open('test/多人石头剪刀布(期末卷12题).eye', 'rb') as f:
	# data = pickle.load(f)
# with open('user_data', 'rb') as f:
	# data = pickle.load(f)

# data['auto_scale'] = True
# data['python_interpreter'] = None
# data['auto_search_python'] = True
# data['show_check_result'] = True
# data['auto_scale'] = False
# data['show_render_time'] = True
# del data['use_highlight']
# data['python_interpreter'] = None
# for s in data:
	# print(s, ':', data[s])
# l = [s for s in data]
# print(l)

# with open('user_data', 'wb') as f:
	# pickle.dump(data, f)

# for s in data:
# 	print(s)
# 	print(data[s])
# 	print()
# import os
# from pathlib import Path


# def search_python():
# 	for s in os.environ['PATH'].split(';'):
# 		if 'Python' in s and 'Scripts' in s:
# 			p = Path(s).parent / 'pythonw.exe'
# 			if p.exists():
# 				break
# 	else:
# 		p = None
# 	return p
# import pickle

# with open('user_data', 'rb') as f:
	# print(pickle.loads(f.read()[::-1]))

# print(search_python())
file = 'user_data'
with open(file, 'rb') as f:
	data = f.read()[::-1]

import pickle
data = pickle.loads(data)
data['close_direct'] = False
data['python_interpreter'] = None
for s in data:
	print(s, data[s])
data = pickle.dumps(data)[::-1]
with open(file, 'wb') as f:
	f.write(data)
