from lxml import etree

class RpcError( StandardError ):

  def __init__( self, cmd, rsp ):
    """
      constructor binds the CMD and RSP values into the exception
    """
    self.cmd = cmd
    self.rsp = rsp

  def __repr__(self):
    return etree.tostring(self.rsp, pretty_print=True)

  @property
  def errors(self):
    """
      return a dictionary of error codes and associated messages
    """
    retdict = {}
    for err in self.rsp.xpath('ERROR'):
      retdict[err.attrib['code']] = err.text
    return retdict

