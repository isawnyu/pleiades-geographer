
from Products.CMFPlone.CatalogTool import registerIndexableAttribute

from pleiades.geographer.geo import location_precision


registerIndexableAttribute('location_precision', location_precision)

