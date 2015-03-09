class Quaternion:
	def __init__(self,a,b,c,d):
		self.x1 = a
		self.xi = b
		self.xj = c
		self.xk = d

	def __repr__(self):
		return "{0} + {1}i + {2}j + {3}k".format(self.x1, self.xi, self.xj, self.xk)

	def real_part(self):
		r"""affiche la partie réelle de self
	"""
		return self.x1

	def forme_complexe(self):
		r"""affiche self sous forme v + wj avec v, w nombres complexes
	"""
		return "({0} + i{1}) + ({2} + i{3})j".format(self.x1, self.xi, self.xj, self.xk)

	def conj(self):
		r"""Renvoie le conjugué quaternionique de self
	"""
		return Quaternion( self.x1, -self.xi, -self.xj, -self.xk)

	def norm(self):
		r"""Renvoie la norme de self
	"""
		return (self * (self.conj())).real_part()

	def __add__(self, autre):
		q = Quaternion(0,0,0,0)
		q.x1 = self.x1 + autre.x1
		q.xi = self.xi + autre.xi
		q.xj = self.xj + autre.xj
		q.xk = self.xk + autre.xk
		return q

	def __mul__(self, autre):
		q1 = self.x1 * autre.x1 - self.xi * autre.xi - self.xj * autre.xj - self.xk * autre.xk
		qi = self.x1 * autre.xi + self.xi * autre.x1 + self.xj * autre.xk - self.xk * autre.xj
		qj = self.x1 * autre.xj + self.xj * autre.x1 + self.xk * autre.xi - self.xi * autre.xk
		qk = self.x1 * autre.xk + self.xk * autre.x1 + self.xi * autre.xj - self.xj * autre.xi
		return Quaternion(q1,qi,qj,qk)

	def __sub__(self, autre):
		moins1 = Quaternion(-1,0,0,0)
		return self.__add__(autre.__mul__(moins1))
