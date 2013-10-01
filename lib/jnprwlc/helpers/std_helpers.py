from .wlc_getfacts import wlc_getfacts

## anything included in the 'std_rpc_helpers' will automatically
## be added to the WLC 'ez' attribute when the WLC object is
## initially created. 

std_rpc_helpers = {
  'facts': wlc_getfacts
}
