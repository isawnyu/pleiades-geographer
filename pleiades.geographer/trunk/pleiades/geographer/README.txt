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

And check that the representative point is a centroid

  >>> from pleiades.geographer.interfaces import IRepresentativePoint
  >>> pt = IRepresentativePoint(p1)
  >>> pt.relation
  'centroid'
  >>> pt.coords
  (-85.980833333333294, 35.269722222222001)

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


Check temporally sensitive Name adapter
---------------------------------------

  >>> atts1 = [{'timePeriod': "roman", 'confidence': "confident"}]
  >>> nid = places[pid1].invokeFactory('Name', 'ninoe')
  >>> ninoe = places[pid1][nid]
  >>> field = ninoe.getField('attestations')
  >>> field.resize(len(atts1))
  >>> ninoe.update(attestations=atts1)
  >>> x = places[pid1]['x']
  >>> field = x.getField('attestations')
  >>> field.resize(len(atts1))
  >>> x.update(attestations=atts1)
  >>> gn = IGeoreferenced(ninoe)
  >>> gn.type
  'Point'
  >>> gn.coordinates
  [-85.480833333333294, 35.769722222222001]

And the representative point

  >>> pt = IRepresentativePoint(ninoe)
  >>> pt.coords
  (-85.480833333333294, 35.769722222222001)
  >>> pt.relation
  'exact'

If there's no colocated location

  >>> x = places[pid1]['x']
  >>> field = x.getField('attestations')
  >>> field.resize(0)
  >>> x.update(attestations=[])
  >>> gn = IGeoreferenced(ninoe)
  Traceback (most recent call last):
  ...
  NotLocatedError: Location cannot be determined
  >>> pt = IRepresentativePoint(ninoe)
  Traceback (most recent call last):
  ...
  NotLocatedError: Location cannot be determined

There have been some problems with 2 locations with identical coordinates:

  >>> from shapely.geometry import asShape
  >>> del p1['location']
  >>> lid = p1.invokeFactory('Location', 'y', geometry='Point:[-85.4808333333333, 35.769722222222]')
  >>> p1.getLocations()
  []
  >>> g = IGeoreferenced(p1)
  >>> asShape(g.geo).centroid.wkt
  None
  >>> g.geo
  {}



