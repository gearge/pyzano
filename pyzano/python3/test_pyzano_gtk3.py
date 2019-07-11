#!/usr/bin/env python3

import importlib
import unittest
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk


# https://www.journaldev.com/22576/python-import
def module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestPyzanoGtk3Window(unittest.TestCase):
    def setUp(self):
        argsDict = {"dialogType": "test"}
        self.pyzanoGtk3Window = pyzanogtk3.PyzanoGtk3Window(argsDict=argsDict)

    @unittest.expectedFailure
    def test_main_wout_args_dict(self):
        self.pyzanoGtk3Window.__init__()

    @unittest.expectedFailure
    def test_main_with_args_dict_invalid_subcommand(self):
        argsDict = {"dialogType": "garbage_option"}
        self.pyzanoGtk3Window.__init__(argsDict=argsDict, test=True)
        self.pyzanoGtk3Window.main()

    def test_main_with_args_dict_known_subcommands(self):
        self.assertTrue(hasattr(self.pyzanoGtk3Window, "knownDialogTypes"))
        self.assertIsInstance(self.pyzanoGtk3Window.knownDialogTypes, list)
        self.assertTrue(len(self.pyzanoGtk3Window.knownDialogTypes) != 0)
        for dialogType in self.pyzanoGtk3Window.knownDialogTypes:
            if dialogType not in ["test", "entry", "password"]:
                argsDict = {"dialogType": dialogType}
                self.pyzanoGtk3Window.__init__(argsDict=argsDict, test=True)
                self.pyzanoGtk3Window.main()

    def test_main_with_args_dict_forms_subcommand(self):
        argsDict = {
          'dialogTitle': 'Change App password ', 'dialogType': 'forms', 'dialogAddEntry': None,
          'dialogAddPassword': ['(current) App password', 'Enter new App password', 'Retype new App password'],
          'dialogText': 'Details... ', 'printSeparator': '\n'
        }
        self.pyzanoGtk3Window.__init__(argsDict=argsDict, test=True)
        self.pyzanoGtk3Window.main()

    def test_main_with_args_dict_info_subcommand(self):
        argsDict = {
            "dialogType": "info",
            "dialogTitle": "რასაცა გასცემ, შენია; რას არა, დაკარგულია!",
            "dialogText": '\n'.join([
                "ვარდთა და ნეხვთა ვინათგან მზე სწორად მოეფინების,",
                "დიდთა და წვრილთა წყალობა შენცა ნუ მოგეწყინების!",
                "უხვი ახსნილსა დააბამს, იგი თვით ების, ვინ ების.",
                "უხვად გასცემდი, ზღვათაცა შესდის და გაედინების."
            ]),
            "dialogTooltipText": "ვეფხისტყაოსანი (შოთა რუსთაველი)"
        }
        self.pyzanoGtk3Window.__init__(argsDict=argsDict, test=True)
        self.pyzanoGtk3Window.main()

    def test_main_with_args_dict_error_subcommand(self):
        argsDict = {
            "dialogType": "error",
            "dialogTitle": "Lose Yourself",
            "dialogText": "<b>This is my life and these times are so hard</b>",
            "dialogTooltipText": '\n'.join([
                "And it's getting even harder tryin' to feed and water my seed, plus",
                "See dishonor caught up between bein' a father and a prima-donna..."
            ])
        }
        self.pyzanoGtk3Window.__init__(argsDict=argsDict, test=True)
        self.pyzanoGtk3Window.main()

    def test_main_with_args_dict_warning_subcommand(self):
        argsDict = {
            "dialogType": "warning",
            "dialogTitle": "This Is the New Shit",
            "dialogText": "<i>This is the new shit, stand up and admit</i>",
            "dialogTooltipText": None
        }
        self.pyzanoGtk3Window.__init__(argsDict=argsDict, test=True)
        self.pyzanoGtk3Window.main()

    def test_main_with_args_dict_question_subcommand(self):
        argsDict = {
            "dialogType": "question",
            "dialogTitle": "Отцы и учители, мыслю: \"что есть ад?\"",
            "dialogText": "Рассуждаю так: \"Страдание о том, что нельзя уже более любить\".",
            "dialogTooltipText": "Братья Карамазовы (Федор Достоевский)"
        }
        self.pyzanoGtk3Window.__init__(argsDict=argsDict, test=True)
        self.pyzanoGtk3Window.main()

    @unittest.skip("WIP")
    def test_main_with_args_dict_entry_subcommand(self):
        argsDict = {
            "dialogType": "entry"
        }
        self.pyzanoGtk3Window.__init__(argsDict=argsDict, test=True)
        self.pyzanoGtk3Window.main()

    @unittest.skip("WIP")
    def test_main_with_args_dict_password_subcommand(self):
        argsDict = {
            "dialogType": "password"
        }
        self.pyzanoGtk3Window.__init__(argsDict=argsDict, test=True)
        self.pyzanoGtk3Window.main()

    @unittest.skip("WIP")
    def test_foo(self):
        self.assertTrue('FOO'.isupper())

    def test_destroy(self):
        with self.assertRaises(SystemExit) as cm:
            self.pyzanoGtk3Window.destroy(None, data={"exit": 1})

        self.assertEqual(cm.exception.code, 1)
        self.assertIsNone(self.pyzanoGtk3Window.destroy(None))

    def test__on_ok_clicked_submit(self):
        with self.assertRaises(SystemExit) as cm:
            self.pyzanoGtk3Window._on_ok_clicked_submit(None)

        self.assertEqual(cm.exception.code, 0)
        print(dir(cm))
        print(cm.msg)

    # def test_(self):
    #     with self.assertRaises(SystemExit) as cm:
    #         self.pyzanoGtk3Window._on_ok_clicked_submit(None)
    #
    #     self.assertEqual(cm.exception.code, 1)
    #
    # def test_(self):
    #     with self.assertRaises(SystemExit) as cm:
    #         self.pyzanoGtk3Window.debugdebugdebugdebugdebugdebugdebug(None)
    #
    #     self.assertEqual(cm.exception.code, 1)
    #
    # def test_(self):
    #     with self.assertRaises(SystemExit) as cm:
    #         self.pyzanoGtk3Window.debugdebugdebugdebugdebugdebugdebug(None)
    #
    #     self.assertEqual(cm.exception.code, 1)
    #
    # def test_(self):
    #     with self.assertRaises(SystemExit) as cm:
    #         self.pyzanoGtk3Window.debugdebugdebugdebugdebugdebugdebug(None)
    #
    #     self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    # print(__name__)    # __main__
    # print(os.sys.argv) # ['./test_pyzano_gtk3.py']

    myAbspath = os.path.abspath(os.sys.argv[0])
    myDirname = os.path.dirname(myAbspath)
    myFilename = os.path.basename(myAbspath)
    fromFilename = myFilename.replace('test_', '')

    pyzanogtk3 = module_from_file("pyzanogtk3", os.path.join(myDirname, fromFilename))

    unittest.main()
