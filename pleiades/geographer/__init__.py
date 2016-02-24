# Make sure collective.geo.geographer continues to read/write
# geographic annotations in the same location that zgeo.geographer did
import collective.geo.geographer.geo
collective.geo.geographer.geo.KEY = 'zgeo.geographer.georeference'
