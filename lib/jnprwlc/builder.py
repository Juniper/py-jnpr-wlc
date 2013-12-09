
import re
from lxml import etree
from lxml.builder import E

TRANSACTIONS_LIST = ['GET', 'GET-STAT', 'SET','ACT','DELETE']

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
  # property: cmd
  #    one of the values in the TRANSACTIONS_LIST
  # ---------------------------------------------------------------------------

  @property
  def cmd(self):
    return self._cmd

  @cmd.setter
  def cmd(self, value):
    value = value.upper()
    assert (value in TRANSACTIONS_LIST)
    self._cmd = value

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
  # property: factory
  #    RpcFactory object
  # ---------------------------------------------------------------------------  

  @property
  def factory(self):
      return self._factory
  @factory.setter
  def factory(self, value):
      self._factory = value


  @property
  def data(self):
      return self._data

  @data.setter
  def data(self, value):
    if isinstance(value,str):
      self._data = E(value)
    else:
      self._data = value
  
  # ===========================================================================
  #                                  CONSTRUCTOR
  # ===========================================================================

  def __init__( self, wlc, cmd='GET', target=None, **kvargs ):
    """
      wlc: should be the WLC object so we can self-invoke the RPC
      trans: transaction type from TRANSACTIONS_LIST
      target: target API object, optional
    """
    self.wlc = wlc
    self.cmd = cmd
    self.target = target
    self.data = None

    template = kvargs.get('Template')
    if template:
      self.template = wlc.Template( template )
      del kvargs['Template']      

    template_vars = kvargs.get('TemplateVars')
    if template_vars:
      self.render( template_vars )
      del kvargs['TemplateVars']

    self.args = kvargs if kvargs else {}

  def data_append( self, xml_data ):
    """
      adds the :xml_data: to the RPC.  The :xml_data: can either be a
      stringy or an lxml Element object
    """
    if isinstance( xml_data, str ) or isinstance( xml_data, unicode ):
      self.data.append( etree.XML( xml_data ))
    elif isinstance( xml_data, etree._Element ):
      # ok, don't bork the caller, just do the right thing
      self.data.append( xml_as_str )
    else:
      raise ValueError( "xml_data is of unknown origin: " + xml_data.__class__.__name__ )

  # ---------------------------------------------------------------------------
  # render - used to render an associated template with variables and then
  # assign the results to the 'data' attribute
  # ---------------------------------------------------------------------------  

  def render( self, vars ):
    """
      Renders the :template: with the provided :vars:  The result 
      is stored (overwrites) the :data: attribute
    """
    if not self.template:
      raise RuntimeError("RPC does not have a template")

    self.data = etree.XML(self.template.render(vars))

  # ---------------------------------------------------------------------------
  # property: as_xml
  #    returns RPC as an Element ready for RPC processing
  # ---------------------------------------------------------------------------  

  @property
  def to_xml(self):
    """
      creates the actual RPC from the associated properties
    """
    rpc_e, trans_e = self._factory( self.cmd, self._target )

    # if there is a target, then add that child element and
    # bind any associated target args

    if self.target != None:
      target_e = trans_e.find(self.target)
      # add any attributes from attrs to the action
      for k,v in self.args.items(): 
        k = re.sub('_','-',k)
        target_e.attrib[k] = str(v)
      at_data = target_e
    else:
      at_data = trans_e

    # if there is data to attach, then append it into the RPC
    # either with the 'target' if one exists, or at the transaction

    if self.data != None:
      at_data.append( self.data )

    return rpc_e

  # ---------------------------------------------------------------------------
  # __repr__: string serialization
  # ---------------------------------------------------------------------------  

  def __repr__(self):
    """
      perform RPC generation and serialize XML to string
      using the etree.tostring() method
    """
    return etree.tostring( self.to_xml, pretty_print=True )

  # ---------------------------------------------------------------------------
  # __call__: invoke RPC against the bound WLC and return the RESP 
  # ---------------------------------------------------------------------------  

  def __call__(self):
    """
      callable object will invoke the RPC against the bound WLC and 
      return the RESP as XML object
    """
    assert( self._wlc )
    return self._wlc.rpc( self.to_xml )
