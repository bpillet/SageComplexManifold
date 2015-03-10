from sage.structure.unique_representation import UniqueRepresentation
from domain import OpenDomain
from manifold import Manifold

class AlmostComplexManifold(Manifold):
	def __init__(self, M, I):
		Manifold.__init__(self, M.dim, M.name, M.latex_name, M.index)
		if not I.domain() == M:
			raise TypeError("The tensor of almost-complex structure must be defined on the whole manifold " + M)
    		if not I.tensor_type() == (1,1):
			raise TypeError("The tensor of almost-complex structure must be of tensor type (1,1)")
		if not I.contract(I) + M.tangent_identity_field() == 0:
			raise TypeError("The tensor of almost-complex structure must square to minus identity")
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
        	r"""
        	Returns the tensor of almost-complex structure.
        	"""
    		return self.almost_complex_structure

  	def nijenhuis_tensor(self):
		I = self.almost_complex_structure
		return "ONGOING"

	def dbarre(self,tau):
        	r"""
        	Returns the antiholormophic part of the exterior derivative of a differential form.
                
		INPUT:
		- ``tau`` -- a complex valued differential n-form of complex type (p,q) on the manifold (or an open domain ??)
		
		OUTPUT:
		- a complex valued differential (n+1)-form on the manifold of complex type (p,q+1)
        	"""
		dtau = tau.exterior_der()
		return (self.tangent_identity_field() + i*I).contract(dtau)

	def drond(self,tau):
        	r"""
        	Returns the antiholormophic part of the exterior derivative of a differential form.
                
		INPUT:
		- ``tau`` -- a complex valued differential n-form of complex type (p,q) on the manifold (or an open domain ??)
		
		OUTPUT:
		- a complex valued differential (n+1)-form of complex type (p,q+1) on the manifold
        	"""
		dtau = tau.exterior_der()
		return (self.tangent_identity_field() - i*I).contract(dtau)

	def is_integrable(self):
		if self.nijenhuis_tensor() == 0:
			return True
		return False

### The Complex Plane as an subclass of AlmostComplexManifold

class ComplexPlaneManifold(AlmostComplexManifold):

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
