from domain import OpenDomain
from manifold import Manifold

class AlmostComplexManifold(Manifold):
  def __init__(self, M, I):
    self.manifold = M
    if not I.type() == (1,1):
	raise TypeError("The almost-complex structure must be of type (1,1)")
    if not I.contract(I) + M.id() == 0:
	raise TypeError("The tensor of structure must square to minus identity")
    self.acstruct = I

  def almost_complex_structure(self):
    return self.acstruct

  def nijenhuis_tensor(self):
    return self.acstruct

  def is_integrable(self):
    return True
