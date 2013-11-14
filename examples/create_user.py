import demowlcutils
from demowlcutils import ppxml, WLC_login
from pprint import pprint as pp 
import jinja2
from lxml import etree
from lxml.builder import E
from time import sleep

wlc = WLC_login()


# define a function to use the WLC to generate encrypted user passwords. This is better 
# then trying to reverse engineer the internal passwd scheme.
    
def encrypt_secret(text, mode='userpass', ssid=''):
    if mode == 'userpass':
        rsp = wlc.rpc.act_encrypt(text=text)
    elif mode == 'psk':
        if ssid == '':
            raise ValueError("To generate an encrypted PSK, you must supply the SSID name")
        rsp = wlc.rpc.act_encrypt(text=text, method='WPA-PSK', ssid=ssid)

    encrypted_str = rsp.find('ENCRYPT-RESP').attrib['etext']
    return encrypted_str


# create an example function to create named and mac user config on the WLC. 
# XXX - revisit this, if the type arg is messed up, i think this will silently fail

def add_user(wlc, username, type='named', password=''):
    rpc = wlc.RpcMaker('set')
    rpc.data = E('AAA', E('USERDB', E('USER-TABLE')))
    user_table = rpc.data.find(".//USER-TABLE")
            
    if type == 'named':
        user_table.append(E('NAMED-USER',{'name':username, 'password':encrypt_secret(password)},
                           E('USER-PARAMETER-LIST')))
    elif type == 'mac':
        user_table.append(E('MAC-USER',{'name':username},
                           E('USER-PARAMETER-LIST')))
    
    return wlc.rpc(rpc.as_xml)
    
    
def delete_user(wlc, username, type='named'):
    rpc = wlc.RpcMaker('delete')
    rpc.data = E('AAA', E('USERDB', E('USER-TABLE')))
    user_table = rpc.data.find(".//USER-TABLE")
            
    if type == 'named':
        user_table.append(E('NAMED-USER',{'name':username}))
    elif type == 'mac':
        user_table.append(E('MAC-USER',{'name':username}))
    
    return wlc.rpc(rpc.as_xml)    
    

user = 'bob'
macuser = '00:01:02:03:04:05'
userpass = 'testing123'
ssid = 'somessid'


# test encrypted string generation
print('raw userpass: %s encrypted text: %s' % (userpass, encrypt_secret(userpass)))
print('raw psk: %s encrypted psk: %s' % (userpass, encrypt_secret(userpass, mode='psk', ssid=ssid)))


# create a named user
print('creating named user: %s with password: %s' % (user, userpass))
r = add_user(wlc, user, password=userpass)

# create a mac user
print('creating mac user: %s' % (macuser))
r = add_user(wlc, macuser, type='mac')

sleep(20)

# delete a named user
print('deleting named user: %s' % (user))
r = delete_user(wlc, user)

# delete a mac user
print('deleting mac user: %s' % (macuser))
r = delete_user(wlc, macuser, type='mac')