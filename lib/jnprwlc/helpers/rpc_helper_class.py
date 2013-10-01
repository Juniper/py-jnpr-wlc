### ---------------------------------------------------------------------------
### ===========================================================================
###
### RpcHelper
###
### ===========================================================================
### ---------------------------------------------------------------------------

import pdb

class RpcHelper(object):

  def __init__(self, wlc, load_helpers=None ):
    self._wlc = wlc
    self._helper_fntbl = {}
    self._children = {}
    if load_helpers: self.Load( load_helpers )

  def Get(self, method):
    return self._helper_fntbl.get( method, False)

  def Set(self, method, method_fn):
    self._helper_fntbl[method] = method_fn
    return method_fn

  def Load( self, helpers ):    
    for method, method_fn in helpers.items():
      self.Set( method, method_fn )

  def Children(self):
    return self._children.keys()

  def Helpers(self):
    return self._helper_fntbl.keys()

  def __getattr__( self, method ):
    """
      implements "method_missing", so perform a lookup in the known
      helpers and return the function if found.  otherwise raise
      an AttributeError exception
    """

    # first see if this is a child request
    if method in self._children:
      return self._children[method]

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
       meta way to add new ez helpers rather than calling the
       Set method.  Using __call__ as the means to add new
       helpers provides a number of options:

       ez( <function> ):
          This will simply add the function to the ez
          helpers table.  Assumes that <function>.__name__
          is usable for later invocations, i.e. its not a lambda

        ez( <function>, alias=<name> ):
          Similar to the above, but allows the name option to
          set the name of the ez function rather than taking
          it from <function>.__name__

        ez( child=<name>, methods=<list> ):
          Creates a child helper object

    """

    if 'child' in kvargs:
      return self._create_child(kvargs)

    new_helper = vargs[0]
    new_name = new_helper.__name__
    if 'alias' in kvargs: new_name = kvargs['alias']

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