
import os
from sys import argv as ARGV
from jnprwlc import JuniperWirelessLanController as WLC
from lxml import etree
from pprint import pprint as pp
import argparse
from getpass import getpass
from urllib2 import HTTPError

### ---------------------------------------------------------------------------
### parse the command line args
### ---------------------------------------------------------------------------

def _parse_args():
  cli = argparse.ArgumentParser(
    description="WLC API runner"
    )
  cli.add_argument( '-u', '--user',     action="store", dest='user',      default=os.getenv('USER'))
  cli.add_argument( '-t', '--target',   action="store", dest='target',    default=None)
  cli.add_argument( '-p', '--password', action="store", dest='password',  default=None )

  cli_args = cli.parse_args()
  if not cli_args.password: cli_args.password = getpass()

  try:
    user,target = cli_args.user.split('@')
    cli_args.user = user
    cli_args.target = target
  except ValueError: pass

  return cli_args

### ---------------------------------------------------------------------------
### 
### ---------------------------------------------------------------------------

def WLC_login():
  cli_args = _parse_args()

  login = {
   'user': cli_args.user,
   'host': cli_args.target,
   'password': cli_args.password
  }

  wlc = WLC( login )

  try_again = 3
  login_ok = False
  while try_again > 1:
    try:
      wlc.open()
      login_ok = True
      break;
    except HTTPError as err:
      if 401 == err.code:  
        print "Password failed, try again."
        try_again -= 1
        wlc.password = getpass()

  if not login_ok:
    print "Too many login failures, exiting"
    os.exit(1)

  return wlc

def ppxml(xml): print etree.tostring(xml,pretty_print=True)

