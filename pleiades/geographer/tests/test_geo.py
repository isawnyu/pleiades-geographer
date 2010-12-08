import unittest
from Testing import ZopeTestCase as ztc
from pleiades.geographer.tests.base import PleiadesGeographerFunctionalTestCase

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        ztc.ZopeDocFileSuite(
            'README.txt', package='pleiades.geographer',
            test_class=PleiadesGeographerFunctionalTestCase)
        )
    return suite

