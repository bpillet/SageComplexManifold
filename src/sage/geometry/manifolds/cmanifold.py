from sage.structure.unique_representation import UniqueRepresentation
from domain import OpenDomain
from manifold import Manifold

class ComplexManifold(OpenDomain):
  def __init__(self, dim, name, latexname=None, start_index=0):
    if not isinstance(n, (int, Integer)):
        raise TypeError("The manifold dimension must be an integer.")
    if n<1:
        raise ValueError("The manifold dimension must be strictly " + "positive.")
    self.dim = n
    OpenDomain.__init__(self, self, name, latex_name)
    self.sindex = start_index
    self.domains = {self.name: self}
  def _repr_(self):
  def
  def forget(self):
    n=self.dimension()
    M=Manifold(2*n, 'M')
    M.domains = self.domains
    M.chart = self.chart ???
    return M    

class ComplexLineManifold(ComplexManifold, UniqueRepresentation):

  def __init__(self):
    from cchart import CChart
    ComplexManifold.__init__(self, 1, name="field C", latex_name=r"\CC")
    CChart(self, 'z_complexline')
  def _repr_(self):
    return "field C of complex numbers"
