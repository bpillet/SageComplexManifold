from sage.structure.unique_representation import UniqueRepresentation
from domain import OpenDomain
from manifold import Manifold

class AlmostComplexManifold(Manifold):
	def __init__(self, M, I):
		Manifold.__init__(self, M.dim, M.name, M.latex_name, M.index)
    		if not I.type() == (1,1):
			raise TypeError("The almost-complex structure must be of type (1,1)")
		if not I.contract(I) + M.tangent_identity_field() == 0:
			raise TypeError("The tensor of structure must square to minus identity")
		self.almost_complex_structure = I

	def _repr_(self):
        	r"""
        	String representation of the object.
        	"""
		description = " endowed with the almost complex structure"
        	if self.almost_complex_structure.name is not None:
        		description += "'%s' " % self.almost_complex_structure._name
	        return Manifold._repr_(M) + description

	def almost_complex_structure(self):
    		return self.almost_complex_structure

  	def nijenhuis_tensor(self):
		I = self.almost_complex_structure
		return "ONGOING"

	def dbarre(self,T):
		return "ONGOING"

	def is_integrable(self):
		if self.nijenhuis_tensor() == 0:
			return True
		return False


class ComplexPlaneManifold(AlmostComplexManifold, UniqueRepresentation):

	def __init__(self):
		from chart import Chart
		Manifold.__init__(self, 2, name="Plane C", latex_name=r"\CC")
		Carte = Chart(self, 'x y')
		dx = Carte.frame()[0]
		dy = Carte.frame()[1]
		dsdx = Carte.coframe()[0]
		dsdx = Carte.coframe()[1]
		J = Manifold.tensor_field(self,1,1,'J')
		J.set_restriction(dx*dsdy - dy*dsdx)
		self.almost_complex_structure = J

	def _repr_(self):
		return "Complex plane of points with real coordinates x and y,"\
			+ " endowed with the integrable almost complex structure J : "\
			+ self.almost_complex_structure.view()
