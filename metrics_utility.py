# Enable debugging flag
be_debug = True

# Enable debugging
def be_debug_enable():
    global be_debug
    be_debug = True

# Disable debugging
def be_debug_disable():
    global be_debug
    be_debug = False

def log_debug(msg):
    global be_debug
    if be_debug:
        print(msg)

def log_error(msg):
        print(msg)

def ssl_enabled():
    return False

