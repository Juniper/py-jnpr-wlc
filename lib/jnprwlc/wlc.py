import pdb

# python stdlib
import subprocess
import os
from urllib2 import Request
from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, HTTPDigestAuthHandler
from urllib2 import HTTPHandler, HTTPSHandler, build_opener
from urllib2 import HTTPError
import base64

# 3rd-party modules
from lxml import etree

# local public modules
from jnprwlc.helpers import RpcHelper, std_rpc_helpers
from jnprwlc.factory import RpcFactory
from jnprwlc.exception import RpcError
from jnprwlc.builder import RpcMaker

# jnprwlc internal modules
from ._rpc_meta import _RpcMetaExec

DEFAULT_HTTP = 'https'
DEFAULT_PORT = 8889
DEFAULT_API_URI = "/trapeze/ringmaster"
DEFAULT_API_USER_AGENT = 'Juniper Networks RingMaster'
DEFAULT_TIMEOUT = 3

LOG_DBAR = '<!--' + '='*50 +'-->\n'
LOG_SBAR = '<!--' + '-'*50 +'-->\n'

### ---------------------------------------------------------------------------
### ===========================================================================
###
### WirelessLanController
###
### ===========================================================================
### ---------------------------------------------------------------------------

class WirelessLanController(object):
  """
    Juniper Wireless Lan Controller (WLC)
  """

  ### ---------------------------------------------------------------------------
  ### property: hostname
  ### ---------------------------------------------------------------------------

  @property
  def hostname(self):
    """
      The hostname/ip-addr of the WLC
    """
    return self._hostname

  ### ---------------------------------------------------------------------------
  ### property: user
  ### ---------------------------------------------------------------------------
  
  @property
  def user(self):
    """
      The login user accessing the WLC
    """
    return self._user

  ### ---------------------------------------------------------------------------
  ### property: password
  ### ---------------------------------------------------------------------------

  @property
  def password(self):
    """
      The login password to access the WLC
    """
    return None  # read-only      

  @password.setter
  def password(self, value):
    self._password = value

  ### ---------------------------------------------------------------------------
  ### property: timeout
  ### ---------------------------------------------------------------------------

  @property  
  def timeout(self):
    """
      The timeout (seconds) before declaring ping-check timeout
    """
    return self._timeout

  @timeout.setter
  def timeout(self, value):
      self._timeout = value
  
  ### ---------------------------------------------------------------------------
  ### property: logfile
  ### ---------------------------------------------------------------------------

  @property
  def logfile(self):
    """
      simply returns the log file object
    """
    return self._logfile

  @logfile.setter
  def logfile(self, value):
    """
      assigns an opened file object to the WLC for logging
      If there is an open logfile, and 'value' is None/False
      then close the existing file
    """
    # got an existing file that we need to close
    if (not value) and (None != self._logfile):
      rc = self._logfile.close()
      self._logfile = False
      return rc

    if not isinstance(value, file):
      raise ValueError("RHS must be a file object")  

    self._logfile = value
    return self._logfile
  
  # ===========================================================================
  #                                  CONSTRUCTOR
  # ===========================================================================

  def __init__(self, *vargs, **kvargs):
    """
      Required name/value arguments:
      ------------------------------
      - host: hostname/ip-address
      - user: login user
      - password: login password

      Optional name/value arguments:
      ------------------------------
      - port: DEFAULT_PORT(8889)
      - timeout: DEFAULT_TIMEOUT(3)
      - http: DEFAULT_HTTP('https')
      - logfile: False/file object
    """
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
    self._logfile = kvargs.get('logfile', False)
    self._api_uri = None

    self._rpc_factory = RpcFactory()
    self.rpc = _RpcMetaExec(self, self._rpc_factory)
    self.ez = RpcHelper(self, load_helpers=std_rpc_helpers)

  ### ---------------------------------------------------------------------------
  ### _setup_http: used to create/setup HTTP transport mechanism
  ### ---------------------------------------------------------------------------

  def _setup_http(self):

    self._api_uri = '{http}://{host}:{port}{uri}'.format(
      http = self._proto,
      host = self._hostname,
      port = self._port,
      uri = DEFAULT_API_URI )

    auth_mgr = HTTPPasswordMgrWithDefaultRealm()
    auth_mgr.add_password( None, self._api_uri, self._user, self._password )
    auth_hndlr = HTTPBasicAuthHandler(auth_mgr)
    http_hndlr = HTTPHandler(debuglevel=0)
    https_hndlr = HTTPSHandler(debuglevel=0)
    self._http_api = build_opener(auth_hndlr, https_hndlr, http_hndlr)
    self._auth_base64 = base64.encodestring('%s:%s' % (self._user, self._password))[:-1]          

  ### ---------------------------------------------------------------------------
  ### _ping_test(): used to ensure WLC is ping reachable
  ### ---------------------------------------------------------------------------

  def _ping_test(self):
    """
      attempts to ping the WLC device.  This only works on Unix systems that 
      has /bin/ping
    """
    if os.uname()[0] == 'Linux':
      ping = subprocess.Popen(
        ["/bin/ping", "-c1", "-w"+str(self._timeout), self._hostname],
        stdout=subprocess.PIPE) 

    if 0 != ping.wait():
      raise RuntimeError("Unable to ping host: " + self._hostname)

  ### ---------------------------------------------------------------------------
  ### open(): sets up HTTP transport and verifies reachablility
  ### ---------------------------------------------------------------------------

  def open(self):
    """
      Uused to setup the HTTP/s process and verify 
      connectivity and user access to the WLC.  When
      successful, the WLC 'facts' are automatically
      loaded and stored into the 'facts' attribute.  These
      facts are then returned by open().  For details on
      the 'facts' see [helpers/wlc_getfacts.py]
    """

    self._setup_http()
    self._ping_test()

    self.ez.facts()
    return self.facts


  def _log_transaction( self, cmd_txt, rsp_txt ):
    """
      log the information as XML with comment/seprators
    """
    self._logfile.write(LOG_DBAR)
    self._logfile.write(cmd_txt)
    self._logfile.write('\n')
    self._logfile.write(LOG_SBAR)
    self._logfile.write(rsp_txt)
    self._logfile.write('\n')
    self._logfile.flush()

  ### ---------------------------------------------------------------------------
  ### execute(): executes an RPC command
  ### ---------------------------------------------------------------------------

  def execute( self, rpc_cmd ):
    """
      executes RPC command (rpc_cmd) and returns back the RPC result.
      The result in the form of an etree Element

      rpc_cmd: can be in one of two forms:
      - str: fully formulated WLC raw XML as string
      - etree._Element: built from the _RpcFactory 
    """

    if not self._api_uri:
      raise RuntimeError("WLC session has not been opened")

    req = Request( self._api_uri )
    req.add_header('User-Agent', DEFAULT_API_USER_AGENT)         
    req.add_header("Authorization", "Basic %s" % self._auth_base64)

    if isinstance(rpc_cmd, str):
      rpc_cmd_txt = rpc_cmd
      rpc_cmd_e = None
    elif isinstance(rpc_cmd, etree._Element):
      rpc_cmd_txt = etree.tostring( rpc_cmd )
      rpc_cmd_e = rpc_cmd
    else:
      raise ValueError("Dont know what to do with rpc of type %s" % rpc_cmd.__class__.__name__)

    # bind XML data into HTTP request, issue the request, and get
    # back the response as text

    req.add_data('XML=' + rpc_cmd_txt)
    rpc_rsp_txt = self._http_api.open(req).read()

    if self._logfile:
      self._log_transaction( rpc_cmd_txt, rpc_rsp_txt )

    # covert string to XML for processing
    rpc_rsp_e = etree.XML( rpc_rsp_txt)

    # now return the XML element starting with the top of
    # the action response; i.e. the first child

    ret_rsp_e = rpc_rsp_e[0] if len(rpc_rsp_e) else rpc_rsp_e

    if 'ERROR-RESP' == ret_rsp_e.tag:
      # if there is an error, then generate
      # an exception.  Always bind the XML data
      # to the exception. So if the rpc cmd was
      # string, then we need to conver to XML
      if not rpc_cmd_e:
        rpc_cmd_e = etree.XML( rpc_cmd )

      raise RpcError( rpc_cmd_e, ret_rsp_e )

    return ret_rsp_e

  ### ---------------------------------------------------------------------------
  ### RpcMaker: creates a new RpcMaker object bound to this WLC
  ### ---------------------------------------------------------------------------

  def RpcMaker( self, trans='GET', target=None, *vargs, **kvargs ):
    """
      creates a new RpcMaker object bound to this WLC
    """
    return RpcMaker( self, trans, target, vargs, **kvargs )

  ### ---------------------------------------------------------------------------
  ### close(): nada, placeholder for future 'cleanup on close'
  ### ---------------------------------------------------------------------------

  def close(self):
    """
      close performs any necessary object termination/cleanup
      nada at the  moment
      caller is responsible for closing the logfile (for now)
    """

    return True
