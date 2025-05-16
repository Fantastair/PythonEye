import socket
import subprocess
from threading import Thread
from multiprocessing import Queue


def get_free_port():
	# 获取可用的端口号
	with socket.socket() as sock:
		sock.bind(('',0))
		port = sock.getsockname()[1]
	return port

class Debugger:
	'''
	这是用于控制代码调试的类；
	调用open_eye方法后即进入调试并等待命令；
	使用do_command方法发送命令并返回调试信息，命令语法和pdb一致；
	do_command方法会阻塞线程直到获得返回信息，
	下延时可以忽略，除非被调试的代码段有明显耗时；
	调试结束后会自动退出，如果中途需要退出，调用close_eye方法；
	'''
	__slots__ = ['finished', 'file', 'python', 'PORT', 'ADDR', 'input_queue', 'output_queue', 'client_thread', 'again', 'pythoneye', 'com_record', 'stdout', 'stdin', 'stderr']

	HOST = 'localhost'
	BUFFSIZE = 1024*64

	def __init__(self, file, python, stdout, stdin, stderr):
		# file：待调试的py文件路径
		# python：解释器路径

		self.finished = True
		self.file = file
		self.python = python
		self.PORT = get_free_port()
		self.ADDR = (self.HOST, self.PORT)
		self.input_queue = Queue() #  输入命令队列
		self.output_queue = Queue()  # 返回信息队列
		self.stdout, self.stdin, self.stderr = stdout, stdin, stderr

	def open_eye(self):  # 开启调试(可以重复开启)
		if not self.finished:  # 结束已开启的调试调试(如果有)
			self.close_eye()
			self.client_thread.join()
			self.pythoneye.terminate()
		# 开启新一轮调试
		self.finished = False
		self.again = True
		self.com_record = []
		self.pythoneye = subprocess.Popen([self.python, '-m', 'eye', self.file, str(self.PORT)])
		self.client_thread = Thread(target=self.start_client)
		self.client_thread.daemon = True
		self.client_thread.start()

	def start_client(self):
		with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as server:
			server.connect(self.ADDR)
			while not self.finished:
				if self.again:
					command = 'None'
					self.again = False
				else:
					command = self.input_queue.get()
					self.again = True
				server.send(command.encode())
				receive = server.recv(self.BUFFSIZE).decode()
				while '<|PythonEye Flag Stdin|>' == receive or '<|PythonEye Flag Stderr|>' in receive or '<|PythonEye Flag Stdout|>' in receive:
					if '<|PythonEye Flag Stdout|>' in receive:
						self.stdout(receive[25:])
						receive = server.recv(self.BUFFSIZE).decode()
					elif '<|PythonEye Flag Stdin|>' == receive:
						server.send(self.stdin().encode())
						receive = server.recv(self.BUFFSIZE).decode()
					else:
						self.stderr(receive[25:])
						receive = server.recv(self.BUFFSIZE).decode()
				if not self.again or receive != '<|PythonEye Flag Empty Info|>':
					self.output_queue.put(receive)
					if receive == '<|PythonEye Flag Debugger Over|>' or self.pythoneye.poll() is not None:
						self.finished = True
			self.pythoneye.terminate()

	def do_command(self, command):  # 输入一条指令并返回调试信息(会阻塞)
		self.input_queue.put(command)
		info = self.output_queue.get().split('<|PythonEye Flag Line|>')
		self.com_record.append(command)
		# print('(Eye)', command)
		# print(info, end='\n\n')
		return info

	def close_eye(self):  # 关闭调试
		self.do_command('q')
		self.pythoneye.terminate()


# ***==========以下为测试用代码==========***


if __name__ == '__main__':
	import os
	debugger = Debugger(
		os.getcwd()+'\\test\\多人石头剪刀布(期末卷12题).py',
		[i for i in os.environ['PATH'].split(';') if 'Python' in i and 'Scripts' not in i][0]+"python.exe")
	debugger.open_eye()

	print(debugger.output_queue.get())
	while not debugger.finished:
		c = input('(Eye) ')
		if not c:
			c = 'None'
		print(str(debugger.do_command(c)))
