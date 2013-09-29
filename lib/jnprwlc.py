
import pdb

import subprocess
import re

from sys import argv as ARGV
from urllib2 import Request
from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, HTTPDigestAuthHandler
from urllib2 import HTTPHandler, HTTPSHandler, build_opener
from urllib2 import HTTPError
import base64

from lxml import etree

### ---------------------------------------------------------------------------
### ===========================================================================
###
### _RpcFactory
###
### ===========================================================================
### ---------------------------------------------------------------------------

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

### ---------------------------------------------------------------------------
### ===========================================================================
###
### _RpcMetaExec
###
### ===========================================================================
### ---------------------------------------------------------------------------

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

### ---------------------------------------------------------------------------
### builtin RPC helpers
### ---------------------------------------------------------------------------

def _wlc_system(wlc, *vargs, **kvargs):
  """
    return a merged dict of the following:
    - BOOTSTATUS 
    - SYSTEMSTATUS
    - SYSTEMGLOBAL

    wlc: WLC object
  """

  run_list = [ wlc.rpc.get_bootstatus,
               wlc.rpc.get_systemstatus,
               wlc.rpc.get_systemglobal ]

  data = {}
  for rpc in run_list:
    rsp = rpc()                   
    data.update(rsp[0].attrib)    # values are in the XML attributes

  return data

_builtin_rpc_helpers = {
  'system': _wlc_system
}

### ---------------------------------------------------------------------------
### ===========================================================================
###
### JuniperWirelessLanController
###
### ===========================================================================
### ---------------------------------------------------------------------------

class JuniperWirelessLanController(object):
  """
    Main class to manage a Juniper Wireless Lan Controller (WLC) product

    ----------------------------
    Public READ-WRITE properties
    ----------------------------
    - user: str, username accessing the WLC    

    - hostname: str, hostname of the WLC

    - timeout: int, time in seconds to call timeout on reaching the  WLC

    ---------------------------
    Public READ-ONLY properties
    ---------------------------
    - password: str, password to access the WLC

    ---------------------------
    Public READ-ONLY attributes
    ---------------------------
    - rpc: used to meta execute RPCs to the WLC

    --------------
    Public methods
    --------------
    - open: 'opens' a connection to the WLC
            verifies reachability(ping) and user/passowrd values

    - close: 'closes' a connection to the WLC.  currently doesn't do anything

    - execute: executes an RPC command and returns the response

  """

  DEFAULT_HTTP = 'https'
  DEFAULT_PORT = 8889
  DEFAULT_API_URI = "/trapeze/ringmaster"
  DEFAULT_API_USER_AGENT = 'Juniper Networks RingMaster'
  DEFAULT_TIMEOUT = 3

  @property
  def hostname(self):
      return self._hostname
  @property
  def user(self):
      return self._user

  @property
  def timeout(self):
      return self._timeout
  @timeout.setter
  def timeout(self, value):
      self._timeout = value
  
  @property
  def password(self):
      return None  # read-only      
  @password.setter
  def password(self, value):
      self._password = value

  def __init__(self, *vargs, **kvargs):
    _rqd_args = 'host user password'.split()

    # flatten vargs into kvargs
    if vargs and isinstance(vargs[0],dict): kvargs.update(vargs[0])

    # ensure required args are provided
    for _a in _rqd_args: 
      assert (_a in kvargs), ("Missing required param: %s" % _a)

    self._hostname = kvargs['host']
    self._user = kvargs['user']
    self._password = kvargs['password']
    self._port = kvargs.get('port', self.__class__.DEFAULT_PORT)
    self._proto = kvargs.get('http', self.__class__.DEFAULT_HTTP)
    self._timeout = kvargs.get('timeout', self.__class__.DEFAULT_TIMEOUT)

    self._rpc_factory = _RpcFactory(self)
    self.rpc = _RpcMetaExec(self, self._rpc_factory)
    self.ez = RpcHelper(self, load_helpers=_builtin_rpc_helpers)

  def _setup_http(self):

    self._api_uri = '{http}://{host}:{port}{api_uri}'.format(
      http=self._proto,
      host=self._hostname,
      port=self._port,
      api_uri = self.__class__.DEFAULT_API_URI )

    auth_mgr = HTTPPasswordMgrWithDefaultRealm()
    auth_mgr.add_password( None, self._api_uri, self._user, self._password )
    auth_hndlr = HTTPBasicAuthHandler(auth_mgr)
    http_hndlr = HTTPHandler(debuglevel=0)
    https_hndlr = HTTPSHandler(debuglevel=0)
    self._http_api = build_opener(auth_hndlr, https_hndlr, http_hndlr)
    self._auth_base64 = base64.encodestring('%s:%s' % (self._user, self._password))[:-1]          

  def _ping_test(self):
    """
      attempts to ping the WLC device.  This only works on Unix systems that 
      has /bin/ping
    """
    ping = subprocess.Popen(
      ["/bin/ping", "-c1", "-w"+str(self._timeout), self._hostname],
      stdout=subprocess.PIPE) 
    if 0 != ping.wait():
      raise RuntimeError("Unable to ping host: " + self._hostname)

  def open(self):
    """
      open is used to setup the HTTP/s process and verify connectivity and user 
      access to the WLC
    """

    self._setup_http()
    self._ping_test()

    # clear to send the HTTP command and see what comes back
    # return True if the response contains no errors.
    # if there is an issue communicating to the WLC, then
    # this action will raise an exception (urllib2)

    rpc_cmd = self._rpc_factory.Next()
    rpc_rsp = self.execute( rpc_cmd )

    return True if rpc_rsp.attrib['nerrors'] == "0" else False

  hello = open    # alias 'hello()' to 'open()'

  def close(self):
    """
      close doesn't do anything ... for now.
    """
    return True

  def execute( self, rpc_cmd ):
    """
      executes RPC command (rpc_cmd) and returns back the RPC result.
      The result in the form of an etree Element

      rpc_cmd: can be in one of two forms:
      - str: fully formulated WLC raw XML as string
      - etree._Element: built from the _RpcFactory 
    """

    req = Request( self._api_uri )
    req.add_header('User-Agent', self.__class__.DEFAULT_API_USER_AGENT)         
    req.add_header("Authorization", "Basic %s" % self._auth_base64)

    if isinstance(rpc_cmd, str):
      req.add_data('XML=' + rpc_cmd )
    elif isinstance(rpc_cmd, etree._Element):
      req.add_data('XML=' + etree.tostring( rpc_cmd ))

    rsp_e = etree.XML(self._http_api.open(req).read())

    # @@@ should do common error checking here
    # @@@ TBD ...

    # now return the XML element starting with the top of
    # the action response; i.e. the first child

    return rsp_e[0] if len(rsp_e) else rsp_e
