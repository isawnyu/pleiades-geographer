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
  >>> from collective.geo.geographer.interfaces import IGeoreferenced
  >>> g = IGeoreferenced(p1)
  >>> gi = g.__geo_interface__
  >>> gi['type']
  'Feature'
  >>> g.type
  'Point'
  >>> g.coordinates
  [-86.4808333333333, 34.769722222222]
  >>> g.bounds
  (-86.4808333333333, 34.769722222222, -86.4808333333333, 34.769722222222)
  >>> g.precision
  'precise'

Add another location to the place and check that we get back a box for p1 and p2

  >>> lid = p1.invokeFactory('Location', 'x', geometry='Point:[-85.4808333333333, 35.769722222222]')
  >>> g = IGeoreferenced(p1)
  >>> gi = g.__geo_interface__
  >>> gi['type']
  'Feature'
  >>> g.type
  'Polygon'
  >>> g.coordinates
  [[[-86.4808333333333, 34.769722222222], [-86.4808333333333, 35.769722222222], [-85.4808333333333, 35.769722222222], [-85.4808333333333, 34.769722222222], [-86.4808333333333, 34.769722222222]]]
  >>> g = IGeoreferenced(p1)
  >>> gi = g.__geo_interface__
  >>> gi['type']
  'Feature'
  >>> g.type
  'Polygon'
  >>> g.coordinates
  [[[-86.4808333333333, 34.769722222222], [-86.4808333333333, 35.769722222222], [-85.4808333333333, 35.769722222222], [-85.4808333333333, 34.769722222222], [-86.4808333333333, 34.769722222222]]]

And check that the representative point is a centroid

  >>> from pleiades.geographer.interfaces import IRepresentativePoint
  >>> pt = IRepresentativePoint(p1)
  >>> pt.precision
  'precise'
  >>> pt.coords
  (-85.9808333333333, 35.269722222222)


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
  [-85.4808333333333, 35.769722222222]

And the representative point

  >>> pt = IRepresentativePoint(ninoe)
  >>> pt.coords
  (-85.4808333333333, 35.769722222222)
  >>> pt.precision
  'precise'

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
  >>> pt.precision
  'unlocated'
  >>> pt.coords is None
  True

