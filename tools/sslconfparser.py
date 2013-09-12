import os
import re
from decimal import Decimal, InvalidOperation

"""
Parses OpenSSL config (typically openssl.cnf) files for use in SSL certificate generation.
"""
class scp(object):
    def __init__(self, conf_file="/etc/ssl/openssl.cnf", defaults={}):
        # Anything loaded?  (default: no)
        self.loaded = False
        
        self.heart = {}
        
        # Only parse the conf file if it exists
        if os.path.isfile(conf_file):
            self.cnf = conf_file
            
            # I'm horrible at regex, but this is what I have found to use that will allow
            # setting options to either "val" or val (i.e.: name="Test" port = 8888)
            conf_match = re.compile(r'([^\s=\[#]+)\s*=\s*([^#]*)#?')

            # Read each line of the config file, match it against the regex, and attempt to save it
            for line in open(conf_file).readlines():
                line_match = conf_match.match(line)

                # We found a match on the line
                if line_match:
                    # The value of the config option (strip out any whitespaces [strip() also removes spaces which we don't want])
                    val = line_match.group(2).strip()

                    # The name of the config option
                    name = line_match.group(1)

                    self.set(name, val)
                    
        self.loaded = True

    """
    Converts config value to bool (if either true,yes,1,false,no,0)

    Otherwise returns None
    """
    def str2bool(self, v):
        ans = None

        try:
            v = v.lower()
        except AttributeError:
            return ans

        if v in ("true", "yes", "1", "t"):
            ans = True
        elif v in ("false", "no", "0", "f"):
            ans = False

        return ans

    """
    Converts config value to numeric, else returns False.

    Uses Decimal() class as its too annoying to try and accomendate every different type.
    """
    def str2num(self, v):
        # Any issues in converting we just return False
        try:
            return Decimal(v)
        except:
            return False

    """
    Converts config value to either its respected format, or returns itself.
    """
    def val2fmt(self, v):
        fmt = self.str2bool(v)

        if fmt == None:
            fmt = self.str2num(v)

            if fmt == False:
                fmt = v

        return fmt
    
    def __getitem__(self, key):
        return self.heart[key]
    
    def __setitem__(self, key, val):
        self.heart[key] = self.val2fmt(val)
        
    """
    Sets class attribute 'name' to 'value'.
    I.e.: set("bob", "hope") would be retrieved as konf.bob which will return hope.

    Returns False if 'name' already exists.  True otherwise.
    """
    def set(self, name, value):
        try:
            self.__getitem__(name)
            return False
        except KeyError:
            self.__setitem__(name, value)
            
            if not self.loaded:
                self.loaded = True
            
            return True
        
    def update(self, name, value):
        try:
            object.__getattribute__(self, name)
            setattr(self, name, self.val2fmt(value))
        except AttributeError:
            pass
