### ---------------------------------------------------------------------------
### ===========================================================================
###
### RpcHelper
###
### ===========================================================================
### ---------------------------------------------------------------------------

class RpcHelper(object):

  def __init__(self, wlc, load_helpers=None ):
    self._wlc = wlc
    self._helper_fntbl = {}
    if load_helpers: self.Load( load_helpers )

  def Get(self, method):
    return self._helper_fntbl.get( method, False)

  def Set(self, method, method_fn):
    self._helper_fntbl[method] = method_fn
    return method_fn

  def Load( self, helpers ):    
    for method, method_fn in helpers.items():
      self.Set( method, method_fn )

  def __getattr__( self, method ):
    """
      implements "method_missing", so perform a lookup in the known
      helpers and return the function if found.  otherwise raise
      an AttributeError exception
    """
    method_fn = self.Get(method)
    if not method_fn: 
      def _no_method_fn(*vargs, **kvargs):
        raise AttributeError("Unknown ez helper: '%s'" % method)
      return _no_method_fn

    def _helper_fn(*vargs, **kvargs):
      return method_fn(self._wlc, vargs, **kvargs)
    return _helper_fn

  def __call__(self, *vargs, **kvargs ):
    """
       meta way to add new ez helpers rather than calling the
       Set method.  Using __call__ as the means to add new
       helpers provides a number of options:

       ez( <function> ):
          This will simply add the function to the ez
          helpers table.  Assumes that <function>.__name__
          is usable for later invocations, i.e. its not a lambda

        ez( <function>, name=<name> ):
          Similar to the above, but allows the name option to
          set the name of the ez function rather than taking
          it from <function>.__name__

    """

    new_helper = vargs[0]
    new_name = new_helper.__name__
    if 'name' in kvargs: new_name = kvargs['name']

    if callable( new_helper ):
      # other is a single callable item
      self.Set( new_name, new_helper)
      return self
    #
    # @@@ todo: add the ability to provide a list of 
    # @@@ callable items
    #
    else:
      raise ValueError, "not callable: %s" % other.__name__