import maya.cmds as cmds
import maya.mel as mel
import json

# Created 17/04/14 Jason Dixon
# http://internetimagery.com/

shot_save_name = "shot_piece"
################### SAVING DATA INTO THE SCENE OUTLINER


def save(uuid, data):
    cmds.fileInfo(uuid, json.dumps(data))


def load(uuid):
    return json.loads(cmds.fileInfo(uuid, q=True)[0].decode("unicode_escape"))


def delete(uuid):
    cmds.fileInfo(rm=uuid)


def listShots():
    return [val for i, val in enumerate(cmds.fileInfo(q=True)) if not i % 2 and shot_save_name in val]


def pieceInit():
    return [ShotPiece(shot) for shot in listShots()]


def uuid():
    i = 0
    name = "%s_%s" % (shot_save_name, i)
    while len(cmds.fileInfo(name, q=True)) != 0:
        i += 1
        name = "%s_%s" % (shot_save_name, i)
    return name

###################


def windowCheck(mod):  # check GUI exists
    return cmds.window(mod.GUI['window'], exists=True)


def dockCheck(mod):
    return cmds.dockControl(mod.GUI["dock"], ex=True)


def warningMessage(message):
    cmds.confirmDialog(title='Oh, hold up a sec...', message=message)

###################


class ShotPiece(object):  # A single shot piece
    def __init__(self, uuid):
        self.id = uuid
        self.data = {}
        self.GUI = {}

        self.data = self.read()

    def update(self, **attr):  # update data details
        for at in attr:
            self.data[at] = attr[at]
            save(self.id, self.data)
        self.updateButton()

    def updateButton(self):
        total = (1/(cmds.playbackOptions(q=True, aet=True) - cmds.playbackOptions(q=True, ast=True)))*(self.data['max'] - self.data['min'])
        height = 25+(30*total)
        try:
            cmds.button(self.GUI['button1'], e=True, l=self.data['nts'], bgc=self.data['col'], h=height)
        except KeyError as e:
            print e
            pass

    def read(self):
        data = self.data if self.data else load(self.id)
        if data:
            self.data['nts'] = data["nts"] if data['nts'] else "Edit text."
            self.data['min'] = data["min"] if data["min"] else 0
            self.data['max'] = data["max"] if data["max"] else 0
            self.data['col'] = data["col"] if data["col"] else [0.3, 0.3, 0.3]
            return self.data

    def createGUI(self, layout):
        total = (1/(cmds.playbackOptions(q=True, aet=True) - cmds.playbackOptions(q=True, ast=True)))*(self.data['max'] - self.data['min'])
        height = 25+(30*total)
        self.GUI['button1'] = cmds.button(p=layout, c=self.setRange, h=height)
        self.updateButton()
        cmds.popupMenu()
        cmds.menuItem(l='Edit', c=Callback(CreatePiece, self, True))
        cmds.menuItem(l='Delete', c=self.removeGUI)

    def removeGUI(self, button):
        for ui in self.GUI:
            cmds.control(self.GUI[ui], e=True, m=False)
        delete(self.id)

    def setRange(self, button):
        cmds.playbackOptions(e=True, min=self.data['min'], max=self.data['max'])

###################


class Callback(object):
        def __init__(self, func, *args, **kwargs):
                self.func = func
                self.args = args
                self.kwargs = kwargs

        def __call__(self, *args):
                return self.func(*self.args, **self.kwargs)

###################


class GUI(object):  # main GUI window

    def __init__(self):
        self.GUI = {}  # set up GUI elements
        piece = pieceInit()

        self.GUI['window'] = cmds.window(title='Shot Pieces', rtf=True, s=False)
        self.GUI['layout1'] = cmds.columnLayout(adjustableColumn=True)
        self.GUI['button1'] = cmds.button(l='Create Shot Piece', h=25, c=self.AddPiece)
        cmds.separator()
        # cmds.setParent('..')
        # cmds.showWindow(self.GUI['window'])
        allowed_areas = ['right', 'left']
        self.GUI['dock'] = cmds.dockControl(a='left', content=self.GUI['window'], aa=allowed_areas, fl=True, l='Shot Pieces', fcc=self.MoveDock, vcc=self.CloseDock)
        if piece:  # generate GUI
            for n in piece:
                n.createGUI(self.GUI['layout1'])

    def AddPiece(self, button):  # create new button
        CreatePiece(self, False)

    def MoveDock(self):
        if cmds.dockControl(self.GUI['dock'], q=True, fl=True):
            print "Window Floating"
        else:
            area = cmds.dockControl(self.GUI['dock'], q=True, a=True)
            print "Window Docked into %s" % area

    def CloseDock(self, *loop):
        visible = cmds.dockControl(self.GUI['dock'], q=True, vis=True)
        if not visible and loop:
            cmds.scriptJob(ie=self.CloseDock, p=self.GUI['dock'], ro=True)
        elif not visible:
            cmds.deleteUI(self.GUI['dock'], control=True)

###################


class CreatePiece(object):
    def __init__(self, mod, edit=False):
        self.GUI = {}
        self.edit = edit
        self.mod = mod

        self.GUI['window'] = cmds.window(title='Create a Shot Piece', rtf=True, s=False)
        self.GUI['layout1'] = cmds.columnLayout(adjustableColumn=True)
        self.GUI['text1'] = cmds.text(l='Describe the Piece of your Shot.', h=25)
        self.GUI['scrollfield1'] = cmds.scrollField(h=80)
        self.GUI['layout2'] = cmds.rowColumnLayout(nc=2)
        self.GUI['int1'] = cmds.intField()
        self.GUI['int2'] = cmds.intField()
        cmds.setParent('..')
        self.GUI['button1'] = cmds.button(l='Use selected range.', h=30, c=self.TimeRange)
        self.GUI['button2'] = cmds.button(l='Choose a colour', h=30, c=self.ColourPick, bgc=[0.25, 0.25, 0.25])
        self.GUI['button3'] = cmds.button(l='Create', h=30, c=self.SendPiece)
        cmds.setParent('..')
        cmds.showWindow(self.GUI['window'])

        if self.edit:
            existing_data = self.mod.read()
            cmds.scrollField(self.GUI['scrollfield1'], e=True, text=existing_data['nts'])
            cmds.intField(self.GUI['int1'], e=True, v=existing_data['min'])
            cmds.intField(self.GUI['int2'], e=True, v=existing_data['max'])
            cmds.button(self.GUI['button2'], e=True, bgc=existing_data['col'])
            cmds.button(self.GUI['button3'], e=True, l='Save Changes')

    def ColourPick(self, button):
        result = cmds.colorEditor(rgb=cmds.button(self.GUI['button2'], q=True, bgc=True))
        buffer = result.split()
        if '1' == buffer[3]:
            self.colour = cmds.colorEditor(query=True, rgb=True)
            cmds.button(self.GUI['button2'], e=True, bgc=cmds.colorEditor(query=True, rgb=True))

    def TimeRange(self, button):
        slider = mel.eval('$tempvar = $gPlayBackSlider')
        if cmds.timeControl(slider, rv=True, q=True):
            (time1, time2) = cmds.timeControl(slider, q=True, ra=True)
        else:
            time1 = cmds.playbackOptions(q=True, min=True)
            time2 = cmds.playbackOptions(q=True, max=True)
        cmds.intField(self.GUI['int1'], e=True, v=time1)
        cmds.intField(self.GUI['int2'], e=True, v=time2)

    def SendPiece(self, button):
        if self.edit or dockCheck(self.mod):
            text = cmds.scrollField(self.GUI['scrollfield1'], q=True, text=True).strip()
            if text:
                time1 = cmds.intField(self.GUI['int1'], v=True, q=True)
                time2 = cmds.intField(self.GUI['int2'], v=True, q=True)
                if time1 > time2:
                    time1, time2 = time2, time1
                lower_limit = cmds.playbackOptions(q=True, ast=True)
                upper_limit = cmds.playbackOptions(q=True, aet=True)
                time1 = time1 if lower_limit < time1 < upper_limit else lower_limit
                time2 = time2 if lower_limit < time2 < upper_limit else upper_limit
                if time1 == time2:
                    warningMessage('There needs to be a time range.')
                else:
                    if self.edit:
                        piece = self.mod
                    else:
                        newid = uuid()  # Generate new ID
                        save(newid, {"nts": "", "min": None, "max": None, "col": []})
                        piece = ShotPiece(newid)
                        piece.createGUI(self.mod.GUI['layout1'])
                    piece.update(nts=text, min=time1, max=time2, col=cmds.button(self.GUI['button2'], q=True, bgc=True))
                    cmds.deleteUI(self.GUI['window'])
            else:
                warningMessage('You need to give your selection a description.')
        else:
            cmds.deleteUI(self.GUI['window'])
