#  London Law -- a networked manhunting board game
#  Copyright (C) 2003-2004 Paul Pelzl
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License, Version 2, as 
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA




# MapWindow.py
#
# Class that displays a scrolling window containing a map.  The map can
# be updated to display player positions.  Users can click on map positions
# to launch a MoveDialog.


from wx import *
from TextPanel import *
from graphicalmap import *
from londonlaw.common.config import *
import os


PlayerNumError = "Player Number Error"


class MapWindow(ScrolledWindow):
   def __init__(self, parent, usernameList):
      ScrolledWindow.__init__(self, parent)

      # load the map image and prepare a DC for it
      mapImageFile   = os.path.normpath(os.path.join(MEDIAROOT, "images/map.jpg"))
      mapImage       = Image(mapImageFile, BITMAP_TYPE_JPEG)
      self.mapBitmap = BitmapFromImage(mapImage)
      self.bmpDC     = MemoryDC()
      mapImageFile        = os.path.normpath(os.path.join(MEDIAROOT, "images/map-quarter.jpg"))
      mapImage            = Image(mapImageFile, BITMAP_TYPE_JPEG)
      self.mapBitmapSmall = BitmapFromImage(mapImage)
      self.bmpDC.SelectObject(self.mapBitmapSmall)

      self.zoomLevel = 2
      self.pushpinOffset = (-8, 35)


      # configure scrollbars
      self.SetVirtualSize((self.mapBitmapSmall.GetWidth(), self.mapBitmapSmall.GetHeight()))
      self.SetScrollRate(10, 10)

      self.maskColour = Colour(10,10,10)
      self.pen        = Pen(BLACK, 3, SOLID)
      self.brush      = Brush(WHITE, SOLID)
      self.bgBrush    = Brush(self.maskColour, SOLID)
      self.pushpinDC  = MemoryDC()

      self.labelsShown = False

      self.playerLoc          = []
      self.pushpins           = []
      self.pushpinBackgrounds = []
      self.pushpinsDrawn      = []
      self.labels             = []
      for i in range(6):
         self.playerLoc.append(0)
         filename     = os.path.normpath(os.path.join(MEDIAROOT, "images/pin" + str(i) + ".png"))
         pushpinImage = Image(filename, BITMAP_TYPE_ANY)
         pushpinImage.SetMaskColour(255, 0, 242) # the purplish colour is not to be drawn
         pushpinBitmap  = BitmapFromImage(pushpinImage)
         self.pushpins.append(pushpinBitmap)
         pushpinBackBmp = EmptyBitmap(pushpinBitmap.GetWidth(), pushpinBitmap.GetHeight(), -1)
         self.pushpinBackgrounds.append(pushpinBackBmp)
         self.labels.append(TextPanel(self, " " + usernameList[i][:20] + " ", 10, SIMPLE_BORDER))
         self.labels[i].Hide()
         self.labels[i].SetBackgroundColour(Colour(220, 220, 220))


      EVT_PAINT(self, self.OnPaint)
      EVT_ERASE_BACKGROUND(self, self.OnEraseBackground)
      # scroll the map on middle or right button drag
      EVT_MIDDLE_DOWN(self, self.handleMiddleOrRightMouse)
      EVT_RIGHT_DOWN(self, self.handleMiddleOrRightMouse)
      EVT_MOTION(self, self.handleMoveMouse)


   def OnPaint(self, event):
      dc = PaintDC(self)
      self.PrepareDC(dc)
      self.OnDraw(dc)


   # try to eliminate flicker from painting the window background.
   # (why doesn't this work in wxGTK?)
   def OnEraseBackground(self, event):
      pass


   # (this could be the beginning of a drag event)
   def handleMiddleOrRightMouse(self, event):
      self.oldX, self.oldY = event.GetPosition()


   # scroll map on right mouse drag, or display
   # tooltips on player marker mouseover
   def handleMoveMouse(self, event):
      newX, newY   = event.GetPosition()
      stepX, stepY = self.GetScrollPixelsPerUnit()
      sX, sY       = self.GetViewStart()
      if (event.m_rightDown or event.m_middleDown) and event.Dragging():
         pixelDX = newX - self.oldX
         pixelDY = newY - self.oldY
         dx = pixelDX / stepX
         dy = pixelDY / stepY
         x, y = self.GetViewStart()
         self.Scroll(x-dx, y-dy)
         self.oldX = newX - (pixelDX % stepX)
         self.oldY = newY - (pixelDY % stepY)
      else:
         loc = pixelToLoc((sX*stepX + newX, sY*stepY + newY), self.zoomLevel)
         if loc > 0:
            for i in range(6):
               if loc == self.playerLoc[i]:
                  self.labels[i].Show()
                  self.labels[i].Raise()
                  self.labelsShown = True
                  break
         elif self.labelsShown:
            self.labelsShown = False
            for i in range(6):
               self.labels[i].Hide()



   # handle blitting the bitmap
   def OnDraw(self, dc):
      (scrollx, scrolly) = self.GetViewStart()
      (dx, dy)           = self.GetScrollPixelsPerUnit()
      (w, h)             = self.GetClientSizeTuple()
      dc.BeginDrawing()
      dc.Blit(scrollx*dx, scrolly*dy, w, h, self.bmpDC, scrollx*dx, scrolly*dy)
      dc.EndDrawing()



   # set the numeric location of a particular player, and update the map
   # bitmap appropriately.  The original map is first restored by blitting
   # the pushpin backgrounds onto it, then the pushpin backgrounds are
   # updated and the pushpins are redrawn.
   # The tooltip label location is also updated.
   def setLocation(self, playerNum, loc):
      # restore the original map bitmap
      for i in self.pushpinsDrawn:
         self.unDrawPushpin(i)
      self.playerLoc[playerNum] = loc
      # update this player's pushpin background
      self.updatePushpinBackground(playerNum)
      # blit all pushpins back on to the map bitmap
      if playerNum not in self.pushpinsDrawn:
         self.pushpinsDrawn.append(playerNum)
      for i in self.pushpinsDrawn:
         self.drawPushpin(i)
      # update the tooltip label location
      mapPixel     = locToPixel(loc, self.zoomLevel)
      stepX, stepY = self.GetScrollPixelsPerUnit()
      sX, sY       = self.GetViewStart()
      self.labels[playerNum].MoveXY(mapPixel[0] - 20 - sX*stepX, mapPixel[1] - 10 - sY*stepY)


   # remove a pushpin from the map bitmap
   def unDrawPushpin(self, playerNum):
      mapPixel = locToPixel(self.playerLoc[playerNum], self.zoomLevel)
      self.pushpinDC.SelectObject(self.pushpinBackgrounds[playerNum])
      self.bmpDC.BeginDrawing()
      self.bmpDC.Blit(mapPixel[0]-self.pushpinOffset[0], mapPixel[1]-self.pushpinOffset[1], 
            self.pushpinBackgrounds[playerNum].GetWidth(),
            self.pushpinBackgrounds[playerNum].GetHeight(), self.pushpinDC, 0, 0)
      self.bmpDC.EndDrawing()


   # update a pushpin background
   def updatePushpinBackground(self, playerNum):
      mapPixel = locToPixel(self.playerLoc[playerNum], self.zoomLevel)
      self.pushpinDC.SelectObject(self.pushpinBackgrounds[playerNum])
      self.pushpinDC.BeginDrawing()
      self.pushpinDC.Blit(0, 0, self.pushpinBackgrounds[playerNum].GetWidth(),
            self.pushpinBackgrounds[playerNum].GetHeight(), 
            self.bmpDC, mapPixel[0]-self.pushpinOffset[0], mapPixel[1]-self.pushpinOffset[1])
      self.pushpinDC.EndDrawing()


   # blit a pushpin image to the map bitmap
   def drawPushpin(self, playerNum):
      mapPixel = locToPixel(self.playerLoc[playerNum], self.zoomLevel)
      self.pushpinDC.SelectObject(self.pushpins[playerNum])
      self.pushpinDC.BeginDrawing()
      self.bmpDC.Blit(mapPixel[0]-self.pushpinOffset[0], mapPixel[1]-self.pushpinOffset[1], 
            self.pushpinBackgrounds[playerNum].GetWidth(),
            self.pushpinBackgrounds[playerNum].GetHeight(), self.pushpinDC, 0, 0, COPY, True)
      self.pushpinDC.EndDrawing()


   # center the map on a particular player        
   def scrollToPlayer(self, playerNum):
      if playerNum in self.pushpinsDrawn:
         mapPixel = locToPixel(self.playerLoc[playerNum], self.zoomLevel)
         w, h = self.GetClientSizeTuple()
         targetX = mapPixel[0] - w/2
         targetY = mapPixel[1] - h/2
         stepX, stepY = self.GetScrollPixelsPerUnit()
         self.Scroll(targetX / stepX, targetY / stepY)


   # unconditional redraw
   def redraw(self):
      w, h = self.GetClientSizeTuple()
      rect = (0, 0, w, h)
      self.RefreshRect(rect)


   # switch to zoom level 1
   def zoomIn(self):
      # restore the original map bitmap
      for i in self.pushpinsDrawn:
         self.unDrawPushpin(i)

      self.zoomLevel = 1
      self.pushpinOffset = (-25, 30)
      self.bmpDC.SelectObject(self.mapBitmap)

      # update all pushpin backgrounds
      for i in self.pushpinsDrawn:
         self.updatePushpinBackground(i)
      # redraw all pushpins
      for i in self.pushpinsDrawn:
         self.drawPushpin(i)

      # update the scrollbar size, and try to scroll so that the center of the
      # map is a fixed point
      sX, sY       = self.GetViewStart()
      self.SetVirtualSize((self.mapBitmap.GetWidth(), self.mapBitmap.GetHeight()))
      stepX, stepY = self.GetScrollPixelsPerUnit()
      w, h         = self.GetClientSizeTuple()
      self.Scroll(sX*2 + w/stepX/2, sY*2 + h/stepY/2)

      # update the tooltip label locations
      for i in self.pushpinsDrawn:
         mapPixel     = locToPixel(self.playerLoc[i], self.zoomLevel)
         sX, sY       = self.GetViewStart()
         self.labels[i].MoveXY(mapPixel[0] - 20 - sX*stepX, mapPixel[1] - 10 - sY*stepY)

      self.Refresh(False)

      
   # switch to zoom level 2
   def zoomOut(self):
      # restore the original map bitmap
      for i in self.pushpinsDrawn:
         self.unDrawPushpin(i)

      self.zoomLevel = 2
      self.pushpinOffset = (-8, 35)
      self.bmpDC.SelectObject(self.mapBitmapSmall)

      # update all pushpin backgrounds
      for i in self.pushpinsDrawn:
         self.updatePushpinBackground(i)
      # redraw all pushpins
      for i in self.pushpinsDrawn:
         self.drawPushpin(i)

      # update the scrollbar size, and try to scroll so that the center of the
      # map is a fixed point
      sX, sY       = self.GetViewStart()
      self.SetVirtualSize((self.mapBitmapSmall.GetWidth(), self.mapBitmapSmall.GetHeight()))
      stepX, stepY = self.GetScrollPixelsPerUnit()
      w, h         = self.GetClientSizeTuple()
      self.Scroll(sX/2 - w/stepX/4, sY/2 - h/stepY/4)

      # update the tooltip label locations
      for i in self.pushpinsDrawn:
         mapPixel     = locToPixel(self.playerLoc[i], self.zoomLevel)
         sX, sY       = self.GetViewStart()
         self.labels[i].MoveXY(mapPixel[0] - 20 - sX*stepX, mapPixel[1] - 10 - sY*stepY)

      self.Refresh(False)





# arch-tag: map window for gui
