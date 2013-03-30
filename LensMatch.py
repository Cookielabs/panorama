

class LensMatch:

	def __init__( self, resource ):
		self.resource = resource
		self.instance_lens = set()
		self.class_lens = set()
		self.default_lens = set()
		self.label_lens = set()

	def addInstanceLens( self, lens ):
		self.instance_lens.add( lens )

	def addClassLens( self, lens ):
		self.class_lens.add( lens )
	
	def addDefaultLens( self, lens ):
		self.default_lens.add( lens )
	
	def addLabelLens( self, lens ):
		self.label_lens.add( lens )

	def getInstanceLens( self ):
		return self.instance_lens

	def getClassLens( self ):
		return self.class_lens

	def getLabelLens( self ):
		return self.label_lens

	def getDefaultLens( self ):
		return self.default_lens
