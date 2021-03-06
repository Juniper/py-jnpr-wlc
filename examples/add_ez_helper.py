
import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

wlc = WLC_login()

##### -------------------------------------------------------------------------
####  add the 'system_services' as an "ez" helper function
##### -------------------------------------------------------------------------

def system_services( wlc, *vargs, **kvargs ):
  """
    create a single dictionary containing information
    about system services: sshd, httpd, tftpd, and telnetd.
    for each of these services we will run the associated 
    GET command, and extract the XML attributes into the
    single/returned dictionary
  """

  run_list = {
    'sshd': wlc.rpc.get_sshd,
    'httpd': wlc.rpc.get_httpd,
    'tftpd': wlc.rpc.get_tftpd,
    'telnetd': wlc.rpc.get_telnetd
  }

  ret_data = {}     # empty dictionary

  for svc, rpc in run_list.items():
    rsp = rpc()                           # execute the RPC
    ret_data[svc] = dict(rsp[0].attrib)   # copy the attributes into a dictionary

  return ret_data
  
##### -------------------------------------------------------------------------
##### MAIN BLOCK
##### -------------------------------------------------------------------------

# add this new routine to the WLC "ez" section.
wlc.ez( helper=system_services )

# now call the service
print "Retrieving System Services ..."
si = wlc.ez.system_services()

# now show the info:
print "System Services:"
pp(si)

# and you could do things like:
# >>> [svc for svc in si.keys() if si[svc]['enabled'] == "YES"]
# ['httpd', 'sshd', 'telnetd']
# >>> [svc for svc in si.keys() if si[svc]['enabled'] != "YES"]
# ['tftpd']


