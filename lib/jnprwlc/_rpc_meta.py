### ---------------------------------------------------------------------------
### ===========================================================================
###
### _RpcMetaExec
###
### ===========================================================================
### ---------------------------------------------------------------------------

import re

class _RpcMetaExec(object):

  def __init__(self, wlc, factory ):
    self._wlc = wlc
    self._factory = factory

  def get(self, target, *vargs, **kvargs ):
    rpc_cmd = self._factory.Get( target, vargs, **kvargs )
    return self( rpc_cmd )

  def get_stat(self, target, *vargs, **kvargs ):
    rpc_cmd = self._factory.GetStat( target, vargs, **kvargs )
    return self( rpc_cmd )

  def delete(self, target, *vargs, **kvargs ):
    rpc_cmd = self._factory.Delete( target, vargs, **kvargs )
    return self( rpc_cmd )    

  def action( self, target, *vargs, **kvargs):
    rpc_cmd = self._factory.Action( target, vargs, **kvargs)
    return self( rpc_cmd )
    
  def __call__(self, rpc_cmd):
    """
    invoking this object as a fuction executes the rpc_cmd on
    the associated WLC
    """
    return self._wlc.execute( rpc_cmd )

  def __getattr__(self, method ):
    """
      metaprograms 'GET' 
      metaprograms 'GET-STAT'
      metaprograms 'ACT'
      metaprograms 'DELETE'
    """
    if method.startswith('get_stat_'):
      x,x,target = method.partition('get_stat_')
      target = re.sub('_','-',target)
      return lambda *v,**kv: self.get_stat( target, v, **kv )      

    elif method.startswith('get_'):
      x,x,target = method.partition('get_')
      target = re.sub('_','-',target)
      return lambda *v,**kv: self.get( target, v, **kv )      

    elif method.startswith('act_'):
      x,x,target = method.partition('act_')
      target = re.sub('_','-',target)
      return lambda *v,**kv: self.action( target, v, **kv )      

    elif method.startswith('delete_'):
      x,x,target = method.partition('delete_')
      target = re.sub('_','-',target)
      return lambda *v,**kv: self.delete( target, v, **kv )      

    else:      
      # don't know what to do, so raise an exception
      raise AttributeError, "Cannot process method %s" % method