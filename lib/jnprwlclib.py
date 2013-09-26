
import pdb

import sys
import os
import subprocess
import re

from sys import argv as ARGV
from urllib2 import Request
from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, HTTPDigestAuthHandler
from urllib2 import HTTPHandler, HTTPSHandler, build_opener
from urllib2 import HTTPError
import base64
from lxml import etree

class _RpcFactory(object):
  HELLO = """
    <TRANSACTION tid="0">
    <SESSION/>
    </TRANSACTION>
  """
  def __init__( self, wlc ):
    self._wlc = wlc
    self._tid = 1

  def next(self):
    rpc_e = etree.XML( self.__class__.HELLO)
    rpc_e.attrib['tid'] = str(self._tid)
    self._tid += 1
    return rpc_e

  def get(self, target, *vargs, **kvargs ):
    """
      ACTION: GET
    """
    rpc_e = self.next()
    get_e = etree.SubElement(rpc_e, "GET")
    get_e.attrib['level'] = 'all'
    target_e = etree.SubElement( get_e, target.upper() )    

    if kvargs:  # kvargs is the <key>=<value> for a unique object
      key, value = next(kvargs.iteritems())
      target_e.attrib[key] = str(value)

    return rpc_e

  def get_stat(self, target, *vargs, **kvargs ):
    """
      ACTION: GET-STAT
    """
    rpc_e = self.next()
    get_e = etree.SubElement(rpc_e, "GET-STAT")
    target_e = etree.SubElement( get_e, target.upper() )    

    if kvargs:  # kvargs is the <key>=<value> for a unique object
      key, value = next(kvargs.iteritems())
      target_e.attrib[key] = str(value)

    return rpc_e

class _RpcHelpers(object):

  def __init__(self, wlc ):
    self._wlc = wlc
    self._helper_fntbl = {}

  def get(self, method):
    if method in self._helper_fntbl:
      return self._helper_fntbl[method]
    return False

  def set(self, method, method_fn):
    self._helper_fntbl[method] = method_fn
    return method_fn

### ---------------------------------------------------------------------------
### builtin RPC helpers
### ---------------------------------------------------------------------------

def _wlc_version(self, *vargs, **kvargs):
  """
    return a merged dict of BOOTSTATUS and SYSTEMSTATUS information
  """
  bs_rpc_rsp = self.rpc(self._rpc.get('bootstatus'))
  ss_rpc_rsp = self.rpc(self._rpc.get('systemstatus'))
  data = {}
  data.update(bs_rpc_rsp[0].attrib)
  data.update(ss_rpc_rsp[0].attrib)
  return data

_builtin_rpc_helpers = {
  'version': _wlc_version
}

### ---------------------------------------------------------------------------
### primary class for managing WLC devices
### ---------------------------------------------------------------------------

class JuniperWirelessLanController(object):

  DEFAULT_HTTP = 'https'
  DEFAULT_PORT = 8889
  DEFAULT_API_URI = "/trapeze/ringmaster"
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

    self._rpc = _RpcFactory( self )
    self._rpc_helpers = _RpcHelpers( self )

    for method, method_fn in _builtin_rpc_helpers.items():
      self._rpc_helpers.set( method, method_fn )

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

    rpc_cmd = self._rpc.next()
    rpc_rsp = self.rpc( rpc_cmd )

    return True if rpc_rsp.attrib['nerrors'] == "0" else False

  hello = open    # alias 'hello()' to 'open()'

  def close(self):
    """
      doesn't do anything ... for now.
    """
    return True

  def rpc( self, rpc_data ):
    """
      transmits RPC command and returns back the RPC result as etree Element

      rpc_data - can be either raw XML as string, or etree Element
    """
    req = Request( self._api_uri )
    req.add_header('User-Agent', 'Juniper Networks RingMaster')         
    req.add_header("Authorization", "Basic %s" % self._auth_base64)

    if isinstance(rpc_data, str):
      req.add_data('XML=' + rpc_data )
    elif isinstance(rpc_data, etree._Element):
      req.add_data('XML=' + etree.tostring( rpc_data ))

    rsp_e = etree.XML(self._http_api.open(req).read())

    # @@@ should do common error checking here
    # return the XML element starting with the top of
    # the action response; i.e. the first child

    return rsp_e[0] if len(rsp_e) else rsp_e

  ### -------------------------------------------------------------------------
  ###
  ### Methods to implement XML RPC invocations
  ###
  ### -------------------------------------------------------------------------

  def add_rpc_helper( self, method, method_fn ):
    return self._rpc_helpers.set( method, method_fn )

  def get(self, target, *vargs, **kvargs ):
    rpc_cmd = self._rpc.get( target, vargs, **kvargs )
    return self.rpc( rpc_cmd )

  def get_stat(self, target, *vargs, **kvargs ):
    rpc_cmd = self._rpc.get_stat( target, vargs, **kvargs )
    return self.rpc( rpc_cmd )
    
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

      # see if there is a helper_rpc for this method call
      fn_helper = self._rpc_helpers.get(method)
      if fn_helper: 
        def _call_helper( *vargs, **kvargs):
          return fn_helper(self, vargs, **kvargs)
        return _call_helper

      # don't know what to do, so raise an exception
      raise AttributeError, "Cannot process method %s" % method


