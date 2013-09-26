import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 

wlc = WLC_login()

# just display the dict of the values
data = wlc.version()
pp(data)
