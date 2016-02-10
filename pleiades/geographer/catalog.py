
import logging

from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import nobody
from plone.indexer.decorator import indexer
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from shapely.geometry import shape

from pleiades.geographer.geo import location_precision, NotLocatedError
from pleiades.geographer.interfaces import IExtent, ILocatable
from pleiades.geographer.interfaces import IRepresentativePoint
from Products.PleiadesEntity.content.interfaces import ILocation

log = logging.getLogger('pleiades.geographer')


# To be registered as an indexable attribute adapter
# For use with pleiades.vaytrouindex
@indexer(ILocation)
def location_geo(obj, **kw):
    url_tool = getToolByName(obj, 'portal_url')
    portal_path = url_tool.getPortalObject().getPhysicalPath()
    ob_path = obj.getPhysicalPath()[len(portal_path):]
    try:
        ex = IExtent(obj).extent
        return dict(
            id=obj.getPhysicalPath(),
            bbox=shape(ex).bounds,
            properties=dict(
                path='/'.join(ob_path),
                pid=obj.getId(),
                title=obj.Title(),
                description=obj.Description(),
                ),
            geometry=ex
            )
    except (AttributeError, NotLocatedError, TypeError, ValueError), e:
        log.warn("Failed to adapt %s in 'location_geo': %s", obj, str(e))
        return None

@indexer(ILocatable)
def location_precision_indexer(obj, **kw):
    return location_precision(obj)

@indexer(ILocatable)
def zgeo_geometry_value(obj, **kw):
    # Execute this as 'Anonymous'
    try:
        sm = getSecurityManager()
        newSecurityManager(None, nobody.__of__(obj.acl_users))
        ex = IExtent(obj)
        setSecurityManager(sm)
        return ex.extent
    except:
        setSecurityManager(sm)
        raise AttributeError

@indexer(ILocatable)
def reprPt_value(obj, **kw):
    # Execute this as 'Anonymous'
    try:
        sm = getSecurityManager()
        newSecurityManager(None, nobody.__of__(obj.acl_users))
        pt = IRepresentativePoint(obj)
        setSecurityManager(sm)
        return pt.coords, pt.precision
    except:
        setSecurityManager(sm)
        raise AttributeError

@indexer(ILocatable)
def bbox_value(obj, **kw):
    # Execute this as 'Anonymous'
    try:
        sm = getSecurityManager()
        newSecurityManager(None, nobody.__of__(obj.acl_users))
        ex = IExtent(obj)
        setSecurityManager(sm)
        return tuple(shape(ex.extent).bounds)
    except:
        setSecurityManager(sm)
        raise AttributeError
        
