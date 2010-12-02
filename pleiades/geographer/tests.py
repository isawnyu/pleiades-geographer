import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

from pleiades.workspace.tests.base import ContentFunctionalTestCase

ztc.installProduct('ATVocabularyManager')
ztc.installProduct('Products.CompoundField')
ztc.installProduct('Products.ATBackRef')
ztc.installProduct('Products.OrderableReferenceField')
ztc.installProduct('pleiades.vocabularies')
ztc.installProduct('PleiadesEntity')

@onsetup
def setup_pleiades_geographer():
    """Set up the additional products required for the Pleiades site policy.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """

    # Load the ZCML configuration for the optilux.policy package.
    
    fiveconfigure.debug_mode = True
    import pleiades.kml
    zcml.load_config('configure.zcml', pleiades.geographer)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    ztc.installPackage('pleiades.vocabularies')
    ztc.installPackage('Products.PleiadesEntity')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the Pleiades package. Then, we let 
# PloneTestCase set up this product on installation.

setup_pleiades_geographer()

ptc.setupPloneSite(products=['PleiadesEntity',])

import pleiades.geographer

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             pleiades.geographer)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

    def afterSetUp(self):
        # Currently this stuff isn't being torn down between doctests. Why not?
        try:
            self.folder.invokeFactory('PlaceContainer', id='places')
        except:
            pass


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='pleiades.geographer',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='pleiades.geographer.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'README.txt', package='pleiades.geographer',
            test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='pleiades.geographer',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
