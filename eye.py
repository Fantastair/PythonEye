import os
import bdb
import sys
import socket
import threading
import multiprocessing
import pdb
from pdb import *
for s in pdb.__dict__:
	if s[0] == '_' and s[1] != '_':
		exec(f'{s} = pdb.{s}')

python_version = sys.version_info[:3]
if python_version[0] < 3 or python_version[1] < 11 or python_version[2] < 4:
	import io
	io.open_ = io.open
	io.open = io.open_code


class Stdout:
	def __init__(self, flag, pythoneye):
		self.flag = flag
		self.pythoneye = pythoneye

	def write(self, data):
		self.pythoneye.output_queue.put(self.flag + data)


class Stdin:
	def __init__(self, flag, pythoneye):
		self.flag = flag
		self.pythoneye = pythoneye
		self.input_queue = multiprocessing.Queue()

	def write(self, data):
		self.input_queue.put(self.input_queue.get()+data if not self.input_queue.empty() else data)

	def readline(self):
		return self.read(i = self.data.find('\n'))

	def read(self, i=-1):
		self.pythoneye.output_queue.put(self.flag)
		data = self.input_queue.get()
		if i != -1:
			result = data[:i+1]
			data = data[i+1:]
		else:
			result = data[:]
			data = ''
		if data:
			self.input_queue.put(data)
		return result


class PythonEye(Pdb):
	HOST = 'localhost'
	BUFFSIZE = 1024*64

	def __init__(self, port):
		super().__init__()
		self.PORT = port
		self.ADDR = (self.HOST, self.PORT)
		self.input_queue = multiprocessing.Queue()
		self.output_queue = multiprocessing.Queue()
		self.debugger_info_temp = []
		threading.Thread(target=self.start_server).start()

	def start_server(self):
		try:
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
				server.bind(self.ADDR)
				server.listen(1)
				conn, addr = server.accept()
				while True:
					info = conn.recv(self.BUFFSIZE).decode()
					if info != '<|PythonEye Flag Receive|>':
						self.input_queue.put(info)
					info = self.output_queue.get()
					while '<|PythonEye Flag Stdin|>' == info or '<|PythonEye Flag Stderr|>' in info or '<|PythonEye Flag Stdout|>' in info:
						conn.send(info.encode())
						if '<|PythonEye Flag Stdin|>' == info:
							info = conn.recv(self.BUFFSIZE).decode()
							sys.stdin.input_queue.put(info)
						info = self.output_queue.get()
					conn.send(info.encode())
					if info == '<|PythonEye Flag Debugger Over|>':
						break
				conn.close()
		except:
			sys.exit()

	def message(self, msg):
		self.debugger_info_temp.append(msg)

	def error(self, msg):
		self.message('<|PythonEye Flag Error|>')
		self.message(msg)

	def cmdloop(self):
		self.preloop()
		stop = None
		while not stop:
			if self.cmdqueue:
				line = self.cmdqueue.pop(0)
				self.message('<|PythonEye Flag Split|>')
			else:
				self.output_queue.put('<|PythonEye Flag Line|>'.join(self.debugger_info_temp) if self.debugger_info_temp else '<|PythonEye Flag Empty Info|>')
				self.debugger_info_temp = []
				line = self.input_queue.get()
			if line[0] == '!':
				self.message('<|PythonEye Flag Insert Code|>')
			line = self.precmd(line)
			stop = self.postcmd(self.onecmd(line), line)

	def do_clear(self, arg):
		self.message('<|PythonEye Flag Delete Breakpoint|>')
		if not arg:
			bplist = [bp for bp in bdb.Breakpoint.bpbynumber if bp]
			self.clear_all_breaks()
			for bp in bplist:
				self.message(f'Deleted {bp}')
		else:
			super().do_clear(arg)

	do_cl = do_clear


def main():
	import getopt
	opts, sys.argv[:] = getopt.getopt(sys.argv[1:], 'mhc:', ['help', 'command='])
	target = _ModuleTarget if any(opt in ['-m'] for opt, optarg in opts) else _ScriptTarget(sys.argv[0])
	target.check()
	pythoneye = PythonEye(int(sys.argv[1]))
	sys.stdout = Stdout('<|PythonEye Flag Stdout|>', pythoneye)
	sys.stderr = Stdout('<|PythonEye Flag Stderr|>', pythoneye)
	sys.stdin = Stdin('<|PythonEye Flag Stdin|>', pythoneye)
	try:
		pythoneye._run(target)
	except SystemExit:
		pythoneye.output_queue.put('<|PythonEye Flag Debugger SystemExit|>')
	except SyntaxError:
		pythoneye.output_queue.put('<|PythonEye Flag Debugger SyntaxError|>')
	except:
		pythoneye.output_queue.put('<|PythonEye Flag Code Error|>')
	pythoneye.output_queue.put('<|PythonEye Flag Debugger Over|>')


if __name__ == '__main__':
	import eye
	from pathlib import Path
	os.chdir(Path(sys.argv[1]).parent)
	eye.main()
