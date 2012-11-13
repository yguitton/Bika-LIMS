"""
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_users
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.config import *
from bika.lims.interfaces import IDoctor
from bika.lims.permissions import *
from bika.lims.content.contact import Contact
from bika.lims import PMF, bikaMessageFactory as _
from zope.interface import implements

schema = Contact.schema.copy() + Schema((
    StringField('DoctorID',
        required=1,
        widget=StringWidget(
            label=_('Doctor ID'),
        ),
    ),
))

class Doctor(Contact):
    implements(IDoctor)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    # This is copied from Client (Contact acquires it, but we cannot)
    security.declarePublic('getContactsDisplayList')
    def getContactsDisplayList(self):
        pc = getToolByName(self, 'portal_catalog')
        pairs = []
        for contact in pc(portal_type = 'Doctor', inactive_state = 'active'):
            contact = contact.getObject()
            pairs.append((contact.UID(), contact.Title()))
        for contact in pc(portal_type = 'Contact', inactive_state = 'active'):
            contact = contact.getObject()
            pairs.append((contact.UID(), contact.Title()))
        for contact in pc(portal_type = 'LabContact', inactive_state = 'active'):
            contact = contact.getObject()
            pairs.append((contact.UID(), contact.Title()))
        # sort the list by the second item
        pairs.sort(lambda x, y:cmp(x[1], y[1]))
        return DisplayList(pairs)

    # This is copied from Contact (In contact, it refers to the parent's
    # getContactsDisplayList, while we define our own
    security.declarePublic('getCCContactsDisplayList')
    def getCCContactsDisplayList(self):
        pairs = []
        all_contacts = self.getContactsDisplayList().items()
        # remove myself
        for item in all_contacts:
            if item[0] != self.UID():
                pairs.append((item[0], item[1]))
        return DisplayList(pairs)

    security.declarePublic('getSamples')
    def getSamples(self):
        """ get all samples taken from this Patient """
        bc = getToolByName(self, 'bika_catalog')
        return [p.getObject() for p in bc(portal_type='Sample', getDoctorUID=self.UID())]

    security.declarePublic('getARs')
    def getARs(self, analysis_state):
        bc = getToolByName(self, 'bika_catalog')
        return [p.getObject() for p in bc(portal_type='AnalysisRequest', getDoctorUID=self.UID())]

atapi.registerType(Doctor, PROJECTNAME)
