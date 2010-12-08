from Products.CMFCore.utils import getToolByName

def setupVarious(context):
    if context.readDataFile('pleiades.geographer_various.txt') is None:
        return
    portal = context.getSite()
    addToCatalog(portal)

def addToCatalog(portal):
    cat = getToolByName(portal, 'portal_catalog', None)
    indexes = [('location_precision', 'KeywordIndex'),]
    reindex = []
    if cat is not None:
        for name, type in indexes:
            if name in cat.indexes():
                continue
            cat.addIndex(name, type)
            reindex.append(name)
        if reindex:
            cat.refreshCatalog()
