import unittest
from pleiades.geographer.tests.base import PleiadesGeographerTestCase
from Products.CMFCore.utils import getToolByName

class SetupTest(PleiadesGeographerTestCase):
    
    def test_location_index(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        self.failUnless('location_precision' in catalog.indexes())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SetupTest))
    return suite
