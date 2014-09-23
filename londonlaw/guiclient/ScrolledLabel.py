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




# ScrolledLabel.py
#
# This class handles a wxStaticText that is managed by a scrolled window.


from wx import *

class ScrolledLabel(ScrolledWindow):
   def __init__(self, parent, label):
      ScrolledWindow.__init__(self, parent, -1, DefaultPosition, DefaultSize, 
         VSCROLL | SIMPLE_BORDER)
      self.SetBackgroundColour(Colour(200, 200, 200))
      self.SetScrollRate(0, 5)

      # create the text that will be scrolled
      self.text = StaticText(self, -1, label, Point(0,0))

      # use a Sizer to handle geometry
      self.topSizer = BoxSizer(VERTICAL)
      self.topSizer.Add(self.text, 1, EXPAND)
      self.SetSizer(self.topSizer)
      self.topSizer.SetVirtualSizeHints(self)

      self.ScrollToEnd()

   def SetText(self, text):
      self.text.SetLabel(text)

      # force the sizer to readjust to the new text, so the scroll bars
      # will properly cover the entire region
      txtsize = self.text.GetSize()
      self.topSizer.SetMinSize(txtsize)
      self.ScrollToEnd()

   def AppendText(self, txt):
      self.text.SetLabel(self.text.GetLabel() + '\n' + txt)

      txtsize = self.text.GetSize()
      self.topSizer.SetMinSize(txtsize)
      self.ScrollToEnd()



   # scroll to the bottom of the text
   def ScrollToEnd(self):
      self.topSizer.SetVirtualSizeHints(self)
      self.Scroll(0, self.GetVirtualSize()[1]/5)


# arch-tag: scrolled label for gui chat
