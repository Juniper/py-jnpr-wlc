### ---------------------------------------------------------------------------
### ===========================================================================
###
### _RpcFactory
###
### ===========================================================================
### ---------------------------------------------------------------------------

from lxml import etree
import re

class RpcFactory(object):

  NEW_TRANS = """
    <TRANSACTION tid="0">
    <SESSION/>
    </TRANSACTION>
  """
  def __init__( self ):
    self._tid = 1

  def Next(self, trans = None):
    """
      create a new toplevel TRANSACTION element and set the 'tid' attribute
    """
    rpc_e = etree.XML( self.__class__.NEW_TRANS)
    rpc_e.attrib['tid'] = str(self._tid)
    self._tid += 1
    trans_e = etree.SubElement( rpc_e, trans ) if trans else None
    return (rpc_e, trans_e)

  def Target( self, parent, target, attrs = {} ):
    """
      add a 'target' child element and associated attribute parameters
    """
    # if a target is not provided, just return the parent.
    # seems silly, but there is a reason for this.
    if not target: return parent

    # create the target child element
    target_e = etree.SubElement( parent, target.upper() )    

    # add any attributes from attrs to the action
    for k,v in attrs.items(): 
      k = re.sub('_','-',k)
      target_e.attrib[k] = str(v)

    return target_e

  def Get(self, target, *vargs, **kvargs ):
    """
      transcation: GET
    """
    rpc_e, trans_e = self.Next('GET')
    trans_e.attrib['level'] = 'all'
    self.Target( trans_e, target, attrs=kvargs )
    return rpc_e

  def GetStat(self, target, *vargs, **kvargs ):
    """
      transaction: GET-STAT
    """
    rpc_e, trans_e = self.Next('GET-STAT')
    self.Target( trans_e, target, attrs=kvargs )
    return rpc_e

  def Delete(self, target, *vargs, **kvargs ):
    """
      transaction: ACT+DELETE
    """
    rpc_e, trans_e = self.Next('ACT')
    del_e = etree.SubElement(trans_e, 'DELETE')
    self.Target( del_e, target, attrs=kvargs )
    return rpc_e

  def Action(self, action, *vargs, **kvargs):
    """
      transaction: ACT
    """
    rpc_e, trans_e = self.Next('ACT');
    self.Target( trans_e, action, attrs=kvargs )
    return rpc_e   

  def Set(self, target, *vargs, **kvargs):
    """
      transaction: SET
    """
    rpc_e, trans_e = self.Next('SET');
    self.Target( trans_e, target, attrs=kvargs )
    return rpc_e       

  def __call__( self, trans, target, *vargs, **kvargs ):
    trans = trans.upper()
    if 'GET' == trans:
      rpc_e = self.Get( target, vargs, **kvargs )
      trans_e = rpc_e.find('GET')
    elif 'GET-STAT' == trans:
      rpc_e = self.GetStat( target, vargs, **kvargs )
      trans_e = rpc_e.find('GET-STAT')
    elif 'DELETE' == trans:
      rpc_e = self.Delete( target, vargs, **kvargs )
      trans_e = rpc_e.find('ACT/DELETE')
    elif 'ACT' == trans:
      rpc_e = self.Action( target, vargs, **kvargs )
      trans_e = rpc_e.find('ACT')
    elif 'SET' == trans:
      rpc_e = self.Set( target, vargs, **kvargs )
      trans_e = rpc_e.find('SET')      
    else:
      raise ValueError("Unknown trans: '%s'" % trans)

    return (rpc_e, trans_e)