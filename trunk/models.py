import datetime

from django.db                      import models
from django.utils.translation       import ugettext_lazy as _
from django.db.models               import permalink
from django.contrib.auth.models     import User

from django.db                      import models
from django.db.models               import signals, Q
from django.template.defaultfilters import slugify
from django.db.models.signals       import pre_save
from tumblelog.agro.models          import Entry

import datetime
import urllib
import urllib2

GEOCODE_REQUEST_URL = "http://maps.google.com/maps/geo?q=%(req)s&output=csv&key=%(key)s"
GOOGLEKEY = 'ABQIAAAAG8P9j9QQO2vTUNEZdr-SshReiASGFcOL9meyLzP_xSrPCnkYihQw3YdDdS63AOOtwipBY7YuQXiJtg'

class GAddress(models.Model):
    name = models.CharField(max_length=100)    
    description = models.CharField(max_length=400, blank=True)        
    address = models.CharField(max_length=100)
    auto_geocode = models.BooleanField(default=True, blank=True,
        help_text="Automatically derive the latitude/longitude from the address above. "
                  "Note that this overrides any manual setting.")
    latitude = models.CharField(max_length=100, blank=True)
    longitude = models.CharField(max_length=100, blank=True)
    
    def __unicode__(self):
        return self.slug or '<no slug>'
        
    def geocode(self):
        loc = [self.address]
        url = GEOCODE_REQUEST_URL % {
            'req': urllib.quote_plus(', '.join(loc)),
            'key': GOOGLEKEY
        }
        data = urllib2.urlopen(url).read()
        response_code, accuracy, latitude, longitude = data.split(',')
        self.latitude = latitude
        self.longitude = longitude
        
    def __unicode__(self):
        return self.name or '<no slug>'
    
class GMap(models.Model):    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100,
        help_text="Make sure there are no hyphens in the slug. It will break.")
    
    description = models.CharField(max_length=500, blank=True)
    
    zoom_level = models.DecimalField(max_digits=2, decimal_places=1,blank=True,
        help_text="Default zoom should be 3.")
    locations = models.ManyToManyField(GAddress)
    entries = models.ManyToManyField(Entry, null=True, blank=True)
    
    javascript = models.TextField(blank=True)
    
    def create_javascript(self):
        javascript = ""
        i = 0
        for address in self.locations.all():
            if i == 0:
                javascript += """\nvar map%s = new GMap2(document.getElementById('map%s'));""" % ( self.slug, self.slug )
                javascript += """\nmap%s.setCenter(new GLatLng(%s, %s), %s);""" % ( self.slug,address.latitude,address.longitude,self.zoom_level)          
            javascript += """\nvar point  = new GLatLng(%s, %s);""" % ( address.latitude,address.longitude )
            javascript += """\nmap%s.addOverlay(new GMarker(point));""" % ( self.slug )
            i += 1
        self.javascript = javascript
    
    def __unicode__(self):
        return self.name or '<no slug>'

def set_geographical_vars(sender, instance, **kwargs):
    try:
        if instance.auto_geocode:
            instance.geocode()
    except urllib2.URLError:
        pass
        
def create_javascript(sender, instance, **kwargs):
    try:
        instance.create_javascript()
    except:
        pass
        
models.signals.pre_save.connect(set_geographical_vars, sender=GAddress)
models.signals.pre_save.connect(create_javascript, sender=GMap)