
from zope.interface import Attribute, Interface

class ILocatable(Interface):
    """Marker interface for location_precision index"""

class IRepresentativePoint(Interface):
    """A representative point for a content item"""
    coords = Attribute("""(x, y) tuple""")
    precision = Attribute("""Precision of related geometries""")
    relation = Attribute("""Relationship to related geometries""")

