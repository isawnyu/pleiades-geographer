# ===========================================================================
# Copyright (C) 2010 ISAW, New York University
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
# About Pleiades
# --------------
#
# Pleiades is an international research network and associated web portal and
# content management system devoted to the study of ancient geography. 
#
# See http://pleiades.stoa.org
#
# Funding for the creation of this software was provided by a grant from the 
# U.S. National Endowment for the Humanities (http://www.neh.gov).
# ===========================================================================

import logging
from shapely.geometry import asShape, mapping, MultiPoint, shape
import simplejson as json

from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import nobody
from plone.memoize.instance import memoize
from zope.interface import implements

from pleiades.capgrids import Grid, parseURL
from pleiades.contentratings.basic import rating
from pleiades.geographer.interfaces import ILocatable, IRepresentativePoint
from pleiades.geographer.interfaces import IConnected, ILocated, IExtent
from Products.PleiadesEntity.content.interfaces import ILocation
from Products.PleiadesEntity.content.interfaces import IPlace
from Products.PleiadesEntity.time import temporal_overlap
from zgeo.geographer.interfaces import IGeoreferenced

log = logging.getLogger('pleiades.geographer')

PRECISIONS = ['precise', 'related', 'rough', 'unlocated']


class NotLocatedError(Exception):
    pass


class LocationGeoItem(object):
    implements(IGeoreferenced)

    def __init__(self, context):
        """Expect getGeometry() returns a string like
        'Point:[-105.0, 40.0]'
        """
        self.context = context
        dc_coverage = self.context.getLocation()
        if context._getGeometryRaw():
            self.geo = json.loads(context.getGeometryJSON())
            g = asShape(self.geo)
            self.geo.update(bbox=g.bounds)
        elif dc_coverage.startswith('http://atlantides.org/capgrids'):
            try:
                mapid, gridsquare = parseURL(dc_coverage)
                grid = Grid(mapid, gridsquare)
                self.geo = dict(
                    bbox=grid.bounds, 
                    relation='relates', 
                    type=grid.type, 
                    coordinates=grid.coordinates)
            except Exception, e:
                log.warn("%s: %s, %s" % (
                    str(e), context, context.getLocation()))
                raise NotLocatedError, "Location cannot be determined"
        else:
            raise NotLocatedError, "Location cannot be determined"
            
    @property
    def __geo_interface__(self):
        return self.geo #.__geo_interface__

    @property
    def bounds(self):
        return self.geo['bbox']

    @property
    def type(self):
        return self.geo['type']

    @property
    def coordinates(self):
        return self.geo['coordinates']

    @property
    def precision(self):
        return 'rough' * (
            self.geo.get('relation', None) is not None) or 'precise'

    @property
    def crs(self):
        return None


class FeatureGeoItem(object):
    implements(IGeoreferenced)
   
    def __init__(self, context):
        """Initialize adapter."""
        self.context = context
        self._adapter = None
        x = list(self.context.getLocations())
        if len(x) == 0:
            raise ValueError, "Unlocated: could not adapt %s" % str(context)
        else:
            self._adapter = IGeoreferenced(x[0])

    @property
    def type(self):
        return self._adapter.type

    @property
    def coordinates(self):
        return self._adapter.coordinates

    @property
    def crs(self):
        return None

    @property
    def __geo_interface__(self):
        context = self.context
        return dict(
            type='Feature',
            id=context.getId(),
            geometry=self._adapter.__geo_interface__
            )


class PlaceGeoItem(object):
    
    """Python expression of a GeoRSS simple item.
    """
    implements(IGeoreferenced)
   
    def __init__(self, context):
        """Initialize adapter."""
        self.context = context
        self.geo = None
        x = []
        for o in self.context.getLocations():
            try:
                x.append(IGeoreferenced(o))
            except NotLocatedError:
                continue
        if len(x) > 0:
            precise = [xx for xx in x if xx.precision == 'precise']
            if len(precise) >= 1:
                x = precise
            self.geo = self._geo(x)
        else:
            geo_parts = []
            for ob in self.context.getFeatures():
                try:
                    # rule out reference circles
                    assert self.context not in ob.getParts()
                    geo_parts.append(IGeoreferenced(ob))
                except:
                    pass
            for ob in self.context.getParts():
                try:
                    # rule out reference circles
                    assert self.context not in ob.getParts()
                    geo_parts.append(IGeoreferenced(ob))
                except:
                    pass
            if geo_parts:
                self.geo = self._geo(geo_parts)
        if self.geo is None:
            raise NotLocatedError, "Location cannot be determined"

    def _geo(self, obs):
        # Returns a geometric object or a bounding box for multiple objects
        if len(obs) == 1:
            return obs[0].geo
        else:
            xs = []
            ys = []
            fuzzy = []
            for o in obs:
                if o.__geo_interface__.has_key('relation'):
                    fuzzy.append(o)
                    continue
                b = o.bounds
                xs += b[0::2]
                ys += b[1::2]
            for o in fuzzy:
                b = o.bounds
                xs += b[0::2]
                ys += b[1::2]
            try:
                x0, x1, y0, y1 = (min(xs), max(xs), min(ys), max(ys))
            except Exception, e:
                log.warn("Failed to adapt %s in _geo(): %s", obs, str(e))
                return None
            coords = [[[x0, y0], [x0, y1], [x1, y1], [x1, y0], [x0, y0]]] 
            return dict(
                bbox=(x0, y0, x1, y1), 
                relation='relates' * int(bool(fuzzy)) or None, 
                type='Polygon', 
                coordinates=coords)
    
    @property
    def bounds(self):
        return self.geo['bbox']
    
    @property
    def type(self):
        return self.geo['type']

    @property
    def coordinates(self):
        return self.geo['coordinates']

    @property
    def precision(self):
        return 'rough' * (
            self.geo.get('relation', None) is not None) or 'precise'

    @property
    def crs(self):
        return None

    @property
    def __geo_interface__(self):
        context = self.context
        return dict(
            type='Feature',
            id=context.getId(),
            bbox=self.geo['bbox'],
            geometry=self.geo
            )

class NameGeoItem(PlaceGeoItem):
    
    """Python expression of a GeoRSS simple item, temporally sensitive
    """
    implements(IGeoreferenced)
   
    def __init__(self, context):
        """Initialize adapter."""
        self.context = context
        self.geo = None
        x = []
        place = self.context.aq_parent
        for o in filter(
            lambda x: temporal_overlap(self.context, x),
            place.getLocations()):
            try:
                x.append(IGeoreferenced(o))
            except NotLocatedError:
                continue
        if len(x) > 0:
            self.geo = self._geo(x)
        else:
            geo_parts = []
            for ob in self.context.getFeatures():
                try:
                    # rule out reference circles
                    assert self.context not in ob.getParts()
                    geo_parts.append(IGeoreferenced(ob))
                except:
                    pass
            for ob in self.context.getParts():
                try:
                    # rule out reference circles
                    assert self.context not in ob.getParts()
                    geo_parts.append(IGeoreferenced(ob))
                except:
                    pass
            if geo_parts:
                self.geo = self._geo(geo_parts)
        if self.geo is None:
            raise NotLocatedError, "Location cannot be determined"


def createGeoItem(context):
    """Factory for adapters."""
    if IPlace.providedBy(context):
        return PlaceGeoItem(context)
    else:
        return FeatureGeoItem(context)


class RepresentativePoint(object):
    """Adapter for Locations and Names."""
    implements(IRepresentativePoint)
    
    def __init__(self, context):
        self.context = context
        try:
            g = IGeoreferenced(context)
            self.precision = g.precision
            if not g.coordinates:
                raise NotLocatedError, "Adapter has no coordinates"
            if g.type == 'Point':
                self.coords = tuple(g.coordinates)
            else:
                self.coords = tuple(asShape(
                    {'type': g.type, 'coordinates': g.coordinates}
                    ).centroid.coords )[0]
        except NotLocatedError:
            self.precision = "unlocated"
            self.coords = None

    @property
    def x(self):
        try:
            return self.coords[0]
        except TypeError:
            raise NotLocatesError, "Context %s is unlocated" % self.context
    @property
    def y(self):
        try:
            return self.coords[1]
        except TypeError:
            raise NotLocatesError, "Context %s is unlocated" % self.context


# Functions to support synoptic views of Pleiades data.

def extent(obj):
    # "unlocated", "rough", "related", "precise"
    # Executed as anonymous to keep unpublished data out
    sm = getSecurityManager()
    try:
        newSecurityManager(None, nobody.__of__(obj.acl_users))
        ex = IExtent(obj)
        setSecurityManager(sm)
        return {'extent': ex.extent, 'precision': ex.precision}
    except NotLocatedError:
        setSecurityManager(sm)
        return {'extent': None, 'precision': 'unlocated'}
    except:
        setSecurityManager(sm)
        log.warn("Failed to adapt %s in 'location_precision'", obj)
        return None


def location_precision(obj):
    # "unlocated", "rough", "related", "precise"
    # Executed as anonymous to keep unpublished data out
    ex = extent(obj)
    return ex and ex.get('precision', 'unlocated') or None


def representative_point(obj):
    # Get a representative point as Anonymous."""
    sm = getSecurityManager()
    try:
        newSecurityManager(None, nobody.__of__(obj.acl_users))
        pt = IRepresentativePoint(obj)
        setSecurityManager(sm)
        return {'precision': pt.precision, 'coords': pt.coords}
    except NotLocatedError:
        setSecurityManager(sm)
        return {'precision': 'unlocated', 'coords': None}
    except:
        setSecurityManager(sm)
        log.warn("Failed to adapt %s in 'representative_point'", obj)
        return None


def zgeo_geometry_centroid(brain):
    """For use on catalog brains"""
    geom = brain.zgeo_geometry
    if geom['type'] == 'Point':
        return tuple(geom['coordinates'])
    else:
        return tuple(asShape(geom).centroid.coords)[0]

# New implementations of ILocated and IConnected

def geometry(o):
    """Returning a mapping or None."""
    if ILocation.providedBy(o) and o._getGeometryRaw():
        geom = json.loads(o.getGeometryJSON())
        g = shape(geom)
        geom.update(bbox=g.bounds)
        return geom
    else:
        return None


def isPrecise(o):
    return ILocation.providedBy(o) and o._getGeometryRaw()


def isGridded(o):
    return ILocation.providedBy(o) and o.getLocation(
        ).startswith('http://atlantides.org/capgrids')


class PlaceLocated(object):
    implements(ILocated)
    
    def __init__(self, context):
        self.context = context
        self.locations = self.context.getLocations()

    def ratedPreciseGeoms(self):
        return sorted(
            (rating(o), geometry(o)
            ) for o in filter(isPrecise, self.locations ))
    
    def ratedGridGeoms(self):
        return sorted(
            (rating(o), mapping(LocationGeoItem(o))
            ) for o in filter(isGridded, self.locations ))


class PlaceConnected(object):
    implements(IConnected)
    
    def __init__(self, context):
        self.context = context
        self.connections = list(
            self.context.getRefs("connectsWith"
                ) + self.context.getBRefs("connectsWith") )

    def preciseExtents(self):
        return map(lambda x: x.extent,
            filter(
                lambda x: x.precision == "precise",
                (PlaceExtent(o) for o in self.connections) ))

    def relatedExtents(self):
        return map(lambda x: x.extent,
            filter(
                lambda x: x.precision in ("related", "rough"),
                (PlaceExtent(o) for o in self.connections) ))

# Extents

def explode(coords):
    """Explode a GeoJSON geometry's coordinates object and yield 
    coordinate tuples."""
    for e in coords:
        if isinstance(e, (float, int, long)):
            yield coords
            break
        else:
            for f in explode(e):
                yield f


def hull(points):
    return mapping(MultiPoint(points).convex_hull)


class PlaceExtent(object):
    implements(IExtent)
    ## Status: working, tests pass 10/29.

    def __init__(self, context):
        self.context = context

    @memoize
    def reprExtent(self):

        points = []

        located = PlaceLocated(self.context)
        rated = located.ratedPreciseGeoms()
        
        if rated:
            positively_rated = filter(lambda x: x[0] > 0, rated)
            unrated = filter(lambda x: x[0] == 0, rated)

            if positively_rated:
                for r, g in positively_rated:
                    points.extend(list(explode(g['coordinates'])))
            if not points and unrated:
                for r, g in unrated:
                    points.extend(list(explode(g['coordinates'])))
            
            return hull(points), "precise"

        connected = PlaceConnected(self.context)
        extents = connected.preciseExtents()
        if extents:
            for g in extents:
                points.extend(list(explode(g['coordinates'])))
            return hull(points), "related"

        rated = located.ratedGridGeoms()
        if rated:
            for r, g in rated:
                points.extend(list(explode(g['coordinates'])))
            return hull(points), "rough"
                
        extents = connected.relatedExtents()
        if extents:
            for g in extents:
                points.extend(list(explode(g['coordinates'])))
            return hull(points), "rough"

        # The end.
        return None, "unlocated"

    @property
    def extent(self):
        """A Polygon."""
        return self.reprExtent()[0]

    @property
    def precision(self):
        return self.reprExtent()[1]


class LocationExtent(PlaceExtent):
    implements(IExtent)

    @memoize
    def reprExtent(self):
        try:
            g = IGeoreferenced(self.context)
            points = list(explode(g.coordinates))
            return hull(points), g.precision
        except:
            return None, "unlocated"


# Repesentative Point

class PlaceReprPt(object):
    implements(IRepresentativePoint)

    def __init__(self, context):
        self.context = context

    @memoize
    def reprPoint(self):
        
        located = PlaceLocated(self.context)
        rated = located.ratedPreciseGeoms()
        if rated:
            sum_positive = []
            weight_positive = 0.0
            sum_unrated = []
            weight_unrated = 0.0
            
            for r, g in rated:
                centroid = shape(g).centroid
                if r > 0.0:
                    sum_positive[:] = (
                        (sum_positive and sum_positive[0] or 0.0) + r*centroid.x, 
                        (sum_positive and sum_positive[1] or 0.0) + r*centroid.y )
                    weight_positive += r
                else:
                    sum_unrated[:] = (
                        (sum_unrated and sum_unrated[0] or 0.0) + centroid.x, 
                        (sum_unrated and sum_unrated[1] or 0.0) + centroid.y )
                    weight_unrated += 1.0
            
            if weight_positive > 0.0:
                return (
                    sum_positive[0]/weight_positive, 
                    sum_positive[1]/weight_positive,
                    "precise" )
            elif weight_unrated > 0.0:
                return (
                    sum_unrated[0]/weight_unrated, 
                    sum_unrated[1]/weight_unrated,
                    "precise" )
            else:
                raise RuntimeError, "Rated locations summed improperly"

        connected = PlaceConnected(self.context)
        extents = connected.preciseExtents()
        if extents:
            c = []
            for g in extents:
                centroid = shape(g).centroid
                c[:] = (c and c[0] or 0.0
                    ) + centroid.x, (c and c[1] or 0.0) + centroid.y
            return c[0]/len(extents), c[1]/len(extents), "related"
        
        rated = located.ratedGridGeoms()
        if rated:
            c = []
            for r, g in rated:
                centroid = shape(g).centroid
                c[:] = (c and c[0] or 0.0
                    ) + centroid.x, (c and c[1] or 0.0) + centroid.y
            return c[0]/len(rated), c[1]/len(rated), "rough"
                
        extents = connected.relatedExtents()
        if extents:
            c = []
            for g in extents:
                centroid = shape(g).centroid
                c[:] = (c and c[0] or 0.0
                    ) + centroid.x, (c and c[1] or 0.0) + centroid.y
            return c[0]/len(extents), c[1]/len(extents), "rough"

        # The end.
        return None, None, "unlocated"

    @property
    def coords(self):
        return tuple(self.reprPoint()[:2])
    
    @property
    def x(self):
        return self.reprPoint()[0]

    @property
    def y(self):
        return self.reprPoint()[1]
    
    @property
    def precision(self):
        return self.reprPoint()[2]

