#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
description = """
python2/pyzano_gtk2.py - Display graphical dialog boxes from shell scripts.
A [janky] attempt at a Python2 + GTK2 implementation of the zenity program,
with similar (but a subset of) command line options. Seek '--help'
"""
# Copyright 2019 Giorgi Tavkelishvili
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Last updated 2019-03-24 by Giorgi T.

import pygtk
pygtk.require('2.0')
import gtk  # pygtk.require() must be called before importing gtk
import argparse, os

# >>> gtk.ver
# (2, 28, 6)
# >>> gtk.gtk_version
# (2, 24, 32)
# >>> gtk.pygtk_version
# (2, 24, 0)

# Example: argsDict = {
#   'dialogTitle': 'Change App password ', 'dialogType': 'forms', 'dialogAddEntry': None,
#   'dialogAddPassword': ['(current) App password', 'Enter new App password', 'Retype new App password'],
#   'dialogText': 'Details... ', 'printSeparator': '\n'
# }
# NOTE: Subclass PyzanoGtk2Window to add features beyond those of 'zenity' v3.x.
class PyzanoGtk2Window():
    def destroy(self, widget, data=None):
        if self.DEBUG: print("destroy: Closing application")
        if self.DEBUG: print("destroy: data = %s" % data)
        if isinstance(data, dict):
            if "exit" in data:
                raise SystemExit(int(data["exit"]))

        # TODO: Find a way to specify the exit code to Gtk.main_quit().
        #       Read source code at /usr/lib/python3/dist-packages/gi/
        gtk.main_quit()

    def _on_ok_clicked_submit(self, widget):
        if self.DEBUG: print("_on_ok_clicked_submit: The OK button was clicked")
        print(self.printSeparator.join([widget.get_text() for widget in self.printList]))
        self.destroy(self.window, data={"exit": 0})

    def _on_ok_clicked_close(self, widget):
        if self.DEBUG: print("_on_ok_clicked_close: The OK button was clicked")
        self.destroy(self.window, data={"exit": 0})

    def _on_cancel_clicked_close(self, widget):
        if self.DEBUG: print("_on_cancel_clicked_close: The Cancel button was clicked")
        self.destroy(self.window, data={"exit": 1})

    def _on_yes_clicked_exit_success(self, widget):
        if self.DEBUG: print("_on_yes_clicked_exit_success: The Yes button was clicked")
        self.destroy(self.window, data={"exit": 0})

    def _on_no_clicked_exit_failure(self, widget):
        if self.DEBUG: print("_on_no_clicked_exit_failure: The No button was clicked")
        self.destroy(self.window, data={"exit": 1})

    def _table_add(self, fieldType, fieldName=None, connectTo=None, iconLabel=None, textLabel=None):
        widgets = []

        if fieldType == "label_and_text_entry":
            widgetLabel = gtk.Label(fieldName)
            widgetLabel.set_alignment(0.0, 0.5)
            widgets += [widgetLabel]

            widgetEntry = gtk.Entry()
            widgetEntry.set_visibility(True)
            if connectTo:
                widgetEntry.connect("changed", connectTo)
            widgets += [widgetEntry]

            self.printList += [widgetEntry]
        elif fieldType == "label_and_password_entry":
            widgetLabel = gtk.Label(fieldName)
            widgetLabel.set_alignment(0.0, 0.5)
            widgets += [widgetLabel]

            widgetEntry = gtk.Entry()
            widgetEntry.set_visibility(False)
            if connectTo:
                widgetEntry.connect("changed", connectTo)
            widgets += [widgetEntry]

            self.printList += [widgetEntry]
        elif fieldType == "stock_icon_and_label":
            widgetImage = gtk.Image()
            widgetImage.set_from_stock(self._get_icon_gtk_stock_id(), gtk.ICON_SIZE_DIALOG)
            widgets += [widgetImage]

            widgetLabel = gtk.Label()
            widgetLabel.set_markup(iconLabel)
            widgets += [widgetLabel]
        elif fieldType == "label":
            pass # TODO:
        elif fieldType == "text_entry":
            pass # TODO:
        elif fieldType == "password_entry":
            pass # TODO:

        nRows = self.table.get_property('n-rows')
        nColumns = self.table.get_property('n-columns')
        if len(self.table) > 0:
            nRows = nRows + 1 # Add a row:
            self.table.resize(nRows, nColumns)

        # Gtk.Table 'attach' parameter:
        #   child: the widget to add.
        #   left_attach: the column number to attach the left side of a child widget to.
        #   right_attach: the column number to attach the right side of a child widget to.
        #   top_attach: the row number to attach the top side of a child widget to.
        #   bottom_attach: the row number to attach the bottom side of a child widget to.
        if len(widgets) == 1:
            self.table.attach(widgets[0], 0, nColumns, nRows - 1, nRows)
        elif len(widgets) == 2:
            self.table.attach(widgets[0], 0, nColumns - 1, nRows - 1, nRows)
            self.table.attach(widgets[1], nColumns - 1, nColumns, nRows - 1, nRows)

        return self

    def _vbox_dialog(self):
        dialogTitle = self.dialogTitle or self.dialogDefaults[self.dialogType]["dialogTitle"]
        dialogText = self.dialogText or self.dialogDefaults[self.dialogType]["dialogText"]
        dialogTooltipText = self.dialogTooltipText or self.dialogDefaults[self.dialogType]["dialogTooltipText"]

        self.window.set_title(dialogTitle)
        self.window.set_tooltip_text(dialogTooltipText)

        if self.dialogType == 'test':
            pass
        elif self.dialogType == 'forms':
            # self.window.set_size_request(432, 292)

            self.label = gtk.Label()
            self.label.set_markup("<b>%s</b>" % dialogText)
            self.label.set_alignment(0.0, 0.5)

            self.table = gtk.Table(rows=1, columns=2, homogeneous=True)
            self.table.set_col_spacings(3)
            self.table.set_row_spacings(3)
            # self.table.set_hexpand(True)

            if isinstance(self.dialogAddEntry, list):
                for fieldName in self.dialogAddEntry:
                    self._table_add('label_and_text_entry', fieldName=fieldName)

            if isinstance(self.dialogAddPassword, list):
                for fieldName in self.dialogAddPassword:
                    self._table_add('label_and_password_entry', fieldName=fieldName)

            self.vbox.pack_start(self.label, True, True, 0)
            self.vbox.pack_start(self.table, True, True, 0)
        elif self.dialogType in ["info", "error", "warning", "question"]:
            # self.window.set_size_request(150, 100)
            self.table = gtk.Table(rows=1, columns=2, homogeneous=False)
            self.table.set_col_spacings(3)
            self.table.set_row_spacings(3)
            self._table_add('stock_icon_and_label', iconLabel=dialogText)
            self.vbox.pack_start(self.table, True, True, 0)
        elif self.dialogType == 'entry':
            pass # TODO:
        elif self.dialogType == 'password':
            pass # TODO:

        self._vbox_append_action_buttons()

        return self

    # Place "Cancel" and "OK" buttons into the right bottom corner of the main VBox.
    # We will use two buttons, one horizontal box and two alignment containers here.
    def _vbox_append_action_buttons(self):
        buttonSizeRequestWidth = 90
        buttonSizeRequestHeight = 30

        # Place the [future] child widget at the bottom using the
        # GTK2 Alignment widget: https://developer.gnome.org/pygtk/stable/class-gtkalignment.html
        valign = gtk.Alignment()
        valign.set(0, 1, 0, 0)
        # Place the Alignment widget into the main VBox.
        self.vbox.pack_start(valign, True, True, 0)

        # GTK2 horizontal box (HBox) widget: https://developer.gnome.org/pygtk/stable/class-gtkhbox.html
        hbox = gtk.HBox(True, 0)

        # Create Button widgets, connect a function to the "clicked" signal from each and put 'em inside the HBox.
        if self.dialogType == "test":
            pass
        elif self.dialogType in ['forms', 'entry', 'password']:
            buttonCancel = gtk.Button("Cancel")
            buttonCancel.set_size_request(buttonSizeRequestWidth, buttonSizeRequestHeight)
            buttonCancel.connect("clicked", self._on_cancel_clicked_close)
            buttonCancel.set_tooltip_text(None)
            hbox.add(buttonCancel)

            buttonOK = gtk.Button("OK")
            buttonOK.set_size_request(buttonSizeRequestWidth, buttonSizeRequestHeight)
            buttonOK.connect("clicked", self._on_ok_clicked_submit)
            buttonOK.set_tooltip_text(None)
            hbox.add(buttonOK)
        elif self.dialogType in ['info', 'error', 'warning']:
            buttonOK = gtk.Button("OK")
            buttonOK.set_size_request(buttonSizeRequestWidth, buttonSizeRequestHeight)
            buttonOK.connect("clicked", self._on_ok_clicked_close)
            buttonOK.set_tooltip_text(None)
            hbox.add(buttonOK)
        elif self.dialogType in ['question']:
            buttonNo = gtk.Button("No")
            buttonNo.set_size_request(buttonSizeRequestWidth, buttonSizeRequestHeight)
            buttonNo.connect("clicked", self._on_no_clicked_exit_failure)
            buttonNo.set_tooltip_text(None)
            hbox.add(buttonNo)

            buttonYes = gtk.Button("Yes")
            buttonYes.set_size_request(buttonSizeRequestWidth, buttonSizeRequestHeight)
            buttonYes.connect("clicked", self._on_yes_clicked_exit_success)
            buttonYes.set_tooltip_text(None)
            hbox.add(buttonYes)
        else:
            raise ValueError("_vbox_append_action_buttons: Unknown dialog type")

        # Create an alignment container that will place its child widget
        # to the right. We add the horizontal box into the alignment
        # container and pack the alignment container into the vertical box.
        halign = gtk.Alignment()
        halign.set(1, 0, 0, 0)
        halign.add(hbox) # Container takes only one child widget.
        self.vbox.pack_start(halign, False, False, 3)

        return self

    def _get_icon_gtk_stock_id(self):
        iconGtkStockIdMap = {
            'info': gtk.STOCK_DIALOG_INFO,
            'error': gtk.STOCK_DIALOG_ERROR,
            'warning': gtk.STOCK_DIALOG_WARNING,
            'question': gtk.STOCK_DIALOG_QUESTION,
            'password': gtk.STOCK_DIALOG_AUTHENTICATION
        }

        if hasattr(self, 'dialogType'):
            if self.dialogType in iconGtkStockIdMap:
                return iconGtkStockIdMap[self.dialogType]

        return None

    def __init__(self, argsDict=None, debug=False, test=False):
        self.DEBUG = debug
        self.TEST = test

        self.printSeparator = '\n'
        self.printList = []

        self.dialogTitle = None
        self.dialogType = None
        self.dialogText = None
        self.dialogTooltipText = None # TODO:
        self.dialogAddEntry = []
        self.dialogAddPassword = []
        self.dialogEntryText = None
        self.dialogHideText = False
        self.dialogShowUsername = False

        self.knownDialogTypes = ["test", "forms", "info", "error", "warning", "question", "entry", "password"]
        self.dialogDefaults = {
            "test": {},
            "forms": {
                "dialogText": "",
                "dialogTooltipText": "",
                "dialogTitle": "pyzano"
            },
            "info": {
                "dialogText": "All updates are complete.",
                "dialogTooltipText": "",
                "dialogTitle": "Information"
            },
            "error": {
                "dialogText": "An error has occurred.",
                "dialogTooltipText": "",
                "dialogTitle": "Error"
            },
            "warning": {
                "dialogText": "Are you sure you want to proceed?",
                "dialogTooltipText": "",
                "dialogTitle": "Warning"
            },
            "question": {
                "dialogText": "Are you sure you want to proceed?",
                "dialogTooltipText": "",
                "dialogTitle": "Question"
            },
            "entry": {},
            "password": {}
        }

        if self.DEBUG: print("__init__: argsDict = %s" % argsDict)
        if argsDict:
            self.dialogType = argsDict.get("dialogType", None) or self.dialogType
            self.dialogTitle = argsDict.get("dialogTitle", None) or self.dialogTitle
            self.dialogText = argsDict.get("dialogText", None) or self.dialogText
            self.dialogTooltipText = argsDict.get("dialogTooltipText", None) or self.dialogTooltipText
            self.dialogAddEntry = argsDict.get("dialogAddEntry", None) or self.dialogAddEntry
            self.dialogAddPassword = argsDict.get("dialogAddPassword", None) or self.dialogAddPassword
            self.dialogEntryText = argsDict.get("dialogEntryText", None) or self.dialogEntryText
            self.dialogHideText = argsDict.get("dialogHideText", None) or self.dialogHideText
            self.dialogShowUsername = argsDict.get("dialogShowUsername", None) or self.dialogShowUsername
            self.printSeparator = argsDict.get("printSeparator", None) or self.printSeparator

        # TODO: This doesn't belong here! Make 'dialogType' a property, add getter and setter methods.
        if isinstance(self.dialogType, str):
            if self.dialogType not in self.knownDialogTypes:
                raise ValueError("__init__: You must specify a valid dialog type")
        else:
            raise TypeError("__init__: You must specify a dialog type")

        # TODO: This doesn't belong here! Make 'dialogType' a property, adding getter and setter methods.
        if self.dialogType == "password":
            self.printSeparator = '|'

        # Main GTK2 Window widget: https://developer.gnome.org/pygtk/stable/class-gtkwindow.html
        self.window = gtk.Window()
        # Main GTK2 vertical box (VBox) widget: https://developer.gnome.org/pygtk/stable/class-gtkvbox.html
        self.vbox = gtk.VBox(False, 0)

    def main(self):
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(False)
        self.window.set_keep_above(True)

        align = gtk.Alignment()
        align.set(0, 0, 0, 0)
        align.set_padding(0, 0, 3, 3)
        align.add(self.vbox)

        self._vbox_dialog()

        # As a GtkBin subclass a GtkWindow can only contain one widget at a time.
        self.window.add(align)
        self.window.connect("destroy", self.destroy)
        self.window.show_all()

        if not self.TEST:
            gtk.main()

        return self


if __name__ == "__main__":
    myName = os.path.basename(__file__)

    parser = argparse.ArgumentParser(description=description, prog='pyzano')
    # ArgumentParser.add_subparsers([title][, description][, prog][, parser_class][, action]
    #                               [, option_string][, dest][, required][, help][, metavar])
    subparsers = parser.add_subparsers(help=None, title="Dialog options", dest='dialogType',
                                       description="""
                                       This is an overview. Use '%(prog)s {subcommand} --help' to show help
                                       for a particular subcommand. E.g. '%(prog)s forms --help'
                                       """)

    # TODO: associate the parser for "forms" command with "--forms" option for 'zenity' syntax compatibility
    #       parserFoo.set_defaults(func=... won't do it as the function is called after argument parsing is complete.
    parserForms = subparsers.add_parser("forms", help="Display forms dialog",
                                        description="Forms dialog options") #, aliases=["--forms"]
    parserForms.add_argument("--add-entry", help="Add a new Entry in forms dialog",
                             metavar="FIELDNAME", action='append', dest="dialogAddEntry")
    parserForms.add_argument("--add-password", help="Add a new Password Entry in forms dialog",
                             metavar="FIELDNAME", action='append', dest="dialogAddPassword")
    parserForms.add_argument("--text", help="Set the dialog text",
                             metavar="STRING", dest="dialogText")
    parserForms.add_argument("--separator", help="Set output separator character",
                             metavar="STRING", dest="printSeparator")
    parserForms.add_argument("--title", help="Set the dialog title",
                             metavar="TITLE", dest="dialogTitle")

    # TODO: associate the parser for "question" command with "--question" option for 'zenity' syntax compatibility
    parserQuestion = subparsers.add_parser("question", help="Display question dialog",
                                           description="Question options") #, aliases=["--question"]
    parserQuestion.add_argument("--text", help="Set the dialog text",
                                metavar="STRING", dest="dialogText")
    parserQuestion.add_argument("--title", help="Set the dialog title",
                                metavar="TITLE", dest="dialogTitle")

    # TODO: associate the parser for "warning" command with "--warning" option for 'zenity' syntax compatibility
    parserWarning = subparsers.add_parser("warning", help="Display warning dialog",
                                          description="Warning options") #, aliases=["--warning"]
    parserWarning.add_argument("--text", help="Set the dialog text",
                               metavar="STRING", dest="dialogText")
    parserWarning.add_argument("--title", help="Set the dialog title",
                               metavar="TITLE", dest="dialogTitle")

    # TODO: associate the parser for "error" command with "--error" option for 'zenity' syntax compatibility
    parserError = subparsers.add_parser("error", help="Display error dialog",
                                        description="Error options") #, aliases=["--error"]
    parserError.add_argument("--text", help="Set the dialog text",
                             metavar="STRING", dest="dialogText")
    parserError.add_argument("--title", help="Set the dialog title",
                             metavar="TITLE", dest="dialogTitle")

    # TODO: associate the parser for "info" command with "--info" option for 'zenity' syntax compatibility
    parserInfo = subparsers.add_parser("info", help="Display info dialog",
                                       description="Info options") #, aliases=["--info"]
    parserInfo.add_argument("--text", help="Set the dialog text",
                            metavar="STRING", dest="dialogText")
    parserInfo.add_argument("--title", help="Set the dialog title",
                            metavar="TITLE", dest="dialogTitle")

    # TODO: associate the parser for "entry" command with "--entry" option for 'zenity' syntax compatibility
    parserEntry = subparsers.add_parser("entry", help="Display text entry dialog",
                                        description="Text entry options") #, aliases=["--entry"]
    parserEntry.add_argument("--text", help="Set the dialog text",
                             metavar="STRING", dest="dialogText")
    parserEntry.add_argument("--entry-text", help="Set the entry text",
                             metavar="STRING", dest="dialogEntryText")
    parserEntry.add_argument("--hide-text", help="Hide the entry text",
                             action='store_true', dest="dialogHideText")
    parserEntry.add_argument("--title", help="Set the dialog title",
                             metavar="TITLE", dest="dialogTitle")

    # TODO: associate the parser for "password" command with "--password" option for 'zenity' syntax compatibility
    parserPassword = subparsers.add_parser("password", help="Display password dialog",
                                           description="Password dialog options") #, aliases=["--password"]
    parserPassword.add_argument("--username", help="Display the username field",
                                action='store_true', dest="dialogShowUsername")
    parserPassword.add_argument("--title", help="Set the dialog title",
                                metavar="TITLE", dest="dialogTitle")

    args = parser.parse_args()

    try:
        win = PyzanoGtk2Window(argsDict=vars(args))
        win.main()     # Will normally raise SystemExit(...
        print("{0}: debug: Peekaboo, I see you used the Close title bar button!".format(myName), file=os.sys.stderr)
        os.sys.exit(1) # Will `exit 1` like `zenity` would.
    except Exception as exc:
        print("{0}: error: {1}. See '{0} --help' for details".format(myName, str(exc)), file=os.sys.stderr)
        os.sys.exit(1)

