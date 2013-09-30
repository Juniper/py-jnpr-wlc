
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

  def __init__(self, wlc=None, trans='GET', target=None ):
    self.wlc = wlc
    self.trans = trans
    self.target = target
    self.data = None

  # ---------------------------------------------------------------------------
  # property: as_rpc
  #    returns RPC as an Element ready for RPC processing
  # ---------------------------------------------------------------------------  

  @property
  def as_rpc(self):
    """
      Creates the actual RPC from the associated properties
    """
    rpc_e, trans_e = self._factory( self._trans, self._target )

    # if there is data to attach, then append it into the RPC
    # either with the 'target' if one exists, or at the transaction

    if self._data != None:
      if self._target != None:
        trans_e.find(self._target).append( self._data )
      else:
        trans_e.append( self._data )

    return rpc_e