from .wlc_getfacts import wlc_getfacts
from .wlc_config import *

std_rpc_helpers = {
  'facts': wlc_getfacts,
  'save_config' : wlc_save_config,
  'get_config' : wlc_get_config
}
