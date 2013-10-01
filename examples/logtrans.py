import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

wlc = WLC_login()

### just let the user play around with the wlc object
### from the python interpreter

wlc.logfile = open(r'/var/tmp/'+wlc.hostname+'.txt', "w+")



