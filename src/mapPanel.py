import wx
import os
import math

import genmap

rotorUpper = 1
rotorLower = 2

def SnapAngle(angle, snap =5):
    angle = angle/snap
    angle = round(angle)
    angle = angle*snap
    return angle

def DrawAngle(gtx, angle, r = 235, offset=(0,0)):
    if ( math.isnan(angle)): return
    angle = angle * math.pi / 180
    x =  offset[0] + math.sin(angle) * r
    y =  offset[1] - math.cos(angle) * r
    gtx.StrokeLine(offset[0], offset[1], x, y)

class MapPanel(wx.Panel):

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        self.Bind(wx.EVT_PAINT,self.OnDraw)
        self.Bind(wx.EVT_LEFT_DOWN,self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP,self.OnMouseUp)
        self.Bind(wx.EVT_MOTION,self.OnMouseMove)
        self.mapBmp =  wx.Bitmap("Map.png", wx.BITMAP_TYPE_ANY)
        self.newSetpoint=-1
        self.enterSetpoint = False
        self.upperSetpoint = float("nan")
        self.upperPosition = float("nan")
        self.lowerPosition = float("nan")
        self.lowerSetpoint = float("nan")
        self.location="JO63PA"
        self.firstDraw = True

    def OnDraw(self,event=None):
        dc = wx.PaintDC(self)
        gdc = wx.GCDC(dc)
        (sx, sy) = self.GetSize()
        if (self.firstDraw):
            print(f"Panelsize: {sx}x{sy}")
            self.firstDraw = False
        x0 = 0
        y0 = sy/2
        dc.SetPen(wx.Pen(wx.BLACK,style=wx.TRANSPARENT))
        dc.DrawRectangle(0,0, sx, sy)
        (bx, by) = self.mapBmp.GetSize()
        dc.DrawBitmap(self.mapBmp, (sx-bx)/2, (sy-by)/2) 
        gtx = gdc.GetGraphicsContext()
        gtx.BeginLayer (0.6)
        gdc.SetPen(wx.Pen(wx.BLUE, 5, style=wx.SHORT_DASH))
        DrawAngle(gtx, self.lowerSetpoint, offset = (sx/2.0, sy/2.0))
        gdc.SetPen(wx.Pen(wx.BLUE, 5, style=wx.SOLID))
        DrawAngle(gtx, self.lowerPosition, offset = (sx/2.0, sy/2.0))
        color = wx.Colour(70,180,70)
        gdc.SetPen(wx.Pen(color, 5, style=wx.SHORT_DASH))
        DrawAngle(gtx, self.upperSetpoint, offset = (sx/2.0, sy/2.0))
        gdc.SetPen(wx.Pen(color, 5, style=wx.SOLID))
        DrawAngle(gtx, self.upperPosition, offset = (sx/2.0, sy/2.0))
        gtx.EndLayer()
        if (self.newSetpoint >= 0):
            gdc.SetPen(wx.Pen(wx.RED, 5, style=wx.SOLID))
            DrawAngle(gtx, self.newSetpoint, offset = (sx/2.0, sy/2.0))


    def OnMouseMove(self,event=None):
        if (self.enterSetpoint != True): return
        (mx,my) =  event.GetPosition().Get()
        (sx,sy) = self.GetSize()
        # Calculate angle
        mx = mx - sx/2
        my = my - sy/2
        angle = math.atan2(mx, -my)/math.pi * 180
        if (angle < 0): angle+=360
        angle = SnapAngle(angle)
        self.setpointCallback(angle)
        

    def OnMouseDown(self,event=None):
        self.enterSetpoint = True
        self.OnMouseMove(event)
        

    def OnMouseUp(self,event=None):
        self.enterSetpoint = False

    def SetpointCallback(self, callback):
        self.setpointCallback = callback

    def SetLocation(self, location):
        fileName = "maps/Map_"+location+".png"
        if (not os.path.isfile(fileName)):
            genmap.GenMap(location)
            # Check again to see if it was actually generated
            if (not os.path.isfile(fileName)):
                wx.MessageBox('Could not generate map for new location', 'Error', wx.OK | wx.ICON_ERROR)
                return
        self.mapBmp.Destroy()
        self.mapBmp =  wx.Bitmap("maps/Map_"+location+".png", wx.BITMAP_TYPE_ANY)
        self.location = location

