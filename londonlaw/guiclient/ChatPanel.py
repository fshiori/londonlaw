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




# ChatPanel.py
#
# This class creates a combined chat entry and chat message display area.

from wx import *
from ScrolledLabel import *

# Wrapped in a StaticBox.
class ChatPanel(Panel):
   def __init__(self, parent, text, enableSendTo):
      Panel.__init__(self, parent, -1)


      # create a scrollable display for the chat messages 
      self.chatDisplay = ScrolledLabel(self, text)

      # create the "send to" radio button
      self.chatRadio = RadioBox(self, -1, "send to:", DefaultPosition, DefaultSize,
         ["all", "team"], 1, RA_SPECIFY_COLS)
      self.chatRadio.Enable(enableSendTo)

      # create a chat entry box
      self.chatEntry = TextCtrl(self, -1, "", DefaultPosition, DefaultSize, TE_PROCESS_ENTER)
      self.chatEntry.SetMaxLength(254)  # messages longer than this would get truncated by ESocket.write_string()


      # set up the geometry.
      # line the chat display and the radio button horizontally...
      sizer2 = BoxSizer(HORIZONTAL)
      sizer2.Add(self.chatDisplay, 1, EXPAND|ALL, 5)
      sizer2.Add(self.chatRadio, 0, ALIGN_BOTTOM|ALL, 5) 

      # ... and line up the rest vertically
      self.topSizer = BoxSizer(VERTICAL)
      self.topSizer.Add(sizer2, 1, EXPAND)
      self.topSizer.Add(self.chatEntry, 0, EXPAND|ALL, 5)
      self.SetSizer(self.topSizer)
      self.topSizer.SetSizeHints(self)


   def GetEntry(self):
      return (self.chatEntry.GetValue(), self.chatRadio.GetStringSelection())

   def ClearEntry(self):
      self.chatEntry.Clear()

   def SetText(self, txt):
      self.chatDisplay.SetText(txt)

   def AppendText(self, txt):
      self.chatDisplay.AppendText(txt)


# arch-tag: gui chat panel
