import pdb

# stdlib
import subprocess
from urllib2 import Request
from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, HTTPDigestAuthHandler
from urllib2 import HTTPHandler, HTTPSHandler, build_opener
from urllib2 import HTTPError
import base64

# 3rd-party modules
from lxml import etree

# local helper module
from jnprwlc.rpc_helper import RpcHelper, std_rpc_helpers

# jnprwlc internal modules
from ._rpc_factory import _RpcFactory
from ._rpc_meta import _RpcMetaExec
from jnprwlc.builder import RpcMaker

DEFAULT_HTTP = 'https'
DEFAULT_PORT = 8889
DEFAULT_API_URI = "/trapeze/ringmaster"
DEFAULT_API_USER_AGENT = 'Juniper Networks RingMaster'
DEFAULT_TIMEOUT = 3

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
    - close: 'closes' a connection to the WLC
    - execute: executes an RPC command and returns the response

  """



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
    self._port = kvargs.get('port', DEFAULT_PORT)
    self._proto = kvargs.get('http', DEFAULT_HTTP)
    self._timeout = kvargs.get('timeout', DEFAULT_TIMEOUT)

    self._rpc_factory = _RpcFactory(self)
    self.rpc = _RpcMetaExec(self, self._rpc_factory)
    self.ez = RpcHelper(self, load_helpers=std_rpc_helpers)

  def _setup_http(self):

    self._api_uri = '{http}://{host}:{port}{api_uri}'.format(
      http=self._proto,
      host=self._hostname,
      port=self._port,
      api_uri = DEFAULT_API_URI )

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

    rpc_cmd, dev_null = self._rpc_factory.Next()
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
    req.add_header('User-Agent', DEFAULT_API_USER_AGENT)         
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
