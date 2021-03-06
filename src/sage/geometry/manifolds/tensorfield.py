r"""
Tensor fields

The class :class:`TensorField` implements tensor fields on differentiable 
manifolds over `\RR`. 
The derived class :class:`TensorFieldParal` is devoted to tensor fields with
values on parallelizable open subsets.

Various derived classes of :class:`TensorField` are devoted to specific tensor
fields:

* :class:`~sage.geometry.manifolds.vectorfield.VectorField` for vector fields 
  (rank-1 contravariant tensor fields)

* :class:`~sage.geometry.manifolds.rank2field.EndomorphismField` for fields of 
  endomorphisms (type (1,1) tensor fields)

  * :class:`~sage.geometry.manifolds.rank2field.AutomorphismField` for fields 
    of invertible endomorphisms

    * :class:`~sage.geometry.manifolds.rank2field.TangentIdentityField` for 
      fields of identity maps on tangent spaces

* :class:`~sage.geometry.manifolds.diffform.DiffForm` for differential forms 
  (fully antisymmetric covariant tensor fields)

  * :class:`~sage.geometry.manifolds.diffform.OneForm` for 1-forms (rank-1 
    covariant tensor fields)


AUTHORS:

- Eric Gourgoulhon, Michal Bejger (2013, 2014) : initial version

EXAMPLES:

A tensor field of type (1,1) on a 2-dimensional manifold::

    sage: M = Manifold(2, 'M', start_index=1)
    sage: c_xy.<x,y> = M.chart()
    sage: t = M.tensor_field(1, 1, 'T') ; t
    field of endomorphisms 'T' on the 2-dimensional manifold 'M'
    sage: t.tensor_type()
    (1, 1)
    sage: t.tensor_rank()
    2

Components w.r.t. the manifold's default frame are created by providing the
relevant indices inside square brackets::

    sage: t[1,1] = x^2

Unset components are initialized to zero::

    sage: t[:]  # list of components w.r.t. the manifold's default vector frame
    [x^2   0]
    [  0   0]

The full set of components w.r.t. a given vector frame is returned by the 
method :meth:`comp`; it is an instance 
of the class :class:`~sage.tensor.modules.comp.Components`::

    sage: t.comp(c_xy.frame())
    2-indices components w.r.t. coordinate frame (M, (d/dx,d/dy)) 
    sage: print type(t.comp(c_xy.frame()))
    <class 'sage.tensor.modules.comp.Components'>

If no vector frame is mentionned in the argument of :meth:`comp`, it is 
assumed to be the manifold's default frame::

    sage: M.default_frame()
    coordinate frame (M, (d/dx,d/dy))
    sage: t.comp() is t.comp(c_xy.frame())
    True

Individual components w.r.t. the manifold's default frame are accessed by 
listing their indices inside double square brackets; they are scalar
fields on the manifold, and therefore instances of the class 
:class:`~sage.geometry.manifolds.scalarfield.ScalarField`::

    sage: t[[1,1]]
    scalar field on the 2-dimensional manifold 'M'
    sage: t[[1,1]].view()
    M --> R
    (x, y) |--> x^2
    sage: t[[1,2]]
    zero scalar field on the 2-dimensional manifold 'M'
    sage: t[[1,2]].view()
    M --> R
    (x, y) |--> 0
    
A direct access to the coordinate expression of some component is obtained
via the single square brackets::

    sage: t[1,1] 
    x^2
    sage: t[1,1] is t[[1,1]].function_chart() # the coordinate function
    True
    sage: t[1,1] is t[[1,1]].function_chart(c_xy)
    True
    sage: t[1,1].expr() is t[[1,1]].expr() # the symbolic expression
    True

In other words, the single square brackets return an instance of 
:class:`~sage.geometry.manifolds.chart.FunctionChart` that is the 
coordinate function representing the component in some chart (by default, 
the manifold's default chart)::

    sage: print type(t[1,1])    # single bracket --> FunctionChart
    <class 'sage.geometry.manifolds.chart.FunctionChart'>
    sage: print type(t[[1,1]])  # double bracket --> ScalarField
    <class 'sage.geometry.manifolds.scalarfield.ScalarFieldAlgebra_with_category.element_class'>

Expressions in a chart different from the manifold's default one are 
obtained by specifying the chart as the last argument inside the
single square brackets::

    sage: c_uv.<u,v> = M.chart()
    sage: xy_to_uv = c_xy.coord_change(c_uv, x+y, x-y)  
    sage: uv_to_xy = xy_to_uv.inverse()
    sage: t[1,1, c_uv] 
    1/4*u^2 + 1/2*u*v + 1/4*v^2

Note that ``t[1,1, c_uv]`` is the component of the tensor t w.r.t. to 
the coordinate frame associated to the chart (x,y) expressed in terms of 
the coordinates (u,v). Indeed, ``t[1,1, c_uv]`` is a shortcut for 
``t.comp(c_xy.frame())[[1,1]].function_chart(c_uv)``::
    
    sage: t[1,1, c_uv] is t.comp(c_xy.frame())[[1,1]].function_chart(c_uv)
    True

Similarly, ``t[1,1]`` is a shortcut for 
``t.comp(c_xy.frame())[[1,1]].function_chart(c_xy)``::

    sage: t[1,1] is t.comp(c_xy.frame())[[1,1]].function_chart(c_xy)            
    True
    sage: t[1,1] is t.comp()[[1,1]].function_chart()  # since c_xy.frame() and c_xy are the manifold's default values                
    True

Internally, the components are stored as a dictionary (attribute 
:attr:`_comp` of the class 
:class:`~sage.tensor.modules.comp.Components`) whose
keys are the indices. Only the non-zero components and non-redundant
components (in case of symmetries) are stored::

    sage: t.comp()._comp
    {(1, 1): scalar field on the 2-dimensional manifold 'M'}

All the components can be set at once via [:]::

    sage: t[:] = [[1, -x], [x*y, 2]]
    sage: t[:]
    [  1  -x]
    [x*y   2]
    
To set the components in a vector frame different from the manifold's 
default one, the method :meth:`set_comp` can be employed::

    sage: e = M.vector_frame('e')
    sage: t.set_comp(e)[1,1] = x+y
    sage: t.set_comp(e)[2,1], t.set_comp(e)[2,2] = y, -3*x
    
but, as a shortcut, one may simply specify the frame as the first argument
of the square brackets::

    sage: t[e,1,1] = x+y
    sage: t[e,2,1], t[e,2,2] = y, -3*x
    sage: t.comp(e)
    2-indices components w.r.t. vector frame (M, (e_1,e_2))
    sage: t.comp(e)[:]
    [x + y     0]
    [    y  -3*x]
    sage: t[e,:]  # a shortcut of the above
    [x + y     0]
    [    y  -3*x]

All the components in some frame can be set at once, via the operator
[:]::

    sage: t[e,:] = [[x+y, 0], [y, -3*x]]
    sage: t[e,:]  # same as above:
    [x + y     0]
    [    y  -3*x]

To avoid any insconstency between the various components, the method 
:meth:`set_comp` clears the components in other frames. 
To keep the other components, one must use the method :meth:`add_comp`::

    sage: t = M.tensor_field(1, 1, 'T')  # Let us restart 
    sage: t[:] = [[1, -x], [x*y, 2]]  # by first setting the components in the frame c_xy.frame()
    sage: # We now set the components in the frame e with add_comp:
    sage: t.add_comp(e)[:] = [[x+y, 0], [y, -3*x]]

The expansion of the tensor field in a given frame is displayed via the 
method :meth:`view` (the symbol * stands for tensor product)::

    sage: t.view()  # expansion in the manifold's default frame
    T = d/dx*dx - x d/dx*dy + x*y d/dy*dx + 2 d/dy*dy
    sage: t.view(e)
    T = (x + y) e_1*e^1 + y e_2*e^1 - 3*x e_2*e^2

By definition, a tensor field acts as a multilinear map on 1-forms and vector 
fields; in the present case, T being of type (1,1), it acts on pairs 
(1-form, vector field)::

    sage: a = M.one_form('a')
    sage: a[:] = (1, x)
    sage: v = M.vector_field('V')
    sage: v[:] = (y, 2)
    sage: t(a,v)
    scalar field 'T(a,V)' on the 2-dimensional manifold 'M'
    sage: t(a,v).view()
    T(a,V): M --> R
       (x, y) |--> x^2*y^2 + 2*x + y
       (u, v) |--> 1/16*u^4 - 1/8*u^2*v^2 + 1/16*v^4 + 3/2*u + 1/2*v
    sage: latex(t(a,v))
    T\left(a,V\right)

Check by means of the component expression of t(a,v)::

    sage: t(a,v).expr() - t[1,1]*a[1]*v[1] - t[1,2]*a[1]*v[2] - t[2,1]*a[2]*v[1] - t[2,2]*a[2]*v[2]
    0

A scalar field (rank-0 tensor field)::

    sage: f = M.scalar_field(x*y + 2, name='f') ; f 
    scalar field 'f' on the 2-dimensional manifold 'M'
    sage: f.tensor_type()
    (0, 0)
    
A scalar field acts on points on the manifold::

    sage: p = M.point((1,2))
    sage: f(p)
    4

See :class:`~sage.geometry.manifolds.scalarfield.ScalarField` for more details
on scalar fields. 
   
A vector field (rank-1 contravariant tensor field)::

    sage: v = M.vector_field('v') ; v
    vector field 'v' on the 2-dimensional manifold 'M'
    sage: v.tensor_type()
    (1, 0)
    sage: v[1], v[2] = -x, y
    sage: v.view()
    v = -x d/dx + y d/dy        

A field of symmetric bilinear forms::

    sage: q = M.sym_bilin_form_field('Q') ; q
    field of symmetric bilinear forms 'Q' on the 2-dimensional manifold 'M'
    sage: q.tensor_type()
    (0, 2)

The components of a symmetric bilinear form are dealt by the subclass 
:class:`~sage.tensor.modules.comp.CompFullySym` of the class 
:class:`~sage.tensor.modules.comp.Components`, which takes into 
account the symmetry between the two indices::

    sage: q[1,1], q[1,2], q[2,2] = (0, -x, y) # no need to set the component (2,1)
    sage: print type(q.comp())
    <class 'sage.tensor.modules.comp.CompFullySym'>
    sage: q[:] # note that the component (2,1) is equal to the component (1,2)
    [ 0 -x]
    [-x  y]
    sage: q.view()
    Q = -x dx*dy - x dy*dx + y dy*dy

Internally (dictionary :attr:`_comp` of the class 
:class:`~sage.tensor.modules.comp.Components`), only
the non-zero and non-redundant components are stored::

    sage: q.comp()._comp
    {(1, 2): scalar field on the 2-dimensional manifold 'M',
    (2, 2): scalar field on the 2-dimensional manifold 'M'}
    sage: q.comp()._comp[(1,2)].expr()
    -x
    sage: q.comp()._comp[(2,2)].expr()
    y

More generally, tensor symmetries or antisymmetries can be specified via
the keywords ``sym`` and ``antisym``. For instance a rank-4 covariant 
tensor symmetric with respect to its first two arguments (no. 0 and no. 1) and 
antisymmetric with respect to its last two ones (no. 2 and no. 3) is declared 
as follows::

    sage: t = M.tensor_field(0, 4, 'T', sym=(0,1), antisym=(2,3))
    sage: t[1,2,1,2] = 3
    sage: t[2,1,1,2] # check of the symmetry with respect to the first 2 indices
    3
    sage: t[1,2,2,1] # check of the antisymmetry with respect to the last 2 indices
    -3

"""

#******************************************************************************
#       Copyright (C) 2013, 2014 Eric Gourgoulhon <eric.gourgoulhon@obspm.fr>
#       Copyright (C) 2013, 2014 Michal Bejger <bejger@camk.edu.pl>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.rings.integer import Integer
from sage.structure.element import ModuleElement  
from sage.tensor.modules.free_module_tensor import FreeModuleTensor
from sage.tensor.modules.tensor_with_indices import TensorWithIndices

class TensorField(ModuleElement):
    r"""
    Base class for tensor fields on an open set of a differentiable manifold, 
    with values on an open subset of a differentiable manifold. 
    
    An instance of this class is a tensor field along an open subset `U` 
    of some manifold `S` with values in an open subset `V` 
    of a manifold `M`, via a differentiable mapping `\Phi: U \rightarrow V`. 
    The standard case of a tensor field *on* a manifold corresponds to `S=M`, 
    `U=V` and `\Phi = \mathrm{Id}`. Another common case is `\Phi` being an
    immersion.

    If `V` is parallelizable, the class :class:`TensorFieldParal` should be
    used instead. 
    
    A tensor field of type `(k,\ell)` is a field `t` on `U`, so that at each 
    point `p\in U`, `t(p)` is a multilinear map of the type:

    .. MATH::

        t(p):\ \underbrace{T_q^*M\times\cdots\times T_q^*M}_{k\ \; \mbox{times}}
        \times \underbrace{T_q M\times\cdots\times T_q M}_{\ell\ \; \mbox{times}}
        \longrightarrow \RR
    
    where `T_q M` stands for the tangent space at the point `q=\Phi(p)` on the
    manifold `M` and `T_q^* M` for its dual vector space. The integer `k+\ell`
    is called the tensor rank. 
    
    INPUT:
    
    - ``vector_field_module`` -- module `\mathcal{X}(U,\Phi)` of vector 
      fields along `U` with values on `\Phi(U)\subset V \subset M`
    - ``tensor_type`` -- pair (k,l) with k being the contravariant rank and l 
      the covariant rank
    - ``name`` -- (default: None) name given to the tensor field
    - ``latex_name`` -- (default: None) LaTeX symbol to denote the tensor field; 
      if none is provided, the LaTeX symbol is set to ``name``
    - ``sym`` -- (default: None) a symmetry or a list of symmetries among the 
      tensor arguments: each symmetry is described by a tuple containing 
      the positions of the involved arguments, with the convention position=0
      for the first argument. For instance:
      
      * sym=(0,1) for a symmetry between the 1st and 2nd arguments 
      * sym=[(0,2),(1,3,4)] for a symmetry between the 1st and 3rd
        arguments and a symmetry between the 2nd, 4th and 5th arguments.

    - ``antisym`` -- (default: None) antisymmetry or list of antisymmetries 
      among the arguments, with the same convention as for ``sym``. 

    EXAMPLES:
    
    Tensor field of type (0,2) on the sphere `S^2`::
    
        sage: M = Manifold(2, 'S^2') # the 2-dimensional sphere S^2
        sage: U = M.open_domain('U') # complement of the North pole
        sage: c_xy.<x,y> = U.chart() # stereographic coordinates from the North pole
        sage: V = M.open_domain('V') # complement of the South pole
        sage: c_uv.<u,v> = V.chart() # stereographic coordinates from the South pole
        sage: M.declare_union(U,V)   # S^2 is the union of U and V
        sage: xy_to_uv = c_xy.transition_map(c_uv, (x/(x^2+y^2), y/(x^2+y^2)), \
                                             intersection_name='W', restrictions1= x^2+y^2!=0, \
                                             restrictions2= u^2+v^2!=0)
        sage: uv_to_xy = xy_to_uv.inverse()
        sage: W = U.intersection(V)
        sage: t = M.tensor_field(0,2, name='t') ; t
        tensor field 't' of type (0,2) on the 2-dimensional manifold 'S^2'
        sage: t.parent()
        module T^(0,2)(S^2) of type-(0,2) tensors fields on the 2-dimensional manifold 'S^2'
        sage: t.parent().category()
        Category of modules over algebra of scalar fields on the 2-dimensional manifold 'S^2'

    The parent of `t` is not a free module, for the sphere `S^2` is not parallelizable::
    
        sage: isinstance(t.parent(), FiniteRankFreeModule)
        False

    To fully define `t`, we have to specify its components in some vector frames 
    defined on subdomains of `S^2`; let us start by the domain `U`::
    
        sage: eU = c_xy.frame()
        sage: t = M.tensor_field(0,2, name='t')
        sage: t[eU,:] = [[1,0], [-2,3]]
        sage: t.view(eU)
        t = dx*dx - 2 dy*dx + 3 dy*dy
    
    To set the components of `t` on `V` consistently, we copy the expressions
    of the components in the common subdomain `W`::
    
        sage: eV = c_uv.frame()
        sage: eVW = eV.restrict(W)
        sage: c_uvW = c_uv.restrict(W)
        sage: t[eV,0,0] = t[eVW,0,0,c_uvW].expr()
        sage: t[eV,0,1] = t[eVW,0,1,c_uvW].expr()
        sage: t[eV,1,0] = t[eVW,1,0,c_uvW].expr()
        sage: t[eV,1,1] = t[eVW,1,1,c_uvW].expr()

    Actually, the above operation can by performed in a single line by means
    of the method :meth:`add_comp_by_continuation`::
    
        sage: t.add_comp_by_continuation(eV, W, chart=c_uv)
    
    At this stage, `t` is fully defined, having components in frames eU and eV, 
    whose domain union is the whole manifold::
    
        sage: t.view(eV)
        t = (u^4 - 4*u^3*v + 10*u^2*v^2 + 4*u*v^3 + v^4)/(u^8 + 4*u^6*v^2 + 6*u^4*v^4 + 4*u^2*v^6 + v^8) du*du - 4*(u^3*v + 2*u^2*v^2 - u*v^3)/(u^8 + 4*u^6*v^2 + 6*u^4*v^4 + 4*u^2*v^6 + v^8) du*dv + 2*(u^4 - 2*u^3*v - 2*u^2*v^2 + 2*u*v^3 + v^4)/(u^8 + 4*u^6*v^2 + 6*u^4*v^4 + 4*u^2*v^6 + v^8) dv*du + (3*u^4 + 4*u^3*v - 2*u^2*v^2 - 4*u*v^3 + 3*v^4)/(u^8 + 4*u^6*v^2 + 6*u^4*v^4 + 4*u^2*v^6 + v^8) dv*dv

    Let us consider two vector fields, `a` and `b`, on `S^2`::
    
        sage: a = M.vector_field(name='a')
        sage: a[eU,:] = [1,x]
        sage: a.add_comp_by_continuation(eV, W, chart=c_uv)
        sage: a.view(eV)
        a = -(u^4 - v^4 + 2*u^2*v)/(u^2 + v^2) d/du - (2*u^3*v + 2*u*v^3 - u^3 + u*v^2)/(u^2 + v^2) d/dv
        sage: b = M.vector_field(name='b')
        sage: b[eU,:] = [y,-1]
        sage: b.add_comp_by_continuation(eV, W, chart=c_uv)
        sage: b.view(eV)
        b = ((2*u + 1)*v^3 + (2*u^3 - u^2)*v)/(u^2 + v^2) d/du - (u^4 - v^4 + 2*u*v^2)/(u^2 + v^2) d/dv
        
    As a tensor field of type (0,2), `t` acts on the pair `(a,b)`, resulting in a scalar 
    field::
    
        sage: f = t(a,b) ; f
        scalar field 't(a,b)' on the 2-dimensional manifold 'S^2'
        sage: f.view()
        t(a,b): S^2 --> R
        on U: (x, y) |--> -(2*x - 1)*y - 3*x
        on V: (u, v) |--> -(3*u^3 + 3*u*v^2 - v^3 - (u^2 - 2*u)*v)/(u^4 + 2*u^2*v^2 + v^4)

    The vectors can be defined only on subdomains of `S^2`, the domain of the
    result is then the common subdomain::
    
        sage: s = t(a.restrict(U), b) ; s
        scalar field 't(a,b)' on the open domain 'U' on the 2-dimensional manifold 'S^2'
        sage: s.view()
        t(a,b): U --> R
           (x, y) |--> -(2*x - 1)*y - 3*x
        on W: (u, v) |--> -(3*u^3 + 3*u*v^2 - v^3 - (u^2 - 2*u)*v)/(u^4 + 2*u^2*v^2 + v^4)
        sage: s = t(a.restrict(U), b.restrict(W)) ; s
        scalar field 't(a,b)' on the open domain 'W' on the 2-dimensional manifold 'S^2'
        sage: s.view()
        t(a,b): W --> R
           (x, y) |--> -(2*x - 1)*y - 3*x
           (u, v) |--> -(3*u^3 + 3*u*v^2 - v^3 - (u^2 - 2*u)*v)/(u^4 + 2*u^2*v^2 + v^4)

    The tensor itself can be defined only on some subdomain of `S^2`, yielding
    a result whose domain is this subdomain::
    
        sage: s = t.restrict(V)(a,b) ; s
        scalar field 't(a,b)' on the open domain 'V' on the 2-dimensional manifold 'S^2'
        sage: s.view()
        t(a,b): V --> R
           (u, v) |--> -(3*u^3 + 3*u*v^2 - v^3 - (u^2 - 2*u)*v)/(u^4 + 2*u^2*v^2 + v^4)
        on W: (x, y) |--> -(2*x - 1)*y - 3*x

    Tests regarding the multiplication by a scalar field::
    
        sage: t.parent().base_ring() is f.parent()
        True
        sage: s = f*t ; s  
        tensor field of type (0,2) on the 2-dimensional manifold 'S^2'
        sage: s[[0,0]] == f*t[[0,0]]
        True
        sage: s.restrict(U) == f.restrict(U)*t.restrict(U)
        True
        sage: s = f*t.restrict(U) ; s
        tensor field of type (0,2) on the open domain 'U' on the 2-dimensional manifold 'S^2'
        sage: s.restrict(U) == f.restrict(U)*t.restrict(U)
        True

        
    """
    def __init__(self, vector_field_module, tensor_type, name=None, 
                 latex_name=None, sym=None, antisym=None):
        ModuleElement.__init__(self, 
                               vector_field_module.tensor_module(*tensor_type))
        self._vmodule = vector_field_module
        self._tensor_type = tuple(tensor_type)
        self._tensor_rank = self._tensor_type[0] + self._tensor_type[1]
        self._name = name
        if latex_name is None:
            self._latex_name = self._name
        else:
            self._latex_name = latex_name
        self._domain = vector_field_module._domain
        self._ambient_domain = vector_field_module._ambient_domain
        self._restrictions = {} # dict. of restrictions of self on subdomains of 
                               # self._domain, with the subdomains as keys
        # Treatment of symmetry declarations:
        self._sym = []
        if sym is not None and sym != []:
            if isinstance(sym[0], (int, Integer)):  
                # a single symmetry is provided as a tuple -> 1-item list:
                sym = [tuple(sym)]
            for isym in sym:
                if len(isym) > 1:
                    for i in isym:
                        if i<0 or i>self._tensor_rank-1:
                            raise IndexError("Invalid position: " + str(i) +
                                 " not in [0," + str(self._tensor_rank-1) + "]")
                    self._sym.append(tuple(isym))       
        self._antisym = []
        if antisym is not None and antisym != []:
            if isinstance(antisym[0], (int, Integer)):  
                # a single antisymmetry is provided as a tuple -> 1-item list:
                antisym = [tuple(antisym)]
            for isym in antisym:
                if len(isym) > 1:
                    for i in isym:
                        if i<0 or i>self._tensor_rank-1:
                            raise IndexError("Invalid position: " + str(i) +
                                " not in [0," + str(self._tensor_rank-1) + "]")
                    self._antisym.append(tuple(isym))
        # Final consistency check:
        index_list = []
        for isym in self._sym:
            index_list += isym
        for isym in self._antisym:
            index_list += isym
        if len(index_list) != len(set(index_list)):
            # There is a repeated index position:
            raise IndexError("Incompatible lists of symmetries: the same " + 
                             "position appears more than once.")
        # Initialization of derived quantities:
        self._init_derived() 

    ####### Required methods for ModuleElement (beside arithmetic) #######
    
    def __nonzero__(self):
        r"""
        Return True if ``self`` is nonzero and False otherwise. 
        
        This method is called by self.is_zero(). 
        
        EXAMPLE:
        
        Tensor field defined by parts on a 2-dimensional manifold::
        
            sage: M = Manifold(2, 'M')
            sage: U = M.open_domain('U')
            sage: c_xy.<x, y> = U.chart()
            sage: V = M.open_domain('V')
            sage: c_uv.<u, v> = V.chart()
            sage: M.declare_union(U,V)   # M is the union of U and V
            sage: t = M.tensor_field(1, 2, name='t')
            sage: tu = U.tensor_field(1, 2, name='t')
            sage: tv = V.tensor_field(1, 2, name='t')
            sage: tu[0,0,0] = 0
            sage: tv[0,0,0] = 0
            sage: t.set_restriction(tv)
            sage: t.set_restriction(tu)
            sage: t.is_zero()
            True
            sage: tv[0,0,0] = 1
            sage: t.set_restriction(tv)
            sage: t.is_zero()
            False

        """
        resu = False
        for rst in self._restrictions.itervalues():
            resu = resu or rst.__nonzero__()
        return resu
                
    ####### End of required methods for ModuleElement (beside arithmetic) #######

    def _repr_(self):
        r"""
        String representation of the object.
        """
        # Special cases
        if self._tensor_type == (0,2) and self._sym == [(0,1)]:
            description = "field of symmetric bilinear forms "
            if self._name is not None:
                description += "'%s' " % self._name
        else:
        # Generic case
            description = "tensor field"
            if self._name is not None:
                description += " '%s'" % self._name
            description += " of type (%s,%s) " % (str(self._tensor_type[0]), 
                                                     str(self._tensor_type[1]))
        return self._final_repr(description)

    def _latex_(self):
        r"""
        LaTeX representation of the object.
        """
        if self._latex_name is None:
            return r'\mbox{' + str(self) + r'}'
        else:
           return self._latex_name

    def set_name(self, name=None, latex_name=None):
        r"""
        Set (or change) the text name and LaTeX name of ``self``.

        INPUT:
        
        - ``name`` -- (string; default: None) name given to the tensor field
        - ``latex_name`` -- (string; default: None) LaTeX symbol to denote 
          the tensor field; if None while ``name`` is provided, the LaTeX 
          symbol is set to ``name``.

        """
        if name is not None:
            self._name = name
            if latex_name is None:
                self._latex_name = self._name
        if latex_name is not None:
            self._latex_name = latex_name
        for rst in self._restrictions.itervalues():
            rst.set_name(name=name, latex_name=latex_name)

    def _new_instance(self):
        r"""
        Create an instance of the same class as ``self`` on the same 
        vector field module, with the same tensor type and same symmetries
        
        """
        return self.__class__(self._vmodule, self._tensor_type, sym=self._sym, 
                                antisym=self._antisym)

    def _final_repr(self, description):
        r"""
        Part of string representation common to all tensor fields.
        """
        if self._domain == self._ambient_domain:
            description += "on the " + str(self._domain)
        else:
            description += "along the " + str(self._domain) + \
                           " with values on the " + str(self._ambient_domain)
        return description

    def _init_derived(self):
        r"""
        Initialize the derived quantities
        """
        self._lie_derivatives = {} # collection of Lie derivatives of self

    def _del_derived(self):
        r"""
        Delete the derived quantities
        """
        # First deletes any reference to self in the vectors' dictionary:
        for vid, val in self._lie_derivatives.iteritems():
            del val[0]._lie_der_along_self[id(self)]
        self._lie_derivatives.clear()

    #### Simple accessors ####
    
    def domain(self):
        r"""
        Return the domain on which the tensor field is defined.
        
        OUTPUT:
        
        - instance of class :class:`~sage.geometry.manifolds.domain.OpenDomain` 
          representing the manifold's open subset on which ``self`` is defined. 
        
        EXAMPLES::
        
            sage: Manifold._clear_cache_() # for doctests only
            sage: M = Manifold(2, 'M')
            sage: c_xy.<x,y> = M.chart()
            sage: t = M.tensor_field(1,2)
            sage: t.domain()
            2-dimensional manifold 'M'
            sage: U = M.open_domain('U', coord_def={c_xy: x<0})
            sage: h = t.restrict(U)
            sage: h.domain()
            open domain 'U' on the 2-dimensional manifold 'M'
        
        """
        return self._domain

    def tensor_type(self):
        r"""
        Return the tensor type of ``self``. 
        
        OUTPUT:
        
        - pair (k,l), where k is the contravariant rank and l is the covariant 
          rank
        
        EXAMPLES::
        
            sage: Manifold._clear_cache_() # for doctests only
            sage: M = Manifold(2, 'M')
            sage: c_xy.<x,y> = M.chart()
            sage: t = M.tensor_field(1,2)
            sage: t.tensor_type()
            (1, 2)
            sage: v = M.vector_field()
            sage: v.tensor_type()
            (1, 0)
        
        """
        return self._tensor_type

    def tensor_rank(self):
        r"""
        Return the tensor rank of ``self``. 
        
        OUTPUT:
        
        - integer k+l, where k is the contravariant rank and l is the covariant 
          rank
        
        EXAMPLES::

            sage: M = Manifold(2, 'M')
            sage: c_xy.<x,y> = M.chart()
            sage: t = M.tensor_field(1,2)
            sage: t.tensor_rank()
            3
            sage: v = M.vector_field()
            sage: v.tensor_rank()
            1
                
        """
        return self._tensor_rank

    def symmetries(self):
        r"""
        Print the list of symmetries and antisymmetries.

        See 
        :meth:`sage.tensor.modules.free_module_tensor.FreeModuleTensor.symmetries`
        for examples.
                
        """
        if len(self._sym) == 0:
            s = "no symmetry; "
        elif len(self._sym) == 1:
            s = "symmetry: " + str(self._sym[0]) + "; "
        else:
            s = "symmetries: " + str(self._sym) + "; " 
        if len(self._antisym) == 0:
            a = "no antisymmetry"
        elif len(self._antisym) == 1:
            a = "antisymmetry: " + str(self._antisym[0])
        else:
            a = "antisymmetries: " + str(self._antisym)   
        print s, a

    #### End of simple accessors #####


    def set_restriction(self, rst):
        r"""
        Define a restriction of ``self`` to some subdomain.

        INPUT:
        
        - ``rst`` -- tensor field of the same type and symmetries as ``self``, 
          defined on a subdomain of ``self._domain`` (must be an instance of
          :class:`TensorField`)
          
        """
        if not isinstance(rst, TensorField):
            raise TypeError("The argument must be a tensor field.")
        if not rst._domain.is_subdomain(self._domain):
            raise ValueError("The domain of the declared restriction is not " +
                             "a subdomain of the current field's domain.")
        if not rst._ambient_domain.is_subdomain(self._ambient_domain):
            raise ValueError("The ambient domain of the declared " + 
                             "restriction is not a subdomain of the current " + 
                             "field's ambient domain.")
        if rst._tensor_type != self._tensor_type:
            raise ValueError("The declared restriction has not the same " + 
                             "tensor type as the current tensor field.")
        if rst._tensor_type != self._tensor_type:
            raise ValueError("The declared restriction has not the same " + 
                             "tensor type as the current tensor field.")
        if rst._sym != self._sym:
            raise ValueError("The declared restriction has not the same " +
                             "symmetries as the current tensor field.")
        if rst._antisym != self._antisym:
            raise ValueError("The declared restriction has not the same " +
                             "antisymmetries as the current tensor field.")
        self._restrictions[rst._domain] = rst.copy()
        self._restrictions[rst._domain].set_name(name=self._name,
                                                 latex_name=self._latex_name)

    def restrict(self, subdomain, dest_map=None):
        r"""
        Return the restriction of ``self`` to some subdomain.
        
        If the restriction has not been defined yet, it is constructed here.

        INPUT:
        
        - ``subdomain`` -- open subset `U` of ``self._domain`` (must be an 
          instance of :class:`~sage.geometry.manifolds.domain.OpenDomain`)
        - ``dest_map`` -- (default: None) destination map 
          `\Phi:\ U \rightarrow V`, where `V` is a subdomain of 
          ``self._codomain``
          (type: :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`)
          If None, the restriction of ``self._vmodule._dest_map`` to `U` is 
          used.
          
        OUTPUT:
        
        - instance of :class:`TensorField` representing the restriction.
        
        EXAMPLES:
        
        Restrictions of a vector field on the 2-sphere::
        
            sage: M = Manifold(2, 'S^2', start_index=1)
            sage: U = M.open_domain('U') # the complement of the North pole
            sage: stereoN.<x,y> = U.chart()  # stereographic coordinates from the North pole
            sage: eN = stereoN.frame() # the associated vector frame
            sage: V =  M.open_domain('V') # the complement of the South pole
            sage: stereoS.<u,v> = V.chart()  # stereographic coordinates from the South pole
            sage: eS = stereoS.frame() # the associated vector frame
            sage: transf = stereoN.transition_map(stereoS, (x/(x^2+y^2), y/(x^2+y^2)), intersection_name='W', \
                                                  restrictions1= x^2+y^2!=0, restrictions2= u^2+v^2!=0)
            sage: inv = transf.inverse() # transformation from stereoS to stereoN
            sage: W = U.intersection(V) # the complement of the North and South poles
            sage: stereoN_W = W.atlas()[0]  # restriction of stereographic coord. from North pole to W
            sage: stereoS_W = W.atlas()[1]  # restriction of stereographic coord. from South pole to W
            sage: eN_W = stereoN_W.frame() ; eS_W = stereoS_W.frame()
            sage: v = M.vector_field('v')
            sage: v.set_comp(eN)[1] = 1  # given the default settings, this can be abriged to v[1] = 1
            sage: v.view()
            v = d/dx
            sage: vU = v.restrict(U) ; vU
            vector field 'v' on the open domain 'U' on the 2-dimensional manifold 'S^2'
            sage: vU.view()
            v = d/dx
            sage: vU == eN[1]
            True
            sage: vW = v.restrict(W) ; vW
            vector field 'v' on the open domain 'W' on the 2-dimensional manifold 'S^2'
            sage: vW.view()
            v = d/dx
            sage: vW.view(eS_W, stereoS_W)
            v = (-u^2 + v^2) d/du - 2*u*v d/dv
            sage: vW == eN_W[1]
            True

        At this stage, defining the restriction of v to domain V fully specifies v::
        
            sage: v.restrict(V)[1] = vW[eS_W, 1, stereoS_W].expr()  # note that eS is the default frame on V
            sage: v.restrict(V)[2] = vW[eS_W, 2, stereoS_W].expr()
            sage: v.view(eS, stereoS)
            v = (-u^2 + v^2) d/du - 2*u*v d/dv
            sage: v.restrict(U).view()
            v = d/dx
            sage: v.restrict(V).view()
            v = (-u^2 + v^2) d/du - 2*u*v d/dv
            
        The restriction of the vector field to its own domain is of course 
        itself::
        
            sage: v.restrict(M) is v
            True
            sage: vU.restrict(U) is vU
            True

        """
        if subdomain == self._domain:
            return self
        if subdomain not in self._restrictions:
            if not subdomain.is_subdomain(self._domain):
                raise ValueError("The provided domain is not a subdomain of " + 
                                 "the current field's domain.")
            if dest_map is None:
                dest_map = self._vmodule._dest_map.restrict(subdomain)
            elif not dest_map._codomain.is_subdomain(self._ambient_domain):
                raise ValueError("Argument dest_map not compatible with " + 
                                 "self._ambient_domain")
            # First one tries to get the restriction from a tighter domain:
            for dom, rst in self._restrictions.iteritems():
                if subdomain.is_subdomain(dom):
                    self._restrictions[subdomain] = rst.restrict(subdomain)
                    break
            # If this fails, the restriction is created from scratch:
            else:
                smodule = subdomain.vector_field_module(dest_map=dest_map)
                self._restrictions[subdomain] = smodule.tensor(self._tensor_type, 
                                                    name=self._name, 
                                                    latex_name=self._latex_name, 
                                                    sym=self._sym, 
                                                    antisym=self._antisym, 
                                                    specific_type=self.__class__)
        return self._restrictions[subdomain]

    def set_comp(self, basis=None):
        r"""
        Return the components of the tensor field in a given vector frame 
        for assignment.
        
        The components with respect to other frames having the same domain 
        as the provided vector frame are deleted, in order to avoid any 
        inconsistency. To keep them, use the method :meth:`add_comp` instead.
        
        INPUT:
        
        - ``basis`` -- (default: None) vector frame in which the components are
          defined; if none is provided, the components are assumed to refer to 
          the tensor field domain's default frame.
         
        OUTPUT: 
        
        - components in the given frame, as an instance of the 
          class :class:`~sage.tensor.modules.comp.Components`; if such 
          components did not exist previously, they are created.  
        
        """
        if basis is None: 
            basis = self._domain._def_frame
        self._del_derived() # deletes the derived quantities
        rst = self.restrict(basis._domain, dest_map=basis._dest_map)
        return rst.set_comp(basis)

    def add_comp(self, basis=None):
        r"""
        Return the components of the tensor field in a given vector frame 
        for assignment.
        
        The components with respect to other frames having the same domain 
        as the provided vector frame are kept. To delete them them, use the 
        method :meth:`set_comp` instead.
        
        INPUT:
        
        - ``basis`` -- (default: None) vector frame in which the components are
          defined; if none is provided, the components are assumed to refer to 
          the tensor field domain's default frame.
         
        OUTPUT: 
        
        - components in the given frame, as an instance of the 
          class :class:`~sage.tensor.modules.comp.Components`; if such 
          components did not exist previously, they are created.  

        """
        if basis is None: 
            basis = self._domain._def_frame
        self._del_derived() # deletes the derived quantities
        rst = self.restrict(basis._domain, dest_map=basis._dest_map)
        return rst.add_comp(basis)

    def add_comp_by_continuation(self, frame, subdomain, chart=None):
        r"""
        Set components w.r.t to a vector frame by continuation of the
        coordinate expression of the components in a subframe.  
        
        The continuation is performed by demanding that the components have
        the same coordinate expression as those on the restriction of the frame
        to a given subdomain. 
        
        INPUT:
        
        - ``frame`` -- vector frame `e` in which the components are to be set
        - ``subdomain`` -- subdomain of `e`'s domain in which the
          components are known or can be evaluated from other components
        - ``chart`` -- (default: None) coordinate chart on `e`'s domain in 
          which the extension of the expression of the components is to be 
          performed; if None, the default's chart of `e`'s domain is assumed
          
        EXAMPLES:
        
        Components of a vector field on the sphere `S^2`::
        
            sage: Manifold._clear_cache_() # for doctests only
            sage: M = Manifold(2, 'S^2', start_index=1)
            sage: # The two open domains covered by stereographic coordinates (North and South): 
            sage: U = M.open_domain('U') ; V = M.open_domain('V')
            sage: M.declare_union(U,V)   # S^2 is the union of U and V
            sage: c_xy.<x,y> = U.chart() ; c_uv.<u,v> = V.chart() # stereographic coordinates
            sage: transf = c_xy.transition_map(c_uv, (x/(x^2+y^2), y/(x^2+y^2)), intersection_name='W', restrictions1= x^2+y^2!=0, restrictions2= u^2+v^2!=0)
            sage: inv = transf.inverse()
            sage: W = U.intersection(V) # The complement of the two poles
            sage: eU = c_xy.frame() ; eV = c_uv.frame()
            sage: a = M.vector_field('a')
            sage: a[eU,:] = [x, 2+y]
        
        At this stage, the vector field has been defined only on the domain U 
        (through its components in the frame eU)::
        
            sage: a.view(eU)
            a = x d/dx + (y + 2) d/dy

        The components with respect to the restriction of eV to the common 
        subdomain W, in terms of the (u,v) coordinates, are obtained by a
        change-of-frame formula on W::
        
            sage: a.view(eV.restrict(W), c_uv.restrict(W))
            a = (-4*u*v - u) d/du + (2*u^2 - 2*v^2 - v) d/dv

        The continuation consists in extending the definition of the vector 
        field to the whole domain V by demanding that the components in the 
        frame eV have the same coordinate expression as the above one::
        
            sage: a.add_comp_by_continuation(eV, W, chart=c_uv)

        We have then::
        
            sage: a.view(eV)
            a = (-4*u*v - u) d/du + (2*u^2 - 2*v^2 - v) d/dv
        
        and `a` is defined on the entire manifold `S^2`. 
        
        """
        dom = frame._domain
        if not dom.is_subdomain(self._domain):
            raise ValueError("The vector frame is not defined on a subdomain" + 
                             " of the tensor field domain.")
        if chart is None:
            chart = dom._def_chart
        sframe = frame.restrict(subdomain)
        schart = chart.restrict(subdomain)
        scomp = self.comp(sframe)
        resu = self.add_comp(frame) # _del_derived is performed here
        for ind in resu.non_redundant_index_generator():
            resu[[ind]] = dom.scalar_field({chart: scomp[[ind]].expr(schart)})
        
    def comp(self, basis=None, from_basis=None):
        r"""
        Return the components in a given vector frame.
        
        If the components are not known already, they are computed by the tensor
        change-of-basis formula from components in another vector frame. 
        
        INPUT:
        
        - ``basis`` -- (default: None) vector frame in which the components are 
          required; if none is provided, the components are assumed to refer to
          the tensor field domain's default frame
        - ``from_basis`` -- (default: None) vector frame from which the
          required components are computed, via the tensor change-of-basis 
          formula, if they are not known already in the basis ``basis``
          
        OUTPUT: 
        
        - components in the vector frame ``basis``, as an instance of the 
          class :class:`~sage.tensor.modules.comp.Components` 

        EXAMPLES:
        
        Components of a type-(1,1) tensor field defined on two open domains::

            sage: Manifold._clear_cache_() # for doctests only
            sage: M = Manifold(2, 'M')
            sage: U = M.open_domain('U')
            sage: c_xy.<x, y> = U.chart()
            sage: e = U.default_frame() ; e
            coordinate frame (U, (d/dx,d/dy))
            sage: V = M.open_domain('V')
            sage: c_uv.<u, v> = V.chart()
            sage: f = V.default_frame() ; f
            coordinate frame (V, (d/du,d/dv))
            sage: M.declare_union(U,V)   # M is the union of U and V
            sage: t = M.tensor_field(1,1, name='t')
            sage: t[e,0,0] = - x + y^3
            sage: t[e,0,1] = 2+x
            sage: t[f,1,1] = - u*v
            sage: t.comp(e)
            2-indices components w.r.t. coordinate frame (U, (d/dx,d/dy))
            sage: t.comp(e)[:]
            [y^3 - x   x + 2]
            [      0       0]
            sage: t.comp(f)
            2-indices components w.r.t. coordinate frame (V, (d/du,d/dv))
            sage: t.comp(f)[:]
            [   0    0]
            [   0 -u*v]

        Since e is M's default frame, the argument e can be omitted::
        
            sage: e is M.default_frame()
            True
            sage: t.comp() is t.comp(e)
            True

        Example of computation of the components via a change of frame::
        
            sage: a = V.automorphism_field()
            sage: a[:] = [[1+v, -u^2], [0, 1-u]]
            sage: h = f.new_frame(a, 'h')
            sage: t.comp(h)
            2-indices components w.r.t. vector frame (V, (h_0,h_1))
            sage: t.comp(h)[:]
            [             0 -u^3*v/(v + 1)]
            [             0           -u*v]

        """
        if basis is None: 
            basis = self._domain._def_frame
        rst = self.restrict(basis._domain, dest_map=basis._dest_map)
        return rst.comp(basis=basis, from_basis=from_basis)

    def view(self, basis=None, chart=None):
        r"""
        Displays the tensor field in terms of its expansion w.r.t to a given
        vector frame.
        
        The output is either text-formatted (console mode) or LaTeX-formatted
        (notebook mode). 
        
        INPUT:
                
        - ``basis`` -- (default: None) vector frame with respect to 
          which the tensor is expanded; if none is provided, the default frame
          of the domain of definition of the tensor field is assumed.
        - ``chart`` -- (default: None) chart with respect to which the 
          components of the tensor field in the selected frame are expressed; 
          if none is provided, the default chart of the vector frame domain
          is assumed.
        
        EXAMPLES:
        
        Display of a type-(1,1) tensor field defined on two open domains::
        
            sage: M = Manifold(2, 'M')
            sage: U = M.open_domain('U')
            sage: c_xy.<x, y> = U.chart()
            sage: e = U.default_frame() ; e
            coordinate frame (U, (d/dx,d/dy))
            sage: V = M.open_domain('V')
            sage: c_uv.<u, v> = V.chart()
            sage: f = V.default_frame() ; f
            coordinate frame (V, (d/du,d/dv))
            sage: M.declare_union(U,V)   # M is the union of U and V
            sage: t = M.tensor_field(1,1, name='t')
            sage: t[e,0,0] = - x + y^3
            sage: t[e,0,1] = 2+x
            sage: t[f,1,1] = - u*v
            sage: t.view(e)
            t = (y^3 - x) d/dx*dx + (x + 2) d/dx*dy
            sage: t.view(f)
            t = -u*v d/dv*dv
            
        Since e is M's default frame, the argument e can be omitted::
        
            sage: e is M.default_frame()
            True
            sage: t.view()
            t = (y^3 - x) d/dx*dx + (x + 2) d/dx*dy

        Similarly, since f is V's default frame, the argument f can be omitted
        when considering the restriction of t to V::
        
            sage: t.restrict(V).view()
            t = -u*v d/dv*dv

        Display w.r.t a frame in which t has not been initialized (automatic
        use of a change-of-frame formula)::
        
            sage: a = V.automorphism_field()
            sage: a[:] = [[1+v, -u^2], [0, 1-u]]
            sage: h = f.new_frame(a, 'h')
            sage: t.view(h)
            t = -u^3*v/(v + 1) h_0*h^1 - u*v h_1*h^1

        """
        if basis is None: 
            basis = self._domain._def_frame
        rst = self.restrict(basis._domain, dest_map=basis._dest_map)
        return rst.view(basis, chart)


    def __getitem__(self, args):
        r"""
        Return a component w.r.t. some frame.

        NB: if ``args`` is a string, this method acts as a shortcut for 
        tensor contractions and symmetrizations, the string containing 
        abstract indices.

        INPUT:
        
        - ``args`` -- list of indices defining the component; if [:] is 
          provided, all the components are returned. The frame can be passed
          as the first item of ``args``; if not, the default frame of the 
          tensor field's domain is assumed. 
    
        """
        if isinstance(args, str): # tensor with specified indices
            return TensorWithIndices(self, args).update()
        if isinstance(args, list):  # case of [[...]] syntax
            if not isinstance(args[0], (int, Integer, slice)):
                frame = args[0]
                args = args[1:]
            else:
                frame = self._domain._def_frame
        else:
            if isinstance(args, (int, Integer, slice)):
                frame = self._domain._def_frame
            elif not isinstance(args[0], (int, Integer, slice)):
                frame = args[0]
                args = args[1:]
            else:
                frame = self._domain._def_frame
        return self.comp(frame)[args]

    def __setitem__(self, args, value):
        r"""
        Sets a component w.r.t to some vector frame. 

        INPUT:
        
       - ``args`` -- list of indices; if [:] is provided, all the components 
          are set. The frame can be passed as the first item of ``args``; if 
          not, the default frame of the tensor field's domain is assumed. 
        - ``value`` -- the value to be set or a list of values if ``args``
          == ``[:]``
    
        """
        if isinstance(args, list):  # case of [[...]] syntax
            if not isinstance(args[0], (int, Integer, slice)):
                frame = args[0]
                args = args[1:]
            else:
                frame = self._domain._def_frame
        else:
            if isinstance(args, (int, Integer, slice)):
                frame = self._domain._def_frame
            elif not isinstance(args[0], (int, Integer, slice)):
                frame = args[0]
                args = args[1:]
            else:
                frame = self._domain._def_frame
        self.set_comp(frame)[args] = value


    def copy(self):
        r"""
        Return an exact copy of ``self``.
        
        The name and the derived quantities are not copied. 
        
        EXAMPLES:
        
        If the original tensor field is modified, the copy is not.
        
        """
        resu = self._new_instance()
        for dom, rst in self._restrictions.iteritems():
            resu._restrictions[dom] = rst.copy()
        return resu

    def _common_subdomains(self, other):
        r"""
        Returns the list of subdomains of self._domain on which both ``self``
        and ``other`` have known restrictions.
        """
        resu = []
        for dom in self._restrictions:
            if dom in other._restrictions:
                resu.append(dom)
        return resu

    def __eq__(self, other):
        r"""
        Comparison (equality) operator. 
        
        INPUT:
        
        - ``other`` -- a tensor field or 0
        
        OUTPUT:
        
        - True if ``self`` is equal to ``other`` and False otherwise
        
        """
        if isinstance(other, (int, Integer)): # other should be 0
            if other == 0:
                return self.is_zero()
            else:
                return False
        elif not isinstance(other, TensorField):
            return False
        else: # other is another tensor field
            if other._vmodule != self._vmodule:
                return False
            if other._tensor_type != self._tensor_type:
                return False
            resu = True
            for dom, rst in self._restrictions.iteritems():
                if dom in other._restrictions:
                    resu = resu and bool(rst == other._restrictions[dom])
            return resu

    def __ne__(self, other):
        r"""
        Inequality operator. 
        
        INPUT:
        
        - ``other`` -- a tensor field or 0
        
        OUTPUT:
        
        - True if ``self`` is different from ``other`` and False otherwise
        
        """
        return not self.__eq__(other)

    def __pos__(self):
        r"""
        Unary plus operator. 
        
        OUTPUT:
        
        - an exact copy of ``self``
    
        """
        resu = self._new_instance()
        for dom, rst in self._restrictions.iteritems():
            resu._restrictions[dom] = + rst
        if self._name is not None:
            resu._name = '+' + self._name 
        if self._latex_name is not None:
            resu._latex_name = '+' + self._latex_name
        return resu

    def __neg__(self):
        r"""
        Unary minus operator. 
        
        OUTPUT:
        
        - the tensor field `-T`, where `T` is ``self``
    
        """
        resu = self._new_instance()
        for dom, rst in self._restrictions.iteritems():
            resu._restrictions[dom] = - rst
        if self._name is not None:
            resu._name = '-' + self._name 
        if self._latex_name is not None:
            resu._latex_name = '-' + self._latex_name
        return resu

    ######### ModuleElement arithmetic operators ########
    
    def _add_(self, other):
        r"""
        Tensor field addition. 
        
        INPUT:
        
        - ``other`` -- a tensor field, in the same tensor module as ``self`` 
        
        OUPUT:
        
        - the tensor field resulting from the addition of ``self`` and ``other``
        
        """
        if other == 0:
            return +self
        if not isinstance(other, TensorField):
            raise TypeError("For the addition, other must be a tensor field.")
        if other._vmodule != self._vmodule:
            raise ValueError("The two tensor fields do not belong to the " + 
                             "same module.")
        if other._tensor_type != self._tensor_type:
            raise TypeError("The two tensor fields are not of the same type.")
        resu_rst = {}
        for dom in self._common_subdomains(other):
            resu_rst[dom] = self._restrictions[dom] + other._restrictions[dom]
        some_rst = resu_rst.values()[0]
        resu_sym = some_rst._sym
        resu_antisym = some_rst._antisym
        resu = self._vmodule.tensor(self._tensor_type, sym=resu_sym, 
                                    antisym=resu_antisym)
        resu._restrictions = resu_rst
        if self._name is not None and other._name is not None:
            resu._name = self._name + '+' + other._name
        if self._latex_name is not None and other._latex_name is not None:
            resu._latex_name = self._latex_name + '+' + other._latex_name
        return resu

    def _sub_(self, other):
        r"""
        Tensor field subtraction. 
        
        INPUT:
        
        - ``other`` -- a tensor field, in the same tensor module as ``self``
        
        OUPUT:
        
        - the tensor field resulting from the subtraction of ``other`` from 
          ``self``
                
        """
        if other == 0:
            return +self
        if not isinstance(other, TensorField):
            raise TypeError("For the subtraction, other must be a tensor " + 
                            "field.")
        if other._vmodule != self._vmodule:
            raise ValueError("The two tensor fields do not belong to the " + 
                             "same module.")
        if other._tensor_type != self._tensor_type:
            raise TypeError("The two tensor fields are not of the same type.")
        resu_rst = {}
        for dom in self._common_subdomains(other):
            resu_rst[dom] = self._restrictions[dom] - other._restrictions[dom]
        some_rst = resu_rst.values()[0]
        resu_sym = some_rst._sym
        resu_antisym = some_rst._antisym
        resu = self._vmodule.tensor(self._tensor_type, sym=resu_sym, 
                                   antisym=resu_antisym)
        resu._restrictions = resu_rst
        if self._name is not None and other._name is not None:
            resu._name = self._name + '-' + other._name
        if self._latex_name is not None and other._latex_name is not None:
            resu._latex_name = self._latex_name + '-' + other._latex_name
        return resu

    def _rmul_(self, scalar):
        r"""
        Multiplication on the left by a scalar field (``scalar``)
        
        This is actually the multiplication by an element of the ring over
        which the tensor field module is constructed. 
        
        """
        #!# The following test is probably not necessary:
        if isinstance(scalar, TensorField):
            raise NotImplementedError("Left tensor product not implemented.")
        # Left multiplication by a scalar field: 
        resu = self._new_instance()
        for dom, rst in self._restrictions.iteritems():
            resu._restrictions[dom] = scalar.restrict(dom) * rst
        return resu

    ######### End of ModuleElement arithmetic operators ########

    def __radd__(self, other):
        r"""
        Addition on the left with ``other``. 
        
        This allows to write "0 + t", where "t" is a tensor
        
        """
        return self.__add__(other)

    def __rsub__(self, other):
        r"""
        Subtraction from ``other``. 

        This allows to write "0 - t", where "t" is a tensor
        
        """
        return (-self).__add__(other)

    def __mul__(self, other):
        r"""
        Tensor product. 
        """
        dom_resu = self._domain.intersection(other._domain)
        ambient_dom_resu = self._ambient_domain.intersection(
                                                         other._ambient_domain)
        self_r = self.restrict(dom_resu)
        other_r = other.restrict(dom_resu)
        if ambient_dom_resu.is_manifestly_parallelizable():
            # call of the FreeModuleTensor version:
            return FreeModuleTensor.__mul__(self_r, other_r)
        dest_map = self._vmodule._dest_map
        dest_map_resu = dest_map.restrict(dom_resu, 
                                          subcodomain=ambient_dom_resu)
        vmodule = dom_resu.vector_field_module(dest_map=dest_map_resu)
        com_dom = []
        for dom in self_r._restrictions:
            if dom in other_r._restrictions:
                com_dom.append(dom)
        resu_rst = []
        for dom in com_dom:
            self_rr = self_r._restrictions[dom]
            other_rr = other_r._restrictions[dom]
            resu_rst.append(self_rr * other_rr)
        k1, l1 = self._tensor_type
        k2, l2 = other._tensor_type
        resu = vmodule.tensor((k1+k2, l1+l2), sym=resu_rst[0]._sym, 
                              antisym=resu_rst[0]._antisym)
        for rst in resu_rst:
            resu._restrictions[rst._domain] = rst
        return resu

    def __div__(self, scalar):
        r"""
        Division (by a scalar field)
        """
        resu = self._new_instance()
        for dom, rst in self._restrictions.iteritems():
            resu._restrictions[dom] = rst / scalar
        return resu

    def up(self, metric, pos=None):
        r"""
        Compute a metric dual by raising some index with a given metric.
        
        If ``self`` is a tensor field `T` of type `(k,\ell)` and `p` is the 
        position of a covariant index (i.e. `k\leq p < k+\ell`), 
        the output with ``pos`` `=p` is the tensor field `T^\sharp` of type 
        `(k+1,\ell-1)` whose components are

        .. MATH::

            (T^\sharp)^{a_1\ldots a_{k+1}}_{\qquad\quad b_1 \ldots b_{\ell-1}}
            = g^{a_{k+1} i} \, 
            T^{a_1\ldots a_k}_{\qquad\ \  b_1 \ldots b_{p-k} \, i \, b_{p-k+1} \ldots b_{\ell-1}},
            
        `g^{ab}` being the components of the inverse metric. 

        The reverse operation is :meth:`TensorField.down`

        INPUT:
        
        - ``metric`` -- metric `g`, as an instance of 
          :class:`~sage.geometry.manifolds.metric.Metric`
        - ``pos`` -- (default: None) position of the index (with the
          convention ``pos=0`` for the first index); if none, the raising is 
          performed over all the covariant indices, starting from the first one
         
        OUTPUT:
        
        - the tensor field `T^\sharp` resulting from the index raising operation

        EXAMPLES:
        
        Raising the index of a 1-form results in a vector field::
        
            sage: M = Manifold(2, 'M', start_index=1)
            sage: c_xy.<x,y> = M.chart()
            sage: g = M.metric('g')
            sage: g[1,1], g[1,2], g[2,2] = 1+x, x*y, 1-y
            sage: w = M.one_form()
            sage: w[:] = [-1, 2]
            sage: v = w.up(g) ; v
            vector field on the 2-dimensional manifold 'M'
            sage: v.view()
            ((2*x - 1)*y + 1)/(x^2*y^2 + (x + 1)*y - x - 1) d/dx - (x*y + 2*x + 2)/(x^2*y^2 + (x + 1)*y - x - 1) d/dy
            sage: ig = g.inverse(); ig[:]
            [ (y - 1)/(x^2*y^2 + (x + 1)*y - x - 1)      x*y/(x^2*y^2 + (x + 1)*y - x - 1)]
            [     x*y/(x^2*y^2 + (x + 1)*y - x - 1) -(x + 1)/(x^2*y^2 + (x + 1)*y - x - 1)]
        
        Using the index notation instead of :meth:`up`::
        
            sage: v == ig['^ab']*w['_b']
            True

        The reverse operation::
        
            sage: w1 = v.down(g) ; w1
            1-form on the 2-dimensional manifold 'M'
            sage: w1.view()
            -dx + 2 dy
            sage: w1 == w
            True

        The reverse operation in index notation::
        
            sage: g['_ab']*v['^b'] == w
            True
            
        Raising the indices of a tensor field of type (0,2)::

            sage: t = M.tensor_field(0, 2)
            sage: t[:] = [[1,2], [3,4]]
            sage: tu0 = t.up(g, 0) ; tu0  # raising the first index
            field of endomorphisms on the 2-dimensional manifold 'M'
            sage: tu0[:]
            [  ((3*x + 1)*y - 1)/(x^2*y^2 + (x + 1)*y - x - 1) 2*((2*x + 1)*y - 1)/(x^2*y^2 + (x + 1)*y - x - 1)]
            [    (x*y - 3*x - 3)/(x^2*y^2 + (x + 1)*y - x - 1)   2*(x*y - 2*x - 2)/(x^2*y^2 + (x + 1)*y - x - 1)]
            sage: tu0 == ig['^ac']*t['_cb'] # the same operation in index notation
            True
            sage: tuu0 = tu0.up(g) ; tuu0 # the two indices have been raised, starting from the first one
            tensor field of type (2,0) on the 2-dimensional manifold 'M'
            sage: tuu0 == tu0['^a_c']*ig['^cb'] # the same operation in index notation
            True
            sage: tu1 = t.up(g, 1) ; tu1 # raising the second index
            field of endomorphisms on the 2-dimensional manifold 'M'
            sage: tu1 == ig['^ac']*t['_bc'] # the same operation in index notation
            True
            sage: tu1[:]
            [((2*x + 1)*y - 1)/(x^2*y^2 + (x + 1)*y - x - 1) ((4*x + 3)*y - 3)/(x^2*y^2 + (x + 1)*y - x - 1)]
            [  (x*y - 2*x - 2)/(x^2*y^2 + (x + 1)*y - x - 1) (3*x*y - 4*x - 4)/(x^2*y^2 + (x + 1)*y - x - 1)]
            sage: tuu1 = tu1.up(g) ; tuu1 # the two indices have been raised, starting from the second one
            tensor field of type (2,0) on the 2-dimensional manifold 'M'
            sage: tuu1 == tu1['^a_c']*ig['^cb'] # the same operation in index notation
            True
            sage: tuu0 == tuu1 # the order of index raising is important
            False
            sage: tuu = t.up(g) ; tuu # both indices are raised, starting from the first one
            tensor field of type (2,0) on the 2-dimensional manifold 'M'
            sage: tuu0 == tuu # the same order for index raising has been applied
            True
            sage: tuu1 == tuu # to get tuu1, indices have been raised from the last one, contrary to tuu 
            False
            sage: d0tuu = tuu.down(g, 0) ; d0tuu # the first index is lowered again
            field of endomorphisms on the 2-dimensional manifold 'M'
            sage: dd0tuu = d0tuu.down(g) ; dd0tuu  # the second index is then lowered
            tensor field of type (0,2) on the 2-dimensional manifold 'M'
            sage: d1tuu = tuu.down(g, 1) ; d1tuu # lowering operation, starting from the last index
            field of endomorphisms on the 2-dimensional manifold 'M'
            sage: dd1tuu = d1tuu.down(g) ; dd1tuu
            tensor field of type (0,2) on the 2-dimensional manifold 'M'
            sage: ddtuu = tuu.down(g) ; ddtuu # both indices are lowered, starting from the last one
            tensor field of type (0,2) on the 2-dimensional manifold 'M'
            sage: ddtuu == t # should be true
            True
            sage: dd0tuu == t # not true, because of the order of index lowering to get dd0tuu
            False
            sage: dd1tuu == t # should be true
            True

        """
        from sage.rings.integer import Integer
        n_con = self._tensor_type[0] # number of contravariant indices = k 
        if pos is None:
            result = self
            for p in range(n_con, self._tensor_rank):
                k = result._tensor_type[0]
                result = result.up(metric, k)
            return result
        if not isinstance(pos, (int, Integer)):
            raise TypeError("The argument 'pos' must be an integer.")
        if pos<n_con or pos>self._tensor_rank-1:
            print "pos = ", pos
            raise ValueError("Position out of range.")
        return self.contract(pos, metric.inverse(), 0)

    def down(self, metric, pos=None):
        r"""
        Compute a metric dual by lowering some index with a given metric.
        
        If ``self`` is a tensor field `T` of type `(k,\ell)` and `p` is the 
        position of a contravariant index (i.e. `0\leq p < k`), the output with
        ``pos`` `=p` is the tensor field `T^\flat` of type `(k-1,\ell+1)` whose 
        components are

        .. MATH::

            (T^\flat)^{a_1\ldots a_{k-1}}_{\qquad\quad b_1 \ldots b_{\ell+1}}
            = g_{b_1 i} \, 
            T^{a_1\ldots a_{p} \, i \, a_{p+1}\ldots a_{k-1}}_{\qquad\qquad\qquad\quad b_2 \ldots b_{\ell+1}},
            
        `g_{ab}` being the components of the metric tensor. 

        The reverse operation is :meth:`TensorField.up`
        
        INPUT:
        
        - ``metric`` -- metric `g`, as an instance of 
          :class:`~sage.geometry.manifolds.metric.Metric`
        - ``pos`` -- (default: None) position of the index (with the 
          convention ``pos=0`` for the first index); if none, the lowering is 
          performed over all the contravariant indices, starting from the last 
          one
         
        OUTPUT:
        
        - the tensor field `T^\flat` resulting from the index lowering operation
        
        EXAMPLES:
        
        Lowering the index of a vector field results in a 1-form::
        
            sage: M = Manifold(2, 'M', start_index=1)
            sage: c_xy.<x,y> = M.chart()
            sage: g = M.metric('g')
            sage: g[1,1], g[1,2], g[2,2] = 1+x, x*y, 1-y
            sage: v = M.vector_field()
            sage: v[:] = [-1,2]
            sage: w = v.down(g) ; w
            1-form on the 2-dimensional manifold 'M'
            sage: w.view()
            (2*x*y - x - 1) dx + (-(x + 2)*y + 2) dy

        Using the index notation instead of :meth:`down`::

            sage: w == g['_ab']*v['^b']
            True

        The reverse operation::
        
            sage: v1 = w.up(g) ; v1
            vector field on the 2-dimensional manifold 'M'
            sage: v1 == v
            True

        Lowering the indices of a tensor field of type (2,0)::
        
            sage: t = M.tensor_field(2, 0)
            sage: t[:] = [[1,2], [3,4]]
            sage: td0 = t.down(g, 0) ; td0  # lowering the first index
            field of endomorphisms on the 2-dimensional manifold 'M'
            sage: td0 == g['_ac']*t['^cb'] # the same operation in index notation
            True
            sage: td0[:]
            [  3*x*y + x + 1   (x - 3)*y + 3]
            [4*x*y + 2*x + 2 2*(x - 2)*y + 4]
            sage: tdd0 = td0.down(g) ; tdd0 # the two indices have been lowered, starting from the first one
            tensor field of type (0,2) on the 2-dimensional manifold 'M'
            sage: tdd0 == g['_ac']*td0['^c_b'] # the same operation in index notation
            True
            sage: tdd0[:]
            [      4*x^2*y^2 + x^2 + 5*(x^2 + x)*y + 2*x + 1 2*(x^2 - 2*x)*y^2 + (x^2 + 2*x - 3)*y + 3*x + 3]
            [(3*x^2 - 4*x)*y^2 + (x^2 + 3*x - 2)*y + 2*x + 2           (x^2 - 5*x + 4)*y^2 + (5*x - 8)*y + 4]
            sage: td1 = t.down(g, 1) ; td1  # lowering the second index
            field of endomorphisms on the 2-dimensional manifold 'M'
            sage: td1 == g['_ac']*t['^bc'] # the same operation in index notation
            True
            sage: td1[:]
            [  2*x*y + x + 1   (x - 2)*y + 2]
            [4*x*y + 3*x + 3 (3*x - 4)*y + 4]
            sage: tdd1 = td1.down(g) ; tdd1 # the two indices have been lowered, starting from the second one
            tensor field of type (0,2) on the 2-dimensional manifold 'M'
            sage: tdd1 == g['_ac']*td1['^c_b'] # the same operation in index notation
            True
            sage: tdd1[:]
            [      4*x^2*y^2 + x^2 + 5*(x^2 + x)*y + 2*x + 1 (3*x^2 - 4*x)*y^2 + (x^2 + 3*x - 2)*y + 2*x + 2]
            [2*(x^2 - 2*x)*y^2 + (x^2 + 2*x - 3)*y + 3*x + 3           (x^2 - 5*x + 4)*y^2 + (5*x - 8)*y + 4]
            sage: tdd1 == tdd0   # the order of index lowering is important
            False
            sage: tdd = t.down(g) ; tdd  # both indices are lowered, starting from the last one
            tensor field of type (0,2) on the 2-dimensional manifold 'M'
            sage: tdd[:]
            [      4*x^2*y^2 + x^2 + 5*(x^2 + x)*y + 2*x + 1 (3*x^2 - 4*x)*y^2 + (x^2 + 3*x - 2)*y + 2*x + 2]
            [2*(x^2 - 2*x)*y^2 + (x^2 + 2*x - 3)*y + 3*x + 3           (x^2 - 5*x + 4)*y^2 + (5*x - 8)*y + 4]
            sage: tdd0 == tdd  # to get tdd0, indices have been lowered from the first one, contrary to tdd 
            False
            sage: tdd1 == tdd  # the same order for index lowering has been applied
            True
            sage: u0tdd = tdd.up(g, 0) ; u0tdd # the first index is raised again
            field of endomorphisms on the 2-dimensional manifold 'M'
            sage: uu0tdd = u0tdd.up(g) ; uu0tdd # the second index is then raised
            tensor field of type (2,0) on the 2-dimensional manifold 'M'
            sage: u1tdd = tdd.up(g, 1) ; u1tdd  # raising operation, starting from the last index
            field of endomorphisms on the 2-dimensional manifold 'M'
            sage: uu1tdd = u1tdd.up(g) ; uu1tdd
            tensor field of type (2,0) on the 2-dimensional manifold 'M'
            sage: uutdd = tdd.up(g) ; uutdd  # both indices are raised, starting from the first one
            tensor field of type (2,0) on the 2-dimensional manifold 'M'
            sage: uutdd == t  # should be true
            True
            sage: uu0tdd == t # should be true
            True
            sage: uu1tdd == t # not true, because of the order of index raising to get uu1tdd
            False
 
        """
        from sage.rings.integer import Integer
        n_con = self._tensor_type[0] # number of contravariant indices = k 
        if pos is None:
            result = self
            for p in range(0, n_con):
                k = result._tensor_type[0]
                result = result.down(metric, k-1)
            return result
        if not isinstance(pos, (int, Integer)):
            raise TypeError("The argument 'pos' must be an integer.")
        if pos<0 or pos>=n_con:
            print "pos = ", pos
            raise ValueError("Position out of range.")
        return metric.contract(1, self, pos)


    def __call__(self, *args):
        r"""
        The tensor field acting on 1-forms and vector fields as a multilinear 
        map.
        
        INPUT:
        
        - ``*args`` -- list of k 1-forms and l vector fields, ``self`` 
          being a tensor of type (k,l). 
          
        """
        p = len(args)
        if p != self._tensor_rank:
            raise TypeError(str(self._tensor_rank) + 
                            " arguments must be provided.")
        # Domain of the result
        dom_resu = self._domain
        ambient_dom = self._ambient_domain
        for arg in args:
            dom_resu = dom_resu.intersection(arg._domain)
            ambient_dom = ambient_dom.intersection(arg._ambient_domain)
        self_r = self.restrict(dom_resu)
        args_r = [args[i].restrict(dom_resu) for i in range(p)]
        if ambient_dom.is_manifestly_parallelizable():
            # TensorFieldParal version
            return self_r(*args_r)
        else:
            resu = dom_resu.scalar_field()
            com_dom = []
            for dom in self_r._restrictions:
                for arg in args_r:
                    if dom not in arg._restrictions:
                        break
                else:
                    com_dom.append(dom)
            for dom in com_dom:
                self_rr = self_r._restrictions[dom]
                args_rr = [args_r[i]._restrictions[dom] for i in range(p)]
                resu_rr = self_rr(*args_rr)
                if resu_rr == 0:
                    for chart in resu_rr._domain._atlas:
                        resu._express[chart] = chart._zero_function
                else:
                    for chart, expr in resu_rr._express.iteritems():
                        resu._express[chart] = expr
            if resu == 0:
                return dom_resu._zero_scalar_field
            # Name of the output:
            res_name = None
            if self._name is not None:
                res_name = self._name + "("
                for i in range(p-1):
                    if args[i]._name is not None:
                        res_name += args[i]._name + ","
                    else:
                        res_name = None
                        break
                if res_name is not None:
                    if args[p-1]._name is not None:
                        res_name += args[p-1]._name + ")"
                    else:
                        res_name = None
            resu._name = res_name       
            # LaTeX symbol of the output:
            res_latex = None
            if self._latex_name is not None:
                res_latex = self._latex_name + r"\left("
                for i in range(p-1):
                    if args[i]._latex_name is not None:
                        res_latex += args[i]._latex_name + ","
                    else:
                        res_latex = None
                        break
                if res_latex is not None:
                    if args[p-1]._latex_name is not None:
                        res_latex += args[p-1]._latex_name + r"\right)"
                    else:
                        res_latex = None
            resu._latex_name = res_latex
            return resu

    def trace(self, pos1=0, pos2=1):
        r""" 
        Trace (contraction) on two slots of the tensor field. 
        
        INPUT:
            
        - ``pos1`` -- (default: 0) position of the first index for the 
          contraction, with the convention ``pos1=0`` for the first slot
        - ``pos2`` -- (default: 1) position of the second index for the 
          contraction, with the same convention as for ``pos1``. The variance 
          type of ``pos2`` must be opposite to that of ``pos1``
          
        OUTPUT:
        
        - tensor field resulting from the (pos1, pos2) contraction
       
        EXAMPLES:

        Trace of a type-(1,1) tensor field on a 2-dimensional 
        non-parallelizable manifold::

            sage: M = Manifold(2, 'M')
            sage: U = M.open_domain('U') ; V = M.open_domain('V') 
            sage: M.declare_union(U,V)   # M is the union of U and V
            sage: c_xy.<x,y> = U.chart() ; c_uv.<u,v> = V.chart()
            sage: transf = c_xy.transition_map(c_uv, (x+y, x-y), intersection_name='W', restrictions1= x>0, restrictions2= u+v>0)
            sage: inv = transf.inverse()
            sage: W = U.intersection(V)
            sage: eU = c_xy.frame() ; eV = c_uv.frame()
            sage: a = M.tensor_field(1,1, name='a')
            sage: a[eU,:] = [[1,x], [2,y]]
            sage: a.add_comp_by_continuation(eV, W, chart=c_uv)
            sage: s = a.trace() ; s
            scalar field on the 2-dimensional manifold 'M'
            sage: s.view()
            M --> R
            on U: (x, y) |--> y + 1
            on V: (u, v) |--> 1/2*u - 1/2*v + 1
            sage: s == a.trace(0,1) # explicit mention of the positions
            True

        Instead of the explicit call to the method :meth:`trace`, one
        may use the index notation with Einstein convention (summation over
        repeated indices); it suffices to pass the indices as a string inside
        square brackets::
        
            sage: a['^i_i']
            scalar field on the 2-dimensional manifold 'M'
            sage: a['^i_i'] == s
            True

        Any letter can be used to denote the repeated index::
        
            sage: a['^b_b'] == s
            True
        
        Trace of a type-(1,2) tensor field::

            sage: b = M.tensor_field(1,2, name='b') ; b
            tensor field 'b' of type (1,2) on the 2-dimensional manifold 'M'
            sage: b[eU,:] = [[[1,x], [2,y]], [[0,y-3], [x*y,y^2]]]
            sage: b.add_comp_by_continuation(eV, W, chart=c_uv)
            sage: s = b.trace(0,1) ; s # contraction on first and second slots
            1-form on the 2-dimensional manifold 'M'
            sage: s.view(eU)
            (x*y + 1) dx + (y^2 + x) dy
            sage: s.view(eV)
            (1/4*u^2 - 1/4*(u - 1)*v + 1/4*u + 1/2) du + (1/4*(u - 1)*v - 1/4*v^2 - 1/4*u + 1/2) dv
            
        Use of the index notation::
        
            sage: b['^k_ki']
            1-form on the 2-dimensional manifold 'M'
            sage: b['^k_ki'] == s
            True

        Indices not involved in the contraction may be replaced by dots::
        
            sage: b['^k_k.'] == s
            True
    
        The symbol '^' may be omitted::

            sage: b['k_k.'] == s
            True
        
        LaTeX notations are allowed::
        
            sage: b['^{k}_{ki}'] == s
            True

        Contraction on first and third slots::
            
            sage: s = b.trace(0,2) ; s
            1-form on the 2-dimensional manifold 'M'
            sage: s.view(eU)
            (y - 2) dx + (y^2 + 2) dy
            sage: s.view(eV)
            (1/8*u^2 - 1/4*(u + 1)*v + 1/8*v^2 + 1/4*u) du + (-1/8*u^2 + 1/4*(u - 1)*v - 1/8*v^2 + 1/4*u - 2) dv
        
        Use of index notation::
        
            sage: b['^k_.k'] == s
            True 

        """
        # The indices at pos1 and pos2 must be of different types: 
        k_con = self._tensor_type[0]
        l_cov = self._tensor_type[1]
        if pos1 < k_con and pos2 < k_con:
            raise IndexError("Contraction on two contravariant indices is " +
                             "not allowed.")
        if pos1 >= k_con and pos2 >= k_con:
            raise IndexError("Contraction on two covariant indices is " +
                             "not allowed.")
        resu_rst = []
        for rst in self._restrictions.itervalues():
            resu_rst.append(rst.trace(pos1, pos2))
        if (k_con, l_cov) == (1,1):
            # scalar field result
            resu = self._domain.scalar_field()
            all_zero = True
            for rst in resu_rst:
                if rst == 0:
                    for chart in rst._domain._atlas:
                        resu._express[chart] = 0
                else:
                    all_zero = False
                    for chart, funct in rst._express.iteritems():
                        resu._express[chart] = funct
            if all_zero:
                resu = self._domain._zero_scalar_field
        else:
            # tensor field result
            resu = self._vmodule.tensor((k_con-1, l_cov-1), 
                            sym=resu_rst[0]._sym, antisym=resu_rst[0]._antisym)
        for rst in resu_rst:
            resu._restrictions[rst._domain] = rst
        return resu

    def contract(self, *args):
        r""" 
        Contraction with another tensor field, on one or more indices.  
        
        INPUT:
            
        - ``pos1`` -- positions of the indices in ``self`` involved in the
          contraction; ``pos1`` must be a sequence of integers, with 0 standing
          for the first index position, 1 for the second one, etc. If ``pos1`` 
          is not provided, a single contraction on the last index position of
          ``self`` is assumed
        - ``other`` -- the tensor field to contract with
        - ``pos2`` -- positions of the indices in ``other`` involved in the
          contraction, with the same conventions as for ``pos1``. If ``pos2``
          is not provided, a single contraction on the first index position of
          ``other`` is assumed
          
        OUTPUT:
        
        - tensor field resulting from the contraction at the positions 
          ``pos1`` and ``pos2`` of ``self`` with ``other``
      
        EXAMPLES:
        
        Contractions of a type-(1,1) tensor field with a type-(2,0) one on 
        a 2-dimensional non-parallelizable manifold::
        
            sage: M = Manifold(2, 'M')
            sage: U = M.open_domain('U') ; V = M.open_domain('V') 
            sage: M.declare_union(U,V)   # M is the union of U and V
            sage: c_xy.<x,y> = U.chart() ; c_uv.<u,v> = V.chart()
            sage: transf = c_xy.transition_map(c_uv, (x+y, x-y), intersection_name='W', restrictions1= x>0, restrictions2= u+v>0)
            sage: inv = transf.inverse()
            sage: W = U.intersection(V)
            sage: eU = c_xy.frame() ; eV = c_uv.frame()
            sage: a = M.tensor_field(1,1, name='a')
            sage: a[eU,:] = [[1,x], [0,2]]
            sage: a.add_comp_by_continuation(eV, W, chart=c_uv)
            sage: b = M.tensor_field(2,0, name='b') 
            sage: b[eU,:] = [[y,-1], [x+y,2]]
            sage: b.add_comp_by_continuation(eV, W, chart=c_uv)
            sage: s = a.contract(b) ; s   # contraction on last index of a and first one of b
            tensor field of type (2,0) on the 2-dimensional manifold 'M'
        
        Check 1: components w.r.t. the manifold's default frame (eU)::

            sage: for i in M.irange():
            ....:     for j in M.irange():
            ....:         print bool(s[i,j] == sum(a[i,k]*b[k,j] for k in M.irange())), 
            ....:         
            True True True True

        Check 2: components w.r.t. frame eV::

            sage: for i in M.irange():
            ....:     for j in M.irange():
            ....:         print bool(s[eV,i,j] == sum(a[eV,i,k]*b[eV,k,j] for k in M.irange())),
            ....:         
            True True True True

        Instead of the explicit call to the method :meth:`contract`, one
        may use the index notation with Einstein convention (summation over
        repeated indices); it suffices to pass the indices as a string inside
        square brackets::

            sage: a['^i_k']*b['^kj'] == s
            True

        Indices not involved in the contraction may be replaced by dots::
        
            sage: a['^._k']*b['^k.'] == s
            True

        LaTeX notation may be used::
        
            sage: a['^{i}_{k}']*b['^{kj}'] == s
            True

        Contraction on the last index of a and last index of b::
        
            sage: s = a.contract(b, 1) ; s
            tensor field of type (2,0) on the 2-dimensional manifold 'M'
            sage: a['^i_k']*b['^jk'] == s
            True

        Contraction on the first index of b and the last index of a::
        
            sage: s = b.contract(0,a,1) ; s
            tensor field of type (2,0) on the 2-dimensional manifold 'M'
            sage: b['^ki']*a['^j_k'] == s
            True
        
        The domain of the result is the intersection of the two tensor fields 
        domain::
        
            sage: aU = a.restrict(U) ; bV = b.restrict(V)
            sage: s = aU.contract(b) ; s
            tensor field of type (2,0) on the open domain 'U' on the 2-dimensional manifold 'M'
            sage: s = a.contract(bV) ; s
            tensor field of type (2,0) on the open domain 'V' on the 2-dimensional manifold 'M'
            sage: s = aU.contract(bV) ; s
            tensor field of type (2,0) on the open domain 'W' on the 2-dimensional manifold 'M'
            sage: s0 = a.contract(b)
            sage: s == s0.restrict(W)
            True

        The contraction can be performed on more than one index: c being a type-(2,2) tensor,
        contracting the indices in positions 2 and 3 of c with respectively those in positions 0 and 1 of b is::

            sage: c = a*a ; c
            tensor field of type (2,2) on the 2-dimensional manifold 'M'
            sage: s = c.contract(2,3, b, 0,1) ; s 
            tensor field of type (2,0) on the 2-dimensional manifold 'M'
            sage: s == c['^.._kl']*b['^kl']  # the same double contraction in index notation
            True

        The symmetries are either conserved or destroyed by the contraction::
        
            sage: c = c.symmetrize(0,1).antisymmetrize(2,3)
            sage: c.symmetries()
            symmetry: (0, 1);  antisymmetry: (2, 3)
            sage: s = b.contract(0, c, 2) ; s
            tensor field of type (3,1) on the 2-dimensional manifold 'M'
            sage: s.symmetries()
            symmetry: (1, 2);  no antisymmetry

        Case of a scalar field result::
        
            sage: a = M.one_form('a')
            sage: a[eU,:] = [y, 1+x]
            sage: a.add_comp_by_continuation(eV, W, chart=c_uv)
            sage: b = M.vector_field('b')
            sage: b[eU,:] = [x, y^2]
            sage: b.add_comp_by_continuation(eV, W, chart=c_uv)
            sage: a.view(eU)
            a = y dx + (x + 1) dy
            sage: b.view(eU)
            b = x d/dx + y^2 d/dy
            sage: s = a.contract(b) ; s
            scalar field on the 2-dimensional manifold 'M'
            sage: s.view()
            M --> R
            on U: (x, y) |--> (x + 1)*y^2 + x*y
            on V: (u, v) |--> 1/8*u^3 - 1/8*u*v^2 + 1/8*v^3 + 1/2*u^2 - 1/8*(u^2 + 4*u)*v
            sage: s == a['_i']*b['^i'] # use of index notation
            True
            sage: s == b.contract(a)
            True

        Case of a vanishing scalar field result::
        
            sage: b = M.vector_field('b')
            sage: b[eU,:] = [1+x, -y]
            sage: b.add_comp_by_continuation(eV, W, chart=c_uv)
            sage: s = a.contract(b) ; s
            zero scalar field on the 2-dimensional manifold 'M'
            sage: s.view()
            M --> R
            on U: (x, y) |--> 0
            on V: (u, v) |--> 0

        """
        nargs = len(args)
        for i, arg in enumerate(args):
            if isinstance(arg, TensorField):
                other = arg
                it = i
                break
        else:
            raise TypeError("A tensor field must be provided in the " +
                            "argument list.")
        if it == 0:
            pos1 = (self._tensor_rank - 1,)
        else:
            pos1 = args[:it]
        if it == nargs-1:
            pos2 = (0,)
        else:
            pos2 = args[it+1:]
        ncontr = len(pos1) # number of contractions
        if len(pos2) != ncontr:
            raise TypeError("Different number of indices for the contraction.")
        if self._domain.is_subdomain(other._domain):
            if not self._ambient_domain.is_subdomain(other._ambient_domain):
                raise TypeError("Incompatible ambient domains for contraction.")
        elif other._domain.is_subdomain(self._domain):
            if not other._ambient_domain.is_subdomain(self._ambient_domain):
                raise TypeError("Incompatible ambient domains for contraction.")
        dom_resu = self._domain.intersection(other._domain)
        ambient_dom_resu = self._ambient_domain.intersection(
                                                         other._ambient_domain)
        self_r = self.restrict(dom_resu)
        other_r = other.restrict(dom_resu)
        k1, l1 = self._tensor_type
        k2, l2 = other._tensor_type
        tensor_type_resu = (k1+k2-ncontr, l1+l2-ncontr)
        if ambient_dom_resu.is_manifestly_parallelizable():
            # call of the FreeModuleTensor version:
            args = pos1 + (other_r,) + pos2 
            return FreeModuleTensor.contract(self_r, *args)
        com_dom = []
        for dom in self_r._restrictions:
            if dom in other_r._restrictions:
                com_dom.append(dom)
        resu_rst = []
        for dom in com_dom:
            self_rr = self_r._restrictions[dom]
            other_rr = other_r._restrictions[dom]
            args = pos1 + (other_rr,) + pos2
            resu_rst.append(self_rr.contract(*args))
        if tensor_type_resu == (0,0):
            # scalar field result
            resu = dom_resu.scalar_field()
            all_zero = True
            for rst in resu_rst:
                if rst == 0:
                    for chart in rst._domain._atlas:
                        resu._express[chart] = 0
                else:
                    all_zero = False
                    for chart, funct in rst._express.iteritems():
                        resu._express[chart] = funct
            if all_zero:
                resu = dom_resu._zero_scalar_field
        else:
            # tensor field result
            dest_map = self._vmodule._dest_map
            dest_map_resu = dest_map.restrict(dom_resu, 
                                              subcodomain=ambient_dom_resu)
            vmodule = dom_resu.vector_field_module(dest_map=dest_map_resu)
    
            resu = vmodule.tensor(tensor_type_resu, sym=resu_rst[0]._sym, 
                                  antisym=resu_rst[0]._antisym)
        for rst in resu_rst:
            resu._restrictions[rst._domain] = rst
        return resu

    def symmetrize(self, *pos):
        r"""
        Symmetrization over some arguments.
        
        INPUT:
        
        - ``pos`` -- (default: None) list of argument positions involved in the 
          symmetrization (with the convention position=0 for the first 
          argument); if none, the symmetrization is performed over all the 
          arguments
                  
        OUTPUT:
        
        - the symmetrized tensor field (instance of :class:`TensorField`)
        
        EXAMPLES:
        
        Symmetrization of a type-(0,2) tensor field on a 2-dimensional 
        non-parallelizable manifold::

            sage: M = Manifold(2, 'M')
            sage: U = M.open_domain('U') ; V = M.open_domain('V') 
            sage: M.declare_union(U,V)   # M is the union of U and V
            sage: c_xy.<x,y> = U.chart() ; c_uv.<u,v> = V.chart()
            sage: transf = c_xy.transition_map(c_uv, (x+y, x-y), intersection_name='W', restrictions1= x>0, restrictions2= u+v>0)
            sage: inv = transf.inverse()
            sage: W = U.intersection(V)
            sage: eU = c_xy.frame() ; eV = c_uv.frame()
            sage: a = M.tensor_field(0,2, name='a')
            sage: a[eU,:] = [[1,x], [2,y]]
            sage: a.add_comp_by_continuation(eV, W, chart=c_uv)
            sage: a[eV,:]
            [ 1/4*u + 3/4 -1/4*u + 3/4]
            [ 1/4*v - 1/4 -1/4*v - 1/4]
            sage: s = a.symmetrize() ; s
            field of symmetric bilinear forms on the 2-dimensional manifold 'M'
            sage: s[eU,:]
            [        1 1/2*x + 1]
            [1/2*x + 1         y]
            sage: s[eV,:]
            [         1/4*u + 3/4 -1/8*u + 1/8*v + 1/4]
            [-1/8*u + 1/8*v + 1/4         -1/4*v - 1/4]
            sage: s == a.symmetrize(0,1)  # explicit positions
            True

        See 
        :meth:`sage.tensor.modules.free_module_tensor.FreeModuleTensor.symmetrize`
        for more details and examples.

        """
        resu_rst = []
        for rst in self._restrictions.itervalues():
            resu_rst.append(rst.symmetrize(*pos))
        resu = self._vmodule.tensor(self._tensor_type, sym=resu_rst[0]._sym, 
                                    antisym=resu_rst[0]._antisym)
        for rst in resu_rst:
            resu._restrictions[rst._domain] = rst
        return resu

    def antisymmetrize(self, *pos):
        r"""
        Antisymmetrization over some arguments.
        
        INPUT:
        
        - ``pos`` -- (default: None) list of argument positions involved in the 
          antisymmetrization (with the convention position=0 for the first 
          argument); if none, the antisymmetrization is performed over all the 
          arguments
                  
        OUTPUT:
        
        - the antisymmetrized tensor field (instance of :class:`TensorField`)

        
        EXAMPLES:
        
        Antisymmetrization of a type-(0,2) tensor field on a 2-dimensional 
        non-parallelizable manifold::

            sage: M = Manifold(2, 'M')
            sage: U = M.open_domain('U') ; V = M.open_domain('V') 
            sage: M.declare_union(U,V)   # M is the union of U and V
            sage: c_xy.<x,y> = U.chart() ; c_uv.<u,v> = V.chart()
            sage: transf = c_xy.transition_map(c_uv, (x+y, x-y), intersection_name='W', restrictions1= x>0, restrictions2= u+v>0)
            sage: inv = transf.inverse()
            sage: W = U.intersection(V)
            sage: eU = c_xy.frame() ; eV = c_uv.frame()
            sage: a = M.tensor_field(0,2, name='a')
            sage: a[eU,:] = [[1,x], [2,y]]
            sage: a.add_comp_by_continuation(eV, W, chart=c_uv)
            sage: a[eV,:]
            [ 1/4*u + 3/4 -1/4*u + 3/4]
            [ 1/4*v - 1/4 -1/4*v - 1/4]
            sage: s = a.antisymmetrize() ; s
            2-form on the 2-dimensional manifold 'M'
            sage: s[eU,:]
            [         0  1/2*x - 1]
            [-1/2*x + 1          0]
            sage: s[eV,:]
            [                   0 -1/8*u - 1/8*v + 1/2]
            [ 1/8*u + 1/8*v - 1/2                    0]
            sage: s == a.antisymmetrize(0,1)  # explicit positions
            True
            sage: s == a.antisymmetrize(1,0)  # the order of positions does not matter
            True

        See 
        :meth:`sage.tensor.modules.free_module_tensor.FreeModuleTensor.antisymmetrize`
        for more details and examples.
        
        """
        resu_rst = []
        for rst in self._restrictions.itervalues():
            resu_rst.append(rst.antisymmetrize(*pos))
        resu = self._vmodule.tensor(self._tensor_type, sym=resu_rst[0]._sym, 
                                    antisym=resu_rst[0]._antisym)
        for rst in resu_rst:
            resu._restrictions[rst._domain] = rst
        return resu

    def lie_der(self, vector):
        r"""
        Compute the Lie derivative with respect to a vector field.
        
        The Lie derivative is stored in the dictionary 
        :attr:`_lie_derivatives`, so that there is no need to 
        recompute it at the next call if neither ``self`` nor ``vector``
        have been modified meanwhile. 
        
        INPUT:
        
        - ``vector`` -- vector field with respect to which the Lie derivative
          is to be taken
          
        OUTPUT:
        
        - the tensor field that is the Lie derivative of ``self`` with respect 
          to ``vector``
        
        EXAMPLES:
        
        see :meth:`TensorFieldParal.lie_der`
        
        """
        if vector._tensor_type != (1,0):
            raise TypeError("The argument must be a vector field.")
        if id(vector) not in self._lie_derivatives:
            # the computation must be performed:
            resu_rst = []
            for dom, rst in self._restrictions.iteritems():
                resu_rst.append(rst.lie_der(vector.restrict(dom)))
            resu = self._vmodule.tensor(self._tensor_type, 
                                        sym=resu_rst[0]._sym, 
                                        antisym=resu_rst[0]._antisym)
            for rst in resu_rst:
                resu._restrictions[rst._domain] = rst
            self._lie_derivatives[id(vector)] = (vector, resu)
            vector._lie_der_along_self[id(self)] = self
        return self._lie_derivatives[id(vector)][1]

    def at(self, point):
        r"""
        Value of the tensor field at a given point on the manifold.
        
        The returned object is a tensor on the tangent space at the given 
        point. 
        
        INPUT:
        
        - ``point`` -- (instance of
          :class:`~sage.geometry.manifolds.point.Point`) point `p` in the 
          domain of ``self`` (denoted `t` hereafter)
        
        OUTPUT:
        
        - instance of 
          :class:`~sage.tensor.modules.free_module_tensor.FreeModuleTensor`
          representing the tensor `t(p)` on the tangent vector space `T_p M` 
          (`M` being the manifold on which ``self`` is defined) 
          
        EXAMPLES:

        Tensor on a tangent space of a non-parallelizable 2-dimensional 
        manifold::
        
            sage: Manifold._clear_cache_() # for doctests only
            sage: M = Manifold(2, 'M')
            sage: U = M.open_domain('U') ; V = M.open_domain('V') 
            sage: M.declare_union(U,V)   # M is the union of U and V
            sage: c_xy.<x,y> = U.chart() ; c_uv.<u,v> = V.chart()
            sage: transf = c_xy.transition_map(c_uv, (x+y, x-y), intersection_name='W', restrictions1= x>0, restrictions2= u+v>0)
            sage: inv = transf.inverse()
            sage: W = U.intersection(V)
            sage: eU = c_xy.frame() ; eV = c_uv.frame()
            sage: a = M.tensor_field(1,1, name='a')
            sage: a[eU,:] = [[1+y,x], [0,x+y]]
            sage: a.add_comp_by_continuation(eV, W, chart=c_uv)
            sage: a.view(eU)
            a = (y + 1) d/dx*dx + x d/dx*dy + (x + y) d/dy*dy
            sage: a.view(eV)
            a = (u + 1/2) d/du*du + (-1/2*u - 1/2*v + 1/2) d/du*dv + 1/2 d/dv*du + (1/2*u - 1/2*v + 1/2) d/dv*dv
            sage: p = M.point((2,3), chart=c_xy, name='p')
            sage: ap = a.at(p) ; ap
            endomorphism a on the tangent space at point 'p' on 2-dimensional manifold 'M'
            sage: ap.parent()
            free module of type-(1,1) tensors on the tangent space at point 'p' on 2-dimensional manifold 'M'
            sage: ap.view()
            a = 4 d/dx*dx + 2 d/dx*dy + 5 d/dy*dy
            sage: ap.view(eV.at(p))
            a = 11/2 d/du*du - 3/2 d/du*dv + 1/2 d/dv*du + 7/2 d/dv*dv
            sage: p.coord(c_uv) # to check the above expression
            (5, -1)

        """
        if point not in self._domain:
            raise TypeError("The " + str(point) + " is not a point in the "
                            "domain of " + str(self) + ".")
        for dom, rst in self._restrictions.iteritems():
            if point in dom:
                return rst.at(point)

#******************************************************************************

class TensorFieldParal(FreeModuleTensor, TensorField):
    r"""
    Base class for tensor fields on an open set of a differentiable manifold, 
    with values on parallelizable open subset of a differentiable manifold. 
    
    An instance of this class is a tensor field along an open subset `U` 
    of some manifold `S` with values in a parallelizable open subset `V` 
    of a manifold `M`, via a differentiable mapping `\Phi: U \rightarrow V`. 
    The standard case of a tensor field *on* a manifold corresponds to `S=M`, 
    `U=V` and `\Phi = \mathrm{Id}`. Another common case is `\Phi` being an
    immersion.

    A tensor field of type `(k,\ell)` is a field `t` on `U`, so that at each 
    point `p\in U`, `t(p)` is a multilinear map of the type:

    .. MATH::

        t(p):\ \underbrace{T_q^*M\times\cdots\times T_q^*M}_{k\ \; \mbox{times}}
        \times \underbrace{T_q M\times\cdots\times T_q M}_{\ell\ \; \mbox{times}}
        \longrightarrow \RR
    
    where `T_q M` stands for the tangent space at the point `q=\Phi(p)` on the
    manifold `M` and `T_q^* M` for its dual vector space. The integer `k+\ell`
    is called the tensor rank. 
    
    INPUT:
    
    - ``vector_field_module`` -- free module `\mathcal{X}(U,\Phi)` of vector 
      fields along `U` with values on `\Phi(U)\subset V \subset M`
    - ``tensor_type`` -- pair (k,l) with k being the contravariant rank and l 
      the covariant rank
    - ``name`` -- (default: None) name given to the tensor field
    - ``latex_name`` -- (default: None) LaTeX symbol to denote the tensor field; 
      if none is provided, the LaTeX symbol is set to ``name``
    - ``sym`` -- (default: None) a symmetry or a list of symmetries among the 
      tensor arguments: each symmetry is described by a tuple containing 
      the positions of the involved arguments, with the convention position=0
      for the first argument. For instance:

      * sym=(0,1) for a symmetry between the 1st and 2nd arguments 
      * sym=[(0,2),(1,3,4)] for a symmetry between the 1st and 3rd
        arguments and a symmetry between the 2nd, 4th and 5th arguments.

    - ``antisym`` -- (default: None) antisymmetry or list of antisymmetries 
      among the arguments, with the same convention as for ``sym``. 


    EXAMPLES:

    A tensor field of type (2,0) on a 3-dimensional manifold::
    
        sage: M = Manifold(3, 'M')
        sage: c_xyz.<x,y,z> = M.chart()
        sage: t = M.tensor_field(2, 0, 'T') ; t
        tensor field 'T' of type (2,0) on the 3-dimensional manifold 'M'

    Tensor fields are considered as elements of a module over the ring 
    `C^\infty(M)` of scalar fields on `M`::
    
        sage: t.parent()
        free module T^(2,0)(M) of type-(2,0) tensors fields on the 3-dimensional manifold 'M'
        sage: t.parent().base_ring()
        algebra of scalar fields on the 3-dimensional manifold 'M'

    The components with respect to the manifold's default frame are set or read
    by means of square brackets::
    
        sage: e = M.vector_frame('e') ; M.set_default_frame(e)
        sage: for i in M.irange():
        ...       for j in M.irange():
        ...           t[i,j] = (i+1)**(j+1)
        ...
        sage: [[ t[i,j] for j in M.irange()] for i in M.irange()]
        [[1, 1, 1], [2, 4, 8], [3, 9, 27]]
    
    A shortcut for the above is using [:]::
    
        sage: t[:]
        [ 1  1  1]
        [ 2  4  8]
        [ 3  9 27]

    The components with respect to another frame are set via the method
    :meth:`set_comp` and read via the method :meth:`comp`; both return an 
    instance of :class:`~sage.tensor.modules.comp.Components`::
    
        sage: f = M.vector_frame('f')  # a new frame defined on M, in addition to e
        sage: t.set_comp(f)[0,0] = -3
        sage: t.comp(f)
        2-indices components w.r.t. vector frame (M, (f_0,f_1,f_2))
        sage: t.comp(f)[0,0]
        -3
        sage: t.comp(f)[:]  # the full list of components
        [-3  0  0]
        [ 0  0  0]
        [ 0  0  0]

    To avoid any insconstency between the various components, the method 
    :meth:`set_comp` deletes the components in other frames. 
    Accordingly, the components in the frame e have been deleted::
    
        sage: t._components
        {vector frame (M, (f_0,f_1,f_2)): 2-indices components w.r.t. vector frame (M, (f_0,f_1,f_2))}

    To keep the other components, one must use the method :meth:`add_comp`::
    
        sage: t = M.tensor_field(2, 0, 'T')  # Let us restart
        sage: t[0,0] = 2                     # sets the components in the frame e
        sage: # We now set the components in the frame f with add_comp:
        sage: t.add_comp(f)[0,0] = -3
        sage: # The components w.r.t. frame e have been kept: 
        sage: t._components
        {vector frame (M, (e_0,e_1,e_2)): 2-indices components w.r.t. vector frame (M, (e_0,e_1,e_2)), vector frame (M, (f_0,f_1,f_2)): 2-indices components w.r.t. vector frame (M, (f_0,f_1,f_2))}

    The basic properties of a tensor field are:: 

        sage: t.domain()
        3-dimensional manifold 'M'
        sage: t.tensor_type()
        (2, 0)

    Internally, the components w.r.t. various vector frames are stored in the
    dictionary :attr:`_components`::

        sage: t._components  # random (dictionary output)
        {vector frame (M, (e_0,e_1,e_2)): 2-indices components w.r.t. vector frame (M, (e_0,e_1,e_2)), vector frame (M, (f_0,f_1,f_2)): 2-indices components w.r.t. vector frame (M, (f_0,f_1,f_2))}

    Symmetries and antisymmetries are declared via the keywords ``sym`` and
    ``antisym``. For instance, a rank-6 covariant tensor that is symmetric with
    respect to its 1st and 3rd arguments and antisymmetric with respect to the 
    2nd, 5th and 6th arguments is set up as follows::
    
        sage: a = M.tensor_field(0, 6, 'T', sym=(0,2), antisym=(1,4,5))
        sage: a[0,0,1,0,1,2] = 3
        sage: a[1,0,0,0,1,2] # check of the symmetry
        3
        sage: a[0,1,1,0,0,2], a[0,1,1,0,2,0] # check of the antisymmetry
        (-3, 3)  

    Multiple symmetries or antisymmetries are allowed; they must then be 
    declared as a list. For instance, a rank-4 covariant tensor that is 
    antisymmetric with respect to its 1st and 2nd arguments and with respect to
    its 3rd and 4th argument must be declared as::
    
        sage: r = M.tensor_field(0, 4, 'T', antisym=[(0,1), (2,3)])
        sage: r[0,1,2,0] = 3
        sage: r[1,0,2,0] # first antisymmetry
        -3
        sage: r[0,1,0,2] # second antisymmetry
        -3
        sage: r[1,0,0,2] # both antisymmetries acting
        3
    
    Tensor fields of the same type can be added and subtracted::
    
        sage: a = M.tensor_field(2, 0)
        sage: a[0,0], a[0,1], a[0,2] = (1,2,3)
        sage: b = M.tensor_field(2, 0)
        sage: b[0,0], b[1,1], b[2,2], b[0,2] = (4,5,6,7)
        sage: s = a + 2*b ; s
        tensor field of type (2,0) on the 3-dimensional manifold 'M'
        sage: a[:], (2*b)[:], s[:]
        (
        [1 2 3]  [ 8  0 14]  [ 9  2 17]
        [0 0 0]  [ 0 10  0]  [ 0 10  0]
        [0 0 0], [ 0  0 12], [ 0  0 12]
        )
        sage: s = a - b ; s
        tensor field of type (2,0) on the 3-dimensional manifold 'M'
        sage: a[:], b[:], s[:]
        (
        [1 2 3]  [4 0 7]  [-3  2 -4]
        [0 0 0]  [0 5 0]  [ 0 -5  0]
        [0 0 0], [0 0 6], [ 0  0 -6]
        )

    Symmetries are preserved by the addition whenever it is possible::
    
        sage: a = M.tensor_field(2, 0, sym=(0,1))
        sage: a[0,0], a[0,1], a[0,2] = (1,2,3)
        sage: s = a + b
        sage: a[:], b[:], s[:]
        (
        [1 2 3]  [4 0 7]  [ 5  2 10]
        [2 0 0]  [0 5 0]  [ 2  5  0]
        [3 0 0], [0 0 6], [ 3  0  6]
        )
        sage: a.symmetries()
        symmetry: (0, 1);  no antisymmetry
        sage: b.symmetries()
        no symmetry;  no antisymmetry
        sage: s.symmetries()
        no symmetry;  no antisymmetry
        sage: # let us now make b symmetric:
        sage: b = M.tensor_field(2, 0, sym=(0,1))
        sage: b[0,0], b[1,1], b[2,2], b[0,2] = (4,5,6,7)
        sage: s = a + b
        sage: a[:], b[:], s[:]
        (
        [1 2 3]  [4 0 7]  [ 5  2 10]
        [2 0 0]  [0 5 0]  [ 2  5  0]
        [3 0 0], [7 0 6], [10  0  6]
        )
        sage: s.symmetries()  # s is symmetric because both a and b are
        symmetry: (0, 1);  no antisymmetry

    The tensor product is taken with the operator \*::
    
        sage: c = a*b ; c
        tensor field of type (4,0) on the 3-dimensional manifold 'M'
        sage: c.symmetries()  # since a and b are both symmetric, a*b has two symmetries:
        symmetries: [(0, 1), (2, 3)];  no antisymmetry

    The tensor product of two fully contravariant tensors is not symmetric in 
    general::
    
        sage: a*b == b*a
        False

    The tensor product of a fully contravariant tensor by a fully covariant one
    is symmetric::
    
        sage: d = M.diff_form(2)  # a fully covariant tensor field
        sage: d[0,1], d[0,2], d[1,2] = (3, 2, 1)
        sage: s = a*d ; s 
        tensor field of type (2,2) on the 3-dimensional manifold 'M'
        sage: s.symmetries()
        symmetry: (0, 1);  antisymmetry: (2, 3)
        sage: s1 = d*a ; s1 
        tensor field of type (2,2) on the 3-dimensional manifold 'M'
        sage: s1.symmetries()
        symmetry: (0, 1);  antisymmetry: (2, 3)
        sage: d*a == a*d
        True

    """
    def __init__(self, vector_field_module, tensor_type, name=None, 
                 latex_name=None, sym=None, antisym=None):
        FreeModuleTensor.__init__(self, vector_field_module, tensor_type,
                                  name=name, latex_name=latex_name,
                                  sym=sym, antisym=antisym)
        # TensorField attributes:
        self._vmodule = vector_field_module
        self._domain = vector_field_module._domain
        self._ambient_domain = vector_field_module._ambient_domain
        # NB: the TensorField attribute self._restrictions is considered as a 
        #     derived quantity in the present case (the primary attribute 
        #     being self._components, which is initialized by 
        #     FreeModuleTensor.__init__ ); accordingly self._restrictions is
        #     initialized by _init_derived() and cleared by _del_derived(). 
        # Initialization of derived quantities:
        self._init_derived() 

    def _repr_(self):
        r"""
        String representation of the object.
        """
        return TensorField._repr_(self)
        
    def _new_instance(self):
        r"""
        Create an instance of the same class as ``self`` on the same 
        vector field module, with the same tensor type and same symmetries
        
        """
        return self.__class__(self._fmodule, self._tensor_type, sym=self._sym, 
                                antisym=self._antisym)

    def _init_derived(self):
        r"""
        Initialize the derived quantities
        """
        FreeModuleTensor._init_derived(self) 
        TensorField._init_derived(self)
        self._restrictions = {} # dict. of restrictions of self on subdomains  
                                # of self._domain, with the subdomains as keys

    def _del_derived(self, del_restrictions=True):
        r"""
        Delete the derived quantities
        
        INPUT:
        
        - ``del_restrictions`` -- (default: True) determines whether the
          restrictions of ``self`` to subdomains are deleted. 
        
        """
        FreeModuleTensor._del_derived(self) 
        TensorField._del_derived(self)
        if del_restrictions:
            self._restrictions.clear()
        
    def set_comp(self, basis=None):
        r"""
        Return the components of the tensor field in a given vector frame 
        for assignment.
        
        The components with respect to other frames on the same domain are 
        deleted, in order to avoid any inconsistency. To keep them, use the 
        method :meth:`add_comp` instead.
        
        INPUT:
        
        - ``basis`` -- (default: None) vector frame in which the components are
          defined; if none is provided, the components are assumed to refer to 
          the tensor field domain's default frame.
         
        OUTPUT: 
        
        - components in the given frame, as an instance of the 
          class :class:`~sage.tensor.modules.comp.Components`; if such 
          components did not exist previously, they are created.  
        
        """
        if basis is None: 
            basis = self._fmodule._def_basis
        if basis._domain == self._domain:
            # Setting components on the tensor field domain:
            return FreeModuleTensor.set_comp(self, basis=basis)
        else:
            # Setting components on a subdomain:
            #
            # Creating or saving the restriction to the subdomain:
            rst = self.restrict(basis._domain, dest_map=basis._dest_map)
            # Deleting all the components on self._domain and the derived
            # quantities:
            self._components.clear()
            self._del_derived()
            # Restoring the restriction to the subdomain (which has been 
            # deleted by _del_derived):
            self._restrictions[basis._domain] = rst
            # The set_comp operation is performed on the subdomain:
            return rst.set_comp(basis=basis)

    def add_comp(self, basis=None):
        r"""
        Return the components of the tensor field in a given vector frame 
        for assignment.
        
        The components with respect to other frames on the same domain are 
        kept. To delete them them, use the method :meth:`set_comp` instead.
        
        INPUT:
        
        - ``basis`` -- (default: None) vector frame in which the components are
          defined; if none is provided, the components are assumed to refer to 
          the tensor field domain's default frame.
         
        OUTPUT: 
        
        - components in the given frame, as an instance of the 
          class :class:`~sage.tensor.modules.comp.Components`; if such 
          components did not exist previously, they are created.  

        """
        if basis is None: 
            basis = self._fmodule._def_basis
        if basis._domain == self._domain:
            # Adding components on the tensor field domain:
            return FreeModuleTensor.add_comp(self, basis=basis)
        else:
            # Adding components on a subdomain:
            # 
            # Creating or saving the restriction to the subdomain:
            rst = self.restrict(basis._domain, dest_map=basis._dest_map)
            # Deleting the derived quantities except for the restrictions to
            # subdomains:
            self._del_derived(del_restrictions=False)
            # The add_comp operation is performed on the subdomain:
            return rst.add_comp(basis=basis)

    def comp(self, basis=None, from_basis=None):
        r"""
        Return the components in a given vector frame.
        
        If the components are not known already, they are computed by the tensor
        change-of-basis formula from components in another vector frame. 
        
        INPUT:
        
        - ``basis`` -- (default: None) vector frame in which the components are 
          required; if none is provided, the components are assumed to refer to
          the tensor field domain's default frame
        - ``from_basis`` -- (default: None) vector frame from which the
          required components are computed, via the tensor change-of-basis 
          formula, if they are not known already in the basis ``basis``
          
        OUTPUT: 
        
        - components in the vector frame ``basis``, as an instance of the 
          class :class:`~sage.tensor.modules.comp.Components` 
 
        """
        if basis is None: 
            basis = self._fmodule._def_basis
        if basis._domain == self._domain:
            # components on the tensor field domain:
            return FreeModuleTensor.comp(self, basis=basis, 
                                         from_basis=from_basis)
        else:
            # components on a subdomain:
            rst = self.restrict(basis._domain, dest_map=basis._dest_map)
            return rst.comp(basis=basis, from_basis=from_basis)


    def common_coord_frame(self, other):
        r"""
        Find a common coordinate frame for the components of ``self`` and 
        ``other``. 
        
        In case of multiple common bases, the domain's default coordinate
        basis is privileged. 
        If the current components of ``self`` and ``other`` are all relative to
        different frames, a common frame is searched by performing a component
        transformation, via the transformations listed in 
        ``self._domain._frame_changes``, still privileging transformations to 
        the domain's default frame.
        
        INPUT:
        
        - ``other`` -- a tensor field (instance of :class:`TensorFieldParal`)
        
        OUPUT:
        
        - common coordinate frame; if no common basis is found, None is 
          returned. 
        
        """
        from vectorframe import CoordFrame
        # Compatibility checks:
        if not isinstance(other, TensorFieldParal):
            raise TypeError("The argument must be of type TensorFieldParal.")
        dom = self._domain
        def_frame = dom._def_frame
        #
        # 1/ Search for a common frame among the existing components, i.e. 
        #    without performing any component transformation. 
        #    -------------------------------------------------------------
        # 1a/ Direct search
        if def_frame in self._components and \
           def_frame in other._components and \
           isinstance(dom._def_frame, CoordFrame):
            return def_frame # the domain's default frame is privileged
        for frame1 in self._components:
            if frame1 in other._components and \
               isinstance(frame1, CoordFrame):
                return frame1
        # 1b/ Search involving subframes
        dom2 = other._domain
        for frame1 in self._components:
            if not isinstance(frame1, CoordFrame):
                continue
            for frame2 in other._components:
                if not isinstance(frame2, CoordFrame):
                    continue
                if frame2 in frame1._subframes:
                    self.comp(frame2)
                    return frame2
                if frame1 in frame2._subframes:
                    other.comp(frame1)
                    return frame1
        #
        # 2/ Search for a common frame via one component transformation
        #    ----------------------------------------------------------
        # If this point is reached, it is indeed necessary to perform at least 
        # one component transformation to get a common frame
        if isinstance(dom._def_frame, CoordFrame):
            if def_frame in self._components:
                for oframe in other._components:
                    if (oframe, def_frame) in dom._frame_changes:
                        other.comp(def_frame, from_basis=oframe)
                        return def_frame
            if def_frame in other._components:
                for sframe in self._components:
                    if (sframe, def_frame) in dom._frame_changes:
                        self.comp(def_frame, from_basis=sframe)
                        return def_frame
        # If this point is reached, then def_frame cannot be a common frame
        # via a single component transformation
        for sframe in self._components:
            if not instance(sframe, CoordFrame):
                continue
            for oframe in other._components:
                if not instance(oframe, CoordFrame):
                    continue
                if (oframe, sframe) in dom._frame_changes:
                    other.comp(sframe, from_basis=oframe)
                    return sframe
                if (sframe, oframe) in dom._frame_changes:
                    self.comp(oframe, from_basis=sframe)
                    return oframe
        #
        # 3/ Search for a common frame via two component transformations
        #    -----------------------------------------------------------
        # If this point is reached, it is indeed necessary to perform at least
        # two component transformations to get a common frame
        for sframe in self._components:
            for oframe in other._components:
                if (sframe, def_frame) in dom._frame_changes and \
                   (oframe, def_frame) in dom._frame_changes and \
                   isinstance(def_frame, CoordFrame):
                    self.comp(def_frame, from_basis=sframe)
                    other.comp(def_frame, from_basis=oframe)
                    return def_frame
                for frame in dom._frames:
                    if (sframe, frame) in dom._frame_changes and \
                       (oframe, frame) in dom._frame_changes and \
                       isinstance(frame, CoordFrame):
                        self.comp(frame, from_basis=sframe)
                        other.comp(frame, from_basis=oframe)
                        return frame
        #
        # If this point is reached, no common frame could be found, even at 
        # the price of component transformations:
        return None
    

    def lie_der(self, vector):
        r"""
        Compute the Lie derivative with respect to a vector field.
        
        The Lie derivative is stored in the dictionary 
        :attr:`_lie_derivatives`, so that there is no need to 
        recompute it at the next call if neither ``self`` nor ``vector``
        have been modified meanwhile. 
        
        INPUT:
        
        - ``vector`` -- vector field with respect to which the Lie derivative
          is to be taken
          
        OUTPUT:
        
        - the tensor field that is the Lie derivative of ``self`` with respect 
          to ``vector``
        
        EXAMPLES:
        
        Lie derivative of a vector::
        
            sage: M = Manifold(2, 'M', start_index=1)
            sage: c_xy.<x,y> = M.chart()
            sage: v = M.vector_field('v')
            sage: v[:] = (-y, x)
            sage: w = M.vector_field()
            sage: w[:] = (2*x+y, x*y)
            sage: w.lie_der(v)
            vector field on the 2-dimensional manifold 'M'
            sage: w.lie_der(v).view()
            ((x - 2)*y + x) d/dx + (x^2 - y^2 - 2*x - y) d/dy

        The Lie derivative is antisymmetric::
        
            sage: w.lie_der(v) == -v.lie_der(w)
            True
            
        For vectors, it coincides with the commutator::

            sage: f = M.scalar_field(x^3 + x*y^2)
            sage: w.lie_der(v)(f).view()
            M --> R
            (x, y) |--> -(x + 2)*y^3 + 3*x^3 - x*y^2 + 5*(x^3 - 2*x^2)*y
            sage: w.lie_der(v)(f) == v(w(f)) - w(v(f))  # rhs = commutator [v,w] acting on f
            True
            
        Lie derivative of a 1-form::
        
            sage: om = M.one_form()
            sage: om[:] = (y^2*sin(x), x^3*cos(y))
            sage: om.lie_der(v)
            1-form on the 2-dimensional manifold 'M'
            sage: om.lie_der(v).view()
            (-y^3*cos(x) + x^3*cos(y) + 2*x*y*sin(x)) dx + (-x^4*sin(y) - 3*x^2*y*cos(y) - y^2*sin(x)) dy
            
        Check of Cartan identity::
        
            sage: om.lie_der(v) == v.contract(0,om.exterior_der(),0) + (om(v)).exterior_der()
            True
        
        """
        if vector._tensor_type != (1,0):
            raise TypeError("The argument must be a vector field.")
        if id(vector) not in self._lie_derivatives:
            # A new computation must be performed
            #
            # 1/ Search for a common coordinate frame:
            coord_frame = self.common_coord_frame(vector)
            if coord_frame is None:
                raise TypeError("No common coordinate frame found.")
            chart = coord_frame._chart
            #
            # 2/ Component computation:
            tc = self._components[coord_frame]
            vc = vector._components[coord_frame]
            # the result has the same tensor type and same symmetries as self:
            resc = self._new_comp(coord_frame) 
            n_con = self._tensor_type[0]
            vf_module = vector._fmodule
            for ind in resc.non_redundant_index_generator():
                rsum = 0
                for i in vf_module.irange():
                    rsum += vc[[i]].function_chart(chart) * \
                           tc[[ind]].function_chart(chart).diff(i)
                # loop on contravariant indices:
                for k in range(n_con): 
                    for i in vf_module.irange():
                        indk = list(ind)
                        indk[k] = i  
                        rsum -= tc[[indk]].function_chart(chart) * \
                                vc[[ind[k]]].function_chart(chart).diff(i)
                # loop on covariant indices:
                for k in range(n_con, self._tensor_rank): 
                    for i in vf_module.irange():
                        indk = list(ind)
                        indk[k] = i  
                        rsum += tc[[indk]].function_chart(chart) * \
                                vc[[i]].function_chart(chart).diff(ind[k])
                resc[[ind]] = rsum.scalar_field()
            #
            # 3/ Final result (the tensor)
            res = vf_module.tensor_from_comp(self._tensor_type, resc)
            self._lie_derivatives[id(vector)] = (vector, res)
            vector._lie_der_along_self[id(self)] = self
        return self._lie_derivatives[id(vector)][1]

    def restrict(self, subdomain, dest_map=None):
        r"""
        Return the restriction of ``self`` to some subdomain.
        
        If such restriction has not been defined yet, it is constructed here.

        INPUT:
        
        - ``subdomain`` -- open subset `U` of ``self._domain`` (must be an 
          instance of :class:`~sage.geometry.manifolds.domain.OpenDomain`)
        - ``dest_map`` -- (default: None) destination map 
          `\Phi:\ U \rightarrow V`, where `V` is a subdomain of 
          ``self._codomain``
          (type: :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`)
          If None, the restriction of ``self._vmodule._dest_map`` to `U` is 
          used.
          
        OUTPUT:
        
        - instance of :class:`TensorFieldParal` representing the restriction.

        EXAMPLES:
        
        Restriction of a vector field defined on `\RR^2` to a disk::
        
            sage: M = Manifold(2, 'R^2')
            sage: c_cart.<x,y> = M.chart() # Cartesian coordinates on R^2
            sage: v = M.vector_field('v')
            sage: v[:] = [x+y, -1+x^2]
            sage: D = M.open_domain('D') # the unit open disc
            sage: c_cart_D = c_cart.restrict(D, x^2+y^2<1)
            sage: v_D = v.restrict(D) ; v_D
            vector field 'v' on the open domain 'D' on the 2-dimensional manifold 'R^2'
            sage: v_D.view()
            v = (x + y) d/dx + (x^2 - 1) d/dy
            
        The symbolic expressions of the components w.r.t. Cartesian coordinates 
        are equal::
        
            sage: bool( v_D[1].expr() == v[1].expr() )
            True
            
        but not the chart functions representing the components (they are 
        defined on different charts)::
        
            sage: v_D[1] == v[1]
            False
            
        nor the scalar fields representing the components (they are 
        defined on different open domains)::
        
            sage: v_D[[1]] == v[[1]]
            False

        The restriction of the vector field to its own domain is of course 
        itself::
        
            sage: v.restrict(M) is v
            True

        """
        if subdomain == self._domain:
            return self
        if subdomain not in self._restrictions:
            if not subdomain.is_subdomain(self._domain):
                raise ValueError("The provided domain is not a subdomain of " + 
                                 "the current field's domain.")
            if dest_map is None:
                dest_map = self._fmodule._dest_map.restrict(subdomain)
            elif not dest_map._codomain.is_subdomain(self._ambient_domain):
                raise ValueError("Argument dest_map not compatible with " + 
                                 "self._ambient_domain")
            #!# First one tries to derive the restriction from a tighter domain:
            #for dom, rst in self._restrictions.iteritems():
            #    if subdomain.is_subdomain(dom):
            #        self._restrictions[subdomain] = rst.restrict(subdomain)
            #        break
            # If this fails, the restriction is created from scratch:
            #else:
            smodule = subdomain.vector_field_module(dest_map=dest_map)
            resu = smodule.tensor(self._tensor_type, name=self._name, 
                                  latex_name=self._latex_name, sym=self._sym, 
                                  antisym=self._antisym, 
                                  specific_type=self.__class__)
            for frame in self._components:
                for sframe in subdomain._covering_frames:
                    if sframe in frame._subframes:
                        comp_store = self._components[frame]._comp
                        scomp = resu._new_comp(sframe)
                        scomp_store = scomp._comp
                        # the components of the restriction are evaluated 
                        # index by index:
                        for ind, value in comp_store.iteritems():
                            scomp_store[ind] = value.restrict(subdomain)
                        resu._components[sframe] = scomp
            self._restrictions[subdomain] = resu
        return self._restrictions[subdomain]

    def __call__(self, *args):
        r"""
        The tensor field acting on 1-forms and vector fields as a multilinear 
        map.
        
        INPUT:
        
        - ``*args`` -- list of k 1-forms and l vector fields, ``self`` 
          being a tensor of type (k,l). 
          
        """
        p = len(args)
        if p != self._tensor_rank:
            raise TypeError(str(self._tensor_rank) + 
                            " arguments must be provided.")
        # Domain of the result
        dom_resu = self._domain
        for arg in args:
            dom_resu = dom_resu.intersection(arg._domain)
        # Restriction to the result domain
        self_r = self.restrict(dom_resu)
        args_r = [args[i].restrict(dom_resu) for i in range(p)]
        # Call of the FreeModuleTensor version
        return FreeModuleTensor.__call__(self_r, *args_r)

    def contract(self, *args):
        r""" 
        Contraction with another tensor field, on one or more indices.  
        
        INPUT:
            
        - ``pos1`` -- positions of the indices in ``self`` involved in the
          contraction; ``pos1`` must be a sequence of integers, with 0 standing
          for the first index position, 1 for the second one, etc. If ``pos1`` 
          is not provided, a single contraction on the last index position of
          ``self`` is assumed
        - ``other`` -- the tensor field to contract with
        - ``pos2`` -- positions of the indices in ``other`` involved in the
          contraction, with the same conventions as for ``pos1``. If ``pos2``
          is not provided, a single contraction on the first index position of
          ``other`` is assumed
          
        OUTPUT:
        
        - tensor field resulting from the contraction at the positions 
          ``pos1`` and ``pos2`` of ``self`` with ``other``
        
        EXAMPLES:
        
        See :meth:`TensorField.contract`.
        
        """
        # This is to ensure the call to the TensorField version instead of
        # the FreeModuleTensor one
        return TensorField.contract(self, *args)

    def __mul__(self, other):
        r"""
        Tensor product. 
        """
        # This is to ensure the call to the TensorField version instead of
        # the FreeModuleTensor one
        return TensorField.__mul__(self, other)

    def at(self, point):
        r"""
        Value of the tensor field at a given point on the manifold.
        
        The returned object is a tensor on the tangent space at the given 
        point. 
        
        INPUT:
        
        - ``point`` -- (instance of
          :class:`~sage.geometry.manifolds.point.Point`) point `p` in the 
          domain of ``self`` (denoted `t` hereafter)
        
        OUTPUT:
        
        - instance of 
          :class:`~sage.tensor.modules.free_module_tensor.FreeModuleTensor`
          representing the tensor `t(p)` on the tangent vector space `T_p M` 
          (`M` being the manifold on which ``self`` is defined) 
          
        EXAMPLES:

        Vector in a tangent space of a 2-dimensional manifold::
        
            sage: Manifold._clear_cache_() # for doctests only
            sage: from sage.geometry.manifolds.tangentspace import TangentSpace # for doctests only
            sage: TangentSpace._clear_cache_() ; Manifold._clear_cache_() # for doctests only
            sage: M = Manifold(2, 'M')
            sage: c_xy.<x,y> = M.chart()
            sage: p = M.point((-2,3), name='p')
            sage: v = M.vector_field('v')
            sage: v[:] = [y, x^2] ; v.view()
            v = y d/dx + x^2 d/dy
            sage: vp = v.at(p) ; vp
            tangent vector v at point 'p' on 2-dimensional manifold 'M'
            sage: vp.parent()
            tangent space at point 'p' on 2-dimensional manifold 'M'
            sage: vp.view()
            v = 3 d/dx + 4 d/dy
            
        A 1-form gives birth to a linear form in the tangent space::
        
            sage: w = M.one_form('w')
            sage: w[:] = [-x, 1+y] ; w.view()
            w = -x dx + (y + 1) dy
            sage: wp = w.at(p) ; wp
            linear form w on the tangent space at point 'p' on 2-dimensional manifold 'M'
            sage: wp.parent()
            dual of the tangent space at point 'p' on 2-dimensional manifold 'M'
            sage: wp.view()
            w = 2 dx + 4 dy
        
        A field of endomorphisms yields an endomorphism in the tangent space::
         
            sage: t = M.endomorphism_field('t')
            sage: t[0,0], t[0,1], t[1,1] = 1+x, x*y, 1-y
            sage: t.view()
            t = (x + 1) d/dx*dx + x*y d/dx*dy + (-y + 1) d/dy*dy
            sage: tp = t.at(p) ; tp
            endomorphism t on the tangent space at point 'p' on 2-dimensional manifold 'M'
            sage: tp.parent()
            free module of type-(1,1) tensors on the tangent space at point 'p' on 2-dimensional manifold 'M'
            sage: tp.view()
            t = -d/dx*dx - 6 d/dx*dy - 2 d/dy*dy

        A 2-form yields an alternating form of degree 2 in the tangent space::

            sage: a = M.diff_form(2, name='a')
            sage: a[0,1] = x*y
            sage: a.view()
            a = x*y dx/\dy
            sage: ap = a.at(p) ; ap
            alternating form a of degree 2 on the tangent space at point 'p' on 2-dimensional manifold 'M'
            sage: ap.parent()
            free module of type-(0,2) tensors on the tangent space at point 'p' on 2-dimensional manifold 'M'
            sage: ap.view()
            a = -6 dx/\dy

        """
        if point not in self._domain:
            raise TypeError("The " + str(point) + " is not a point in the "
                            "domain of " + str(self) + ".")
        ts = point.tangent_space()
        resu = ts.tensor(self._tensor_type, name=self._name, 
                         latex_name=self._latex_name, sym=self._sym, 
                         antisym=self._antisym)
        for frame, comp in self._components.iteritems():
            comp_resu = resu.add_comp(frame.at(point))
            for ind, val in comp._comp.iteritems():
                comp_resu._comp[ind] = val(point) 
        return resu

            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
