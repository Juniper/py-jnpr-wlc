### ---------------------------------------------------------------------------
### ===========================================================================
###
### RpcHelper
###
### ===========================================================================
### ---------------------------------------------------------------------------

class RpcHelper(object):
  """
    RpcHelper is a metaprogramming object that allows a programmer
    to bind helper functions to a WLC object 'ez' attribute.  Each
    RpcHelper maintains a list of helper functions and a list of 
    child RpcHelpers.  In this way, a RpcHelper can provide a
    hierarchy of helpers
  """

  def __init__(self, wlc, load_helpers=None ):
    """
      wlc: WLC object
      load_helpers: dict of name/functions
    """
    self._wlc = wlc
    self._helper_fntbl = {}
    self._children = {}
    if load_helpers: self.Load( load_helpers )

  def Get(self, method):
    """
      retrieves a the helper function named 'method'
    """
    return self._helper_fntbl.get( method, False)

  def Set(self, method, method_fn):
    """
      binds a helper function to the RpcHelper
    """
    self._helper_fntbl[method] = method_fn
    return method_fn

  def Load( self, helpers ):    
    """
      binds a dictonary of name/helpers
    """
    for method, method_fn in helpers.items():
      self.Set( method, method_fn )

  def Children(self):
    """
      returns a list of RpcHelper child names
    """
    return self._children.keys()

  def Helpers(self):
    """
      returns a list of RpcHelper function names
    """
    return self._helper_fntbl.keys()

  def __getattr__( self, method ):
    """
      if 'method' is a child name, then the child RpcHelper is 
      returned.  otherwise ...

      implements "method_missing", so perform a lookup in the known
      helpers and return the function if found.  otherwise raise
      an AttributeError exception
    """

    # first see if this is a child request
    if method in self._children:
      return self._children[method]

    # ok, so not a child request, see if we know
    # about this method request

    method_fn = self.Get(method)

    # if this helper doesn't know about the
    # request method, then return a function
    # that will raise an AttributeError

    if not method_fn: 
      def _no_method_fn(*vargs, **kvargs):
        raise AttributeError("Unknown ez helper: '%s'" % method)
      return _no_method_fn

    # otherwise, return a function that will in turn
    # invoke the helper function passing the associated
    # WLC object and called arguments

    def _helper_fn(*vargs, **kvargs):
      return method_fn(self._wlc, vargs, **kvargs)
    return _helper_fn

  def _create_child( self, options ):
    name = options['child']
    new_helper = self.__class__(self._wlc, options.get('load'))
    self._children[name] = new_helper
    return new_helper

  def __call__(self, *vargs, **kvargs ):
    """
    Entry point for managing the RpcHelper:

     ( helper=<function> ):
        This will simply add the function to the ez
        helpers table.  Assumes that <function>.__name__
        is usable for later invocations, i.e. its not a lambda

     ( helper=<function>, alias=<name> ):
        Similar to the above, but allows the name option to
        set the name of the ez function rather than taking
        it from <function>.__name__

      ( child=<name>, load=<dict> ):
        Creates a child helper object.  If load is provided
        then that dictory of name/helpers is also loaded into 
        the new child RpcHelper.  The child is returned.
    """

    if 'child' in kvargs:
      return self._create_child(kvargs)

    new_helper = kvargs['helper']
    new_name = new_helper.__name__
    if 'alias' in kvargs: new_name = kvargs['alias']

    if callable( new_helper ):
      # other is a single callable item
      self.Set( new_name, new_helper)
      return self
    else:
      raise ValueError, "not callable: %s" % other.__name__