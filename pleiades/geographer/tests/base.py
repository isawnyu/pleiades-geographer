from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc

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
    fiveconfigure.debug_mode = True
    import pleiades.geographer
    zcml.load_config('configure.zcml', pleiades.geographer)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    ztc.installPackage('pleiades.vocabularies')
    ztc.installPackage('Products.PleiadesEntity')
    ztc.installPackage('pleiades.geographer')


# The order here is important: We first call the (deferred) function which
# installs the products we need for the Pleiades package. Then, we let
# PloneTestCase set up this product on installation.

setup_pleiades_geographer()
ptc.setupPloneSite(products=['PleiadesEntity', 'pleiades.geographer'])


class PleiadesGeographerTestCase(ptc.PloneTestCase):
    """Base class for unit tests"""


class PleiadesGeographerFunctionalTestCase(ptc.PloneTestCase):
    def afterSetUp(self):
        # Currently this stuff isn't being torn down between doctests. Why not?
        try:
            self.folder.invokeFactory('PlaceContainer', id='places')
        except:
            pass
