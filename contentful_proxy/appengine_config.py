import os

from google.appengine.ext import vendor
vendor.add(os.path.join(os.path.dirname(__file__), '../ext'))
