import maya.cmds as cmds
import maya.mel as mel

# Created 17/04/14 Jason Dixon
# http://internetimagery.com/

################### SAVING DATA INTO THE SCENE OUTLINER

data_name = 'Shot_Pieces_Data'

def hideChannels(node): #hide transforms etc for visual cleanliness
	if cmds.objExists(node):
		default_attr = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
		cmds.setAttr( (node+'.v'), False)
		for attr in default_attr:
			cmds.setAttr( (node+'.'+attr), k=False, cb=False )

def createNodeContainer():
	if not cmds.objExists(data_name):
		cmds.group( n= data_name, em=True, w=True)
		hideChannels(data_name)

def listNodes(): #encapsulate then list nodes
	new = []
	if cmds.objExists(data_name):
		node_list = cmds.listRelatives(data_name)
		if node_list:
			for n in node_list:
				if cmds.attributeQuery('nts',n=n,ex=True) and cmds.attributeQuery('max',n=n,ex=True) and cmds.attributeQuery('min',n=n,ex=True) and cmds.attributeQuery('col',n=n,ex=True):
					new.append( ShotPiece(n) )
	return new

def createNode(): #create node to hold information
	createNodeContainer()
	node = cmds.group( n= 'Shot_Piece', em = True, p=data_name)
	hideChannels(node)
	cmds.addAttr( node, sn='nts', ln='notes', dt='string')
	cmds.addAttr( node, sn='min' , ln='minRange', h=True)
	cmds.addAttr( node, sn='max' , ln='maxRange')
	cmds.addAttr( node, sn='col' , ln='colour', dt='float3')
	return node

def deleteNode(node):
	if cmds.objExists(node):
		cmds.delete(node)

def setAttribute(obj, attr, value): #set attribute, regardles of type.
	try:
		cmds.setAttr((obj+'.'+attr),value)
	except RuntimeError:
		try:
			cmds.setAttr((obj+'.'+attr),value,type='string')
		except RuntimeError:
			try:
				cmds.setAttr((obj+'.'+attr),value[0],value[1],value[2],type='float3')
			except RuntimeError:
				raise

###################

def windowCheck(mod): #check GUI exists
	return cmds.window( mod.GUI['window'], exists=True, q=True)

def warningMessage(message):
	cmds.confirmDialog(title='Oh, hold up a sec...', message=message)

###################

class ShotPiece(object): #A single shot piece
	def __init__(self, node = None):
		self.data = {}
		self.GUI = {}

		if node and cmds.objExists(node):
			self.node = node
		else:
			self.node = createNode()
		self.read()

	def update(self, **attr ): #update data details
		for at in attr:
			if cmds.objExists(self.node) and cmds.attributeQuery(at,n=self.node,ex=True):
				setAttribute(self.node, at, attr[at])
				self.data[at] = attr[at]
		self.updateButton()

	def updateButton(self):
		total = (1/(cmds.playbackOptions( q=True, aet=True ) - cmds.playbackOptions( q=True, ast=True )))*(self.data['max'] - self.data['min'])
		height = 25+(30*total)
		try:
			cmds.button( self.GUI['button1'], e=True, l=self.data['nts'], bgc=self.data['col'], h=height)
		except KeyError:
			pass
	def read(self):
		if self.node and cmds.objExists(self.node):
			self.data['nts'] = cmds.getAttr( (self.node+'.nts') ) if cmds.getAttr( (self.node+'.nts') ) else 'Edit text.'
			self.data['min'] = cmds.getAttr( (self.node+'.min') )
			self.data['max'] = cmds.getAttr( (self.node+'.max') )
			self.data['col'] = cmds.getAttr( (self.node+'.col') )[0] if cmds.getAttr( (self.node+'.col') ) else [0.3,0.3,0.3]
			return self.data

	def createGUI(self, layout):
		total = (1/(cmds.playbackOptions( q=True, aet=True ) - cmds.playbackOptions( q=True, ast=True )))*(self.data['max'] - self.data['min'])
		height = 25+(30*total)
		self.GUI['button1'] = cmds.button(p=layout, c=self.setRange, h=height)
		self.updateButton()
		cmds.popupMenu()
		cmds.menuItem(l='Edit', c=Callback(CreatePiece, self, True))
		cmds.menuItem(l='Delete', c=self.removeGUI)

	def removeGUI(self, button):
		for ui in self.GUI:
			cmds.control( self.GUI[ui], e=True, m=False)
		deleteNode(self.node)

	def setRange(self, button):
		cmds.playbackOptions(e=True, min=self.data['min'], max=self.data['max'] )

###################

class Callback(object):
		def __init__(self, func, *args, **kwargs):
				self.func = func
				self.args = args
				self.kwargs = kwargs
		def __call__(self, *args):
				return self.func( *self.args, **self.kwargs )

###################

class GUI(object): #main GUI window
	def __init__(self):
		self.GUI = {} #set up GUI elements
		nodes = listNodes()

		self.GUI['window'] = cmds.window( title = 'Shot Pieces', rtf=True, s=False)
		self.GUI['layout1'] = cmds.columnLayout( adjustableColumn=True )
		self.GUI['button1'] = cmds.button( l='Create Shot Piece', h=25, c=self.AddPiece )
		cmds.separator()
		#cmds.setParent('..')
		#cmds.showWindow( self.GUI['window'] )
		allowed_areas = ['right', 'left']
		self.GUI['dock'] = cmds.dockControl(a='left',content=self.GUI['window'],aa=allowed_areas,fl=True,l='Shot Pieces')
		if nodes: #generate GUI
			for n in nodes:
				n.createGUI( self.GUI['layout1'] )

	def AddPiece(self, button): #create new button
		CreatePiece( self, False )

###################

class CreatePiece(object):
	def __init__(self, mod, edit = False):
		self.GUI = {}
		self.edit = edit
		self.mod = mod

		self.GUI['window'] = cmds.window( title = 'Create a Shot Piece', rtf=True, s=False)
		self.GUI['layout1'] = cmds.columnLayout( adjustableColumn=True )
		self.GUI['text1'] = cmds.text( l='Describe the Piece of your Shot.', h=25)
		self.GUI['scrollfield1'] = cmds.scrollField( h=80 )
		self.GUI['layout2'] = cmds.rowColumnLayout( nc=2 )
		self.GUI['int1'] = cmds.intField()
		self.GUI['int2'] = cmds.intField()
		cmds.setParent('..')
		self.GUI['button1'] = cmds.button( l='Use selected range.', h=30, c=self.TimeRange )
		self.GUI['button2'] = cmds.button( l='Choose a colour', h=30, c=self.ColourPick, bgc=[0.25,0.25,0.25] )
		self.GUI['button3'] = cmds.button( l='Create', h=30, c=self.SendPiece )
		cmds.setParent('..')
		cmds.showWindow( self.GUI['window'] )

		if self.edit:
			existing_data = self.mod.read()
			cmds.scrollField( self.GUI['scrollfield1'], e=True, text=existing_data['nts'])
			cmds.intField( self.GUI['int1'], e=True, v=existing_data['min'])
			cmds.intField( self.GUI['int2'], e=True, v=existing_data['max'])
			cmds.button( self.GUI['button2'], e=True, bgc=existing_data['col'])
			cmds.button( self.GUI['button3'], e=True, l='Save Changes')

	def ColourPick(self, button):
		result = cmds.colorEditor(rgb=cmds.button(self.GUI['button2'],q=True,bgc=True))
		buffer = result.split()
		if '1' == buffer[3]:
			self.colour = cmds.colorEditor(query=True, rgb=True)
			cmds.button( self.GUI['button2'], e=True, bgc=cmds.colorEditor(query=True, rgb=True))

	def TimeRange(self, button):
		slider = mel.eval('$tempvar = $gPlayBackSlider')
		if cmds.timeControl(slider, rv=True, q=True ):
			(time1,time2) = cmds.timeControl(slider, q=True, ra=True )
		else:
			time1 = cmds.playbackOptions( q=True, min=True )
			time2 = cmds.playbackOptions( q=True, max=True )
		cmds.intField( self.GUI['int1'], e=True, v=time1 )
		cmds.intField( self.GUI['int2'], e=True, v=time2 )

	def SendPiece(self, button):
		if self.edit or windowCheck(self.mod):
			text = cmds.scrollField( self.GUI['scrollfield1'], q=True, text=True).strip()
			if text:
				time1 = cmds.intField( self.GUI['int1'], v=True, q=True )
				time2 = cmds.intField( self.GUI['int2'], v=True, q=True )
				if time1 > time2:
				   	time1, time2 = time2, time1
				lower_limit = cmds.playbackOptions(q=True,ast=True)
				upper_limit = cmds.playbackOptions(q=True,aet=True)
				time1 = time1 if lower_limit < time1 < upper_limit else lower_limit
				time2 = time2 if lower_limit < time2 < upper_limit else upper_limit
				if time1 == time2:
					warningMessage('There needs to be a time range.')
				else:
					if self.edit:
						piece = self.mod
					else:
						node = createNode()
						piece = ShotPiece(node)
						piece.createGUI(self.mod.GUI['layout1'])
					piece.update( nts=text, min=time1, max=time2, col=cmds.button(self.GUI['button2'],q=True,bgc=True) )
					cmds.deleteUI(self.GUI['window'])
			else:
				warningMessage('You need to give your selection a description.')
		else:
			cmds.deleteUI(self.GUI['window'])