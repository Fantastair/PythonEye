'''
import os

def search(folder):
	for file in os.listdir(folder):
		if os.path.isdir(folder+'\\'+file):
			search(folder+'\\'+file)
		elif os.path.isfile(folder+'\\'+file) and file.endswith('.py'):
			# print(folder+'\\'+file)
			with open(folder+'\\'+file, 'r', encoding='utf-8') as f:
				if 'pygame.error:' in f.read():
					print('->', folder+'\\'+file)

search('C:\\Python\\myvenv\\pygame_env\\Lib\\site-packages\\pygame')
'''
import pickle
from pathlib import Path

data = pickle.load('user_data')

# data['last_file'] = 'c:/python/01.机场霸王/v_0.7/main.py'
# data['python_interpreter'] = 'c:/python/myvenv/pygame_env/scripts/pythonw.exe'
# data['python_interpreter'] = Path('c:/python/myvenv/pygame_env/scripts/python.exe')
# data['python_interpreter'] = None
# data['show_recorder_tip'] = True
# data['last_eye'] = None
# data['python_interpreter'] = None
print(data)
# for s in data:
	# print(s)
	# print(data[s])
	# print()

# with open('user_data', 'wb') as f:
# 	pickle.dump(data, f)
'''
import os

# print(os.environ['path'])
print([i for i in os.environ['PATH'].split(';') if 'Python' in i and 'Scripts' not in i][0]+"pythonw.exe")

'''
