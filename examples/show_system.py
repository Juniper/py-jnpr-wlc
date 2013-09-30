import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

wlc = WLC_login()

# just display the dict of the values
si = wlc.ez.facts()

print "System Name: %s" % si['name']
print "System IP Address: %s" % si['ip-addr']
print "System MAC: %s" % si['macaddress']
print "System Serial Number: %s" % si['serialnumber']
print "S/W Version: %s" % si['booted-version']
print "H/W Model: %s" % si['model']
print "H/W Version: %s" % si['platform']


#print "DUMPNIG ALL DATA":
#pp(si)

