### ---------------------------------------------------------------------------
### ===========================================================================
###
### _RpcFactory
###
### ===========================================================================
### ---------------------------------------------------------------------------

from lxml import etree

class _RpcFactory(object):

  NEW_TRANS = """
    <TRANSACTION tid="0">
    <SESSION/>
    </TRANSACTION>
  """
  def __init__( self, wlc ):
    self._tid = 1
    self._wlc = wlc       # not used, but keeping tabs on it, just in case

  def Next(self):
    rpc_e = etree.XML( self.__class__.NEW_TRANS)
    rpc_e.attrib['tid'] = str(self._tid)
    self._tid += 1
    return rpc_e

  def Get(self, target, *vargs, **kvargs ):
    """
      transcation: GET
    """
    rpc_e = self.Next()
    get_e = etree.SubElement(rpc_e, "GET")
    get_e.attrib['level'] = 'all'
    target_e = etree.SubElement( get_e, target.upper() )    

    if kvargs:  # kvargs is the <key>=<value> for a unique object
      key, value = next(kvargs.iteritems())
      target_e.attrib[key] = str(value)

    return rpc_e

  def GetStat(self, target, *vargs, **kvargs ):
    """
      transaction: GET-STAT
    """
    rpc_e = self.Next()
    trans_e = etree.SubElement(rpc_e, "GET-STAT")
    target_e = etree.SubElement( trans_e, target.upper() )    

    if kvargs:  # kvargs is the <key>=<value> for a unique object
      key, value = next(kvargs.iteritems())
      target_e.attrib[key] = str(value)

    return rpc_e

  def Delete(self, target, *vargs, **kvargs ):
    """
      transaction: ACT+DELETE
    """
    rpc_e = self.Next()
    trans_e = etree.SubElement(rpc_e, 'ACT')
    del_e = etree.SubElement(trans_e, 'DELETE')
    target_e = etree.SubElement( del_e, target.upper() )    

    if kvargs:  # kvargs is the <key>=<value> for a unique object
      key, value = next(kvargs.iteritems())
      target_e.attrib[key] = str(value)

    return rpc_e

  def Action(self, action, *vargs, **kvargs):
    """
      transaction: ACT
    """
    rpc_e = self.Next();
    trans_e = etree.SubElement(rpc_e,"ACT")
    act_e = etree.SubElement(trans_e, action.upper())

    # add any attributes from kvargs to the action
    for k,v in kvargs.items(): 
      k = re.sub('_','-',k)
      act_e.attrib[k] = v

    return rpc_e   