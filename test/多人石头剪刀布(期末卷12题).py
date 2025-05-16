from random import randint

def redo():
	for i in range(n):
		if hand[i] != 0:
			hand[i] = randint(1, 3)
	print('\n开始：', hand, end=' ')


def counter():
	s = [0] * 4
	for i in range(n):
		j = hand[i]
		s[j] += 1
	return s


def out(k):
	for i in range(n):
		if hand[i] == k:
			hand[i] = 0
			print('^', end='  ')
		else:
			print(' ', end='  ')


n = 6
hand = [9] * n 
cnt = [0] * 4

while True:
	redo()
	cnt = counter()
	lost = win = 0
	if cnt[1] == 0 and cnt[2] > 0 and cnt[3] > 0:
		lost = 3
		win = 2
	if cnt[2] == 0 and cnt[3] > 0 and cnt[1] > 0:
		lost = 1
		win = 3
	if cnt[3] == 0 and cnt[1] > 0 and cnt[2] > 0:
		lost = 2
		win = 1
	if lost > 0:
		print('\n出局：', end='  ')
		out(lost)
		cnt[lost] = 0
	if counter()[0] == n-1:
		print('\n结果：', hand)
		for i in range(n):
			if hand[i] > 0:
				print('\n获胜编号：', i)
				break
		break
