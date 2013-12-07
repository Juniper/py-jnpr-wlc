import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
from lxml.builder import E
from lxml import etree
from jinja2 import Template
import random

wlc = WLC_login()
rpc = wlc.RpcMaker('set')


# for this example we assume that the service profile we want to modify already exists
serviceprofile = 'test_ssid'
psks = ['random1234', 'random2341', 'random3412']


# this is the encrypt fn out of the create_user example. This probably needs a better 
# place to live.
def encrypt_secret(text, mode='userpass', ssid=''):
    if mode == 'userpass':
        rsp = wlc.rpc.act_encrypt(text=text)
    elif mode == 'psk':
        if ssid == '':
            raise ValueError("To generate an encrypted PSK, you must supply the SSID name")
        rsp = wlc.rpc.act_encrypt(text=text, method='WPA-PSK', ssid=ssid)

    encrypted_str = rsp.find('ENCRYPT-RESP').attrib['etext']
    return encrypted_str


# we need to grab the existing service profiles so we can update the PSK
config = wlc.rpc.get_configuration()

# grab the service profile table and the service profile we're interested in
sptable = config.find(".//SERVICE-PROFILE-TABLE")
sp = sptable.find(".//SERVICE-PROFILE[@name='%s']" % (serviceprofile))

# SSID name may not match service profile name and the generated psk will need the actual
# beaconed SSID.
ssid = sp.attrib['ssid']
newpsk = random.choice(psks)
encryptedpsk = encrypt_secret(newpsk, mode='psk', ssid=ssid)
print('rotating psk for SSID: %s to new PSK: %s' % (ssid, newpsk))
print('encrypted psk: %s' % (encryptedpsk))

# update the sp (with the new psk)
sp.set('the-psk', encryptedpsk)

# create the NSYSTEM object and append the updated serivce profile settings
rpc.data = E('NSYSTEM')
rpc.data.append(sptable) 

# fire! 
r = rpc()

# we've finished creating the filter and mapping it, save config
wlc.rpc.act_write_configuration()


