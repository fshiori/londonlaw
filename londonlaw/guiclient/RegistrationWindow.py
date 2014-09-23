#  London Law -- a networked manhunting board game
#  Copyright (C) 2003-2004, 2005 Paul Pelzl
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




# RegistrationWindow.py
#
# This module contains the classes that generate the list of players within a
# game room, permit changing teams, etc.


from twisted.python import log
from wx import *
from londonlaw.common.protocol import *
from londonlaw.common.config import *
from AutoListCtrl import *
from ChatPanel import *
import os.path



# Create a small dialog for choosing a team.
class TeamDialog(Dialog):
   def __init__(self, parent):
      Dialog.__init__(self, parent, -1, "Choose a Team", DefaultPosition, DefaultSize, DEFAULT_DIALOG_STYLE|SUNKEN_BORDER)
      panel = Panel(self, -1, DefaultPosition, DefaultSize, TAB_TRAVERSAL)

      self.choice = RadioBox(panel, -1, "team: ", DefaultPosition, DefaultSize,
         ["Detectives", "Mr. X"], 1, RA_SPECIFY_COLS)
      self.submitButton = Button(panel, ID_OK, "OK")
      self.cancelButton = Button(panel, ID_CANCEL, "Cancel")

      buttonSizer = BoxSizer(HORIZONTAL)
      buttonSizer.Add(self.cancelButton, 0, ALIGN_CENTRE|ALL, 5)
      buttonSizer.Add(self.submitButton, 0, ALIGN_CENTRE|ALL, 5)

      vSizer = BoxSizer(VERTICAL)
      vSizer.Add(self.choice, 0, ALIGN_CENTRE|ALL, 5)
      vSizer.Add((1, 1), 1, EXPAND)
      vSizer.Add(buttonSizer, 0, ALIGN_RIGHT|ALL, 5)

      panel.SetSizer(vSizer)
      vSizer.Fit(panel)
      sizer = BoxSizer(VERTICAL)
      sizer.Add(panel, 1, EXPAND | ALL, 5)
      self.SetSizer(sizer)
      sizer.Fit(self)
      self.SetAutoLayout(1)

      EVT_BUTTON(self, ID_OK, self.submit)
      EVT_BUTTON(self, ID_CANCEL, self.cancel) 


   def submit(self, event):
      self.EndModal(self.choice.GetSelection())

   def cancel(self, event):
      self.EndModal(-1)





# Generate the main registration window.
class RegistrationWindow(Frame):
   def __init__(self, parent, ID, title, messenger):
      Frame.__init__(self, parent, ID, title)

      self._messenger = messenger

      DISCONNECT = 100
      EXIT       = 101

      # Create a menu bar
      fileMenu = Menu("File")
      fileMenu.Append(DISCONNECT, "Disconnect", "Disconnect from server")
      fileMenu.Append(EXIT, "Exit\tCTRL+Q", "Exit London Law")
      menuBar = MenuBar()
      menuBar.Append(fileMenu, "File")
      self.SetMenuBar(menuBar)

      self.status = self.CreateStatusBar()

      # stick everything in a panel
      mainPanel = Panel(self, -1)

      self.list = AutoListCtrl(mainPanel, -1,
            ("Player", "Team", "Votes to Start?", "Pawns"),
            ("(no players joined)", "", "", ""))

      self.list.SetColumnWidth(1, 140) 

      mainSizer = BoxSizer(VERTICAL)
      mainSizer.Add(self.list, 3, ALIGN_CENTRE|EXPAND|ALL, 5)

      self.chatWindow = ChatPanel(mainPanel, "", False)
      mainSizer.Add(self.chatWindow, 2, EXPAND|ALL, 5)

      self.leaveButton = Button(mainPanel, -1, "Leave Game")
      self.teamButton  = Button(mainPanel, -1, "Choose Team")
      self.voteButton  = Button(mainPanel, -1, "Vote to Start")
      buttonSizer      = BoxSizer(HORIZONTAL)
      buttonSizer.Add(self.leaveButton, 0, ALIGN_CENTRE | LEFT | RIGHT | BOTTOM | ALL, 5)
      buttonSizer.Add((1, 1), 1, EXPAND)
      buttonSizer.Add(self.teamButton, 0, ALIGN_CENTRE | RIGHT | BOTTOM | ALL, 5)
      buttonSizer.Add(self.voteButton, 0, ALIGN_CENTRE | RIGHT | BOTTOM | ALL, 5)
      mainSizer.Add(buttonSizer, 0, EXPAND, 0)

      mainPanel.SetSizer(mainSizer)
      mainSizer.Fit(mainPanel)

      EVT_MENU(self, EXIT, self.menuExit)
      EVT_MENU(self, DISCONNECT, self.menuDisconnect)
      EVT_BUTTON(self, self.leaveButton.GetId(), self.leaveGame)
      EVT_BUTTON(self, self.teamButton.GetId(), self.chooseTeam)
      EVT_BUTTON(self, self.voteButton.GetId(), self.voteStart)
      EVT_TEXT_ENTER(self, self.chatWindow.chatEntry.GetId(), self.chatSend)


   def addPlayer(self, data):
      log.msg("called RegistrationWindow.addPlayer()")
      self.list.addItem(data)


   def removePlayer(self, data):
      log.msg("called RegistrationWindow.removePlayer()")
      self.list.removeItemByData(data)


   def addChatMessage(self, chatType, data):
      log.msg("called RegistrationWindow.addChatMessage()")
      self.chatWindow.AppendText("<" + data[0] + "> " + data[1])


   def chatSend(self, event):
      (text, sendTo) = self.chatWindow.GetEntry()
      if len(text) > 0:
         self.chatWindow.ClearEntry()
         self._messenger.netSendChat(text, sendTo)


   def enableSelectButton(self, event):
      self.selectButton.Enable(True)


   def disableSelectButton(self, event):
      self.selectButton.Disable()

      
   def disableVoteButton(self):
      self.voteButton.Disable()


   def chooseTeam(self, event):
      teamDialog = TeamDialog(self)
      value = teamDialog.ShowModal()  # 0 == Detectives, 1 == Mr. X
      if value == 0:
         self._messenger.netSetTeam("Detectives")
      elif value == 1:
         self._messenger.netSetTeam("Mr. X")


   def leaveGame(self, event):
      self._messenger.netLeaveGame()


   def showInfoAlert(self, info):
      self.PushStatusText("")
      alert = MessageDialog(self, info,
         "Server Message", OK|ICON_INFORMATION)
      alert.ShowModal()


   def voteStart(self, event):
      self._messenger.netVoteStart()


   def menuExit(self, event):
      alert = MessageDialog(self, "Disconnect from the server and exit London Law?",
         "Disconnect and Quit", YES_NO|ICON_EXCLAMATION)
      if alert.ShowModal() == ID_YES:
         self._messenger.netDisconnect()
         self.Close()


   def menuDisconnect(self, event):
      alert = MessageDialog(self, "Disconnect from the server?",
         "Disconnect", YES_NO|ICON_EXCLAMATION)
      if alert.ShowModal() == ID_YES:
         self._messenger.netDisconnect()
         self._messenger.guiLaunchConnectionWindow()

      



# arch-tag: DO_NOT_CHANGE_0d8bbe23-c615-4456-9f0d-4c927786fcfe 
