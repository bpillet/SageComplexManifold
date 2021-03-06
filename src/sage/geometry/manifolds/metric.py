r"""
Pseudo-Riemannian metrics

The class :class:`Metric` implements pseudo-Riemannian metrics on 
differentiable manifolds over `\RR`. 

Derived classes of :class:`Metric` are 

* :class:`RiemannMetric` for Riemannian metrics 
* :class:`LorentzMetric` for Lorentzian metrics 

Other derived classes are devoted to the special cases of metrics with
values on a parallelizable open subset of a differentiable manifold:

* :class:`MetricParal`

  * :class:`RiemannMetricParal`
  * :class:`LorentzMetricParal`

See the documentation of class :class:`Metric` for an introduction. 

AUTHORS:

- Eric Gourgoulhon, Michal Bejger (2013, 2014) : initial version

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

from tensorfield import TensorField, TensorFieldParal
from sage.rings.integer import Integer

class Metric(TensorField):
    r"""
    Base class for pseudo-Riemannian metrics with values on an
    open subset of a differentiable manifold. 

    An instance of this class is a field of nondegenerate symmetric bilinear 
    forms (metric field) along an open subset `U` of some manifold `S` with 
    values in an open subset `V` of a manifold `M`, via a 
    differentiable mapping `\Phi: U \rightarrow V`. 
    The standard case of a metric field *on* a manifold corresponds to `S=M`, 
    `U=V` and `\Phi = \mathrm{Id}`. Another common case is `\Phi` being an
    immersion.

    If `V` is parallelizable, the class :class:`MetricParal` should be
    used instead. 

    A *metric* `g` is a field on `U`, so that at each 
    point `p\in U`, `g(p)` is a bilinear map of the type:

    .. MATH::

        g(p):\ T_q M\times T_q M  \longrightarrow \RR
    
    where `T_q M` stands for the tangent space at the point `q=\Phi(p)` on the
    manifold `M`, such that `g(p)` is symmetric: 
    `\forall (u,v)\in  T_q M\times T_q M, \ g(p)(v,u) = g(p)(u,v)` 
    and nondegenerate: 
    `(\forall v\in T_q M,\ \ g(p)(u,v) = 0) \Longrightarrow u=0`. 
    
    INPUT:
    
    - ``vector_field_module`` -- module `\mathcal{X}(U,\Phi)` of vector 
      fields along `U` with values on `\Phi(U)\subset V \subset M`
    - ``name`` -- name given to the metric
    - ``signature`` -- (default: None) signature `S` of the metric as a single 
      integer: `S = n_+ - n_-`, where `n_+` (resp. `n_-`) is the number of 
      positive terms (resp. number of negative terms) in any diagonal writing 
      of the metric components; if ``signature`` is not provided, `S` is set to 
      the dimension of manifold `M` (Riemannian signature)
    - ``latex_name`` -- (default: None) LaTeX symbol to denote the metric; if
      none, it is formed from ``name``      

    EXAMPLES:
    
    Standard metric on the sphere `S^2`::
    
        sage: Manifold._clear_cache_() # for doctests only
        sage: M = Manifold(2, 'S^2', start_index=1)
        sage: # The two open domains covered by stereographic coordinates (North and South): 
        sage: U = M.open_domain('U') ; V = M.open_domain('V') 
        sage: M.declare_union(U,V)   # S^2 is the union of U and V
        sage: c_xy.<x,y> = U.chart() ; c_uv.<u,v> = V.chart() # stereographic coord 
        sage: transf = c_xy.transition_map(c_uv, (x/(x^2+y^2), y/(x^2+y^2)), intersection_name='W', restrictions1= x^2+y^2!=0, restrictions2= u^2+v^2!=0)
        sage: inv = transf.inverse()
        sage: W = U.intersection(V) # The complement of the two poles
        sage: eU = c_xy.frame() ; eV = c_uv.frame()
        sage: c_xyW = c_xy.restrict(W) ; c_uvW = c_uv.restrict(W)
        sage: eUW = c_xyW.frame() ; eVW = c_uvW.frame()
        sage: g = M.metric('g') ; g
        pseudo-Riemannian metric 'g' on the 2-dimensional manifold 'S^2'

    The metric is considered as a tensor field of type (0,2) on `S^2`::
    
        sage: g.parent()
        module T^(0,2)(S^2) of type-(0,2) tensors fields on the 2-dimensional manifold 'S^2'

    We define g by its components on domain U (factorizing them to have a nicer
    view)::
    
        sage: g[eU,1,1], g[eU,2,2] = 4/(1+x^2+y^2)^2, 4/(1+x^2+y^2)^2
        sage: g.view(eU) # the components of the output are expanded 
        g = 4/(x^4 + y^4 + 2*(x^2 + 1)*y^2 + 2*x^2 + 1) dx*dx + 4/(x^4 + y^4 + 2*(x^2 + 1)*y^2 + 2*x^2 + 1) dy*dy
        sage: g[eU,1,1].factor() ; g[eU,2,2].factor() # we enforce the factorization
        4/(x^2 + y^2 + 1)^2
        4/(x^2 + y^2 + 1)^2
        sage: g.view(eU) # the output looks nicer
        g = 4/(x^2 + y^2 + 1)^2 dx*dx + 4/(x^2 + y^2 + 1)^2 dy*dy

    A matrix view of the components::
    
        sage: g[eU,:]
        [4/(x^2 + y^2 + 1)^2                   0]
        [                  0 4/(x^2 + y^2 + 1)^2]

    The components of g on domain V expressed in terms of (u,v) coordinates are
    similar to those on domain U expressed in (x,y) coordinates, as we can 
    check explicitely by asking for the component transformation on the 
    common subdomain W::
    
        sage: g.view(eVW, c_uvW)
        g = 4/(u^4 + v^4 + 2*(u^2 + 1)*v^2 + 2*u^2 + 1) du*du + 4/(u^4 + v^4 + 2*(u^2 + 1)*v^2 + 2*u^2 + 1) dv*dv

    Therefore, we set::
    
        sage: g[eV,1,1], g[eV,2,2] = 4/(1+u^2+v^2)^2, 4/(1+u^2+v^2)^2
        sage: g[eV,1,1].factor() ; g[eV,2,2].factor()
        4/(u^2 + v^2 + 1)^2
        4/(u^2 + v^2 + 1)^2
        sage: g.view(eV)
        g = 4/(u^2 + v^2 + 1)^2 du*du + 4/(u^2 + v^2 + 1)^2 dv*dv

    At this stage, the metric is fully defined on the whole sphere. Its 
    restriction to some subdomain is itself a metric (by default, it bears the
    same symbol)::
    
        sage: g.restrict(U)
        pseudo-Riemannian metric 'g' on the open domain 'U' on the 2-dimensional manifold 'S^2'
        sage: g.restrict(U).parent()
        free module T^(0,2)(U) of type-(0,2) tensors fields on the open domain 'U' on the 2-dimensional manifold 'S^2'

    The parent of `g|_U` is a free module because is `U` is a parallelizable 
    domain, contrary to `S^2`. Actually, `g` and `g|_U` have different Python
    type::
    
        sage: type(g)
        <class 'sage.geometry.manifolds.metric.Metric'>
        sage: type(g.restrict(U))
        <class 'sage.geometry.manifolds.metric.MetricParal'>

    As a field of bilinear forms, the metric acts on pairs of tensor fields,
    yielding a scalar field::
    
        sage: a = M.vector_field('a')
        sage: a[eU,:] = [x, 2+y]
        sage: a.add_comp_by_continuation(eV, W, chart=c_uv)
        sage: b = M.vector_field('b')
        sage: b[eU,:] = [-y, x]
        sage: b.add_comp_by_continuation(eV, W, chart=c_uv)
        sage: s = g(a,b) ; s
        scalar field 'g(a,b)' on the 2-dimensional manifold 'S^2'
        sage: s.view()
        g(a,b): S^2 --> R
        on U: (x, y) |--> 8*x/(x^4 + y^4 + 2*(x^2 + 1)*y^2 + 2*x^2 + 1)
        on V: (u, v) |--> 8*(u^3 + u*v^2)/(u^4 + v^4 + 2*(u^2 + 1)*v^2 + 2*u^2 + 1)

    The inverse metric is::
    
        sage: ginv = g.inverse() ; ginv
        tensor field 'inv_g' of type (2,0) on the 2-dimensional manifold 'S^2'
        sage: ginv.parent()
        module T^(2,0)(S^2) of type-(2,0) tensors fields on the 2-dimensional manifold 'S^2'
        sage: latex(ginv)
        g^{-1}
        sage: ginv.view(eU) # again the components are expanded
        inv_g = (1/4*x^4 + 1/4*y^4 + 1/2*(x^2 + 1)*y^2 + 1/2*x^2 + 1/4) d/dx*d/dx + (1/4*x^4 + 1/4*y^4 + 1/2*(x^2 + 1)*y^2 + 1/2*x^2 + 1/4) d/dy*d/dy
        sage: ginv.view(eV)
        inv_g = (1/4*u^4 + 1/4*v^4 + 1/2*(u^2 + 1)*v^2 + 1/2*u^2 + 1/4) d/du*d/du + (1/4*u^4 + 1/4*v^4 + 1/2*(u^2 + 1)*v^2 + 1/2*u^2 + 1/4) d/dv*d/dv

    We have::
    
        sage: ginv.restrict(U) is g.restrict(U).inverse()
        True
        sage: ginv.restrict(V) is g.restrict(V).inverse()
        True
        sage: ginv.restrict(W) is g.restrict(W).inverse()
        True
    
    The volume form (Levi-Civita tensor) associated with `g`::
    
        sage: eps = g.volume_form() ; eps
        2-form 'eps_g' on the 2-dimensional manifold 'S^2'
        sage: eps.view(eU)
        eps_g = 4/(x^4 + y^4 + 2*(x^2 + 1)*y^2 + 2*x^2 + 1) dx/\dy
        sage: eps.view(eV)
        eps_g = 4/(u^4 + v^4 + 2*(u^2 + 1)*v^2 + 2*u^2 + 1) du/\dv

    The unique non-trivial component of the volume form is nothing but the
    square root of the determinant of g in the corresponding frame::
    
        sage: eps[[eU,1,2]] == g.sqrt_abs_det(eU)
        True
        sage: eps[[eV,1,2]] == g.sqrt_abs_det(eV)
        True
        
    The Levi-Civita connection associated with the metric `g`::
    
        sage: nabla = g.connection() ; nabla
        Levi-Civita connection 'nabla_g' associated with the pseudo-Riemannian metric 'g' on the 2-dimensional manifold 'S^2'
        sage: latex(nabla)
        \nabla_{g}
    
    The Christoffel symbols `\Gamma^i_{\ \, jk}` associated with some coordinates::
    
        sage: g.christoffel_symbols(c_xy)
        3-indices components w.r.t. coordinate frame (U, (d/dx,d/dy)), with symmetry on the index positions (1, 2)
        sage: g.christoffel_symbols(c_xy)[:]
        [[[-2*x/(x^2 + y^2 + 1), -2*y/(x^2 + y^2 + 1)],
          [-2*y/(x^2 + y^2 + 1), 2*x/(x^2 + y^2 + 1)]],
         [[2*y/(x^2 + y^2 + 1), -2*x/(x^2 + y^2 + 1)],
          [-2*x/(x^2 + y^2 + 1), -2*y/(x^2 + y^2 + 1)]]]
        sage: g.christoffel_symbols(c_uv)[:]
        [[[-2*u/(u^2 + v^2 + 1), -2*v/(u^2 + v^2 + 1)],
          [-2*v/(u^2 + v^2 + 1), 2*u/(u^2 + v^2 + 1)]],
         [[2*v/(u^2 + v^2 + 1), -2*u/(u^2 + v^2 + 1)],
          [-2*u/(u^2 + v^2 + 1), -2*v/(u^2 + v^2 + 1)]]]

    The Christoffel symbols are nothing but the connection coefficients w.r.t.
    the coordinate frame::
    
        sage: g.christoffel_symbols(c_xy) is nabla.coef(c_xy.frame())
        True
        sage: g.christoffel_symbols(c_uv) is nabla.coef(c_uv.frame())
        True

    Test that nabla is the connection compatible with `g`::
    
        sage: t = nabla(g) ; t
        tensor field 'nabla_g g' of type (0,3) on the 2-dimensional manifold 'S^2'
        sage: t.view(eU)
        nabla_g g = 0
        sage: t.view(eV)
        nabla_g g = 0
        sage: t == 0
        True
    
    The Riemann curvature tensor of `g`::
    
        sage: riem = g.riemann() ; riem
        tensor field 'Riem(g)' of type (1,3) on the 2-dimensional manifold 'S^2'
        sage: riem.view(eU)
        Riem(g) = 4/(x^4 + y^4 + 2*(x^2 + 1)*y^2 + 2*x^2 + 1) d/dx*dy*dx*dy - 4/(x^4 + y^4 + 2*(x^2 + 1)*y^2 + 2*x^2 + 1) d/dx*dy*dy*dx - 4/(x^4 + y^4 + 2*(x^2 + 1)*y^2 + 2*x^2 + 1) d/dy*dx*dx*dy + 4/(x^4 + y^4 + 2*(x^2 + 1)*y^2 + 2*x^2 + 1) d/dy*dx*dy*dx
        sage: riem.view(eV)
        Riem(g) = 4/(u^4 + v^4 + 2*(u^2 + 1)*v^2 + 2*u^2 + 1) d/du*dv*du*dv - 4/(u^4 + v^4 + 2*(u^2 + 1)*v^2 + 2*u^2 + 1) d/du*dv*dv*du - 4/(u^4 + v^4 + 2*(u^2 + 1)*v^2 + 2*u^2 + 1) d/dv*du*du*dv + 4/(u^4 + v^4 + 2*(u^2 + 1)*v^2 + 2*u^2 + 1) d/dv*du*dv*du

    The Ricci tensor of `g`::

        sage: ric = g.ricci() ; ric
        field of symmetric bilinear forms 'Ric(g)' on the 2-dimensional manifold 'S^2'
        sage: ric.view(eU)
        Ric(g) = 4/(x^4 + y^4 + 2*(x^2 + 1)*y^2 + 2*x^2 + 1) dx*dx + 4/(x^4 + y^4 + 2*(x^2 + 1)*y^2 + 2*x^2 + 1) dy*dy
        sage: ric.view(eV)
        Ric(g) = 4/(u^4 + v^4 + 2*(u^2 + 1)*v^2 + 2*u^2 + 1) du*du + 4/(u^4 + v^4 + 2*(u^2 + 1)*v^2 + 2*u^2 + 1) dv*dv
        sage: ric == g
        True

    The Ricci scalar of `g`::
    
        sage: r = g.ricci_scalar() ; r
        scalar field 'r(g)' on the 2-dimensional manifold 'S^2'
        sage: r.view()
        r(g): S^2 --> R
        on U: (x, y) |--> 2
        on V: (u, v) |--> 2
    
    In dimension 2, the Riemann tensor can be expressed entirely in terms of
    the Ricci scalar `r`:

    .. MATH::
        
        R^i_{\ \, jlk} = \frac{r}{2} \left( \delta^i_{\ \, k} g_{jl}
            - \delta^i_{\ \, l} g_{jk} \right)
    
    This formula can be checked here, with the r.h.s. rewritten as 
    `-r g_{j[k} \delta^i_{\ \, l]}`::
        
        sage: delta = M.tangent_identity_field()
        sage: riem == - r*(g*delta).antisymmetrize(2,3)
        True

    """
    def __init__(self, vector_field_module, name, signature=None, 
                 latex_name=None):
        TensorField.__init__(self, vector_field_module, (0,2), 
                             name=name, latex_name=latex_name, sym=(0,1))
        # signature:
        ndim = self._ambient_domain._manifold._dim
        if signature is None:
            signature = ndim
        else:
            if not isinstance(signature, (int, Integer)):
                raise TypeError("The metric signature must be an integer.")
            if (signature < - ndim) or (signature > ndim):
                raise ValueError("Metric signature out of range.")
            if (signature+ndim)%2 == 1:
                if ndim%2 == 0:
                    raise ValueError("The metric signature must be even.")
                else:
                    raise ValueError("The metric signature must be odd.")
        self._signature = signature
        # the pair (n_+, n_-):
        self._signature_pm = ((ndim+signature)/2, (ndim-signature)/2)
        self._indic_signat = 1 - 2*(self._signature_pm[1]%2)  # (-1)^n_-
        Metric._init_derived(self)

    def _repr_(self):
        r"""
        String representation of the object.
        """
        description = "pseudo-Riemannian metric '%s' " % self._name
        return self._final_repr(description)

    def _new_instance(self):
        r"""
        Create an instance of the same class as ``self`` with the same 
        signature.
        
        """
        return self.__class__(self._vmodule, 'unnamed metric', 
                              signature=self._signature, 
                              latex_name=r'\mbox{unnamed metric}')

    def _init_derived(self):
        r"""
        Initialize the derived quantities
        """
        # Initialization of quantities pertaining to the mother class:
        TensorField._init_derived(self) 
        # inverse metric:
        inv_name = 'inv_' + self._name
        inv_latex_name = self._latex_name + r'^{-1}'
        self._inverse = self._vmodule.tensor((2,0), name=inv_name, 
                                             latex_name=inv_latex_name, 
                                             sym=(0,1))
        self._connection = None  # Levi-Civita connection (not set yet)
        self._ricci_scalar = None # Ricci scalar (not set yet)
        self._weyl = None # Weyl tensor (not set yet)
        self._determinants = {} # determinants in various frames
        self._sqrt_abs_dets = {} # sqrt(abs(det g)) in various frames
        self._vol_forms = [] # volume form and associated tensors

    def _del_derived(self):
        r"""
        Delete the derived quantities
        """
        # First the derived quantities from the mother class are deleted:
        TensorField._del_derived(self)
        # The inverse metric is cleared: 
        self._del_inverse()
        # The connection, Ricci scalar and Weyl tensor are reset to None:
        self._connection = None
        self._ricci_scalar = None
        self._weyl = None
        # The dictionary of determinants over the various frames is cleared:
        self._determinants.clear()
        self._sqrt_abs_dets.clear()
        # The volume form and the associated tensors is deleted:
        del self._vol_forms[:]

    def _del_inverse(self):
        r"""
        Delete the inverse metric
        """
        self._inverse._restrictions.clear()
        self._inverse._del_derived()

    def signature(self):
        r"""
        Signature of the metric. 
        
        OUTPUT:

        - signature `S` of the metric, defined as the integer 
          `S = n_+ - n_-`, where `n_+` (resp. `n_-`) is the number of 
          positive terms (resp. number of negative terms) in any diagonal 
          writing of the metric components
        
        EXAMPLES:
        
        Signatures on a 2-dimensional manifold::
        
            sage: M = Manifold(2, 'M')
            sage: X.<x,y> = M.chart()
            sage: g = M.metric('g') # if not specified, the signature is Riemannian
            sage: g.signature() 
            2
            sage: h = M.metric('h', signature=0)
            sage: h.signature()
            0

        """
        return self._signature

    def restrict(self, subdomain, dest_map=None):
        r"""
        Return the restriction of the metric to some subdomain.
        
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
        
        - instance of :class:`Metric` representing the restriction.

        EXAMPLES:
        
        See the top documentation of :class:`Metric`. 
        
        """
        if subdomain == self._domain:
            return self
        if subdomain not in self._restrictions:
            # Construct the restriction at the tensor field level:
            resu = TensorField.restrict(self, subdomain, dest_map=dest_map)
            # the type is correctly handled by TensorField.restrict, i.e.
            # resu is of type self.__class__, but the signature is not handled 
            # by TensorField.restrict; we have to set it here:
            resu._signature = self._signature
            resu._signature_pm = self._signature_pm
            resu._indic_signat = self._indic_signat
            # Restrictions of derived quantities:
            resu._inverse = self.inverse().restrict(subdomain)
            if self._connection is not None:
                resu._connection = self._connection.restrict(subdomain)
            if self._ricci_scalar is not None:
                resu._ricci_scalar = self._ricci_scalar.restrict(subdomain)
            if self._weyl is not None:
                resu._weyl = self._weyl.restrict(subdomain)
            if self._vol_forms != []:
                for eps in self._vol_forms:
                    resu._vol_forms.append(eps.restrict(subdomain))
            # NB: no initialization of resu._determinants nor 
            # resu._sqrt_abs_dets
            # The restriction is ready:
            self._restrictions[subdomain] = resu
        return self._restrictions[subdomain]

    def set(self, symbiform):
        r"""
        Defines the metric from a field of symmetric bilinear forms
        
        INPUT:
    
        - ``symbiform`` -- instance of
          :class:`~sage.geometry.manifolds.tensorfield.TensorField` 
          representing a field of symmetric bilinear forms

        EXAMPLE:
        
        Metric defined from a field of symmetric bilinear forms on a 
        non-parallelizable 2-dimensional manifold::
    
            sage: Manifold._clear_cache_() # for doctests only
            sage: M = Manifold(2, 'M')
            sage: U = M.open_domain('U') ; V = M.open_domain('V') 
            sage: M.declare_union(U,V)   # M is the union of U and V
            sage: c_xy.<x,y> = U.chart() ; c_uv.<u,v> = V.chart()
            sage: transf = c_xy.transition_map(c_uv, (x+y, x-y), intersection_name='W', restrictions1= x>0, restrictions2= u+v>0)
            sage: inv = transf.inverse()
            sage: W = U.intersection(V)
            sage: eU = c_xy.frame() ; eV = c_uv.frame()
            sage: h = M.sym_bilin_form_field(name='h')
            sage: h[eU,0,0], h[eU,0,1], h[eU,1,1] = 1+x, x*y, 1-y
            sage: h.add_comp_by_continuation(eV, W, c_uv)
            sage: h.view(eU)
            h = (x + 1) dx*dx + x*y dx*dy + x*y dy*dx + (-y + 1) dy*dy
            sage: h.view(eV)
            h = (1/8*u^2 - 1/8*v^2 + 1/4*v + 1/2) du*du + 1/4*u du*dv + 1/4*u dv*du + (-1/8*u^2 + 1/8*v^2 + 1/4*v + 1/2) dv*dv
            sage: g = M.metric('g')
            sage: g.set(h)
            sage: g.view(eU)
            g = (x + 1) dx*dx + x*y dx*dy + x*y dy*dx + (-y + 1) dy*dy
            sage: g.view(eV)
            g = (1/8*u^2 - 1/8*v^2 + 1/4*v + 1/2) du*du + 1/4*u du*dv + 1/4*u dv*du + (-1/8*u^2 + 1/8*v^2 + 1/4*v + 1/2) dv*dv

        """
        if not isinstance(symbiform, TensorField):
            raise TypeError("The argument must be a tensor field.")
        if symbiform._tensor_type != (0,2):
            raise TypeError("The argument must be of tensor type (0,2).")
        if symbiform._sym != [(0,1)]:
            raise TypeError("The argument must be symmetric.")
        if not symbiform._domain.is_subdomain(self._domain):
            raise TypeError("The symmetric bilinear form is not defined " + 
                            "on the metric domain.")
        self._del_derived()
        self._restrictions.clear()
        if isinstance(symbiform, TensorFieldParal):
            rst = self.restrict(symbiform._domain)
            rst.set(symbiform)
        else:
            for dom, symbiform_rst in symbiform._restrictions.iteritems():
                rst = self.restrict(dom)
                rst.set(symbiform_rst)
    

    def inverse(self):
        r"""
        Return the inverse metric.
        
        OUTPUT:
        
        - instance of
          :class:`~sage.geometry.geometry.tensorfield.TensorField`
          with tensor_type = (2,0) representing the inverse metric
        
        EXAMPLES:
        
        See the top documentation of :class:`Metric`. 

        """
        # Is the inverse metric up to date ?
        for dom, rst in self._restrictions.iteritems():
            self._inverse._restrictions[dom] = rst.inverse() # forces the 
                                                    # update of the restriction
        return self._inverse

    def connection(self, name=None, latex_name=None):
        r"""
        Return the unique torsion-free affine connection compatible with 
        ``self``.
        
        This is the so-called Levi-Civita connection.
        
        INPUT:
        
        - ``name`` -- (default: None) name given to the Levi-Civita connection; 
          if none, it is formed from the metric name
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the 
          Levi-Civita connection; if none, it is formed from the symbol 
          `\nabla` and the metric symbol
          
        OUTPUT:
        
        - the Levi-Civita connection, as an instance of 
          :class:`~sage.geometry.manifolds.connection.LeviCivitaConnection`. 
          
        EXAMPLES:
        
        Levi-Civitation connection associated with the Euclidean metric on 
        `\RR^3`::
        
            sage: M = Manifold(3, 'R^3', start_index=1)
            sage: # Let us use spherical coordinates on R^3:
            sage: U = M.open_domain('U') # the complement of the half-plane (y=0, x>=0)
            sage: c_spher.<r,th,ph> = U.chart(r'r:(0,+oo) th:(0,pi):\theta ph:(0,2*pi):\phi')
            sage: g = U.metric('g')
            sage: g[1,1], g[2,2], g[3,3] = 1, r^2 , (r*sin(th))^2  # the Euclidean metric
            sage: g.connection()
            Levi-Civita connection 'nabla_g' associated with the pseudo-Riemannian metric 'g' on the open domain 'U' on the 3-dimensional manifold 'R^3'
            sage: g.connection()[:]  # Christoffel symbols w.r.t. spherical coordinates
            [[[0, 0, 0], [0, -r, 0], [0, 0, -r*sin(th)^2]], 
            [[0, 1/r, 0], [1/r, 0, 0], [0, 0, -cos(th)*sin(th)]], 
            [[0, 0, 1/r], [0, 0, cos(th)/sin(th)], [1/r, cos(th)/sin(th), 0]]]

        Test of compatibility with the metric::
        
            sage: Dg = g.connection()(g) ; Dg
            tensor field 'nabla_g g' of type (0,3) on the open domain 'U' on the 3-dimensional manifold 'R^3'
            sage: Dg == 0
            True
            sage: Dig = g.connection()(g.inverse()) ; Dig
            tensor field 'nabla_g inv_g' of type (2,1) on the open domain 'U' on the 3-dimensional manifold 'R^3'
            sage: Dig == 0
            True
        
        """
        from connection import LeviCivitaConnection
        if self._connection is None:
            if name is None:
                name = 'nabla_' + self._name
            if latex_name is None:
                latex_name = r'\nabla_{' + self._latex_name + '}'
            self._connection = LeviCivitaConnection(self, name, latex_name)
        return self._connection

    def christoffel_symbols(self, chart=None):
        r"""
        Christoffel symbols of ``self`` with respect to a chart.
        
        INPUT:
        
        - ``chart`` -- (default: None) chart with respect to which the 
          Christoffel symbolds are required; if none is provided, the 
          manifold's default chart is assumed.
          
        OUTPUT:
        
        - the set of Christoffel symbols in the given chart, as an instance of
          :class:`~sage.tensor.modules.comp.CompWithSym`
          
        EXAMPLES:
        
        Christoffel symbols of the flat metric on `\RR^3` with respect to 
        spherical coordinates::
        
            sage: M = Manifold(3, 'R3', r'\RR^3', start_index=1)
            sage: U = M.open_domain('U') # the complement of the half-plane (y=0, x>=0)
            sage: X.<r,th,ph> = U.chart(r'r:(0,+oo) th:(0,pi):\theta ph:(0,2*pi):\phi')
            sage: g = U.metric('g')
            sage: g[1,1], g[2,2], g[3,3] = 1, r^2, r^2*sin(th)^2
            sage: g.view()  # the standard flat metric expressed in spherical coordinates
            g = dr*dr + r^2 dth*dth + r^2*sin(th)^2 dph*dph
            sage: Gam = g.christoffel_symbols() ; Gam
            3-indices components w.r.t. coordinate frame (U, (d/dr,d/dth,d/dph)), with symmetry on the index positions (1, 2)
            sage: print type(Gam)
            <class 'sage.tensor.modules.comp.CompWithSym'>
            sage: Gam[:]
            [[[0, 0, 0], [0, -r, 0], [0, 0, -r*sin(th)^2]], 
            [[0, 1/r, 0], [1/r, 0, 0], [0, 0, -cos(th)*sin(th)]], 
            [[0, 0, 1/r], [0, 0, cos(th)/sin(th)], [1/r, cos(th)/sin(th), 0]]]
            sage: Gam[1,2,2]
            -r
            sage: Gam[2,1,2]
            1/r
            sage: Gam[3,1,3]
            1/r
            sage: Gam[3,2,3]
            cos(th)/sin(th)
            sage: Gam[2,3,3]
            -cos(th)*sin(th)
        
        """
        if chart is None:
            frame = self._domain._def_chart._frame
        else:
            frame = chart._frame
        return self.connection().coef(frame)
          
    def riemann(self, name=None, latex_name=None):
        r""" 
        Return the Riemann curvature tensor associated with the metric.

        This method is actually a shortcut for ``self.connection().riemann()``
        
        The Riemann curvature tensor is the tensor field `R` of type (1,3) 
        defined by

        .. MATH::
            
            R(\omega, u, v, w) = \left\langle \omega, \nabla_u \nabla_v w
                - \nabla_v \nabla_u w - \nabla_{[u, v]} w \right\rangle
        
        for any 1-form  `\omega`  and any vector fields `u`, `v` and `w`. 

        INPUT:
        
        - ``name`` -- (default: None) name given to the Riemann tensor; 
          if none, it is set to "Riem(g)", where "g" is the metric's name
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the 
          Riemann tensor; if none, it is set to "\\mathrm{Riem}(g)", where "g" 
          is the metric's name

        OUTPUT:
        
        - the Riemann curvature tensor `R`, as an instance of 
          :class:`~sage.geometry.manifolds.tensorfield.TensorField`
        
        EXAMPLES:

        Riemann tensor of the standard metric on the 2-sphere::
        
            sage: Manifold._clear_cache_() # for doctests only
            sage: M = Manifold(2, 'S^2', start_index=1)
            sage: U = M.open_domain('U') # the complement of a meridian (domain of spherical coordinates)
            sage: c_spher.<th,ph> = U.chart(r'th:(0,pi):\theta ph:(0,2*pi):\phi')
            sage: a = var('a') # the sphere radius 
            sage: g = U.metric('g')
            sage: g[1,1], g[2,2] = a^2, a^2*sin(th)^2
            sage: g.view() # standard metric on the 2-sphere of radius a:
            g = a^2 dth*dth + a^2*sin(th)^2 dph*dph
            sage: g.riemann()
            tensor field 'Riem(g)' of type (1,3) on the open domain 'U' on the 2-dimensional manifold 'S^2'
            sage: g.riemann()[:]
            [[[[0, 0], [0, 0]], [[0, sin(th)^2], [-sin(th)^2, 0]]],
             [[[0, (cos(th)^2 - 1)/sin(th)^2], [1, 0]], [[0, 0], [0, 0]]]]
             
        In dimension 2, the Riemann tensor can be expressed entirely in terms of
        the Ricci scalar `r`:

        .. MATH::
            
            R^i_{\ \, jlk} = \frac{r}{2} \left( \delta^i_{\ \, k} g_{jl}
                - \delta^i_{\ \, l} g_{jk} \right)
        
        This formula can be checked here, with the r.h.s. rewritten as 
        `-r g_{j[k} \delta^i_{\ \, l]}`::
        
            sage: g.riemann() == -g.ricci_scalar()*(g*U.tangent_identity_field()).antisymmetrize(2,3)
            True
        
        """
        return self.connection().riemann(name, latex_name)

        
    def ricci(self, name=None, latex_name=None):
        r""" 
        Return the Ricci tensor associated with the metric.
        
        This method is actually a shortcut for ``self.connection().ricci()``
                
        The Ricci tensor is the tensor field `Ric` of type (0,2) 
        defined from the Riemann curvature tensor `R` by 

        .. MATH::
            
            Ric(u, v) = R(e^i, u, e_i, v)
        
        for any vector fields `u` and `v`, `(e_i)` being any vector frame and
        `(e^i)` the dual coframe. 

        INPUT:
        
        - ``name`` -- (default: None) name given to the Ricci tensor; 
          if none, it is set to "Ric(g)", where "g" is the metric's name
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the 
          Ricci tensor; if none, it is set to "\\mathrm{Ric}(g)", where "g" 
          is the metric's name
          
        OUTPUT:
        
        - the Ricci tensor `Ric`, as an instance of 
          :class:`~sage.geometry.manifolds.tensorfield.TensorField` of tensor
          type (0,2) and symmetric
        
        EXAMPLES:
        
        Ricci tensor of the standard metric on the 2-sphere::
        
            sage: Manifold._clear_cache_() # for doctests only
            sage: M = Manifold(2, 'S^2', start_index=1)
            sage: U = M.open_domain('U') # the complement of a meridian (domain of spherical coordinates)
            sage: c_spher.<th,ph> = U.chart(r'th:(0,pi):\theta ph:(0,2*pi):\phi')
            sage: a = var('a') # the sphere radius 
            sage: g = U.metric('g')
            sage: g[1,1], g[2,2] = a^2, a^2*sin(th)^2
            sage: g.view() # standard metric on the 2-sphere of radius a:
            g = a^2 dth*dth + a^2*sin(th)^2 dph*dph
            sage: g.ricci()
            field of symmetric bilinear forms 'Ric(g)' on the open domain 'U' on the 2-dimensional manifold 'S^2'
            sage: g.ricci()[:]
            [        1         0]
            [        0 sin(th)^2]
            sage: g.ricci() == a^(-2) * g
            True

        """
        return self.connection().ricci(name, latex_name)

    def ricci_scalar(self, name=None, latex_name=None):
        r""" 
        Return the Ricci scalar associated with the metric.
        
        The Ricci scalar is the scalar field `r` defined from the Ricci tensor 
        `Ric` and the metric tensor `g` by 

        .. MATH::
            
            r = g^{ij} Ric_{ij}
        
        INPUT:
        
        - ``name`` -- (default: None) name given to the Ricci scalar; 
          if none, it is set to "r(g)", where "g" is the metric's name
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the 
          Ricci scalar; if none, it is set to "\\mathrm{r}(g)", where "g" 
          is the metric's name

        OUTPUT:
        
        - the Ricci scalar `r`, as an instance of 
          :class:`~sage.geometry.manifolds.scalarfield.ScalarField`

        EXAMPLES:
        
        Ricci scalar of the standard metric on the 2-sphere::
        
            sage: Manifold._clear_cache_() # for doctests only
            sage: M = Manifold(2, 'S^2', start_index=1)
            sage: U = M.open_domain('U') # the complement of a meridian (domain of spherical coordinates)
            sage: c_spher.<th,ph> = U.chart(r'th:(0,pi):\theta ph:(0,2*pi):\phi')
            sage: a = var('a') # the sphere radius 
            sage: g = U.metric('g')
            sage: g[1,1], g[2,2] = a^2, a^2*sin(th)^2
            sage: g.view() # standard metric on the 2-sphere of radius a:
            g = a^2 dth*dth + a^2*sin(th)^2 dph*dph
            sage: g.ricci_scalar()
            scalar field 'r(g)' on the open domain 'U' on the 2-dimensional manifold 'S^2'
            sage: g.ricci_scalar().view() # The Ricci scalar is constant:
            r(g): U --> R
               (th, ph) |--> 2/a^2

        """
        if self._ricci_scalar is None:
            resu = self.inverse().contract(0, 1, self.ricci(), 0, 1)
            if name is None:
                name = "r(" + self._name + ")"
            if latex_name is None:
                latex_name = r"\mathrm{r}\left(" + self._latex_name + \
                              r"\right)"
            resu._name = name
            resu._latex_name = latex_name
            self._ricci_scalar = resu
        return self._ricci_scalar

    def weyl(self, name=None, latex_name=None):
        r""" 
        Return the Weyl conformal tensor associated with the metric.
                        
        The Weyl conformal tensor is the tensor field `C` of type (1,3) 
        defined as the trace-free part of the Riemann curvature tensor `R`

        INPUT:
        
        - ``name`` -- (default: None) name given to the Weyl conformal tensor; 
          if none, it is set to "C(g)", where "g" is the metric's name
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the 
          Weyl conformal tensor; if none, it is set to "\\mathrm{C}(g)", where 
          "g" is the metric's name

        OUTPUT:
        
        - the Weyl conformal tensor `C`, as an instance of 
          :class:`~sage.geometry.manifolds.tensorfield.TensorField`
        
        EXAMPLES:
        
        Checking that the Weyl tensor identically vanishes on a 3-dimensional 
        manifold, for instance the hyperbolic space `H^3`::
        
            sage: M = Manifold(3, 'H^3', start_index=1)
            sage: U = M.open_domain('U') # the complement of the half-plane (y=0, x>=0)
            sage: X.<rh,th,ph> = U.chart(r'rh:(0,+oo):\rho th:(0,pi):\theta  ph:(0,2*pi):\phi')
            sage: g = U.metric('g')
            sage: b = var('b')                                                        
            sage: g[1,1], g[2,2], g[3,3] = b^2, (b*sinh(rh))^2, (b*sinh(rh)*sin(th))^2
            sage: g.view()  # standard metric on H^3:
            g = b^2 drh*drh + b^2*sinh(rh)^2 dth*dth + b^2*sin(th)^2*sinh(rh)^2 dph*dph
            sage: C = g.weyl() ; C
            tensor field 'C(g)' of type (1,3) on the open domain 'U' on the 3-dimensional manifold 'H^3'
            sage: C == 0 
            True

        """
        if self._weyl is None:
            n = self._ambient_domain._manifold._dim
            if n < 3:
                raise ValueError("The Weyl tensor is not defined for a " + 
                                 "manifold of dimension n <= 2.")
            delta = self._domain.tangent_identity_field(dest_map=
                                                       self._vmodule._dest_map)
            riem = self.riemann()
            ric = self.ricci()
            rscal = self.ricci_scalar()
            # First index of the Ricci tensor raised with the metric
            ricup = ric.up(self, 0) 
            aux = self*ricup + ric*delta - rscal/(n-1)* self*delta
            self._weyl = riem + 2/(n-2)* aux.antisymmetrize(2,3) 
            if name is None:
                name = "C(" + self._name + ")"
            if latex_name is None:
                latex_name = r"\mathrm{C}\left(" + self._latex_name + r"\right)"
            self._weyl.set_name(name=name, latex_name=latex_name)
        return self._weyl

    def determinant(self, frame=None):
        r"""
        Determinant of the metric components in the specified frame.
        
        INPUT:
        
        - ``frame`` -- (default: None) vector frame with 
          respect to which the components `g_{ij}` of ``self`` are defined; 
          if None, the default frame of the metric's domain is used. If a 
          chart is provided instead of a frame, the associated coordinate 
          frame is used
          
        OUTPUT:
        
        - the determinant `\det (g_{ij})`, as an instance of 
          :class:`~sage.geometry.manifolds.scalarfield.ScalarField`
        
        EXAMPLES:
        
        Metric determinant on a 2-dimensional manifold::
        
            sage: M = Manifold(2, 'M', start_index=1)
            sage: X.<x,y> = M.chart()
            sage: g = M.metric('g')
            sage: g[1,1], g[1, 2], g[2, 2] = 1+x, x*y , 1-y
            sage: g[:]
            [ x + 1    x*y]
            [   x*y -y + 1]
            sage: s = g.determinant()  # determinant in M's default frame
            sage: s.expr()
            -x^2*y^2 - (x + 1)*y + x + 1

        Determinant in a frame different from the default's one::
            
            sage: Y.<u,v> = M.chart()
            sage: ch_X_Y = X.coord_change(Y, x+y, x-y)   
            sage: ch_X_Y.inverse()
            coordinate change from chart (M, (u, v)) to chart (M, (x, y))                 
            sage: g.comp(Y.frame())[:, Y]
            [ 1/8*u^2 - 1/8*v^2 + 1/4*v + 1/2                            1/4*u]
            [                           1/4*u -1/8*u^2 + 1/8*v^2 + 1/4*v + 1/2]
            sage: g.determinant(Y.frame()).expr()
            -1/4*x^2*y^2 - 1/4*(x + 1)*y + 1/4*x + 1/4
            sage: g.determinant(Y.frame()).expr(Y)
            -1/64*u^4 - 1/64*v^4 + 1/32*(u^2 + 2)*v^2 - 1/16*u^2 + 1/4*v + 1/4

        A chart can be passed instead of a frame::
        
            sage: g.determinant(X) is g.determinant(X.frame())
            True
            sage: g.determinant(Y) is g.determinant(Y.frame())
            True

        The metric determinant depends on the frame::
        
            sage: g.determinant(X.frame()) == g.determinant(Y.frame())
            False
        
        """
        from sage.matrix.constructor import matrix
        from utilities import simple_determinant, simplify_chain
        manif = self._ambient_domain._manifold
        dom = self._domain
        if frame is None:
            frame = dom._def_frame
        if frame in dom._atlas:   
            # frame is actually a chart and is changed to the associated 
            # coordinate frame:
            frame = frame._frame
        if frame not in self._determinants:
            # a new computation is necessary
            resu = frame._domain.scalar_field()
            gg = self.comp(frame)
            i1 = manif._sindex
            for chart in gg[[i1, i1]]._express:
                gm = matrix( [[ gg[i, j, chart]._express 
                            for j in manif.irange()] for i in manif.irange()] )
                detgm = simplify_chain(simple_determinant(gm))
                resu.add_expr(detgm, chart=chart)
            self._determinants[frame] = resu
        return self._determinants[frame]

    def sqrt_abs_det(self, frame=None):
        r"""
        Square root of the absolute value of the determinant of the metric 
        components in the specified frame.
        
        INPUT:
        
        - ``frame`` -- (default: None) vector frame with 
          respect to which the components `g_{ij}` of ``self`` are defined; 
          if None, the domain's default frame is used. If a chart is 
          provided, the associated coordinate frame is used
          
        OUTPUT:
        
        - `\sqrt{|\det (g_{ij})|}`, as an instance of 
          :class:`~sage.geometry.manifolds.scalarfield.ScalarField`
        
        EXAMPLES:
        
        Standard metric in the Euclidean space `\RR^3` with spherical 
        coordinates::
        
            sage: M = Manifold(3, 'M', start_index=1)
            sage: U = M.open_domain('U') # the complement of the half-plane (y=0, x>=0)
            sage: c_spher.<r,th,ph> = U.chart(r'r:(0,+oo) th:(0,pi):\theta ph:(0,2*pi):\phi')
            sage: g = U.metric('g')
            sage: g[1,1], g[2,2], g[3,3] = 1, r^2, (r*sin(th))^2
            sage: g.view()
            g = dr*dr + r^2 dth*dth + r^2*sin(th)^2 dph*dph
            sage: g.sqrt_abs_det().expr()
            r^2*sin(th)
            
        Metric determinant on a 2-dimensional manifold::
        
            sage: M = Manifold(2, 'M', start_index=1)
            sage: X.<x,y> = M.chart()
            sage: g = M.metric('g')
            sage: g[1,1], g[1, 2], g[2, 2] = 1+x, x*y , 1-y
            sage: g[:]
            [ x + 1    x*y]
            [   x*y -y + 1]
            sage: s = g.sqrt_abs_det() ; s
            scalar field on the 2-dimensional manifold 'M'
            sage: s.expr()
            sqrt(-x^2*y^2 - (x + 1)*y + x + 1)

        Determinant in a frame different from the default's one::
            
            sage: Y.<u,v> = M.chart()
            sage: ch_X_Y = X.coord_change(Y, x+y, x-y)   
            sage: ch_X_Y.inverse()
            coordinate change from chart (M, (u, v)) to chart (M, (x, y))                    
            sage: g[Y.frame(),:,Y]
            [ 1/8*u^2 - 1/8*v^2 + 1/4*v + 1/2                            1/4*u]
            [                           1/4*u -1/8*u^2 + 1/8*v^2 + 1/4*v + 1/2]
            sage: g.sqrt_abs_det(Y.frame()).expr()
            1/2*sqrt(-x^2*y^2 - (x + 1)*y + x + 1)
            sage: g.sqrt_abs_det(Y.frame()).expr(Y)
            1/8*sqrt(-u^4 - v^4 + 2*(u^2 + 2)*v^2 - 4*u^2 + 16*v + 16)

        A chart can be passed instead of a frame::
        
            sage: g.sqrt_abs_det(Y) is g.sqrt_abs_det(Y.frame())
            True

        The metric determinant depends on the frame::
        
            sage: g.sqrt_abs_det(X.frame()) == g.sqrt_abs_det(Y.frame()) 
            False

        """
        from sage.functions.other import sqrt
        from utilities import simplify_chain
        dom = self._domain
        if frame is None:
            frame = dom._def_frame
        if frame in dom._atlas:   
            # frame is actually a chart and is changed to the associated 
            # coordinate frame:
            frame = frame._frame
        if frame not in self._sqrt_abs_dets:
            # a new computation is necessary
            detg = self.determinant(frame)
            resu = frame._domain.scalar_field()
            for chart in detg._express:
                x = self._indic_signat * detg._express[chart]._express # |g|
                x = simplify_chain(sqrt(x))
                resu.add_expr(x, chart=chart)
            self._sqrt_abs_dets[frame] = resu
        return self._sqrt_abs_dets[frame]

    def volume_form(self, contra=0):
        r"""
        Volume form (Levi-Civita tensor) `\epsilon` associated with the metric.
        
        This assumes that the manifold is orientable. 
        
        The volume form `\epsilon` is a `n`-form (`n` being the manifold's 
        dimension) such that for any vector basis `(e_i)` that is orthonormal
        with respect to the metric, 
        
        .. MATH::
            
            \epsilon(e_1,\ldots,e_n) = \pm 1 

        There are only two such `n`-forms, which are opposite of each other. 
        The volume form `\epsilon` is selected such that the domain's default 
        frame is right-handed with respect to it. 
        
        INPUT:
        
        - ``contra`` -- (default: 0) number of contravariant indices of the
          returned tensor
        
        OUTPUT:
        
        - if ``contra = 0`` (default value): the volume `n`-form `\epsilon`, as 
          an instance of 
          :class:`~sage.geometry.manifolds.diffform.DiffForm`
        - if ``contra = k``, with `1\leq k \leq n`, the tensor field of type 
          (k,n-k) formed from `\epsilon` by raising the first k indices with the 
          metric (see method :meth:`TensorField.up`); the output is then an
          instance of 
          :class:`~sage.geometry.manifolds.tensorfield.TensorField`, with the 
          appropriate antisymmetries
       
        EXAMPLES:
        
        Volume form on `\RR^3` with spherical coordinates::
        
            sage: M = Manifold(3, 'M', start_index=1)
            sage: U = M.open_domain('U') # the complement of the half-plane (y=0, x>=0)
            sage: c_spher.<r,th,ph> = U.chart(r'r:(0,+oo) th:(0,pi):\theta ph:(0,2*pi):\phi')
            sage: g = U.metric('g')
            sage: g[1,1], g[2,2], g[3,3] = 1, r^2, (r*sin(th))^2
            sage: g.view()
            g = dr*dr + r^2 dth*dth + r^2*sin(th)^2 dph*dph
            sage: eps = g.volume_form() ; eps
            3-form 'eps_g' on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: eps.view()
            eps_g = r^2*sin(th) dr/\dth/\dph
            sage: eps[[1,2,3]] == g.sqrt_abs_det()
            True
            sage: latex(eps)
            \epsilon_{g}
            
            
        The tensor field of components `\epsilon^i_{\ \, jk}` (``contra=1``)::
        
            sage: eps1 = g.volume_form(1) ; eps1
            tensor field of type (1,2) on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: eps1.symmetries()
            no symmetry;  antisymmetry: (1, 2)
            sage: eps1[:]
            [[[0, 0, 0], [0, 0, r^2*sin(th)], [0, -r^2*sin(th), 0]],
             [[0, 0, -sin(th)], [0, 0, 0], [sin(th), 0, 0]],
             [[0, 1/sin(th), 0], [-1/sin(th), 0, 0], [0, 0, 0]]]
            
        The tensor field of components `\epsilon^{ij}_{\ \ k}` (``contra=2``)::
        
            sage: eps2 = g.volume_form(2) ; eps2
            tensor field of type (2,1) on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: eps2.symmetries()
            no symmetry;  antisymmetry: (0, 1)
            sage: eps2[:]
            [[[0, 0, 0], [0, 0, sin(th)], [0, -1/sin(th), 0]],
             [[0, 0, -sin(th)], [0, 0, 0], [1/(r^2*sin(th)), 0, 0]],
             [[0, 1/sin(th), 0], [-1/(r^2*sin(th)), 0, 0], [0, 0, 0]]]
            
        The tensor field of components `\epsilon^{ijk}` (``contra=3``)::
        
            sage: eps3 = g.volume_form(3) ; eps3
            tensor field of type (3,0) on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: eps3.symmetries()
            no symmetry;  antisymmetry: (0, 1, 2)
            sage: eps3[:]
            [[[0, 0, 0], [0, 0, 1/(r^2*sin(th))], [0, -1/(r^2*sin(th)), 0]],
             [[0, 0, -1/(r^2*sin(th))], [0, 0, 0], [1/(r^2*sin(th)), 0, 0]],
             [[0, 1/(r^2*sin(th)), 0], [-1/(r^2*sin(th)), 0, 0], [0, 0, 0]]]
            sage: eps3[1,2,3]
            1/(r^2*sin(th))
            sage: eps3[[1,2,3]] * g.sqrt_abs_det() == 1
            True
        
        """
        if self._vol_forms == []:
            # a new computation is necessary
            manif = self._ambient_domain._manifold
            dom = self._domain
            ndim = manif._dim
            # The result is constructed on the vector field module, 
            # so that dest_map is taken automatically into account:
            eps = self._vmodule.alternating_form(ndim, name='eps_'+self._name, 
                                latex_name=r'\epsilon_{'+self._latex_name+r'}')
            ind = tuple(range(manif._sindex, manif._sindex+ndim))
            for frame in dom._top_frames:
                eps.add_comp(frame)[[ind]] = self.sqrt_abs_det(frame)
            self._vol_forms.append(eps)  # Levi-Civita tensor constructed
            # Tensors related to the Levi-Civita one by index rising:
            for k in range(1, ndim+1):
                epskm1 = self._vol_forms[k-1]
                epsk = epskm1.up(self, k-1)
                if k > 1:
                    # restoring the antisymmetry after the up operation: 
                    epsk = epsk.antisymmetrize(*range(k)) 
                self._vol_forms.append(epsk)
        return self._vol_forms[contra]

#*****************************************************************************

class RiemannMetric(Metric):
    r"""
    Riemannian metric with values on an open subset of a 
    differentiable manifold.
    
    A Riemannian metric is a field of positive-definite symmetric bilinear 
    forms on the manifold. 

    See :class:`Metric` for a complete documentation. 
    
    INPUT:
    
    - ``vector_field_module`` -- module `\mathcal{X}(U,\Phi)` of vector 
      fields along `U` with values on `\Phi(U)\subset V \subset M`
    - ``name`` -- name given to the metric
    - ``latex_name`` -- (default: None) LaTeX symbol to denote the metric; if
      none, it is formed from ``name``      

    """
    def __init__(self, vector_field_module, name, latex_name=None):
        dim = vector_field_module._ambient_domain._manifold._dim
        Metric.__init__(self, vector_field_module, name, signature=dim,
                             latex_name=latex_name)

    def _repr_(self):
        r"""
        String representation of the object.
        """
        description = "Riemannian metric '%s' " % self._name
        return self._final_repr(description)

    def _new_instance(self):
        r"""
        Create a :class:`RiemannMetric` instance on the same domain.
        
        """
        return self.__class__(self._vmodule, 'unnamed metric', 
                              latex_name=r'\mbox{unnamed metric}')

#*****************************************************************************

class LorentzMetric(Metric):
    r"""
    Lorentzian metric with values on an open subset of a 
    differentiable manifold.
    
    A Lorentzian metric is a field of symmetric bilinear 
    forms with signature `(-,+,\cdots,+)` or `(+,-,\cdots,-)`. 

    See :class:`Metric` for a complete documentation. 
    
    INPUT:
    
    - ``vector_field_module`` -- module `\mathcal{X}(U,\Phi)` of vector 
      fields along `U` with values on `\Phi(U)\subset V \subset M`
    - ``name`` -- name given to the metric
    - ``signature`` -- (default: 'positive') sign of the metric signature: 
        * if set to 'positive', the signature is n-2, where n is the manifold's
          dimension, i.e. `(-,+,\cdots,+)`
        * if set to 'negative', the signature is -n+2, i.e. `(+,-,\cdots,-)`
    - ``latex_name`` -- (default: None) LaTeX symbol to denote the metric; if
      none, it is formed from ``name``      

    """
    def __init__(self, vector_field_module, name, signature='positive', 
                 latex_name=None):
        dim = vector_field_module._ambient_domain._manifold._dim
        if signature=='positive':
            signat = dim - 2
        else:
            signat = 2 - dim
        Metric.__init__(self, vector_field_module, name, signature=signat,
                        latex_name=latex_name)

    def _repr_(self):
        r"""
        String representation of the object.
        """
        description = "Lorentzian metric '%s' " % self._name
        return self._final_repr(description)

    def _new_instance(self):
        r"""
        Create a :class:`LorentzMetric` instance on the same domain.
        
        """
        if self._signature >= 0:
            signature_type = 'positive'
        else:
            signature_type = 'negative'            
        return self.__class__(self._vmodule, 'unnamed metric', 
                              signature=signature_type, 
                              latex_name=r'\mbox{unnamed metric}')



#******************************************************************************

class MetricParal(Metric, TensorFieldParal):
    r"""
    Base class for pseudo-Riemannian metrics with values on a parallelizable 
    open subset of a differentiable manifold. 

    An instance of this class is a field of nondegenerate symmetric bilinear 
    forms (metric field) along an open subset `U` of some manifold `S` with 
    values in a parallelizable open subset `V` of a manifold `M`, via a 
    differentiable mapping `\Phi: U \rightarrow V`. 
    The standard case of a metric field *on* a manifold corresponds to `S=M`, 
    `U=V` and `\Phi = \mathrm{Id}`. Another common case is `\Phi` being an
    immersion.

    A *metric* `g` is a field on `U`, so that at each 
    point `p\in U`, `g(p)` is a bilinear map of the type:

    .. MATH::

        g(p):\ T_q M\times T_q M  \longrightarrow \RR
    
    where `T_q M` stands for the tangent space at the point `q=\Phi(p)` on the
    manifold `M`, such that `g(p)` is symmetric: 
    `\forall (u,v)\in  T_q M\times T_q M, \ g(p)(v,u) = g(p)(u,v)` 
    and nondegenerate: 
    `(\forall v\in T_q M,\ \ g(p)(u,v) = 0) \Longrightarrow u=0`. 
    
    INPUT:
    
    - ``vector_field_module`` -- free module `\mathcal{X}(U,\Phi)` of vector 
      fields along `U` with values on `\Phi(U)\subset V \subset M`
    - ``name`` -- name given to the metric
    - ``signature`` -- (default: None) signature `S` of the metric as a single 
      integer: `S = n_+ - n_-`, where `n_+` (resp. `n_-`) is the number of 
      positive terms (resp. number of negative terms) in any diagonal writing 
      of the metric components; if ``signature`` is not provided, `S` is set to 
      the dimension of manifold `M` (Riemannian signature)
    - ``latex_name`` -- (default: None) LaTeX symbol to denote the metric; if
      none, it is formed from ``name``      

    EXAMPLES:
    
    Metric on a 2-dimensional manifold::
    
        sage: M = Manifold(2, 'M', start_index=1)
        sage: c_xy.<x,y> = M.chart()
        sage: g = M.metric('g') ; g
        pseudo-Riemannian metric 'g' on the 2-dimensional manifold 'M'
        sage: latex(g)
        g
   
    A metric is a special kind of tensor field and therefore inheritates all the
    properties from class 
    :class:`~sage.geometry.manifolds.tensorfield.TensorField`::
    
        sage: g.parent()
        free module T^(0,2)(M) of type-(0,2) tensors fields on the 2-dimensional manifold 'M'
        sage: g._tensor_type
        (0, 2)
        sage: g.symmetries()  # g is symmetric:
        symmetry: (0, 1);  no antisymmetry
       
    Setting the metric components in the manifold's default frame::
    
        sage: g[1,1], g[1,2], g[2,2] = 1+x, x*y, 1-x 
        sage: g[:]
        [ x + 1    x*y]
        [   x*y -x + 1]
        sage: g.view()
        g = (x + 1) dx*dx + x*y dx*dy + x*y dy*dx + (-x + 1) dy*dy

    Metric components in a frame different from the manifold's default one::
    
        sage: c_uv.<u,v> = M.chart()  # new chart on M
        sage: xy_to_uv = c_xy.coord_change(c_uv, x+y, x-y) ; xy_to_uv
        coordinate change from chart (M, (x, y)) to chart (M, (u, v))
        sage: uv_to_xy = xy_to_uv.inverse() ; uv_to_xy
        coordinate change from chart (M, (u, v)) to chart (M, (x, y))
        sage: M.atlas()
        [chart (M, (x, y)), chart (M, (u, v))]
        sage: M.frames()
        [coordinate frame (M, (d/dx,d/dy)), coordinate frame (M, (d/du,d/dv))]
        sage: g[c_uv.frame(),:]  # metric components in frame c_uv.frame() expressed in M's default chart (x,y)
        [ 1/2*x*y + 1/2          1/2*x]
        [         1/2*x -1/2*x*y + 1/2]
        sage: g.view(c_uv.frame())
        g = (1/2*x*y + 1/2) du*du + 1/2*x du*dv + 1/2*x dv*du + (-1/2*x*y + 1/2) dv*dv
        sage: g[c_uv.frame(),:,c_uv]   # metric components in frame c_uv.frame() expressed in chart (u,v)
        [ 1/8*u^2 - 1/8*v^2 + 1/2            1/4*u + 1/4*v]
        [           1/4*u + 1/4*v -1/8*u^2 + 1/8*v^2 + 1/2]
        sage: g.view(c_uv.frame(), c_uv)
        g = (1/8*u^2 - 1/8*v^2 + 1/2) du*du + (1/4*u + 1/4*v) du*dv + (1/4*u + 1/4*v) dv*du + (-1/8*u^2 + 1/8*v^2 + 1/2) dv*dv


    The inverse metric is obtained via :meth:`inverse`::
    
        sage: ig = g.inverse() ; ig
        tensor field 'inv_g' of type (2,0) on the 2-dimensional manifold 'M'
        sage: ig[:]
        [ (x - 1)/(x^2*y^2 + x^2 - 1)      x*y/(x^2*y^2 + x^2 - 1)]
        [     x*y/(x^2*y^2 + x^2 - 1) -(x + 1)/(x^2*y^2 + x^2 - 1)]
        sage: ig.view()
        inv_g = (x - 1)/(x^2*y^2 + x^2 - 1) d/dx*d/dx + x*y/(x^2*y^2 + x^2 - 1) d/dx*d/dy + x*y/(x^2*y^2 + x^2 - 1) d/dy*d/dx - (x + 1)/(x^2*y^2 + x^2 - 1) d/dy*d/dy

    """
    def __init__(self, vector_field_module, name, signature=None, 
                 latex_name=None):
        TensorFieldParal.__init__(self, vector_field_module, (0,2), 
                                  name=name, latex_name=latex_name, sym=(0,1))
        # signature:
        ndim = self._ambient_domain._manifold._dim
        if signature is None:
            signature = ndim
        else:
            if not isinstance(signature, (int, Integer)):
                raise TypeError("The metric signature must be an integer.")
            if (signature < - ndim) or (signature > ndim):
                raise ValueError("Metric signature out of range.")
            if (signature+ndim)%2 == 1:
                if ndim%2 == 0:
                    raise ValueError("The metric signature must be even.")
                else:
                    raise ValueError("The metric signature must be odd.")
        self._signature = signature
        # the pair (n_+, n_-):
        self._signature_pm = ((ndim+signature)/2, (ndim-signature)/2)
        self._indic_signat = 1 - 2*(self._signature_pm[1]%2)  # (-1)^n_-
        MetricParal._init_derived(self)
        
    def _init_derived(self):
        r"""
        Initialize the derived quantities
        """
        # Initialization of quantities pertaining to the mother classes:
        TensorFieldParal._init_derived(self) 
        Metric._init_derived(self) 

    def _del_derived(self, del_restrictions=True):
        r"""
        Delete the derived quantities
        
        INPUT:
        
        - ``del_restrictions`` -- (default: True) determines whether the
          restrictions of ``self`` to subdomains are deleted. 
        
        """
        # The derived quantities from the mother classes are deleted:
        TensorFieldParal._del_derived(self, del_restrictions=del_restrictions)
        Metric._del_derived(self)

    def _del_inverse(self):
        r"""
        Delete the inverse metric
        """
        self._inverse._components.clear()
        self._inverse._del_derived()

    def restrict(self, subdomain, dest_map=None):
        r"""
        Return the restriction of the metric to some subdomain.
        
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
        
        - instance of :class:`MetricParal` representing the restriction.
        
        """
        if subdomain == self._domain:
            return self
        if subdomain not in self._restrictions:
            # Construct the restriction at the tensor field level:
            resu = TensorFieldParal.restrict(self, subdomain, dest_map=dest_map)
            # the type is correctly handled by TensorFieldParal.restrict, i.e.
            # resu is of type self.__class__, but the signature is not handled 
            # by TensorFieldParal.restrict; we have to set it here:
            resu._signature = self._signature
            resu._signature_pm = self._signature_pm
            resu._indic_signat = self._indic_signat
            # Restrictions of derived quantities:
            resu._inverse = self.inverse().restrict(subdomain)
            if self._connection is not None:
                resu._connection = self._connection.restrict(subdomain)
            if self._ricci_scalar is not None:
                resu._ricci_scalar = self._ricci_scalar.restrict(subdomain)
            if self._weyl is not None:
                resu._weyl = self._weyl.restrict(subdomain)
            if self._vol_forms != []:
                for eps in self._vol_forms:
                    resu._vol_forms.append(eps.restrict(subdomain))
            # NB: no initialization of resu._determinants nor 
            # resu._sqrt_abs_dets
            # The restriction is ready:
            self._restrictions[subdomain] = resu
        return self._restrictions[subdomain]


    def set(self, symbiform):
        r"""
        Defines the metric from a field of symmetric bilinear forms
        
        INPUT:
    
        - ``symbiform`` -- instance of
          :class:`~sage.geometry.manifolds.tensorfield.TensorFieldParal` 
          representing a field of symmetric bilinear forms

        """
        if not isinstance(symbiform, TensorFieldParal):
            raise TypeError("The argument must be a tensor field with " + 
                            "values on a parallelizable domain.")
        if symbiform._tensor_type != (0,2):
            raise TypeError("The argument must be of tensor type (0,2).")
        if symbiform._sym != [(0,1)]:
            raise TypeError("The argument must be symmetric.")
        if symbiform._vmodule is not self._vmodule:
            raise TypeError("The symmetric bilinear form and the metric are " + 
                            "not defined on the same vector field module.")
        self._del_derived()
        self._components.clear()
        for frame in symbiform._components:
            self._components[frame] = symbiform._components[frame].copy()
        
    def inverse(self):
        r"""
        Return the inverse metric.
        
        OUTPUT:
        
        - instance of
          :class:`~sage.geometry.geometry.tensorfield.TensorFieldParal`
          with tensor_type = (2,0) representing the inverse metric

        EXAMPLES:
        
        Inverse metric on a 2-dimensional manifold::
    
            sage: M = Manifold(2, 'M', start_index=1)
            sage: c_xy.<x,y> = M.chart()
            sage: g = M.metric('g') 
            sage: g[1,1], g[1,2], g[2,2] = 1+x, x*y, 1-x 
            sage: g[:]  # components in the manifold's default frame
            [ x + 1    x*y]
            [   x*y -x + 1]
            sage: ig = g.inverse() ; ig
            tensor field 'inv_g' of type (2,0) on the 2-dimensional manifold 'M'
            sage: ig[:]
            [ (x - 1)/(x^2*y^2 + x^2 - 1)      x*y/(x^2*y^2 + x^2 - 1)]
            [     x*y/(x^2*y^2 + x^2 - 1) -(x + 1)/(x^2*y^2 + x^2 - 1)]

        If the metric is modified, the inverse metric is automatically updated::
        
            sage: g[1,2] = 0 ; g[:]
            [ x + 1      0]
            [     0 -x + 1]
            sage: g.inverse()[:]
            [ 1/(x + 1)          0]
            [         0 -1/(x - 1)]

        """
        from sage.matrix.constructor import matrix
        from sage.tensor.modules.comp import CompFullySym
        from vectorframe import CoordFrame
        from utilities import simplify_chain
        # Is the inverse metric up to date ?
        for frame in self._components:
            if frame not in self._inverse._components:
                # the computation is necessary
                fmodule = self._fmodule
                si = fmodule._sindex ; nsi = fmodule._rank + si
                dom = self._domain
                if isinstance(frame, CoordFrame):
                    chart = frame._chart
                else:
                    chart = dom._def_chart
                try:    
                    gmat = matrix(
                              [[self.comp(frame)[i, j, chart]._express 
                              for j in range(si, nsi)] for i in range(si, nsi)])
                except (KeyError, ValueError):
                    continue
                gmat_inv = gmat.inverse()
                cinv = CompFullySym(fmodule._ring, frame, 2, start_index=si,
                                    output_formatter=fmodule._output_formatter)
                for i in range(si, nsi):
                    for j in range(i, nsi):   # symmetry taken into account
                        cinv[i, j] = {chart: simplify_chain(gmat_inv[i-si,j-si])}
                self._inverse._components[frame] = cinv
        return self._inverse

    def ricci_scalar(self, name=None, latex_name=None):
        r""" 
        Return the metric's Ricci scalar.
        
        The Ricci scalar is the scalar field `r` defined from the Ricci tensor 
        `Ric` and the metric tensor `g` by 

        .. MATH::
            
            r = g^{ij} Ric_{ij}
        
        INPUT:
        
        - ``name`` -- (default: None) name given to the Ricci scalar; 
          if none, it is set to "r(g)", where "g" is the metric's name
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the 
          Ricci scalar; if none, it is set to "\\mathrm{r}(g)", where "g" 
          is the metric's name
          
        OUTPUT:
        
        - the Ricci scalar `r`, as an instance of 
          :class:`~sage.geometry.manifolds.scalarfield.ScalarField`
        
        EXAMPLES:
        
        Ricci scalar of the standard metric on the 2-sphere::
        
            sage: Manifold._clear_cache_() # for doctests only
            sage: M = Manifold(2, 'S^2', start_index=1)
            sage: U = M.open_domain('U') # the complement of a meridian (domain of spherical coordinates)
            sage: c_spher.<th,ph> = U.chart(r'th:(0,pi):\theta ph:(0,2*pi):\phi')
            sage: a = var('a') # the sphere radius 
            sage: g = U.metric('g')
            sage: g[1,1], g[2,2] = a^2, a^2*sin(th)^2
            sage: g.view() # standard metric on the 2-sphere of radius a:
            g = a^2 dth*dth + a^2*sin(th)^2 dph*dph
            sage: g.ricci_scalar()
            scalar field 'r(g)' on the open domain 'U' on the 2-dimensional manifold 'S^2'
            sage: g.ricci_scalar().view() # The Ricci scalar is constant:
            r(g): U --> R
               (th, ph) |--> 2/a^2

        """
        if self._ricci_scalar is None:            
            manif = self._domain._manifold
            ric = self.ricci()
            ig = self.inverse()
            frame = ig.common_basis(ric)
            cric = ric._components[frame]
            cig = ig._components[frame]
            rsum1 = 0
            for i in manif.irange():
                rsum1 += cig[[i,i]] * cric[[i,i]]
            rsum2 = 0
            for i in manif.irange():
                for j in manif.irange(start=i+1):
                    rsum2 += cig[[i,j]] * cric[[i,j]]
            self._ricci_scalar = rsum1 + 2*rsum2
            if name is None:
                self._ricci_scalar._name = "r(" + self._name + ")"
            else:
                self._ricci_scalar._name = name
            if latex_name is None:
                self._ricci_scalar._latex_name = r"\mathrm{r}\left(" + \
                                                 self._latex_name + r"\right)"
            else:
                self._ricci_scalar._latex_name = latex_name
        return self._ricci_scalar 

#*****************************************************************************

class RiemannMetricParal(MetricParal):
    r"""
    Riemannian metric with values on a parallelizable open subset of a 
    differentiable manifold.
    
    A Riemannian metric is a field of positive-definite symmetric bilinear 
    forms on the manifold. 

    See :class:`MetricParal` for a complete documentation. 
    
    INPUT:
    
    - ``vector_field_module`` -- free module `\mathcal{X}(U,\Phi)` of vector 
      fields along `U` with values on `\Phi(U)\subset V \subset M`
    - ``name`` -- name given to the metric
    - ``latex_name`` -- (default: None) LaTeX symbol to denote the metric; if
      none, it is formed from ``name``      

    EXAMPLE:
    
    Standard metric on the Euclidean plane::
    
        sage: M = Manifold(2, 'R^2', start_index=1)
        sage: c_cart.<x,y> = M.chart()  # Cartesian coordinates
        sage: g = M.riemann_metric('g') ; g
        Riemannian metric 'g' on the 2-dimensional manifold 'R^2'
        sage: type(g)
        <class 'sage.geometry.manifolds.metric.RiemannMetricParal'>
        sage: g.parent()
        free module T^(0,2)(R^2) of type-(0,2) tensors fields on the 2-dimensional manifold 'R^2'
        sage: g[1,1], g[2,2] = 1, 1
        sage: g.view()
        g = dx*dx + dy*dy
        sage: g.signature()
        2
        sage: g.riemann()
        tensor field 'Riem(g)' of type (1,3) on the 2-dimensional manifold 'R^2'
        sage: g.riemann().view()  # the Euclidean metric is flat:
        Riem(g) = 0

    """
    def __init__(self, vector_field_module, name, latex_name=None):
        dim = vector_field_module._ambient_domain._manifold._dim
        MetricParal.__init__(self, vector_field_module, name, signature=dim,
                             latex_name=latex_name)

    def _repr_(self):
        r"""
        String representation of the object.
        """
        description = "Riemannian metric '%s' " % self._name
        return self._final_repr(description)

    def _new_instance(self):
        r"""
        Create a :class:`RiemannMetricParal` instance on the same domain.
        
        """
        return self.__class__(self._fmodule, 'unnamed metric',
                              latex_name=r'\mbox{unnamed metric}')


#*****************************************************************************

class LorentzMetricParal(MetricParal):
    r"""
    Lorentzian metric with values on a parallelizable open subset of a 
    differentiable manifold.
    
    A Lorentzian metric is a field of symmetric bilinear 
    forms with signature `(-,+,\cdots,+)` or `(+,-,\cdots,-)`. 

    See :class:`MetricParal` for a complete documentation. 
    
    INPUT:
    
    - ``vector_field_module`` -- free module `\mathcal{X}(U,\Phi)` of vector 
      fields along `U` with values on `\Phi(U)\subset V \subset M`
    - ``name`` -- name given to the metric
    - ``signature`` -- (default: 'positive') sign of the metric signature: 
        * if set to 'positive', the signature is n-2, where n is the manifold's
          dimension, i.e. `(-,+,\cdots,+)`
        * if set to 'negative', the signature is -n+2, i.e. `(+,-,\cdots,-)`
    - ``latex_name`` -- (default: None) LaTeX symbol to denote the metric; if
      none, it is formed from ``name``      

    EXAMPLE:
    
    Metric of Minkowski spacetime::
    
        sage: M = Manifold(4, 'M')
        sage: c_cart.<t,x,y,z> = M.chart()
        sage: g = M.lorentz_metric('g') ; g
        Lorentzian metric 'g' on the 4-dimensional manifold 'M'
        sage: type(g)
        <class 'sage.geometry.manifolds.metric.LorentzMetricParal'>
        sage: g.parent()
        free module T^(0,2)(M) of type-(0,2) tensors fields on the 4-dimensional manifold 'M'
        sage: g[0,0], g[1,1], g[2,2], g[3,3] = -1, 1, 1, 1
        sage: g.view()
        g = -dt*dt + dx*dx + dy*dy + dz*dz
        sage: g.signature()
        2
        
    The negative signature convention can be chosen::
    
        sage: g1 = M.lorentz_metric('g', signature='negative') 
        sage: g1.signature()
        -2

    The Minkowski metric is flat::
    
        sage: g.riemann()
        tensor field 'Riem(g)' of type (1,3) on the 4-dimensional manifold 'M'
        sage: g.riemann().view()
        Riem(g) = 0

    """
    def __init__(self, vector_field_module, name, signature='positive', 
                 latex_name=None):
        dim = vector_field_module._ambient_domain._manifold._dim
        if signature=='positive':
            signat = dim - 2
        else:
            signat = 2 - dim
        MetricParal.__init__(self, vector_field_module, name, signature=signat,
                             latex_name=latex_name)

    def _repr_(self):
        r"""
        String representation of the object.
        """
        description = "Lorentzian metric '%s' " % self._name
        return self._final_repr(description)

    def _new_instance(self):
        r"""
        Create a :class:`LorentzMetricParal` instance on the same domain.
        
        """
        if self._signature >= 0:
            signature_type = 'positive'
        else:
            signature_type = 'negative'            
        return self.__class__(self._fmodule, 'unnamed metric', 
                              signature=signature_type,
                              latex_name=r'\mbox{unnamed metric}')

