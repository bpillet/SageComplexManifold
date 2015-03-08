class Quaternion:
	def __init__(self,a,b,c,d):
		self.x1 = a
		self.xi = b
		self.xj = c
		self.xk = d
	def __repr__(self):
		print("{0} + {1}i + {2}j + {3}k", self.x1, self.xi, self.xj, self.xk)
	def forme_complexe(self):
		print("{0} + {1}j", self.x1 + i*self.xi, self.xj+ i*self.xk)
	def __add__(self, autre):
		q = Quaternion(0,0,0,0)
		q.x1 = self.x1 + autre.x1
		q.xi = self.xi + autre.xi
		q.xj = self.xj + autre.xj
		q.xk = self.xk + autre.xk
		return q
	def __mul__(self, autre):
		q = Quaternion(0,0,0,0)
		q.x1 = self.x1 * autre.x1 - self.xi * autre.xi - self.xj * autre.xj - self.xk * autre.xk
		q.xi = self.x1 * autre.xi + self.xi * autre.x1 + self.xj * autre.xk - self.xk * autre.xj
		q.xj = 
		q.xk = 
		return q
	def __sub__(self, autre):
		moins1 = Quaternion(-1,0,0,0)
		return self.__add__(autre.__mul__(moins1))
