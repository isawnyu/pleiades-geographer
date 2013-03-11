
from zope.publisher.browser import BrowserView

from pleiades.geographer.interfaces import IRepresentativePoint
from pleiades.geographer.interfaces import IExtent
from pleiades.geographer.geo import explode

class Where(BrowserView):
    def __call__(self):
        pt = IRepresentativePoint(self.context).coords
        extent = IExtent(self.context).extent
        bounds = None
        if extent and pt:
            coords = list(explode(extent['coordinates']))
            xy = zip(*coords)
            minx = min(xy[0])
            maxx = max(xy[0])
            miny = min(xy[1])
            maxy = max(xy[1])
            return { 
                'bbox': (minx, miny, maxx, maxy), 
                'reprPt': pt, 
                'extent': extent }
        else:
            return None

