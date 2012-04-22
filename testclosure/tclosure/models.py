from django.db import models
from closuretree.models import ClosureModel

# Create your models here.

class TC(ClosureModel):
	parent2 = models.ForeignKey("self", related_name="children", null=True, blank=True)
	name = models.CharField(max_length=32)
	blah = models.ForeignKey("Blah", related_name="tcs", null=True, blank=True)

	class ClosureMeta(object):
		parent_attr = "parent2"

	def __unicode__(self):
		return "%s: %s" % (self.id, self.name)

class Blah(models.Model):
	thing = models.CharField(max_length=32)

class TCSUB(TC):
	extrafield = models.IntegerField()

class TCSUB2(TCSUB):
	ef = models.IntegerField()

TCClosure = TC.create_closure_model()



class A(models.Model):
	foo = models.CharField(max_length=1, default='N')
	
	def __init__(self, *args, **kwargs):
		super(A, self).__init__(*args, **kwargs)
		

	def __setattr__(self, item, value):
		super(A, self).__setattr__(item, value)
	
class B(A):
	bar = models.CharField(max_length=1, default='X')

