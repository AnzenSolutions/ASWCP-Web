import os
import re
from decimal import Decimal, InvalidOperation

"""
This config class is based on the code found here:
https://github.com/jpf/Twilio-TFA/blob/master/konfig.py

The idea behind it was nice, but we expanded it:

- If ".config" is not found in the current directory, it checks ~/.config
- Instead of storing values in a dictionary, we store it as an attribute of the class itself

This can also be used for plugins to read files and store config settings for plugins.
Though, not heavily advised, due to increased risk of a setting not being set.

If a config setting is already found, it'll be passed over and not stored.

Optional arguments:
conf_file - Config file to look for (default: .config)
defaults - Default settings for any required settings (default: nothing [nothing is required])
"""
class Konf(object):
	def __init__(self, conf_file=".config", defaults={}):
		# Used more for safe keeping than anything else
		filename = conf_file

		# Anything loaded?  (default: no)
		self.loaded = False

		# True if config file found, else false (default)
		conf_file_found = False

		# If the filename doesn't exist, see if its in the user's home directory
		if not os.path.isfile(filename):
			filename = "%s/%s" % (os.path.expanduser("~"), filename)

			# Still not found?  No config exists
			if os.path.isfile(filename):
				conf_file_found = True
		else:
			conf_file_found = True

		# Only parse the conf file if it exists
		if conf_file_found:
			# I'm horrible at regex, but this is what I have found to use that will allow
			# setting options to either "val" or val (i.e.: name="Test" port = 8888)
			conf_match = re.compile(r'([^\s=]+)\s*=\s*\"?([^\"]*)\"?')

			# Read each line of the config file, match it against the regex, and attempt to save it
			for line in open(filename).readlines():
				line_match = conf_match.match(line)

				# We found a match on the line
				if line_match:
					# The value of the config option (strip out any whitespaces [strip() also removes spaces which we don't want])
					val = str(line_match.group(2)).strip("\r\n")

					# The name of the config option
					name = line_match.group(1)

					self.set(name, val)

		self.load_defaults(defaults)
		
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

	"""
	Sets class attribute 'name' to 'value'.
	I.e.: set("bob", "hope") would be retrieved as konf.bob which will return hope.

	Returns False if 'name' already exists.  True otherwise.
	"""
	def set(self, name, value):
		try:
			object.__getattribute__(self, name)
			return False
		except AttributeError:
			setattr(self, name, self.val2fmt(value))
			
			if not self.loaded:
				self.loaded = True

			return True

	def update(self, name, value):
		try:
			object.__getattribute__(self, name)
			setattr(self, name, self.val2fmt(value))
		except AttributeError:
			pass

	"""
	After the config file has been read, we want to set up any missing conf values that are required.

	Iterate through a dictionary (passed by plugin [plugin.defaults]) of default config values.
	"""
	def load_defaults(self, defaults):
		for name,value in defaults.iteritems():
			# If it exists don't do anything
			try:
				object.__getattribute__(self, name)
			except AttributeError:
				# If it doesn't exist, AttributeError is raised, which means we need to set it
				setattr(self, name, self.val2fmt(value))

	"""
	Similar to __getattr__().
	Retrieves a class' attribute, otherwise returns None if environment fallback fails.

	Basically, when konf.some_name is called, it goes through this process:
	- Checks if class has the attribute
	- If not (AttributeError exception), check to see if its in the environment
	- If not (NameError), return None
	"""
	def __getattribute__(self, name):
		try:
			return object.__getattribute__(self, name)
		except AttributeError:
			try:
				return os.getenv(key)
			except NameError:
				return None
