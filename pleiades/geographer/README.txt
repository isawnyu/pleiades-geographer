Introduction
============

  >>> folder = self.folder
  >>> places = folder['places']

Test the geo adapters
---------------------

First place, explicitly located
    
  >>> pid1 = places.invokeFactory('Place', '1', title='Ninoe')
  >>> p1 = places[pid1]
  >>> lid = p1.invokeFactory('Location', 'location', title='Point 1', geometry='Point:[-86.4808333333333, 34.769722222222]')
  >>> from zgeo.geographer.interfaces import IGeoreferenced
  >>> g = IGeoreferenced(p1)
  >>> gi = g.__geo_interface__
  >>> gi['type']
  'Feature'
  >>> g.type
  'Point'
  >>> g.coordinates
  [-86.480833333333294, 34.769722222222001]
  >>> g.bounds
  (-86.480833333333294, 34.769722222222001, -86.480833333333294, 34.769722222222001)
  >>> g.precision
  'precise'

Add second place
  
  >>> pid2 = places.invokeFactory('Place', '2', title='Ninoe')
  >>> p2 = places[pid2]
  >>> p2.setParts([p1])

For a "fuzzy" place with no location of its own, we should get the envelope of
its parts. A point in this case.

  >>> g = IGeoreferenced(p2)
  >>> gi = g.__geo_interface__
  >>> gi['type']
  'Feature'
  >>> g.type
  'Point'
  >>> g.coordinates
  [-86.480833333333294, 34.769722222222001]

Add another location to the part and check that we get back a box for p1 and p2

  >>> lid = p1.invokeFactory('Location', 'x', geometry='Point:[-85.4808333333333, 35.769722222222]')
  >>> g = IGeoreferenced(p1)
  >>> gi = g.__geo_interface__
  >>> gi['type']
  'Feature'
  >>> g.type
  'Polygon'
  >>> g.coordinates
  [[[-86.480833333333294, 34.769722222222001], [-86.480833333333294, 35.769722222222001], [-85.480833333333294, 35.769722222222001], [-85.480833333333294, 34.769722222222001], [-86.480833333333294, 34.769722222222001]]]
  >>> g2 = IGeoreferenced(p2)
  >>> gi2 = g2.__geo_interface__
  >>> gi2['type']
  'Feature'
  >>> g2.type
  'Polygon'
  >>> g2.coordinates
  [[[-86.480833333333294, 34.769722222222001], [-86.480833333333294, 35.769722222222001], [-85.480833333333294, 35.769722222222001], [-85.480833333333294, 34.769722222222001], [-86.480833333333294, 34.769722222222001]]]

Add another place part

  >>> pid3 = places.invokeFactory('Place', '3', title='Ninoe')
  >>> p3 = places[pid3]
  >>> _ = p3.invokeFactory('Location', 'x', geometry='Point:[0.0, 0.0]')
  >>> p2.setParts([p1, p3])
  >>> g2 = IGeoreferenced(p2)
  >>> gi2 = g2.__geo_interface__
  >>> gi2['type']
  'Feature'
  >>> g2.type
  'Polygon'
  >>> g2.coordinates
  [[[-86.480833333333294, 0.0], [-86.480833333333294, 35.769722222222001], [0.0, 35.769722222222001], [0.0, 0.0], [-86.480833333333294, 0.0]]]
  >>> g2.precision
  'precise'

Test the index value callable

  >>> from pleiades.geographer.geo import location_precision
  >>> pid4 = places.invokeFactory('Place', '4', title='Ninoe')
  >>> p4 = places[pid4]
  >>> location_precision(p4, None)
  'unlocated'
  >>> _ = p4.invokeFactory('Location', 'x', location="http://atlantides.org/capgrids/65/b2")
  >>> location_precision(p4, None)
  'rough'
  >>> p4['x'].setGeometry('Point:[0.0, 0.0]')
  >>> location_precision(p4, None)
  'precise'


