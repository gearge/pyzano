# Display graphical dialog boxes from shell scripts

usage: pyzano [-h] {forms,question,warning,error,info,entry,password} ...

## python2/pyzano_gtk2.py

A [janky] attempt at a Python2 + GTK2 implementation of the zenity program, with similar (but a subset of) command line options. Seek '--help'

    optional arguments:
      -h, --help            show this help message and exit

    Dialog options:
      This is an overview. Use 'pyzano {subcommand} --help' to show help for a
      particular subcommand. E.g. 'pyzano forms --help'

      {forms,question,warning,error,info,entry,password}
        forms               Display forms dialog
        question            Display question dialog
        warning             Display warning dialog
        error               Display error dialog
        info                Display info dialog
        entry               Display text entry dialog
        password            Display password dialog

## python3/pyzano_gtk3.py

A [janky] attempt at a Python3 + GTK3 implementation of the zenity program, with similar (but a subset of) command line options. Seek '--help'

    optional arguments:
      -h, --help            show this help message and exit

    Dialog options:
      This is an overview. Use 'pyzano {subcommand} --help' to show help for a
      particular subcommand. E.g. 'pyzano forms --help'

      {forms,question,warning,error,info,entry,password}
        forms               Display forms dialog
        question            Display question dialog
        warning             Display warning dialog
        error               Display error dialog
        info                Display info dialog
        entry               Display text entry dialog
        password            Display password dialog


