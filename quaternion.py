class Quaternion:
	def __init__(self,a,b,c,d):
		self.x1 = a
		self.xi = b
		self.xj = c
		self.xk = d
		self.v = a + i*b
		self.w = c + i*d
	def __repr__(self):
		print("{0} + {1}i + {2}j + {3}k", self.x1, self.xi, self.xj, self.xk)
	def forme_complexe(self):
		print("{0} + {1}j", self.v, self.w)
	def __add__(self, autre):
		q = self
		q.x1 = self.x1 + autre.x1
		q.xi = self.xi + autre.xi
		q.xj = self.xj + autre.xj
		q.xk = self.xk + autre.xk
		q.v = self.v + autre.v
		q.w = self.w + autre.w
		return q
	def __sub__(self,autre):
		moins1 = Quaternion(-1,0,0,0)
		return self.__add__(autre.__mul__(moins1))
