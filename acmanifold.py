from sage.structure.unique_representation import UniqueRepresentation
from domain import OpenDomain
from manifold import Manifold

class AlmostComplexManifold(Manifold):
  def __init__(self, M, I):
    Manifold.__init__(self, M.dim, M.name, M.latex_name, M.index)
    if not I.type() == (1,1):
	raise TypeError("The almost-complex structure must be of type (1,1)")
    if not I.contract(I) + M.id() == 0:
	raise TypeError("The tensor of structure must square to minus identity")
    self.almost_complex_structure = I

  def almost_complex_structure(self):
    return self.almost_complex_structure

  def nijenhuis_tensor(self):
    I = self.almost_complex_structure
    return I

  def dbarre(self.tensor) ??

  def is_integrable(self):
    if self.nijenhuis_tensor() == 0:
	return True
    return False


class ComplexPlaneManifold(AlmostComplexManifold, UniqueRepresentation):

  def __init__(self):
    from chart import Chart
    Manifold.__init__(self, 2, name="Plane C", latex_name=r"\CC")
    Carte = Chart(self, 'x y')
    self.manifold.tensor_field(self.almost_complex_structure,1,1)
  def _repr_(self):
    return "Complex plane of points with real coordinates x and y."
