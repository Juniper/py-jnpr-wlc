def wlc_save_config(wlc, *vargs, **kvargs):
  # write the config.  if there happens to be an exception
  # it will get thrown.  otherwise, everything is OK, and 
  # just return True
  wlc.rpc.act_write_configuration()
  return True

def wlc_get_config(wlc, *vargs, **kvargs):
  # shorty cut for grabbing the entire XML config, yo!
  return wlc.rpc.get_configuration()
