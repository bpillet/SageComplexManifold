r"""
Tensors on free modules

The class :class:`FreeModuleTensor` implements tensors over a free module `M`,
i.e. elements of the free module `T^{(k,l)}(M)` of tensors of type `(k,l)`
acting as multilinear forms on `M`. 

A *tensor of type* `(k,l)` is a multilinear map:

.. MATH::

    \underbrace{M^*\times\cdots\times M^*}_{k\ \; \mbox{times}}
    \times \underbrace{M\times\cdots\times M}_{l\ \; \mbox{times}}
    \longrightarrow R
    
where `R` is the commutative ring over which the free module `M` is defined and
`M^*=\mathrm{Hom}_R(M,R)` is the dual of `M`. The integer `k+l` is called the 
*tensor rank*. 

Various derived classes of :class:`FreeModuleTensor` are devoted to specific 
tensors:

* :class:`FiniteRankFreeModuleElement` for elements of `M`, considered as 
  type-(1,0) tensors thanks to the canonical identification `M^{**}=M`, which
  holds since `M` is a free module of finite rank

* :class:`~sage.tensor.modules.free_module_alt_form.FreeModuleAltForm` for 
  fully antisymmetric type-`(0,l)` tensors (alternating forms)

  * :class:`~sage.tensor.modules.free_module_alt_form.FreeModuleLinForm` for 
    type-(0,1) tensors (linear forms)

* :class:`~sage.tensor.modules.free_module_tensor_spec.FreeModuleEndomorphism` 
  for type-(1,1) tensors (endomorphisms)

  * :class:`~sage.tensor.modules.free_module_tensor_spec.FreeModuleAutomorphism` 
    for invertible endomorphisms

    * :class:`~sage.tensor.modules.free_module_tensor_spec.FreeModuleIdentityMap` 
      for the identity map on a free module

:class:`FreeModuleTensor` is a Sage *element* class, the corresponding *parent*
class being :class:`~sage.tensor.modules.tensor_free_module.TensorFreeModule`. 


AUTHORS:

- Eric Gourgoulhon, Michal Bejger (2014): initial version

EXAMPLES:

    A tensor of type (1,1) on a rank-3 free module over `\ZZ`::
    
        sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
        sage: t = M.tensor((1,1), name='t') ; t
        endomorphism t on the rank-3 free module M over the Integer Ring
        sage: t.parent()
        free module of type-(1,1) tensors on the rank-3 free module M over the Integer Ring
        sage: t.parent() is M.tensor_module(1,1)
        True
        sage: t in M.tensor_module(1,1)
        True
        
    Setting some component of the tensor in a given basis::
    
        sage: e = M.basis('e') ; e
        basis (e_0,e_1,e_2) on the rank-3 free module M over the Integer Ring
        sage: t.set_comp(e)[0,0] = -3  # the component [0,0] w.r.t. basis e is set to -3
        
    The unset components are assumed to be zero::
    
        sage: t.comp(e)[:]  # list of all components w.r.t. basis e
        [-3  0  0]
        [ 0  0  0]
        [ 0  0  0]
        sage: t.view(e)  # expansion of t on the basis e_i*e^j of T^(1,1)(M) 
        t = -3 e_0*e^0

    The commands t.set_comp(e) and t.comp(e) can be abridged by providing 
    the basis as the first argument in the square brackets::
    
        sage: t[e,0,0] = -3
        sage: t[e,:]
        [-3  0  0]
        [ 0  0  0]
        [ 0  0  0]

    Actually, since e is M's default basis, the mention of e can be omitted::
    
        sage: t[0,0] = -3
        sage: t[:]
        [-3  0  0]
        [ 0  0  0]
        [ 0  0  0]
    
    Tensor components can be modified (reset) at any time::
    
        sage: t[0,0] = 0
        sage: t[:]
        [0 0 0]
        [0 0 0]
        [0 0 0]

    Checking that t is zero::
    
        sage: t.is_zero()
        True
        sage: t == 0
        True
        sage: t == M.tensor_module(1,1).zero()  # the zero element of the module of all type-(1,1) tensors on M
        True

    The components are managed by the class :class:`~sage.tensor.modules.comp.Components`::
    
        sage: type(t.comp(e))
        <class 'sage.tensor.modules.comp.Components'>

    Only non-zero components are actually stored, in the dictionary :attr:`_comp`
    of class :class:`~sage.tensor.modules.comp.Components`, whose keys are the indices::
    
        sage: t.comp(e)._comp
        {}
        sage: t.set_comp(e)[0,0] = -3 ; t.set_comp(e)[1,2] = 2
        sage: t.comp(e)._comp  # random output order (dictionary)
        {(0, 0): -3, (1, 2): 2}
        sage: t.view(e)
        t = -3 e_0*e^0 + 2 e_1*e^2

    Further tests of the comparison operator::
    
        sage: t.is_zero()
        False
        sage: t == 0
        False
        sage: t == M.tensor_module(1,1).zero()
        False
        sage: t1 = t.copy()
        sage: t1 == t
        True
        sage: t1[2,0] = 4
        sage: t1 == t
        False

    As a multilinear map `M^*\times M \rightarrow \ZZ`, the type-(1,1) tensor t 
    acts on pairs formed by a linear form and a module element::
    
        sage: a = M.linear_form(name='a') ; a[:] = (2, 1, -3) ; a
        linear form a on the rank-3 free module M over the Integer Ring
        sage: b = M([1,-6,2], name='b') ; b
        element b of the rank-3 free module M over the Integer Ring
        sage: t(a,b)
        -2

    
"""
#******************************************************************************
#       Copyright (C) 2014 Eric Gourgoulhon <eric.gourgoulhon@obspm.fr>
#       Copyright (C) 2014 Michal Bejger <bejger@camk.edu.pl>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.rings.integer import Integer
from sage.structure.element import ModuleElement  
from comp import Components, CompWithSym, CompFullySym, CompFullyAntiSym
from tensor_with_indices import TensorWithIndices

class FreeModuleTensor(ModuleElement):
    r"""
    Tensor over a free module of finite rank over a commutative ring.
    
    INPUT:
    
    - ``fmodule`` -- free module `M` over a commutative ring `R` (must be an 
      instance of :class:`FiniteRankFreeModule`)
    - ``tensor_type`` -- pair (k,l) with k being the contravariant rank and l 
      the covariant rank
    - ``name`` -- (default: None) name given to the tensor
    - ``latex_name`` -- (default: None) LaTeX symbol to denote the tensor; 
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

    A tensor of type (1,1) on a rank-3 free module over `\ZZ`::
    
        sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
        sage: t = M.tensor((1,1), name='t') ; t
        endomorphism t on the rank-3 free module M over the Integer Ring

    Tensors are *Element* objects whose parents are tensor free modules::
    
        sage: t.parent()
        free module of type-(1,1) tensors on the rank-3 free module M over the Integer Ring
        sage: t.parent() is M.tensor_module(1,1)
        True
        
    """
    def __init__(self, fmodule, tensor_type, name=None, latex_name=None,
                 sym=None, antisym=None):
        ModuleElement.__init__(self, fmodule.tensor_module(*tensor_type))
        self._fmodule = fmodule
        self._tensor_type = tuple(tensor_type)
        self._tensor_rank = self._tensor_type[0] + self._tensor_type[1]
        self._name = name
        if latex_name is None:
            self._latex_name = self._name
        else:
            self._latex_name = latex_name
        self._components = {}  # dict. of the sets of components on various 
                              # bases, with the bases as keys (initially empty)
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
        FreeModuleTensor._init_derived(self) 

    ####### Required methods for ModuleElement (beside arithmetic) #######
    
    def __nonzero__(self):
        r"""
        Return True if ``self`` is nonzero and False otherwise. 
        
        This method is called by self.is_zero(). 
        """
        basis = self.pick_a_basis()
        return not self._components[basis].is_zero()
        
    ####### End of required methods for ModuleElement (beside arithmetic) #######
    
    def _repr_(self):
        r"""
        String representation of the object.
        """
        # Special cases
        if self._tensor_type == (0,2) and self._sym == [(0,1)]:
            description = "symmetric bilinear form "
        else:
        # Generic case
            description = "type-(%s,%s) tensor" % \
                         (str(self._tensor_type[0]), str(self._tensor_type[1]))
        if self._name is not None:
            description += " " + self._name
        description += " on the " + str(self._fmodule)
        return description

    def _latex_(self):
        r"""
        LaTeX representation of the object.
        """
        if self._latex_name is None:
            return r'\mbox{' + str(self) + r'}'
        else:
           return self._latex_name

    def _init_derived(self):
        r"""
        Initialize the derived quantities
        """
        pass # no derived quantities

    def _del_derived(self):
        r"""
        Delete the derived quantities
        """
        pass # no derived quantities

    #### Simple accessors ####
    
    def tensor_type(self):
        r"""
        Return the tensor type of ``self``. 
        
        OUTPUT:
        
        - pair (k,l), where k is the contravariant rank and l is the covariant 
          rank
        
        EXAMPLES::
        
            sage: M = FiniteRankFreeModule(ZZ, 3)
            sage: M.an_element().tensor_type()
            (1, 0)
            sage: t = M.tensor((2,1))
            sage: t.tensor_type()
            (2, 1)
   
        """
        return self._tensor_type

    def tensor_rank(self):
        r"""
        Return the tensor rank of ``self``. 
        
        OUTPUT:
        
        - integer k+l, where k is the contravariant rank and l is the covariant 
          rank
        
        EXAMPLES::

            sage: M = FiniteRankFreeModule(ZZ, 3)
            sage: M.an_element().tensor_rank()
            1
            sage: t = M.tensor((2,1))
            sage: t.tensor_rank()
            3

        """
        return self._tensor_rank

    def symmetries(self):
        r"""
        Print the list of symmetries and antisymmetries.
        
        EXAMPLES:
        
        Various symmetries / antisymmetries for a rank-4 tensor::
        
            sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
            sage: t = M.tensor((4,0), name='T') # no symmetry declared
            sage: t.symmetries()
            no symmetry;  no antisymmetry
            sage: t = M.tensor((4,0), name='T', sym=(0,1))
            sage: t.symmetries()
            symmetry: (0, 1);  no antisymmetry
            sage: t = M.tensor((4,0), name='T', sym=[(0,1), (2,3)])
            sage: t.symmetries()
            symmetries: [(0, 1), (2, 3)];  no antisymmetry
            sage: t = M.tensor((4,0), name='T', sym=(0,1), antisym=(2,3))
            sage: t.symmetries()
            symmetry: (0, 1);  antisymmetry: (2, 3)
            
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

    def view(self, basis=None, format_spec=None):
        r"""
        Displays the tensor in terms of its expansion onto a given basis.
        
        The output is either text-formatted (console mode) or LaTeX-formatted
        (notebook mode). 
        
        INPUT:
                
        - ``basis`` -- (default: None) basis of the free module with respect to 
          which the tensor is expanded; if none is provided, the module's 
          default basis is assumed
        - ``format_spec`` -- (default: None) format specification passed to 
          ``self._fmodule._output_formatter`` to format the output.

        EXAMPLES:
        
        Display of a module element (type-(1,0) tensor)::
        
            sage: M = FiniteRankFreeModule(QQ, 2, name='M', start_index=1)
            sage: e = M.basis('e')
            sage: v = M([1/3,-2], name='v')
            sage: v.view()
            v = 1/3 e_1 - 2 e_2
            sage: latex(v.view())  # display in the notebook
            v = \frac{1}{3} e_1 -2 e_2

        Display of a linear form (type-(0,1) tensor)::
        
            sage: de = e.dual_basis()
            sage: w = - 3/4 * de[1] + de[2] ; w
            linear form on the rank-2 free module M over the Rational Field
            sage: w.set_name('w', latex_name='\omega')
            sage: w.view()
            w = -3/4 e^1 + e^2
            sage: latex(w.view())  # display in the notebook
            \omega = -\frac{3}{4} e^1 +e^2

        Display of a type-(1,1) tensor::
        
            sage: t = v*w ; t  # the type-(1,1) is formed as the tensor product of v by w
            endomorphism v*w on the rank-2 free module M over the Rational Field
            sage: t.view()
            v*w = -1/4 e_1*e^1 + 1/3 e_1*e^2 + 3/2 e_2*e^1 - 2 e_2*e^2
            sage: latex(t.view())  # display in the notebook
            v\otimes \omega = -\frac{1}{4} e_1\otimes e^1 + \frac{1}{3} e_1\otimes e^2 + \frac{3}{2} e_2\otimes e^1 -2 e_2\otimes e^2

        Display in a basis which is not the default one::
        
            sage: a = M.automorphism()
            sage: a[:] = [[1,2],[3,4]]
            sage: f = e.new_basis(a, 'f')
            sage: v.view(f) # the components w.r.t basis f are first computed via the change-of-basis formula defined by a
            v = -8/3 f_1 + 3/2 f_2
            sage: w.view(f)
            w = 9/4 f^1 + 5/2 f^2
            sage: t.view(f)
            v*w = -6 f_1*f^1 - 20/3 f_1*f^2 + 27/8 f_2*f^1 + 15/4 f_2*f^2

        The output format can be set via the argument ``output_formatter`` 
        passed at the module construction::

            sage: N = FiniteRankFreeModule(QQ, 2, name='N', start_index=1, output_formatter=Rational.numerical_approx)
            sage: e = N.basis('e')
            sage: v = N([1/3,-2], name='v')
            sage: v.view()  # default format (53 bits of precision)
            v = 0.333333333333333 e_1 - 2.00000000000000 e_2
            sage: latex(v.view()) 
            v = 0.333333333333333 e_1 -2.00000000000000 e_2
            
        The output format is then controled by the argument ``format_spec`` of
        the method :meth:`view`::
        
            sage: v.view(format_spec=10)  # 10 bits of precision
            v = 0.33 e_1 - 2.0 e_2
                    
        """
        from sage.misc.latex import latex
        from format_utilities import is_atomic, FormattedExpansion
        if basis is None:
            basis = self._fmodule._def_basis
        cobasis = basis.dual_basis()
        comp = self.comp(basis)
        terms_txt = []
        terms_latex = []
        n_con = self._tensor_type[0]
        for ind in comp.index_generator():
            ind_arg = ind + (format_spec,)
            coef = comp[ind_arg]
            if coef != 0:
                bases_txt = []
                bases_latex = []
                for k in range(n_con):
                    bases_txt.append(basis[ind[k]]._name)
                    bases_latex.append(latex(basis[ind[k]]))
                for k in range(n_con, self._tensor_rank):
                    bases_txt.append(cobasis[ind[k]]._name)
                    bases_latex.append(latex(cobasis[ind[k]]))
                basis_term_txt = "*".join(bases_txt)    
                basis_term_latex = r"\otimes ".join(bases_latex)    
                if coef == 1:
                    terms_txt.append(basis_term_txt)
                    terms_latex.append(basis_term_latex)
                elif coef == -1:
                    terms_txt.append("-" + basis_term_txt)
                    terms_latex.append("-" + basis_term_latex)
                else:
                    coef_txt = repr(coef)
                    coef_latex = latex(coef)
                    if is_atomic(coef_txt):
                        terms_txt.append(coef_txt + " " + basis_term_txt)
                    else:
                        terms_txt.append("(" + coef_txt + ") " + 
                                         basis_term_txt)
                    if is_atomic(coef_latex):
                        terms_latex.append(coef_latex + basis_term_latex)
                    else:
                        terms_latex.append(r"\left(" + coef_latex + r"\right)" + 
                                           basis_term_latex)
        if terms_txt == []:
            expansion_txt = "0"
        else:
            expansion_txt = terms_txt[0]
            for term in terms_txt[1:]:
                if term[0] == "-":
                    expansion_txt += " - " + term[1:]
                else:
                    expansion_txt += " + " + term
        if terms_latex == []:
            expansion_latex = "0"
        else:
            expansion_latex = terms_latex[0]
            for term in terms_latex[1:]:
                if term[0] == "-":
                    expansion_latex += term
                else:
                    expansion_latex += "+" + term
        result = FormattedExpansion(self)            
        if self._name is None:
            result.txt = expansion_txt
        else:
            result.txt = self._name + " = " + expansion_txt
        if self._latex_name is None:
            result.latex = expansion_latex
        else:
            result.latex = latex(self) + " = " + expansion_latex
        return result
             
    def set_name(self, name=None, latex_name=None):
        r"""
        Set (or change) the text name and LaTeX name of the tensor.

        INPUT:
        
        - ``name`` -- (string; default: None) name given to the tensor
        - ``latex_name`` -- (string; default: None) LaTeX symbol to denote the 
          tensor; if None while ``name`` is provided, the LaTeX symbol is set 
          to ``name``.

        """
        if name is not None:
            self._name = name
            if latex_name is None:
                self._latex_name = self._name
        if latex_name is not None:
            self._latex_name = latex_name
       
    def _new_instance(self):
        r"""
        Create a tensor of the same tensor type and with the same symmetries 
        as ``self``. 

        """
        return self.__class__(self._fmodule, self._tensor_type, sym=self._sym, 
                              antisym=self._antisym)

    def _new_comp(self, basis): 
        r"""
        Create some components in the given basis. 
        
        This method, to be called by :meth:`comp`, must be redefined by derived 
        classes to adapt the output to the relevant subclass of 
        :class:`~sage.tensor.modules.comp.Components`.
        
        OUTPUT:
        
        - an instance of :class:`~sage.tensor.modules.comp.Components` (or of one of its subclass)
        
        """
        fmodule = self._fmodule  # the base free module
        if self._sym == [] and self._antisym == []:
            return Components(fmodule._ring, basis, self._tensor_rank,
                              start_index=fmodule._sindex,
                              output_formatter=fmodule._output_formatter)
        for isym in self._sym:
            if len(isym) == self._tensor_rank:
                return CompFullySym(fmodule._ring, basis, self._tensor_rank,
                                    start_index=fmodule._sindex,
                                    output_formatter=fmodule._output_formatter)
        for isym in self._antisym:
            if len(isym) == self._tensor_rank:
                return CompFullyAntiSym(fmodule._ring, basis, self._tensor_rank, 
                                        start_index=fmodule._sindex,
                                     output_formatter=fmodule._output_formatter)
        return CompWithSym(fmodule._ring, basis, self._tensor_rank, 
                           start_index=fmodule._sindex, 
                           output_formatter=fmodule._output_formatter,
                           sym=self._sym, antisym=self._antisym)        

    def comp(self, basis=None, from_basis=None):
        r"""
        Return the components in a given basis.
        
        If the components are not known already, they are computed by the tensor
        change-of-basis formula from components in another basis. 
        
        INPUT:
        
        - ``basis`` -- (default: None) basis in which the components are 
          required; if none is provided, the components are assumed to refer to
          the module's default basis
        - ``from_basis`` -- (default: None) basis from which the
          required components are computed, via the tensor change-of-basis 
          formula, if they are not known already in the basis ``basis``; 
          if none, a basis is picked in ``self._components``.
 
        OUTPUT: 
        
        - components in the basis ``basis``, as an instance of the 
          class :class:`~sage.tensor.modules.comp.Components` 
        
        EXAMPLES:
        
        Components of a tensor of type-(1,1)::
        
            sage: M = FiniteRankFreeModule(ZZ, 3, name='M', start_index=1)
            sage: e = M.basis('e')
            sage: t = M.tensor((1,1), name='t')
            sage: t[1,2] = -3 ; t[3,3] = 2
            sage: t.comp()
            2-indices components w.r.t. basis (e_1,e_2,e_3) on the rank-3 free module M over the Integer Ring
            sage: t.comp() is t.comp(e)  # since e is M's default basis
            True
            sage: t.comp()[:]
            [ 0 -3  0]
            [ 0  0  0]
            [ 0  0  2]

        A direct access to the components w.r.t. the module's default basis is
        provided by the square brackets applied to the tensor itself::

            sage: t[1,2] is t.comp(e)[1,2]
            True
            sage: t[:]
            [ 0 -3  0]
            [ 0  0  0]
            [ 0  0  2]

        Components computed via a change-of-basis formula::
        
            sage: a = M.automorphism()
            sage: a[:] = [[0,0,1], [1,0,0], [0,-1,0]]
            sage: f = e.new_basis(a, 'f')
            sage: t.comp(f)
            2-indices components w.r.t. basis (f_1,f_2,f_3) on the rank-3 free module M over the Integer Ring
            sage: t.comp(f)[:]
            [ 0  0  0]
            [ 0  2  0]
            [-3  0  0]
            
        """
        fmodule = self._fmodule
        if basis is None: 
            basis = fmodule._def_basis
        if basis not in self._components:
            # The components must be computed from 
            # those in the basis from_basis
            if from_basis is None: 
                for known_basis in self._components:
                    if (known_basis, basis) in self._fmodule._basis_changes \
                        and (basis, known_basis) in self._fmodule._basis_changes:
                        from_basis = known_basis
                        break
                if from_basis is None:
                    raise ValueError("No basis could be found for computing " + 
                                     "the components in the " + str(basis))
            elif from_basis not in self._components:
                raise ValueError("The tensor components are not known in the " +
                                 "basis "+ str(from_basis))
            (n_con, n_cov) = self._tensor_type
            if n_cov > 0:
                if (from_basis, basis) not in fmodule._basis_changes:
                    raise ValueError("The change-of-basis matrix from the " + 
                                     str(from_basis) + " to the " + str(basis) 
                                     + " has not been set.")
                pp = \
                  fmodule._basis_changes[(from_basis, basis)].comp(from_basis)
                # pp not used if n_cov = 0 (pure contravariant tensor)
            if n_con > 0:
                if (basis, from_basis) not in fmodule._basis_changes:
                    raise ValueError("The change-of-basis matrix from the " + 
                                     str(basis) + " to the " + str(from_basis) +
                                     " has not been set.")
                ppinv = \
                  fmodule._basis_changes[(basis, from_basis)].comp(from_basis)
                # ppinv not used if n_con = 0 (pure covariant tensor)
            old_comp = self._components[from_basis]
            new_comp = self._new_comp(basis)
            rank = self._tensor_rank
            # loop on the new components:
            for ind_new in new_comp.non_redundant_index_generator(): 
                # Summation on the old components multiplied by the proper 
                # change-of-basis matrix elements (tensor formula): 
                res = 0 
                for ind_old in old_comp.index_generator(): 
                    t = old_comp[[ind_old]]
                    for i in range(n_con): # loop on contravariant indices
                        t *= ppinv[[ind_new[i], ind_old[i]]]
                    for i in range(n_con,rank):  # loop on covariant indices
                        t *= pp[[ind_old[i], ind_new[i]]]
                    res += t
                new_comp[ind_new] = res
            self._components[basis] = new_comp
            # end of case where the computation was necessary
        return self._components[basis]

    def set_comp(self, basis=None):
        r"""
        Return the components in a given basis for assignment.
        
        The components with respect to other bases are deleted, in order to 
        avoid any inconsistency. To keep them, use the method :meth:`add_comp` 
        instead.
        
        INPUT:
        
        - ``basis`` -- (default: None) basis in which the components are
          defined; if none is provided, the components are assumed to refer to 
          the module's default basis.
         
        OUTPUT: 
        
        - components in the given basis, as an instance of the 
          class :class:`~sage.tensor.modules.comp.Components`; if such components did not exist
          previously, they are created.  
        
        EXAMPLES:
        
        Setting components of a type-(1,1) tensor::
        
            sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
            sage: e = M.basis('e')
            sage: t = M.tensor((1,1), name='t')
            sage: t.set_comp()[0,1] = -3
            sage: t.view()
            t = -3 e_0*e^1
            sage: t.set_comp()[1,2] = 2
            sage: t.view()
            t = -3 e_0*e^1 + 2 e_1*e^2
            sage: t.set_comp(e)
            2-indices components w.r.t. basis (e_0,e_1,e_2) on the rank-3 free module M over the Integer Ring
            
        Setting components in a new basis::
        
            sage: f =  M.basis('f')
            sage: t.set_comp(f)[0,1] = 4
            sage: t._components.keys() # the components w.r.t. basis e have been deleted
            [basis (f_0,f_1,f_2) on the rank-3 free module M over the Integer Ring]
            sage: t.view(f)
            t = 4 f_0*f^1
            
        The components w.r.t. basis e can be deduced from those w.r.t. basis f,
        once a relation between the two bases has been set::
        
            sage: a = M.automorphism()
            sage: a[:] = [[0,0,1], [1,0,0], [0,-1,0]]
            sage: M.set_basis_change(e, f, a)
            sage: t.view(e)
            t = -4 e_1*e^2
            sage: t._components.keys()  # random output (dictionary keys)
            [basis (e_0,e_1,e_2) on the rank-3 free module M over the Integer Ring,
             basis (f_0,f_1,f_2) on the rank-3 free module M over the Integer Ring]

        """
        if basis is None: 
            basis = self._fmodule._def_basis
        if basis not in self._components:
            if basis not in self._fmodule._known_bases:
                raise ValueError("The " + str(basis) + " has not been " +
                                 "defined on the " + str(self._fmodule))
            self._components[basis] = self._new_comp(basis)
        self._del_derived() # deletes the derived quantities
        self.del_other_comp(basis)
        return self._components[basis]

    def add_comp(self, basis=None):
        r"""
        Return the components in a given basis for assignment, keeping the
        components in other bases. 
        
        To delete the components in other bases, use the method 
        :meth:`set_comp` instead. 
        
        INPUT:
        
        - ``basis`` -- (default: None) basis in which the components are
          defined; if none is provided, the components are assumed to refer to
          the module's default basis.
          
        .. WARNING::
        
            If the tensor has already components in other bases, it 
            is the user's responsability to make sure that the components
            to be added are consistent with them. 
         
        OUTPUT: 
        
        - components in the given basis, as an instance of the 
          class :class:`~sage.tensor.modules.comp.Components`; if such components did not exist
          previously, they are created.  
        
        EXAMPLES:
        
        Setting components of a type-(1,1) tensor::
        
            sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
            sage: e = M.basis('e')
            sage: t = M.tensor((1,1), name='t')
            sage: t.add_comp()[0,1] = -3
            sage: t.view()
            t = -3 e_0*e^1
            sage: t.add_comp()[1,2] = 2
            sage: t.view()
            t = -3 e_0*e^1 + 2 e_1*e^2
            sage: t.add_comp(e)
            2-indices components w.r.t. basis (e_0,e_1,e_2) on the rank-3 free module M over the Integer Ring
            
        Adding components in a new basis::
        
            sage: f =  M.basis('f')
            sage: t.add_comp(f)[0,1] = 4
            
        The components w.r.t. basis e have been kept::
        
            sage: t._components.keys() # # random output (dictionary keys) 
            [basis (e_0,e_1,e_2) on the rank-3 free module M over the Integer Ring,
             basis (f_0,f_1,f_2) on the rank-3 free module M over the Integer Ring]
            sage: t.view(f)
            t = 4 f_0*f^1
            sage: t.view(e)
            t = -3 e_0*e^1 + 2 e_1*e^2

        """
        if basis is None: basis = self._fmodule._def_basis
        if basis not in self._components:
            if basis not in self._fmodule._known_bases:
                raise ValueError("The " + str(basis) + " has not been " +
                                 "defined on the " + str(self._fmodule))
            self._components[basis] = self._new_comp(basis)
        self._del_derived() # deletes the derived quantities
        return self._components[basis]


    def del_other_comp(self, basis=None):
        r"""
        Delete all the components but those corresponding to ``basis``.
        
        INPUT:
        
        - ``basis`` -- (default: None) basis in which the components are
          kept; if none the module's default basis is assumed

        EXAMPLE:
        
        Deleting components of a module element::
        
            sage: M = FiniteRankFreeModule(ZZ, 3, name='M', start_index=1)
            sage: e = M.basis('e')
            sage: u = M([2,1,-5])
            sage: f = M.basis('f')
            sage: u.add_comp(f)[:] = [0,4,2]
            sage: u._components.keys() # random output (dictionary keys)
            [basis (e_1,e_2,e_3) on the rank-3 free module M over the Integer Ring,
             basis (f_1,f_2,f_3) on the rank-3 free module M over the Integer Ring]
            sage: u.del_other_comp(f)
            sage: u._components.keys()
            [basis (f_1,f_2,f_3) on the rank-3 free module M over the Integer Ring]

        Let us restore the components w.r.t. e and delete those w.r.t. f::
        
            sage: u.add_comp(e)[:] = [2,1,-5]
            sage: u._components.keys()  # random output (dictionary keys)
            [basis (e_1,e_2,e_3) on the rank-3 free module M over the Integer Ring,
             basis (f_1,f_2,f_3) on the rank-3 free module M over the Integer Ring]
            sage: u.del_other_comp()  # default argument: basis = e
            sage: u._components.keys()
            [basis (e_1,e_2,e_3) on the rank-3 free module M over the Integer Ring]

        """
        if basis is None: basis = self._fmodule._def_basis
        if basis not in self._components:
            raise ValueError("The components w.r.t. the " + 
                             str(basis) + " have not been defined.")
        to_be_deleted = []
        for other_basis in self._components:
            if other_basis != basis:
                to_be_deleted.append(other_basis)
        for other_basis in to_be_deleted:
            del self._components[other_basis]

    def __getitem__(self, args):
        r"""
        Return a component w.r.t. some basis.
        
        NB: if ``args`` is a string, this method acts as a shortcut for 
        tensor contractions and symmetrizations, the string containing 
        abstract indices.

        INPUT:
        
        - ``args`` -- list of indices defining the component; if [:] is 
          provided, all the components are returned. The basis can be passed
          as the first item of ``args``; if not, the free module's default 
          basis is assumed. 
    
        """
        if isinstance(args, str): # tensor with specified indices
            return TensorWithIndices(self, args).update()
        if isinstance(args, list):  # case of [[...]] syntax
            if isinstance(args[0], (int, Integer, slice)):
                basis = self._fmodule._def_basis
            else:
                basis = args[0]
                args = args[1:]
        else:
            if isinstance(args, (int, Integer, slice)):
                basis = self._fmodule._def_basis
            elif not isinstance(args[0], (int, Integer, slice)):
                basis = args[0]
                args = args[1:]
                if len(args)==1:
                    args = args[0]  # to accommodate for [e,:] syntax 
            else:
                basis = self._fmodule._def_basis
        return self.comp(basis)[args]

       
    def __setitem__(self, args, value):
        r"""
        Set a component w.r.t. some basis.

        INPUT:

        - ``args`` -- list of indices defining the component; if [:] is 
          provided, all the components are set. The basis can be passed
          as the first item of ``args``; if not, the free module's default 
          basis is assumed. 
        - ``value`` -- the value to be set or a list of values if ``args``
          == ``[:]``
   
        """        
        if isinstance(args, list):  # case of [[...]] syntax
            if isinstance(args[0], (int, Integer, slice, tuple)):
                basis = self._fmodule._def_basis
            else:
                basis = args[0]
                args = args[1:]
        else:
            if isinstance(args, (int, Integer, slice)):
                basis = self._fmodule._def_basis
            elif not isinstance(args[0], (int, Integer, slice)):
                basis = args[0]
                args = args[1:]
                if len(args)==1:
                    args = args[0]  # to accommodate for [e,:] syntax 
            else:
                basis = self._fmodule._def_basis
        self.set_comp(basis)[args] = value


    def copy(self):
        r"""
        Return an exact copy of ``self``.
        
        The name and the derived quantities are not copied. 
        
        EXAMPLES:
        
        Copy of a tensor of type (1,1)::
        
            sage: M = FiniteRankFreeModule(ZZ, 3, name='M', start_index=1)
            sage: e = M.basis('e')
            sage: t = M.tensor((1,1), name='t')
            sage: t[1,2] = -3 ; t[3,3] = 2
            sage: t1 = t.copy()
            sage: t1[:]
            [ 0 -3  0]
            [ 0  0  0]
            [ 0  0  2]
            sage: t1 == t
            True

        If the original tensor is modified, the copy is not::
        
            sage: t[2,2] = 4
            sage: t1[:]
            [ 0 -3  0]
            [ 0  0  0]
            [ 0  0  2]
            sage: t1 == t
            False

        """
        resu = self._new_instance()
        for basis, comp in self._components.iteritems():
             resu._components[basis] = comp.copy()
        return resu

    def common_basis(self, other):
        r"""
        Find a common basis for the components of ``self`` and ``other``. 
        
        In case of multiple common bases, the free module's default basis is 
        privileged. 
        If the current components of ``self`` and ``other`` are all relative to
        different bases, a common basis is searched by performing a component
        transformation, via the transformations listed in 
        ``self._fmodule._basis_changes``, still privileging transformations to 
        the free module's default basis.
        
        INPUT:
        
        - ``other`` -- a tensor (instance of :class:`FreeModuleTensor`)
        
        OUPUT:
        
        - instance of 
          :class:`~sage.tensor.modules.free_module_basis.FreeModuleBasis`
          representing the common basis; if no common basis is found, None is 
          returned. 
          
        EXAMPLES:
        
        Common basis for the components of two module elements::
        
            sage: M = FiniteRankFreeModule(ZZ, 3, name='M', start_index=1)
            sage: e = M.basis('e')
            sage: u = M([2,1,-5])
            sage: f = M.basis('f')
            sage: M._basis_changes.clear() # to ensure that bases e and f are unrelated at this stage
            sage: v = M([0,4,2], basis=f)
            sage: u.common_basis(v) 
            
        The above result is None since u and v have been defined on different
        bases and no connection between these bases have been set::
        
            sage: u._components.keys()
            [basis (e_1,e_2,e_3) on the rank-3 free module M over the Integer Ring]
            sage: v._components.keys()
            [basis (f_1,f_2,f_3) on the rank-3 free module M over the Integer Ring]

        Linking bases e and f changes the result::
        
            sage: a = M.automorphism()
            sage: a[:] = [[0,0,1], [1,0,0], [0,-1,0]]
            sage: M.set_basis_change(e, f, a)
            sage: u.common_basis(v)
            basis (e_1,e_2,e_3) on the rank-3 free module M over the Integer Ring

        Indeed, v is now known in basis e::
        
            sage: v._components.keys() # random output (dictionary keys)
            [basis (f_1,f_2,f_3) on the rank-3 free module M over the Integer Ring,
             basis (e_1,e_2,e_3) on the rank-3 free module M over the Integer Ring]

        """
        # Compatibility checks:
        if not isinstance(other, FreeModuleTensor):
            raise TypeError("The argument must be a tensor on a free module.")
        fmodule = self._fmodule
        if other._fmodule != fmodule:
            raise TypeError("The two tensors are not defined on the same " +
                            "free module.")
        def_basis = fmodule._def_basis
        #
        # 1/ Search for a common basis among the existing components, i.e. 
        #    without performing any component transformation. 
        #    -------------------------------------------------------------
        if def_basis in self._components and def_basis in other._components:
            return def_basis # the module's default basis is privileged
        for basis1 in self._components:
            if basis1 in other._components:
                return basis1
        # 2/ Search for a common basis via one component transformation
        #    ----------------------------------------------------------
        # If this point is reached, it is indeed necessary to perform at least 
        # one component transformation to get a common basis
        if def_basis in self._components:
            for obasis in other._components:
                if (obasis, def_basis) in fmodule._basis_changes:
                    other.comp(def_basis, from_basis=obasis)
                    return def_basis
        if def_basis in other._components:
            for sbasis in self._components:
                if (sbasis, def_basis) in fmodule._basis_changes:
                    self.comp(def_basis, from_basis=sbasis)
                    return def_basis
        # If this point is reached, then def_basis cannot be a common basis
        # via a single component transformation
        for sbasis in self._components:
            for obasis in other._components:
                if (obasis, sbasis) in fmodule._basis_changes:
                    other.comp(sbasis, from_basis=obasis)
                    return sbasis
                if (sbasis, obasis) in fmodule._basis_changes:
                    self.comp(obasis, from_basis=sbasis)
                    return obasis
        #
        # 3/ Search for a common basis via two component transformations
        #    -----------------------------------------------------------
        # If this point is reached, it is indeed necessary to perform at two
        # component transformation to get a common basis
        for sbasis in self._components:
            for obasis in other._components:
                if (sbasis, def_basis) in fmodule._basis_changes and \
                   (obasis, def_basis) in fmodule._basis_changes:
                    self.comp(def_basis, from_basis=sbasis)
                    other.comp(def_basis, from_basis=obasis)
                    return def_basis
                for basis in fmodule._known_bases:
                    if (sbasis, basis) in fmodule._basis_changes and \
                       (obasis, basis) in fmodule._basis_changes:
                        self.comp(basis, from_basis=sbasis)
                        other.comp(basis, from_basis=obasis)
                        return basis
        #
        # If this point is reached, no common basis could be found, even at 
        # the price of component transformations:
        return None
    
    def pick_a_basis(self):
        r"""
        Return a basis in which the tensor components are defined. 
        
        The free module's default basis is privileged. 

        OUTPUT:
        
        - instance of 
          :class:`~sage.tensor.modules.free_module_basis.FreeModuleBasis` 
          representing the basis 

        """
        if self._fmodule._def_basis in self._components:
            return self._fmodule._def_basis  # the default basis is privileged
        else:
            # a basis is picked arbitrarily:
            return self._components.items()[0][0]  

    def __eq__(self, other):
        r"""
        Comparison (equality) operator. 
        
        INPUT:
        
        - ``other`` -- a tensor or 0
        
        OUTPUT:
        
        - True if ``self`` is equal to ``other`` and False otherwise
        
        """
        if self._tensor_rank == 0:
            raise NotImplementedError("Scalar comparison not implemented.")
        if isinstance(other, (int, Integer)): # other should be 0
            if other == 0:
                return self.is_zero()
            else:
                return False
        elif not isinstance(other, FreeModuleTensor):
            return False
        else: # other is another tensor
            if other._fmodule != self._fmodule:
                return False
            if other._tensor_type != self._tensor_type:
                return False
            basis = self.common_basis(other)
            if basis is None:
                raise ValueError("No common basis for the comparison.")
            return bool(self._components[basis] == other._components[basis])

    def __ne__(self, other):
        r"""
        Inequality operator. 
        
        INPUT:
        
        - ``other`` -- a tensor or 0
        
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
        result = self._new_instance()
        for basis in self._components:
            result._components[basis] = + self._components[basis]
        if self._name is not None:
            result._name = '+' + self._name 
        if self._latex_name is not None:
            result._latex_name = '+' + self._latex_name
        return result

    def __neg__(self):
        r"""
        Unary minus operator. 
        
        OUTPUT:
        
        - the tensor `-T`, where `T` is ``self``
    
        """
        result = self._new_instance()
        for basis in self._components:
            result._components[basis] = - self._components[basis]
        if self._name is not None:
            result._name = '-' + self._name 
        if self._latex_name is not None:
            result._latex_name = '-' + self._latex_name
        return result

    ######### ModuleElement arithmetic operators ########
    
    def _add_(self, other):
        r"""
        Tensor addition. 
        
        INPUT:
        
        - ``other`` -- a tensor, of the same type as ``self``
        
        OUPUT:
        
        - the tensor resulting from the addition of ``self`` and ``other``
        
        """
        # No need for consistency check since self and other are guaranted
        # to belong to the same tensor module
        if other == 0:
            return +self
        basis = self.common_basis(other)
        if basis is None:
            raise ValueError("No common basis for the addition.")
        comp_result = self._components[basis] + other._components[basis]
        result = self._fmodule.tensor_from_comp(self._tensor_type, comp_result)
        if self._name is not None and other._name is not None:
            result._name = self._name + '+' + other._name
        if self._latex_name is not None and other._latex_name is not None:
            result._latex_name = self._latex_name + '+' + other._latex_name
        return result

    def _sub_(self, other):
        r"""
        Tensor subtraction. 
        
        INPUT:
        
        - ``other`` -- a tensor, of the same type as ``self``
        
        OUPUT:
        
        - the tensor resulting from the subtraction of ``other`` from ``self``
        
        """
        # No need for consistency check since self and other are guaranted
        # to belong to the same tensor module
        if other == 0:
            return +self
        basis = self.common_basis(other)
        if basis is None:
            raise ValueError("No common basis for the subtraction.")
        comp_result = self._components[basis] - other._components[basis]
        result = self._fmodule.tensor_from_comp(self._tensor_type, comp_result)
        if self._name is not None and other._name is not None:
            result._name = self._name + '-' + other._name
        if self._latex_name is not None and other._latex_name is not None:
            result._latex_name = self._latex_name + '-' + other._latex_name
        return result

    def _rmul_(self, other):
        r"""
        Multiplication on the left by ``other``. 
        
        """
        #!# The following test is probably not necessary:
        if isinstance(other, FreeModuleTensor):
            raise NotImplementedError("Left tensor product not implemented.")
        # Left multiplication by a scalar: 
        result = self._new_instance()
        for basis in self._components:
            result._components[basis] = other * self._components[basis]
        return result

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
        from format_utilities import format_mul_txt, format_mul_latex
        if isinstance(other, FreeModuleTensor):
            basis = self.common_basis(other)
            if basis is None:
                raise ValueError("No common basis for the tensor product.")
            comp_prov = self._components[basis] * other._components[basis]
            # Reordering of the contravariant and covariant indices:
            k1, l1 = self._tensor_type
            k2, l2 = other._tensor_type
            if l1 != 0:
                comp_result = comp_prov.swap_adjacent_indices(k1, 
                                                              self._tensor_rank, 
                                                              self._tensor_rank+k2)
            else:
                comp_result = comp_prov  # no reordering is necessary
            result = self._fmodule.tensor_from_comp((k1+k2, l1+l2), comp_result)
            result._name = format_mul_txt(self._name, '*', other._name)
            result._latex_name = format_mul_latex(self._latex_name, r'\otimes ', 
                                                 other._latex_name)
            return result
        else:
            # multiplication by a scalar: 
            result = self._new_instance()
            for basis in self._components:
                result._components[basis] = other * self._components[basis]
            return result


    def __div__(self, other):
        r"""
        Division (by a scalar)
        """
        result = self._new_instance()
        for basis in self._components:
            result._components[basis] = self._components[basis] / other
        return result
        

    def __call__(self, *args):
        r"""
        The tensor acting on linear forms and module elements as a multilinear 
        map.
        
        INPUT:
        
        - ``*args`` -- list of k linear forms and l module elements, ``self`` 
          being a tensor of type (k,l). 
          
        """
        from free_module_alt_form import FreeModuleLinForm
        # Consistency checks:
        p = len(args)
        if p != self._tensor_rank:
            raise TypeError(str(self._tensor_rank) + 
                            " arguments must be provided.")
        for i in range(self._tensor_type[0]):
            if not isinstance(args[i], FreeModuleLinForm):
                raise TypeError("The argument no. " + str(i+1) + 
                                " must be a linear form.")
        for i in range(self._tensor_type[0],p):
            if not isinstance(args[i], FiniteRankFreeModuleElement):
                raise TypeError("The argument no. " + str(i+1) + 
                                " must be a module element.")
        fmodule = self._fmodule
        # Search for a common basis
        basis = None
        # First try with the module's default basis 
        def_basis = fmodule._def_basis
        if def_basis in self._components:
            basis = def_basis
            for arg in args:
                if def_basis not in arg._components:
                    basis = None
                    break
        if basis is None:
            # Search for another basis:
            for bas in self._components:
                basis = bas
                for arg in args:
                    if bas not in arg._components:
                        basis = None
                        break
                if basis is not None: # common basis found ! 
                    break
        if basis is None:
            # A last attempt to find a common basis, possibly via a 
            # change-of-components transformation
            for arg in args:
                self.common_basis(arg) # to trigger some change of components
            for bas in self._components:
                basis = bas
                for arg in args:
                    if bas not in arg._components:
                        basis = None
                        break
                if basis is not None: # common basis found ! 
                    break
        if basis is None:
            raise ValueError("No common basis for the components.")
        t = self._components[basis]
        v = [args[i]._components[basis] for i in range(p)]
        res = 0
        for ind in t.index_generator():
            prod = t[[ind]]
            for i in range(p):
                prod *= v[i][[ind[i]]]
            res += prod
        # Name of the output:
        if hasattr(res, '_name'): 
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
            res._name = res_name       
        # LaTeX symbol of the output:
        if hasattr(res, '_latex_name'): 
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
            res._latex_name = res_latex
        return res

    def trace(self, pos1=0, pos2=1):
        r""" 
        Trace (contraction) on two slots of the tensor. 
        
        INPUT:
            
        - ``pos1`` -- (default: 0) position of the first index for the 
          contraction, with the convention ``pos1=0`` for the first slot
        - ``pos2`` -- (default: 1) position of the second index for the 
          contraction, with the same convention as for ``pos1``. The variance 
          type of ``pos2`` must be opposite to that of ``pos1``
          
        OUTPUT:
        
        - tensor or scalar resulting from the (pos1, pos2) contraction
       
        EXAMPLES:
        
        Trace of a type-(1,1) tensor::

            sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
            sage: e = M.basis('e') ; e
            basis (e_0,e_1,e_2) on the rank-3 free module M over the Integer Ring
            sage: a = M.tensor((1,1), name='a') ; a
            endomorphism a on the rank-3 free module M over the Integer Ring
            sage: a[:] = [[1,2,3], [4,5,6], [7,8,9]]
            sage: a.trace() 
            15 
            sage: a.trace(0,1)  # equivalent to above (contraction of slot 0 with slot 1)
            15
            sage: a.trace(1,0)  # the order of the slots does not matter
            15
            
        Instead of the explicit call to the method :meth:`trace`, one
        may use the index notation with Einstein convention (summation over
        repeated indices); it suffices to pass the indices as a string inside
        square brackets::
        
            sage: a['^i_i']
            15

        The letter 'i' to denote the repeated index can be replaced by any
        other letter::
        
            sage: a['^s_s']
            15

        Moreover, the symbol '^' can be omitted::
        
            sage: a['i_i']
            15

        The contraction on two slots having the same tensor type cannot occur::
        
            sage: b =  M.tensor((2,0), name='b') ; b
            type-(2,0) tensor b on the rank-3 free module M over the Integer Ring
            sage: b[:] = [[1,2,3], [4,5,6], [7,8,9]]
            sage: b.trace(0,1)
            Traceback (most recent call last):
            ...
            IndexError: Contraction on two contravariant indices is not allowed.

        The contraction either preserves or destroys the symmetries::
        
            sage: b = M.alternating_form(2, 'b') ; b
            alternating form b of degree 2 on the rank-3 free module M over the Integer Ring
            sage: b[0,1], b[0,2], b[1,2] = 3, 2, 1
            sage: t = a*b ; t
            type-(1,3) tensor a*b on the rank-3 free module M over the Integer Ring
            sage: # by construction, t is a tensor field antisymmetric w.r.t. its last two slots:
            sage: t.symmetries()
            no symmetry;  antisymmetry: (2, 3)
            sage: s = t.trace(0,1) ; s   # contraction on the first two slots
            alternating form of degree 2 on the rank-3 free module M over the Integer Ring
            sage: s.symmetries()    # the antisymmetry is preserved
            no symmetry;  antisymmetry: (0, 1)
            sage: s[:]
            [  0  45  30]
            [-45   0  15]
            [-30 -15   0]
            sage: s == 15*b  # check
            True
            sage: s = t.trace(0,2) ; s   # contraction on the first and third slots
            type-(0,2) tensor on the rank-3 free module M over the Integer Ring
            sage: s.symmetries()  # the antisymmetry has been destroyed by the above contraction:
            no symmetry;  no antisymmetry
            sage: s[:]  # indeed:
            [-26  -4   6]
            [-31  -2   9]
            [-36   0  12]
            sage: s[:] == matrix( [[sum(t[k,i,k,j] for k in M.irange()) for j in M.irange()] for i in M.irange()] )  # check
            True
            
        Use of index notation instead of :meth:`trace`::
        
            sage: t['^k_kij'] == t.trace(0,1)
            True
            sage: t['^k_{kij}'] == t.trace(0,1) # LaTeX notation
            True
            sage: t['^k_ikj'] == t.trace(0,2)
            True
            sage: t['^k_ijk'] == t.trace(0,3)
            True

        Index symbols not involved in the contraction may be replaced by
        dots::
        
            sage: t['^k_k..'] == t.trace(0,1)
            True
            sage: t['^k_.k.'] == t.trace(0,2)
            True
            sage: t['^k_..k'] == t.trace(0,3)
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
        # Frame selection for the computation: 
        if self._fmodule._def_basis in self._components:
            basis = self._fmodule._def_basis
        else: # a basis is picked arbitrarily:
            basis = self.pick_a_basis()     
        resu_comp = self._components[basis].trace(pos1, pos2)
        if self._tensor_rank == 2:  # result is a scalar
            return resu_comp
        else:
            return self._fmodule.tensor_from_comp((k_con-1, l_cov-1), resu_comp)

    def contract(self, *args):
        r""" 
        Contraction on one or more indices with another tensor. 
        
        INPUT:
            
        - ``pos1`` -- positions of the indices in ``self`` involved in the
          contraction; ``pos1`` must be a sequence of integers, with 0 standing
          for the first index position, 1 for the second one, etc. If ``pos1`` 
          is not provided, a single contraction on the last index position of
          ``self`` is assumed
        - ``other`` -- the tensor to contract with
        - ``pos2`` -- positions of the indices in ``other`` involved in the
          contraction, with the same conventions as for ``pos1``. If ``pos2``
          is not provided, a single contraction on the first index position of
          ``other`` is assumed
                    
        OUTPUT:
        
        - tensor resulting from the contraction at the positions ``pos1`` and
          ``pos2`` of ``self`` with ``other``
       
        EXAMPLES:
        
        Contraction of a tensor of type (0,1) with a tensor of type (1,0)::
        
            sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
            sage: e = M.basis('e')
            sage: a = M.linear_form()  # tensor of type (0,1) is a linear form
            sage: a[:] = [-3,2,1]
            sage: b = M([2,5,-2])  # tensor of type (1,0) is a module element
            sage: s = a.contract(b) ; s
            2
            sage: s in M.base_ring()
            True
            sage: s == a[0]*b[0] + a[1]*b[1] + a[2]*b[2]  # check of the computation
            True

        The positions of the contraction indices can be set explicitely::
        
            sage: s == a.contract(0, b, 0)
            True
            sage: s == a.contract(0, b)
            True
            sage: s == a.contract(b, 0)
            True
        
        Instead of the explicit call to the method :meth:`contract`, the index 
        notation can be used to specify the contraction, via Einstein 
        conventation (summation on repeated indices); it suffices to pass the 
        indices as a string inside square brackets::
        
            sage: s1 = a['_i']*b['^i'] ; s1
            2
            sage: s1 == s
            True

        In the present case, performing the contraction is identical to 
        applying the linear form to the module element::
        
            sage: a.contract(b) == a(b)
            True

        or to applying the module element, considered as a tensor of type (1,0),
        to the linear form::
        
            sage: a.contract(b) == b(a)
            True

        We have also::

            sage: a.contract(b) == b.contract(a)
            True

        Contraction of a tensor of type (1,1) with a tensor of type (1,0)::
        
            sage: a = M.endomorphism()  # tensor of type (1,1)
            sage: a[:] = [[-1,2,3],[4,-5,6],[7,8,9]]
            sage: s = a.contract(b) ; s
            element of the rank-3 free module M over the Integer Ring
            sage: s.view()
            2 e_0 - 29 e_1 + 36 e_2
    
        Since the index positions have not been specified, the contraction
        takes place on the last position of a (i.e. no. 1) and the first
        position of b (i.e. no. 0)::
        
            sage: a.contract(b) == a.contract(1, b, 0)
            True
            sage: a.contract(b) == b.contract(0, a, 1)
            True
            sage: a.contract(b) == b.contract(a, 1) 
            True
            
        Using the index notation with Einstein convention::
        
            sage: a['^i_j']*b['^j'] == a.contract(b)
            True

        The index i can be replaced by a dot::
        
            sage: a['^._j']*b['^j'] == a.contract(b)
            True

        and the symbol '^' may be omitted, the distinction between 
        contravariant and covariant indices being the position with respect to 
        the symbol '_'::
        
            sage: a['._j']*b['j'] == a.contract(b)
            True
                        
        Contraction is possible only between a contravariant index and a 
        covariant one::
        
            sage: a.contract(0, b)
            Traceback (most recent call last):
            ...
            TypeError: Contraction on two contravariant indices not permitted.

        In the present case, performing the contraction is identical to 
        applying the endomorphism to the module element::
        
            sage: a.contract(b) == a(b)
            True

        Contraction of a tensor of type (2,1) with a tensor of type (0,2)::
        
            sage: a = a*b ; a
            type-(2,1) tensor on the rank-3 free module M over the Integer Ring
            sage: b = M.tensor((0,2))
            sage: b[:] = [[-2,3,1], [0,-2,3], [4,-7,6]]
            sage: s = a.contract(1, b, 1) ; s
            type-(1,2) tensor on the rank-3 free module M over the Integer Ring
            sage: s[:]
            [[[-9, 16, 39], [18, -32, -78], [27, -48, -117]],
             [[36, -64, -156], [-45, 80, 195], [54, -96, -234]],
             [[63, -112, -273], [72, -128, -312], [81, -144, -351]]]
            sage: # check of the computation:
            sage: for i in range(3):
            ....:     for j in range(3):
            ....:         for k in range(3):
            ....:             print s[i,j,k] == a[i,0,j]*b[k,0]+a[i,1,j]*b[k,1]+a[i,2,j]*b[k,2],
            ....:             
            True True True True True True True True True True True True True True True True True True True True True True True True True True True

        Using index notation::
        
            sage: a['il_j']*b['_kl'] == a.contract(1, b, 1)
            True
            
        LaTeX notation are allowed::
        
            sage: a['^{il}_j']*b['_{kl}'] == a.contract(1, b, 1)
            True

        Indices not involved in the contraction may be replaced by dots::
        
            sage: a['.l_.']*b['_.l'] == a.contract(1, b, 1)
            True
       
        The two tensors do not have to be defined on the same basis for the 
        contraction to take place, reflecting the fact that the contraction is 
        basis-independent::
        
            sage: A = M.automorphism()
            sage: A[:] =  [[0,0,1], [1,0,0], [0,-1,0]]
            sage: h = e.new_basis(A, 'h')
            sage: b.comp(h)[:]  # forces the computation of b's components w.r.t. basis h
            [-2 -3  0]
            [ 7  6 -4]
            [ 3 -1 -2]
            sage: b.del_other_comp(h)  # deletes components w.r.t. basis e
            sage: b._components.keys()  # indeed:
            [basis (h_0,h_1,h_2) on the rank-3 free module M over the Integer Ring]
            sage: a._components.keys()  # while a is known only in basis e:
            [basis (e_0,e_1,e_2) on the rank-3 free module M over the Integer Ring]
            sage: s1 = a.contract(1, b, 1) ; s1  # yet the computation is possible
            type-(1,2) tensor on the rank-3 free module M over the Integer Ring
            sage: s1 == s  # ... and yields the same result as previously:
            True

        The contraction can be performed on more than a single index; for 
        instance a 2-indices contraction of a type-(2,1) tensor with a 
        type-(1,2) one is::
        
            sage: a  # a is a tensor of type-(2,1)
            type-(2,1) tensor on the rank-3 free module M over the Integer Ring
            sage: b = M([1,-1,2])*b ; b # a tensor of type (1,2)
            type-(1,2) tensor on the rank-3 free module M over the Integer Ring
            sage: s = a.contract(1,2,b,1,0) ; s # the double contraction 
            endomorphism on the rank-3 free module M over the Integer Ring
            sage: s[:]
            [ -36   30   15]
            [-252  210  105]
            [-204  170   85]
            sage: s == a['^.k_l']*b['^l_k.']  # the same thing in index notation
            True
            
        """
        #
        # Treatment of the input
        #
        nargs = len(args)
        for i, arg in enumerate(args):
            if isinstance(arg, FreeModuleTensor):
                other = arg
                it = i
                break
        else:
            raise TypeError("A tensor must be provided in the argument list.")
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
        k1, l1 = self._tensor_type
        k2, l2 = other._tensor_type
        for i in range(ncontr):
            p1 = pos1[i]
            p2 = pos2[i]
            if p1 < k1 and p2 < k2:
                raise TypeError("Contraction on two contravariant indices " + 
                                "not permitted.")
            if p1 >= k1 and p2 >= k2:
                raise TypeError("Contraction on two covariant indices " + 
                                "not permitted.")
        #
        # Contraction at the component level
        #
        basis = self.common_basis(other)
        if basis is None:
            raise ValueError("No common basis for the contraction.")
        args = pos1 + (other._components[basis],) + pos2
        cmp_res = self._components[basis].contract(*args)
        if self._tensor_rank + other._tensor_rank - 2*ncontr == 0:
            # Case of scalar output:
            return cmp_res
        #
        # Reordering of the indices to have all contravariant indices first:
        #
        nb_cov_s = 0  # Number of covariant indices of self not involved in the
                      # contraction
        for pos in range(k1,k1+l1):
            if pos not in pos1:
                nb_cov_s += 1
        nb_con_o = 0  # Number of contravariant indices of other not involved 
                      # in the contraction
        for pos in range(0,k2):
            if pos not in pos2:
                nb_con_o += 1
        if nb_cov_s != 0 and nb_con_o !=0:
            # some reodering is necessary:
            p2 = k1 + l1 - ncontr 
            p1 = p2 - nb_cov_s
            p3 = p2 + nb_con_o
            cmp_res = cmp_res.swap_adjacent_indices(p1, p2, p3)
        type_res = (k1+k2-ncontr, l1+l2-ncontr)
        return self._fmodule.tensor_from_comp(type_res, cmp_res)

    def symmetrize(self, *pos, **kwargs):
        r"""
        Symmetrization over some arguments.
        
        INPUT:
        
        - ``pos`` -- list of argument positions involved in the 
          symmetrization (with the convention position=0 for the first 
          argument); if none, the symmetrization is performed over all the 
          arguments
        - ``basis`` -- (default: None) module basis with respect to which the 
          component computation is to be performed; if none, the module's 
          default basis is used if the tensor field has already components
          in it; otherwise another basis w.r.t. which the tensor has 
          components will be picked
                  
        OUTPUT:
        
        - the symmetrized tensor (instance of :class:`FreeModuleTensor`)
          
        EXAMPLES:
        
        Symmetrization of a tensor of type (2,0)::
        
            sage: M = FiniteRankFreeModule(QQ, 3, name='M')
            sage: e = M.basis('e')
            sage: t = M.tensor((2,0))
            sage: t[:] = [[2,1,-3],[0,-4,5],[-1,4,2]]
            sage: s = t.symmetrize() ; s
            type-(2,0) tensor on the rank-3 free module M over the Rational Field
            sage: t[:], s[:]
            (
            [ 2  1 -3]  [  2 1/2  -2]
            [ 0 -4  5]  [1/2  -4 9/2]
            [-1  4  2], [ -2 9/2   2]
            )
            sage: s.symmetries()
            symmetry: (0, 1);  no antisymmetry
            sage: # Check:
            sage: for i in range(3):
            ....:     for j in range(3):
            ....:         print s[i,j] == 1/2*(t[i,j]+t[j,i]),
            ....:         
            True True True True True True True True True
    
        Instead of invoking the method :meth:`symmetrize`, one may use the 
        index notation with parentheses to denote the symmetrization; it 
        suffices to pass the indices as a string inside square brackets::
        
            sage: t['(ij)']
            type-(2,0) tensor on the rank-3 free module M over the Rational Field
            sage: t['(ij)'].symmetries()
            symmetry: (0, 1);  no antisymmetry
            sage: t['(ij)'] == t.symmetrize()
            True

        The indices names are not significant; they can even be replaced by 
        dots::
            
            sage: t['(..)'] == t.symmetrize()
            True

        The LaTeX notation can be used as well::
        
            sage: t['^{(ij)}'] == t.symmetrize()
            True

        Symmetrization of a tensor of type (0,3) on the first two arguments::
        
            sage: t = M.tensor((0,3))
            sage: t[:] = [[[1,2,3], [-4,5,6], [7,8,-9]], [[10,-11,12], [13,14,-15], [16,17,18]], [[19,-20,-21], [-22,23,24], [25,26,-27]]]
            sage: s = t.symmetrize(0,1) ; s  # (0,1) = the first two arguments
            type-(0,3) tensor on the rank-3 free module M over the Rational Field
            sage: s.symmetries()
            symmetry: (0, 1);  no antisymmetry
            sage: s[:]
            [[[1, 2, 3], [3, -3, 9], [13, -6, -15]],
             [[3, -3, 9], [13, 14, -15], [-3, 20, 21]],
             [[13, -6, -15], [-3, 20, 21], [25, 26, -27]]]
            sage: # Check:
            sage: for i in range(3):
            ....:     for j in range(3):
            ....:         for k in range(3):
            ....:             print s[i,j,k] == 1/2*(t[i,j,k]+t[j,i,k]), 
            ....:             
            True True True True True True True True True True True True True True True True True True True True True True True True True True True
            sage: s.symmetrize(0,1) == s  # another test
            True

        Again the index notation can be used::
        
            sage: t['_(ij)k'] == t.symmetrize(0,1)
            True
            sage: t['_(..).'] == t.symmetrize(0,1)  # no index name
            True
            sage: t['_{(ij)k}'] == t.symmetrize(0,1)  # LaTeX notation
            True
            sage: t['_{(..).}'] == t.symmetrize(0,1)  # this also allowed
            True

        Symmetrization of a tensor of type (0,3) on the first and last arguments::

            sage: s = t.symmetrize(0,2) ; s  # (0,2) = first and last arguments
            type-(0,3) tensor on the rank-3 free module M over the Rational Field
            sage: s.symmetries()
            symmetry: (0, 2);  no antisymmetry
            sage: s[:]
            [[[1, 6, 11], [-4, 9, -8], [7, 12, 8]],
             [[6, -11, -4], [9, 14, 4], [12, 17, 22]],
             [[11, -4, -21], [-8, 4, 24], [8, 22, -27]]]
            sage: for i in range(3):
            ....:     for j in range(3):
            ....:         for k in range(3):
            ....:             print s[i,j,k] == 1/2*(t[i,j,k]+t[k,j,i]),
            ....:             
            True True True True True True True True True True True True True True True True True True True True True True True True True True True
            sage: s.symmetrize(0,2) == s  # another test
            True

        Symmetrization of a tensor of type (0,3) on the last two arguments::
        
            sage: s = t.symmetrize(1,2) ; s  # (1,2) = the last two arguments
            type-(0,3) tensor on the rank-3 free module M over the Rational Field
            sage: s.symmetries()
            symmetry: (1, 2);  no antisymmetry
            sage: s[:]
            [[[1, -1, 5], [-1, 5, 7], [5, 7, -9]],
             [[10, 1, 14], [1, 14, 1], [14, 1, 18]],
             [[19, -21, 2], [-21, 23, 25], [2, 25, -27]]]
            sage: # Check:
            sage: for i in range(3):
            ....:     for j in range(3):
            ....:         for k in range(3):
            ....:             print s[i,j,k] == 1/2*(t[i,j,k]+t[i,k,j]),  
            ....:             
            True True True True True True True True True True True True True True True True True True True True True True True True True True True
            sage: s.symmetrize(1,2) == s  # another test
            True
    
        Use of the index notation::
        
            sage: t['_i(jk)'] == t.symmetrize(1,2)
            True
            sage: t['_.(..)'] == t.symmetrize(1,2)
            True
            sage: t['_{i(jk)}'] == t.symmetrize(1,2)  # LaTeX notation
            True

        Full symmetrization of a tensor of type (0,3)::
        
            sage: s = t.symmetrize() ; s
            type-(0,3) tensor on the rank-3 free module M over the Rational Field
            sage: s.symmetries()
            symmetry: (0, 1, 2);  no antisymmetry
            sage: s[:]
            [[[1, 8/3, 29/3], [8/3, 7/3, 0], [29/3, 0, -5/3]],
             [[8/3, 7/3, 0], [7/3, 14, 25/3], [0, 25/3, 68/3]],
             [[29/3, 0, -5/3], [0, 25/3, 68/3], [-5/3, 68/3, -27]]]
            sage: # Check:
            sage: for i in range(3):
            ....:     for j in range(3):
            ....:         for k in range(3):
            ....:             print s[i,j,k] == 1/6*(t[i,j,k]+t[i,k,j]+t[j,k,i]+t[j,i,k]+t[k,i,j]+t[k,j,i]),
            ....:             
            True True True True True True True True True True True True True True True True True True True True True True True True True True True
            sage: s.symmetrize() == s  # another test
            True
            
        Index notation for the full symmetrization::
        
            sage: t['_(ijk)'] == t.symmetrize()
            True
            sage: t['_{(ijk)}'] == t.symmetrize()  # LaTeX notation
            True
            
        Symmetrization can be performed only on arguments on the same type::
        
            sage: t = M.tensor((1,2))
            sage: t[:] = [[[1,2,3], [-4,5,6], [7,8,-9]], [[10,-11,12], [13,14,-15], [16,17,18]], [[19,-20,-21], [-22,23,24], [25,26,-27]]]
            sage: s = t.symmetrize(0,1) 
            Traceback (most recent call last):
            ...
            TypeError: 0 is a contravariant position, while 1 is a covariant position; 
            symmetrization is meaningfull only on tensor arguments of the same type.
            sage: s = t.symmetrize(1,2) # OK: both 1 and 2 are covariant positions

        The order of positions does not matter::
        
            sage: t.symmetrize(2,1) == t.symmetrize(1,2)
            True
        
        Use of the index notation::
        
            sage: t['^i_(jk)'] == t.symmetrize(1,2)
            True
            sage: t['^._(..)'] ==  t.symmetrize(1,2)
            True
        
        The character '^' can be skipped, the character '_' being sufficient
        to separate contravariant indices from covariant ones::
        
            sage: t['i_(jk)'] == t.symmetrize(1,2)
            True
        
        The LaTeX notation can be employed::
        
            sage: t['^{i}_{(jk)}'] == t.symmetrize(1,2)
            True

        """
        if not pos:
            pos = range(self._tensor_rank)
        # check whether the symmetrization is possible:
        pos_cov = self._tensor_type[0]   # first covariant position 
        pos0 = pos[0]
        if pos0 < pos_cov:  # pos0 is a contravariant position
            for k in range(1,len(pos)):
                if pos[k] >= pos_cov:
                    raise TypeError(
                        str(pos[0]) + " is a contravariant position, while " + 
                        str(pos[k]) + " is a covariant position; \n"
                        "symmetrization is meaningfull only on tensor " + 
                        "arguments of the same type.")
        else:  # pos0 is a covariant position
            for k in range(1,len(pos)):
                if pos[k] < pos_cov:
                    raise TypeError(
                        str(pos[0]) + " is a covariant position, while " + \
                        str(pos[k]) + " is a contravariant position; \n"
                        "symmetrization is meaningfull only on tensor " + 
                        "arguments of the same type.")                
        if 'basis' in kwargs:
            basis = kwargs['basis']
        else:
            basis = self.pick_a_basis()
        res_comp = self._components[basis].symmetrize(*pos)
        return self._fmodule.tensor_from_comp(self._tensor_type, res_comp)

        
    def antisymmetrize(self, *pos, **kwargs):
        r"""
        Antisymmetrization over some arguments.
        
        INPUT:
        
        - ``pos`` -- list of argument positions involved in the 
          antisymmetrization (with the convention position=0 for the first 
          argument); if none, the antisymmetrization is performed over all the 
          arguments
        - ``basis`` -- (default: None) module basis with respect to which the 
          component computation is to be performed; if none, the module's 
          default basis is used if the tensor field has already components
          in it; otherwise another basis w.r.t. which the tensor has 
          components will be picked
                  
        OUTPUT:
        
        - the antisymmetrized tensor (instance of :class:`FreeModuleTensor`)
          
        EXAMPLES:
                
        Antisymmetrization of a tensor of type (2,0)::
        
            sage: M = FiniteRankFreeModule(QQ, 3, name='M')
            sage: e = M.basis('e')
            sage: t = M.tensor((2,0))
            sage: t[:] = [[1,-2,3], [4,5,6], [7,8,-9]]
            sage: s = t.antisymmetrize() ; s
            type-(2,0) tensor on the rank-3 free module M over the Rational Field
            sage: s.symmetries()
            no symmetry;  antisymmetry: (0, 1)
            sage: t[:], s[:]
            (
            [ 1 -2  3]  [ 0 -3 -2]
            [ 4  5  6]  [ 3  0 -1]
            [ 7  8 -9], [ 2  1  0]
            )
            sage: # Check:
            sage: for i in range(3):
            ....:     for j in range(3):
            ....:         print s[i,j] == 1/2*(t[i,j]-t[j,i]),
            ....:         
            True True True True True True True True True
            sage: s.antisymmetrize() == s  # another test
            True
            sage: t.antisymmetrize() == t.antisymmetrize(0,1)
            True

        Antisymmetrization of a tensor of type (0,3) over the first two 
        arguments::

            sage: t = M.tensor((0,3))
            sage: t[:] = [[[1,2,3], [-4,5,6], [7,8,-9]], [[10,-11,12], [13,14,-15], [16,17,18]], [[19,-20,-21], [-22,23,24], [25,26,-27]]]
            sage: s = t.antisymmetrize(0,1) ; s  # (0,1) = the first two arguments
            type-(0,3) tensor on the rank-3 free module M over the Rational Field
            sage: s.symmetries()
            no symmetry;  antisymmetry: (0, 1)
            sage: s[:]
            [[[0, 0, 0], [-7, 8, -3], [-6, 14, 6]],
             [[7, -8, 3], [0, 0, 0], [19, -3, -3]],
             [[6, -14, -6], [-19, 3, 3], [0, 0, 0]]]
            sage: # Check:
            sage: for i in range(3):
            ....:     for j in range(3):
            ....:         for k in range(3):
            ....:             print s[i,j,k] == 1/2*(t[i,j,k]-t[j,i,k]),
            ....:             
            True True True True True True True True True True True True True True True True True True True True True True True True True True True
            sage: s.antisymmetrize(0,1) == s  # another test
            True
            sage: s.symmetrize(0,1) == 0  # of course
            True

        Instead of invoking the method :meth:`antisymmetrize`, one can use
        the index notation with square brackets denoting the 
        antisymmetrization; it suffices to pass the indices as a string 
        inside square brackets::
        
            sage: s1 = t['_[ij]k'] ; s1
            type-(0,3) tensor on the rank-3 free module M over the Rational Field
            sage: s1.symmetries()
            no symmetry;  antisymmetry: (0, 1)
            sage: s1 == s
            True

        The LaTeX notation is recognized::
        
            sage: t['_{[ij]k}'] == s
            True
            
        Note that in the index notation, the name of the indices is irrelevant; 
        they can even be replaced by dots::
        
            sage: t['_[..].'] == s
            True

        Antisymmetrization of a tensor of type (0,3) over the first and last 
        arguments::

            sage: s = t.antisymmetrize(0,2) ; s  # (0,2) = first and last arguments
            type-(0,3) tensor on the rank-3 free module M over the Rational Field
            sage: s.symmetries()
            no symmetry;  antisymmetry: (0, 2)
            sage: s[:]
            [[[0, -4, -8], [0, -4, 14], [0, -4, -17]],
             [[4, 0, 16], [4, 0, -19], [4, 0, -4]],
             [[8, -16, 0], [-14, 19, 0], [17, 4, 0]]]
            sage: # Check:
            sage: for i in range(3):
            ....:     for j in range(3):
            ....:         for k in range(3):
            ....:             print s[i,j,k] == 1/2*(t[i,j,k]-t[k,j,i]),
            ....:             
            True True True True True True True True True True True True True True True True True True True True True True True True True True True
            sage: s.antisymmetrize(0,2) == s  # another test
            True
            sage: s.symmetrize(0,2) == 0  # of course
            True
            sage: s.symmetrize(0,1) == 0  # no reason for this to hold
            False
        
        Antisymmetrization of a tensor of type (0,3) over the last two 
        arguments::

            sage: s = t.antisymmetrize(1,2) ; s  # (1,2) = the last two arguments
            type-(0,3) tensor on the rank-3 free module M over the Rational Field
            sage: s.symmetries()
            no symmetry;  antisymmetry: (1, 2)
            sage: s[:]
            [[[0, 3, -2], [-3, 0, -1], [2, 1, 0]],
             [[0, -12, -2], [12, 0, -16], [2, 16, 0]],
             [[0, 1, -23], [-1, 0, -1], [23, 1, 0]]]
            sage: # Check:
            sage: for i in range(3):
            ....:     for j in range(3):
            ....:         for k in range(3):
            ....:             print s[i,j,k] == 1/2*(t[i,j,k]-t[i,k,j]),
            ....:             
            True True True True True True True True True True True True True True True True True True True True True True True True True True True
            sage: s.antisymmetrize(1,2) == s  # another test
            True
            sage: s.symmetrize(1,2) == 0  # of course
            True

        The index notation can be used instead of the explicit call to 
        :meth:`antisymmetrize`::
        
            sage: t['_i[jk]'] == t.antisymmetrize(1,2)
            True

        Full antisymmetrization of a tensor of type (0,3)::
        
            sage: s = t.antisymmetrize() ; s
            alternating form of degree 3 on the rank-3 free module M over the Rational Field
            sage: s.symmetries()
            no symmetry;  antisymmetry: (0, 1, 2)
            sage: s[:]
            [[[0, 0, 0], [0, 0, 2/3], [0, -2/3, 0]],
             [[0, 0, -2/3], [0, 0, 0], [2/3, 0, 0]],
             [[0, 2/3, 0], [-2/3, 0, 0], [0, 0, 0]]]
            sage: # Check:
            sage: for i in range(3):
            ....:     for j in range(3):
            ....:         for k in range(3):
            ....:             print s[i,j,k] == 1/6*(t[i,j,k]-t[i,k,j]+t[j,k,i]-t[j,i,k]+t[k,i,j]-t[k,j,i]),
            ....:             
            True True True True True True True True True True True True True True True True True True True True True True True True True True True
            sage: s.antisymmetrize() == s  # another test
            True
            sage: s.symmetrize(0,1) == 0  # of course
            True
            sage: s.symmetrize(0,2) == 0  # of course
            True
            sage: s.symmetrize(1,2) == 0  # of course
            True
            sage: t.antisymmetrize() == t.antisymmetrize(0,1,2)
            True

        The index notation can be used instead of the explicit call to 
        :meth:`antisymmetrize`::
        
            sage: t['_[ijk]'] == t.antisymmetrize()
            True
            sage: t['_[abc]'] == t.antisymmetrize()
            True
            sage: t['_[...]'] == t.antisymmetrize()
            True
            sage: t['_{[ijk]}'] == t.antisymmetrize() # LaTeX notation
            True

        Antisymmetrization can be performed only on arguments on the same type::
        
            sage: t = M.tensor((1,2))
            sage: t[:] = [[[1,2,3], [-4,5,6], [7,8,-9]], [[10,-11,12], [13,14,-15], [16,17,18]], [[19,-20,-21], [-22,23,24], [25,26,-27]]]
            sage: s = t.antisymmetrize(0,1) 
            Traceback (most recent call last):
            ...
            TypeError: 0 is a contravariant position, while 1 is a covariant position; 
            antisymmetrization is meaningfull only on tensor arguments of the same type.
            sage: s = t.antisymmetrize(1,2) # OK: both 1 and 2 are covariant positions

        The order of positions does not matter::
        
            sage: t.antisymmetrize(2,1) == t.antisymmetrize(1,2)
            True
        
        Again, the index notation can be used::
        
            sage: t['^i_[jk]'] == t.antisymmetrize(1,2)
            True
            sage: t['^i_{[jk]}'] == t.antisymmetrize(1,2)  # LaTeX notation
            True

        The character '^' can be skipped::
        
            sage: t['i_[jk]'] == t.antisymmetrize(1,2)
            True
            
        """
        if not pos:
            pos = range(self._tensor_rank)
        # check whether the antisymmetrization is possible:
        pos_cov = self._tensor_type[0]   # first covariant position 
        pos0 = pos[0]
        if pos0 < pos_cov:  # pos0 is a contravariant position
            for k in range(1,len(pos)):
                if pos[k] >= pos_cov:
                    raise TypeError(
                        str(pos[0]) + " is a contravariant position, while " + 
                        str(pos[k]) + " is a covariant position; \n"
                        "antisymmetrization is meaningfull only on tensor " + 
                        "arguments of the same type.")
        else:  # pos0 is a covariant position
            for k in range(1,len(pos)):
                if pos[k] < pos_cov:
                    raise TypeError(
                        str(pos[0]) + " is a covariant position, while " + \
                        str(pos[k]) + " is a contravariant position; \n"
                        "antisymmetrization is meaningfull only on tensor " + 
                        "arguments of the same type.")                
        if 'basis' in kwargs:
            basis = kwargs['basis']
        else:
            basis = self.pick_a_basis()
        res_comp = self._components[basis].antisymmetrize(*pos)
        return self._fmodule.tensor_from_comp(self._tensor_type, res_comp)


#******************************************************************************

# From sage/modules/module.pyx:
#-----------------------------
### The Element should also implement _rmul_ (or _lmul_)
#
# class MyElement(sage.structure.element.ModuleElement):
#     def _rmul_(self, c):
#         ...


class FiniteRankFreeModuleElement(FreeModuleTensor):
    r"""
    Element of a free module of finite rank over a commutative ring.
    
    The class :class:`FiniteRankFreeModuleElement` inherits from 
    :class:`FreeModuleTensor` because the elements of a free module `M` of 
    finite rank over a commutative ring `R` are identified with tensors of 
    type (1,0) on `M` via the canonical map
    
    .. MATH::

        \begin{array}{lllllll}
        \Phi: & M & \longrightarrow & M^{**}  &  &   & \\
              & v & \longmapsto & \bar v : & M^* & \longrightarrow & R \\
              &   &             &          & a   & \longmapsto & a(v) 
        \end{array}
    
    Note that for free modules of finite rank, this map is actually an 
    isomorphism, enabling the canonical identification: `M^{**}= M`.
    
    INPUT:
    
    - ``fmodule`` -- free module `M` over a commutative ring `R` (must be an 
      instance of :class:`FiniteRankFreeModule`)
    - ``name`` -- (default: None) name given to the element
    - ``latex_name`` -- (default: None) LaTeX symbol to denote the element; 
      if none is provided, the LaTeX symbol is set to ``name``
    
    EXAMPLES:
    
    Let us consider a rank-3 free module over `\ZZ`::
    
        sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
        sage: e = M.basis('e') ; e
        basis (e_0,e_1,e_2) on the rank-3 free module M over the Integer Ring
        
    There are three ways to construct an element of the free module M: the first 
    one (recommended) is via the operator __call__ acting on the free module::
    
        sage: v = M([2,0,-1], basis=e, name='v') ; v
        element v of the rank-3 free module M over the Integer Ring
        sage: v.view()  # expansion on the default basis (e)
        v = 2 e_0 - e_2
        sage: v.parent() is M
        True


    The second way is to construct a tensor of type (1,0) on `M` (cf. the
    canonical identification `M^{**}=M` recalled above)::
    
        sage: v2 = M.tensor((1,0), name='v')
        sage: v2[0], v2[2] = 2, -1 ; v2
        element v of the rank-3 free module M over the Integer Ring
        sage: v2.view()
        v = 2 e_0 - e_2
        sage: v2 == v
        True
        
    Finally, the third way is via some linear combination of the basis 
    elements::
    
        sage: v3 = 2*e[0] - e[2]
        sage: v3.set_name('v') ; v3 # in this case, the name has to be set separately
        element v of the rank-3 free module M over the Integer Ring
        sage: v3.view()
        v = 2 e_0 - e_2
        sage: v3 == v
        True
    
    The canonical identification `M^{**}=M` is implemented by letting the
    module elements act on linear forms, providing the same result as the
    reverse operation (cf. the map `\Phi` defined above)::
    
        sage: a = M.linear_form(name='a')
        sage: a[:] = (2, 1, -3) ; a
        linear form a on the rank-3 free module M over the Integer Ring
        sage: v(a)
        7
        sage: a(v)
        7
        sage: a(v) == v(a)
        True
    
    ARITHMETIC EXAMPLES:
    
    Addition::
    
        sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
        sage: e = M.basis('e') ; e
        basis (e_0,e_1,e_2) on the rank-3 free module M over the Integer Ring
        sage: a = M([0,1,3], name='a') ; a
        element a of the rank-3 free module M over the Integer Ring
        sage: a.view()
        a = e_1 + 3 e_2
        sage: b = M([2,-2,1], name='b') ; b
        element b of the rank-3 free module M over the Integer Ring
        sage: b.view()
        b = 2 e_0 - 2 e_1 + e_2
        sage: s = a + b ; s
        element a+b of the rank-3 free module M over the Integer Ring
        sage: s.view()
        a+b = 2 e_0 - e_1 + 4 e_2
        sage: # Test of the addition:
        sage: for i in M.irange(): print s[i] == a[i] + b[i],
        True True True

    Subtraction::
    
        sage: s = a - b ; s
        element a-b of the rank-3 free module M over the Integer Ring
        sage: s.view()
        a-b = -2 e_0 + 3 e_1 + 2 e_2
        sage: # Test of the substraction:
        sage: for i in M.irange(): print s[i] == a[i] - b[i],
        True True True
        
    Multiplication by a scalar::
    
        sage: s = 2*a ; s
        element of the rank-3 free module M over the Integer Ring
        sage: s.view()
        2 e_1 + 6 e_2
        sage: a.view()
        a = e_1 + 3 e_2

    Tensor product::
    
        sage: s = a*b ; s
        type-(2,0) tensor a*b on the rank-3 free module M over the Integer Ring
        sage: s.symmetries()
        no symmetry;  no antisymmetry
        sage: s[:]
        [ 0  0  0]
        [ 2 -2  1]
        [ 6 -6  3]
        sage: s = a*s ; s
        type-(3,0) tensor a*a*b on the rank-3 free module M over the Integer Ring
        sage: s[:]
        [[[0, 0, 0], [0, 0, 0], [0, 0, 0]],
         [[0, 0, 0], [2, -2, 1], [6, -6, 3]],
         [[0, 0, 0], [6, -6, 3], [18, -18, 9]]]

    """
    def __init__(self, fmodule, name=None, latex_name=None):
        FreeModuleTensor.__init__(self, fmodule, (1,0), name=name, 
                                  latex_name=latex_name)

    def _repr_(self):
        r"""
        String representation of the object.
        """
        description = "element "
        if self._name is not None:
            description += self._name + " " 
        description += "of the " + str(self._fmodule)
        return description

    def _new_comp(self, basis): 
        r"""
        Create some components in the given basis. 
              
        This method, which is already implemented in 
        :meth:`FreeModuleTensor._new_comp`, is redefined here for efficiency
        """
        fmodule = self._fmodule  # the base free module
        return Components(fmodule._ring, basis, 1, start_index=fmodule._sindex,
                          output_formatter=fmodule._output_formatter)


    def _new_instance(self):
        r"""
        Create an instance of the same class as ``self``. 
        
        """
        return self.__class__(self._fmodule)

