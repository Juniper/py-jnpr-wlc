
import re
from lxml import etree
from lxml.builder import ElementMaker

TRANSACTIONS_LIST = ['GET','SET','ACT','DELETE']

class RpcMaker(object):

  # ---------------------------------------------------------------------------
  # property: wlc
  #    WLC object
  # ---------------------------------------------------------------------------

  @property
  def wlc(self):
      return self._wlc

  @wlc.setter
  def wlc(self, value):
      self._wlc = value
      if value == None:
        return
      self._factory = self._wlc._rpc_factory
  
  # ---------------------------------------------------------------------------
  # property: trans
  #    one of the values in the TRANSACTIONS_LIST
  # ---------------------------------------------------------------------------

  @property
  def trans(self):
    return self._trans

  @trans.setter
  def trans(self, value):
    value = value.upper()
    assert (value in TRANSACTIONS_LIST)
    self._trans = value

  # ---------------------------------------------------------------------------
  # property: target
  #    element name of the transaction
  # ---------------------------------------------------------------------------  

  @property
  def target(self):
      return self._target
  @target.setter
  def target(self, value):
      value = value.upper() if value else None
      self._target = value
      return self._target

  # ---------------------------------------------------------------------------
  # property: args
  #    target arguments, dict
  # ---------------------------------------------------------------------------  

  @property
  def args(self):
      return self._args

  @args.setter  
  def args(self, value):
      self._args = value
  

  # ---------------------------------------------------------------------------
  # property: data
  #    XML data contained in 'taget'.  This is typcially used for SET/CREATE
  #    type operations
  # ---------------------------------------------------------------------------  

  @property
  def data(self):
      return self._data
  @data.setter
  def data(self, value):
      self._data = value

  # ---------------------------------------------------------------------------
  # property: factory
  #    RpcFactory object
  # ---------------------------------------------------------------------------  

  @property
  def factory(self):
      return self._factory
  @factory.setter
  def factory(self, value):
      self._factory = value

  # ===========================================================================
  #                                  CONSTRUCTOR
  # ===========================================================================

  def __init__(self, wlc, trans='GET', target=None, *vargs, **kvargs ):
    """
      wlc: should be the WLC object so we can self-invoke the RPC
      trans: transaction type from TRANSACTIONS_LIST
      target: target API object, optional
    """
    self.wlc = wlc
    self.trans = trans
    self.target = target
    self.data = None
    self.args = kvargs

  # ---------------------------------------------------------------------------
  # property: as_rpc
  #    returns RPC as an Element ready for RPC processing
  # ---------------------------------------------------------------------------  

  @property
  def as_xml(self):
    """
      creates the actual RPC from the associated properties
    """
    rpc_e, trans_e = self._factory( self._trans, self._target )

    # if there is a target, then add that child element and
    # bind any associated target args

    if self._target != None:
      target_e = trans_e.find(self._target)
      # add any attributes from attrs to the action
      for k,v in self._args.items(): 
        k = re.sub('_','-',k)
        target_e.attrib[k] = str(v)
      at_data = target_e
    else:
      at_data = trans_e

    # if there is data to attach, then append it into the RPC
    # either with the 'target' if one exists, or at the transaction

    if self._data != None:
      at_data.append( self._data )

    return rpc_e

  # ---------------------------------------------------------------------------
  # __repr__: string serialization
  # ---------------------------------------------------------------------------  

  def __repr__(self):
    """
      perform RPC generation and serialize XML to string
      using the etree.tostring() method
    """
    return etree.tostring( self.as_xml, pretty_print=True )

  # ---------------------------------------------------------------------------
  # __call__: invoke RPC against the bound WLC and return the RESP 
  # ---------------------------------------------------------------------------  

  def __call__(self):
    """
      callable object will invoke the RPC against the bound WLC and 
      return the RESP as XML object
    """
    assert( self._wlc )
    return self._wlc.rpc( self.as_xml )
