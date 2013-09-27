
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
      ACTION: GET
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
      ACTION: GET-STAT
    """
    rpc_e = self.Next()
    get_e = etree.SubElement(rpc_e, "GET-STAT")
    target_e = etree.SubElement( get_e, target.upper() )    

    if kvargs:  # kvargs is the <key>=<value> for a unique object
      key, value = next(kvargs.iteritems())
      target_e.attrib[key] = str(value)

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
    return self._wlc( rpc_cmd )

  def get_stat(self, target, *vargs, **kvargs ):
    rpc_cmd = self._factory.GetStat( target, vargs, **kvargs )
    return self._wlc( rpc_cmd )
    
  def __getattr__(self, method ):
    """
      metaprograms 'GET' 
      metaprograms 'GET-STAT'
    """
    if method.startswith('get_stat_'):

      x,x,target = method.partition('get_stat_')
      target = re.sub('_','-',target)
      return lambda *v,**kv: self.get_stat( target, v, **kv )      

    elif method.startswith('get_'):

      x,x,target = method.partition('get_')
      target = re.sub('_','-',target)
      return lambda *v,**kv: self.get( target, v, **kv )      

    else:      
      # don't know what to do, so raise an exception
      raise AttributeError, "Cannot process method %s" % method

### ---------------------------------------------------------------------------
### ===========================================================================
###
### _RpcHelpers
###
### ===========================================================================
### ---------------------------------------------------------------------------

class _RpcHelpers(object):

  def __init__(self, wlc, load_helpers=None ):
    self._wlc = wlc
    self._helper_fntbl = {}
    if load_helpers: self.load( load_helpers )

  def get(self, method):
    return self._helper_fntbl.get( method, False)

  def set(self, method, method_fn):
    self._helper_fntbl[method] = method_fn
    return method_fn

  add = set       # alias    

  def load( self, helpers ):    
    for method, method_fn in helpers.items():
      self.set( method, method_fn )

  def __getattr__( self, method ):
    """
      implements "method_missing", so perform a lookup in the known
      helpers and return the function if found.  otherwise raise
      an AttributeError exception
    """
    method_fn = self.get(method)
    if not method_fn: raise AttributeErrror, "Unknown helper: %s" % method
    
    def _helper_fn(*vargs, **kvargs):
      return method_fn(self._wlc, vargs, **kvargs)
    return _helper_fn

  def __iadd__(self, other):
    """
       meta way to add new ez helpers rather than calling the
       set method
    """
    if callable(other):
      # other is a single callable item
      self.set( other.__name__, other)
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
    self.ez = _RpcHelpers(self, load_helpers=_builtin_rpc_helpers)

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

  def open(self):
    """
      open is used to setup the HTTP/s process and verify connectivity and user 
      access to the WLC
    """

    self._setup_http()

    # first do a quick ping and see if the device is reachable
    ping = subprocess.Popen(
      ["/bin/ping", "-c1", "-w"+str(self._timeout), self._hostname],
      stdout=subprocess.PIPE) 
    if 0 != ping.wait():
      raise RuntimeError("Unable to ping host: " + self._hostname)

    # clear to send the HTTP command and see what comes back
    # return True if the response contains no errors.
    # if there is an issue communicating to the WLC, then
    # this action will raise an exception (urllib2)

    rpc_cmd = self._rpc_factory.Next()
    rpc_rsp = self.__call__( rpc_cmd )

    return True if rpc_rsp.attrib['nerrors'] == "0" else False

  hello = open    # alias 'hello()' to 'open()'

  def close(self):
    """
      close doesn't do anything ... for now.
    """
    return True

  def __call__( self, rpc_cmd ):
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
