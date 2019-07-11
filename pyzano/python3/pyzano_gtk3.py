#!/usr/bin/env python3
description = """
python3/pyzano_gtk3.py - Display graphical dialog boxes from shell scripts.
A [janky] attempt at a Python3 + GTK3 implementation of the zenity program,
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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
import argparse, os

# >>> (gtk.MAJOR_VERSION, gtk.MINOR_VERSION, gtk.MICRO_VERSION)
# (3, 22, 30)

# Example: argsDict = {
#   'dialogTitle': 'Change App password ', 'dialogType': 'forms', 'dialogAddEntry': None,
#   'dialogAddPassword': ['(current) App password', 'Enter new App password', 'Retype new App password'],
#   'dialogText': 'Details... ', 'printSeparator': '\n'
# }
# NOTE: Subclass PyzanoGtk3Window to add features beyond those of 'zenity' v3.x.
class PyzanoGtk3Window():
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

    def gtk_grid_get_property(self, grid, propName):
        if propName == 'n-columns':
            cols = 0
            for child in grid.get_children():
                # The column number the left side of child is attached to:
                left_attach = grid.child_get_property(child, 'left-attach')
                # The number of columns that child spans:
                width = grid.child_get_property(child, 'width')
                cols = max(cols, left_attach + width)

            return cols
        elif propName == 'n-rows':
            rows = 0
            for child in grid.get_children():
                # The row number the top side of child is attached to:
                top_attach = grid.child_get_property(child, 'top-attach')
                # The number of rows that child spans:
                height = grid.child_get_property(child, 'height')
                rows = max(rows, top_attach + height)

            return rows

        return None

    def _grid_add(self, fieldType, fieldName=None, connectTo=None, iconLabel=None, textLabel=None):
        widgets = []

        if fieldType == "label_and_text_entry":
            # TODO: PyGTKDeprecationWarning: Using positional arguments with the GObject constructor has been deprecated.
            #       Please specify keyword(s) for "label" or use a class specific constructor.
            #       See: https://wiki.gnome.org/PyGObject/InitializerDeprecations
            widgetLabel = gtk.Label(fieldName)
            widgetLabel.set_xalign(0.0)
            widgets += [widgetLabel]

            widgetEntry = gtk.Entry()
            widgetEntry.set_visibility(True)
            if connectTo:
                widgetEntry.connect("changed", connectTo)
            widgets += [widgetEntry]

            self.printList += [widgetEntry]
        elif fieldType == "label_and_password_entry":
            # TODO: PyGTKDeprecationWarning: Using positional arguments with the GObject constructor has been deprecated.
            #       Please specify keyword(s) for "label" or use a class specific constructor.
            #       See: https://wiki.gnome.org/PyGObject/InitializerDeprecations
            widgetLabel = gtk.Label(fieldName)
            widgetLabel.set_xalign(0.0)
            widgets += [widgetLabel]

            widgetEntry = gtk.Entry()
            widgetEntry.set_visibility(False)
            if connectTo:
                widgetEntry.connect("changed", connectTo)
            widgets += [widgetEntry]

            self.printList += [widgetEntry]
        elif fieldType == "stock_icon_and_label":
            widgetImage = gtk.Image()
            # TODO: DeprecationWarning: Gtk.Image.set_from_stock is deprecated
            widgetImage.set_from_stock(self._get_icon_gtk_stock_id(), gtk.IconSize.DIALOG)
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

        nRows = self.gtk_grid_get_property(self.grid, 'n-rows')
        nColumns = self.gtk_grid_get_property(self.grid, 'n-columns') or 2

        # Gtk.Grid 'attach' parameters:
        #   child: the widget to add.
        #   left: the column number to attach the left side of child to.
        #   top: the row number to attach the top side of child to.
        #   width: the number of columns that child will span.
        #   height: the number of rows that child will span.
        if len(widgets) == 1:
            self.grid.attach(widgets[0], 0, nRows, nColumns, 1)
        elif len(widgets) == 2:
            self.grid.attach(widgets[0], 0, nRows, 1, 1)
            self.grid.attach_next_to(widgets[1], widgets[0], gtk.PositionType.RIGHT, nColumns - 1, 1)

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
            self.label.set_xalign(0.0)

            self.grid = gtk.Grid(column_homogeneous=True, column_spacing=3, row_spacing=3)
            # self.grid.set_hexpand(True)

            if isinstance(self.dialogAddEntry, list):
                for fieldName in self.dialogAddEntry:
                    self._grid_add('label_and_text_entry', fieldName=fieldName)

            if isinstance(self.dialogAddPassword, list):
                for fieldName in self.dialogAddPassword:
                    self._grid_add('label_and_password_entry', fieldName=fieldName)

            self.vbox.pack_start(self.label, True, True, 0)
            self.vbox.pack_start(self.grid, True, True, 0)
        elif self.dialogType in ["info", "error", "warning", "question"]:
            # self.window.set_size_request(150, 100)
            self.grid = gtk.Grid(column_homogeneous=False, column_spacing=3, row_spacing=3)
            self._grid_add('stock_icon_and_label', iconLabel=dialogText)
            self.vbox.pack_start(self.grid, True, True, 0)
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
        # GTK3 Alignment widget: https://lazka.github.io/pgi-docs/Gtk-3.0/classes/Alignment.html
        valign = gtk.Alignment.new(0, 1, 0, 0)  # TODO: DeprecationWarning: Gtk.Alignment.new is deprecated
        # Place the Alignment widget into the main VBox.
        self.vbox.pack_start(valign, True, True, 0)

        # GTK3 horizontal box (HBox) widget: https://lazka.github.io/pgi-docs/Gtk-3.0/classes/HBox.html
        # TODO: PyGTKDeprecationWarning: Using positional arguments with the GObject constructor has been deprecated.
        #       Please specify keyword(s) for "homogeneous, spacing" or use a class specific constructor.
        #       See: https://wiki.gnome.org/PyGObject/InitializerDeprecations
        hbox = gtk.HBox(True, 0)

        # Create Button widgets, connect a function to the "clicked" signal from each and put 'em inside the HBox.
        if self.dialogType == "test":
            pass
        elif self.dialogType in ['forms', 'entry', 'password']:
            buttonCancel = gtk.Button.new_with_mnemonic("_Cancel")
            buttonCancel.set_size_request(buttonSizeRequestWidth, buttonSizeRequestHeight)
            buttonCancel.connect("clicked", self._on_cancel_clicked_close)
            buttonCancel.set_tooltip_text(None)
            hbox.add(buttonCancel)

            buttonOK = gtk.Button.new_with_mnemonic("_OK")
            buttonOK.set_size_request(buttonSizeRequestWidth, buttonSizeRequestHeight)
            buttonOK.connect("clicked", self._on_ok_clicked_submit)
            buttonOK.set_tooltip_text(None)
            hbox.add(buttonOK)
        elif self.dialogType in ['info', 'error', 'warning']:
            buttonOK = gtk.Button.new_with_mnemonic("_OK")
            buttonOK.set_size_request(buttonSizeRequestWidth, buttonSizeRequestHeight)
            buttonOK.connect("clicked", self._on_ok_clicked_close)
            buttonOK.set_tooltip_text(None)
            hbox.add(buttonOK)
        elif self.dialogType in ['question']:
            buttonNo = gtk.Button.new_with_mnemonic("_No")
            buttonNo.set_size_request(buttonSizeRequestWidth, buttonSizeRequestHeight)
            buttonNo.connect("clicked", self._on_no_clicked_exit_failure)
            buttonNo.set_tooltip_text(None)
            hbox.add(buttonNo)

            buttonYes = gtk.Button.new_with_mnemonic("_Yes")
            buttonYes.set_size_request(buttonSizeRequestWidth, buttonSizeRequestHeight)
            buttonYes.connect("clicked", self._on_yes_clicked_exit_success)
            buttonYes.set_tooltip_text(None)
            hbox.add(buttonYes)
        else:
            raise ValueError("_vbox_append_action_buttons: Unknown dialog type")

        # Create an alignment container that will place its child widget
        # to the right. We add the horizontal box into the alignment
        # container and pack the alignment container into the vertical box.
        halign = gtk.Alignment.new(1, 0, 0, 0)
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

        # Main GTK3 Window widget: https://lazka.github.io/pgi-docs/Gtk-3.0/classes/Window.html
        self.window = gtk.Window()
        # Main GTK3 vertical box (VBox) widget: https://lazka.github.io/pgi-docs/Gtk-3.0/classes/VBox.html
        # TODO: PyGTKDeprecationWarning: Using positional arguments with the GObject constructor has been deprecated.
        #       Please specify keyword(s) for "homogeneous, spacing" or use a class specific constructor.
        #       See: https://wiki.gnome.org/PyGObject/InitializerDeprecations
        self.vbox = gtk.VBox(False, 0)

    def main(self):
        self.window.set_position(gtk.WindowPosition.CENTER)
        self.window.set_resizable(False)
        self.window.set_keep_above(True)

        self.vbox.set_margin_right(3)  # TODO: DeprecationWarning: Gtk.Widget.set_margin_right is deprecated
        self.vbox.set_margin_left(3)   # TODO: DeprecationWarning: Gtk.Widget.set_margin_left is deprecated

        self._vbox_dialog()

        # As a GtkBin subclass a GtkWindow can only contain one widget at a time.
        self.window.add(self.vbox)
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
        win = PyzanoGtk3Window(argsDict=vars(args))
        win.main()     # Will normally raise SystemExit(...
        print("{0}: debug: Peekaboo, I see you used the Close title bar button!".format(myName), file=os.sys.stderr)
        os.sys.exit(1) # Will `exit 1` like `zenity` would.
    except Exception as exc:
        print("{0}: error: {1}. See '{0} --help' for details".format(myName, str(exc)), file=os.sys.stderr)
        os.sys.exit(1)

