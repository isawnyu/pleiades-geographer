from zope.interface import Attribute, Interface


class ILocatable(Interface):
    """Marker interface for location_precision index"""


class IConnected(Interface):
    """A thing connected to the extents of other things."""

    def preciseExtents():
        """Returns a sequence of precise extent geometries."""

    def relatedExtents():
        """Returns a sequence of related or fuzzy extent geometries."""


class IRepresentativePoint(Interface):
    """A representative point for a content item"""

    coords = Attribute("""(x, y) tuple""")

    precision = Attribute("""Precision of the representative point.
        'precise' means that it's computed from precise locations of the thing.
        'related' means that it's computed from precisely located connections
        of the thing. 'rough' means that it's computed from grid locations of
        the thing or roughly located connections.""")

    x = Attribute("""X coordinate value""")

    y = Attribute("""Y coordinate value""")


class IExtent(Interface):
    """The geographic extent of a thing"""

    extent = Attribute("""A GeoJSON-ish geometry mapping. May be any
        type. The extent of a point place is a point.""")

    precision = Attribute("""Precision of the representative point.
        'precise' means that it's computed from precise locations of the thing.
        'related' means that it's computed from precisely located connections
        of the thing. 'rough' means that it's computed from grid locations of
        the thing or roughly located connections.""")
