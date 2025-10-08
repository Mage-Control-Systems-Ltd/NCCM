# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-0-g80c4cb6)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid

import gettext
_ = gettext.gettext

###########################################################################
## Class NetClassClearanceMatrixDialog
###########################################################################

class NetClassClearanceMatrixDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Net Class Clearance Matrix"), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        mainSizer = wx.BoxSizer( wx.VERTICAL )

        gridSizer = wx.BoxSizer( wx.HORIZONTAL )

        self.gridNCCM = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        # Grid
        self.gridNCCM.CreateGrid( 0, 0 )
        self.gridNCCM.EnableEditing( True )
        self.gridNCCM.EnableGridLines( True )
        self.gridNCCM.EnableDragGridSize( True )
        self.gridNCCM.SetMargins( 0, 0 )

        # Columns
        self.gridNCCM.AutoSizeColumns()
        self.gridNCCM.EnableDragColMove( False )
        self.gridNCCM.EnableDragColSize( False )
        self.gridNCCM.SetColLabelSize( wx.grid.GRID_AUTOSIZE )
        self.gridNCCM.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Rows
        self.gridNCCM.AutoSizeRows()
        self.gridNCCM.EnableDragRowSize( False )
        self.gridNCCM.SetRowLabelSize( wx.grid.GRID_AUTOSIZE )
        self.gridNCCM.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Label Appearance
        self.gridNCCM.SetLabelBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
        self.gridNCCM.SetLabelFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Arial" ) )
        self.gridNCCM.SetLabelTextColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )

        # Cell Defaults
        self.gridNCCM.SetDefaultCellAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )
        gridSizer.Add( self.gridNCCM, 0, wx.ALL, 5 )


        mainSizer.Add( gridSizer, 0, wx.ALL|wx.EXPAND, 5 )


        mainSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        btnSizer = wx.BoxSizer( wx.HORIZONTAL )

        self.btnUpdateCR = wx.Button( self, wx.ID_ANY, _(u"Update Custom Rules"), wx.DefaultPosition, wx.DefaultSize, 0 )

        self.btnUpdateCR.SetBitmapPosition( wx.BOTTOM )
        btnSizer.Add( self.btnUpdateCR, 0, wx.ALL|wx.ALIGN_BOTTOM, 5 )

        self.btnRemoveFromCR = wx.Button( self, wx.ID_ANY, _(u"Remove From Custom Rules"), wx.DefaultPosition, wx.DefaultSize, 0 )
        btnSizer.Add( self.btnRemoveFromCR, 0, wx.ALL|wx.ALIGN_BOTTOM, 5 )


        btnSizer.Add( ( 10, 0), 1, wx.ALIGN_CENTER, 5 )

        self.btnExit = wx.Button( self, wx.ID_ANY, _(u"Exit"), wx.DefaultPosition, wx.DefaultSize, 0 )
        btnSizer.Add( self.btnExit, 0, wx.ALL|wx.ALIGN_BOTTOM, 5 )


        mainSizer.Add( btnSizer, 0, wx.EXPAND, 5 )


        self.SetSizer( mainSizer )
        self.Layout()
        mainSizer.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.gridNCCM.Bind( wx.grid.EVT_GRID_CELL_CHANGED, self.check_cells )
        self.btnUpdateCR.Bind( wx.EVT_BUTTON, self.update_custom_rules )
        self.btnRemoveFromCR.Bind( wx.EVT_BUTTON, self.remove_from_custom_rules )
        self.btnExit.Bind( wx.EVT_BUTTON, self.gui_exit )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def check_cells( self, event ):
        event.Skip()

    def update_custom_rules( self, event ):
        event.Skip()

    def remove_from_custom_rules( self, event ):
        event.Skip()

    def gui_exit( self, event ):
        event.Skip()


###########################################################################
## Class InfoDialog
###########################################################################

class InfoDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Net Class Clearance Matrix"), pos = wx.DefaultPosition, size = wx.Size( 321,133 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        mainDialogSizer = wx.BoxSizer( wx.VERTICAL )

        textSizer = wx.BoxSizer( wx.VERTICAL )

        self.txtMessage = wx.StaticText( self, wx.ID_ANY, _(u"Text"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.txtMessage.Wrap( -1 )

        textSizer.Add( self.txtMessage, 0, wx.ALL, 5 )


        mainDialogSizer.Add( textSizer, 1, wx.EXPAND, 5 )

        buttonSizer = wx.BoxSizer( wx.HORIZONTAL )


        buttonSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.btnOkay = wx.Button( self, wx.ID_ANY, _(u"Okay"), wx.DefaultPosition, wx.DefaultSize, 0 )
        buttonSizer.Add( self.btnOkay, 0, wx.ALL|wx.ALIGN_BOTTOM, 5 )


        buttonSizer.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        mainDialogSizer.Add( buttonSizer, 1, wx.EXPAND, 5 )


        self.SetSizer( mainDialogSizer )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.btnOkay.Bind( wx.EVT_BUTTON, self.okay )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def okay( self, event ):
        event.Skip()


