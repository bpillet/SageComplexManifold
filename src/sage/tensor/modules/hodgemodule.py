
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.parent import Parent
from sage.categories.modules import Modules
from free_module_tensor import FiniteRankFreeModuleElement

class PureHodgeModule(FiniteRankFreeModule):
    
    def __init__(self, ring, rank, weight ,name=None, latex_name=None, start_index=0,
                 output_formatter=None):
        if (weight<0):
            raise TypeError("The pure hodge structure must have non-negative weight.")
        if not ring.is_commutative():
            raise TypeError("The module base ring must be commutative.")
        if not ring.is_subring(SR):
            raise Error("The module base ring must be a subring of the complex numbers.")
        Parent.__init__(self, base=ring, category=Modules(ring))
        self._ring = ring # same as self._base
        self._rank = rank 
        self._name = name
        if latex_name is None:
            self._latex_name = self._name
        else:
            self._latex_name = latex_name
        self._sindex = start_index
        self._output_formatter = output_formatter
        # Dictionary of the tensor modules built on self 
        #   (dict. keys = (k,l) --the tensor type)
        self._tensor_modules = {(1,0): self} # self is considered as the set of
                                            # tensors of type (1,0)
        self._known_bases = []  # List of known bases on the free module
        self._def_basis = None # default basis
        self._basis_changes = {} # Dictionary of the changes of bases
        # Zero element:
        if not hasattr(self, '_zero_element'):
            self._zero_element = self._element_constructor_(name='zero', 
                                                            latex_name='0')
