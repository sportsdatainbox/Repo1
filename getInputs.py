#import required modules
from Tkinter import *
import Tkinter as ttk
from ttk import *
import base64, zlib, os, tempfile,datetime

def startMenu():
    """
    function to produce popup window which will then pass the season, round and day of round to the rest of the
    program.  Once the model is making money this section will be automated and replaced.
    """
    now = datetime.datetime.now()

    root = Tk()

    #create popup window (with TK icon removed), change the title to none, alter the size of the popup, create button, and pack / place
    icon = zlib.decompress(base64.b64decode('eJxjYGAEQgEBBiDJwZDBy'
        'sAgxsDAoAHEQCEGBQaIOAg4sDIgACMUj4JRMApGwQgF/ykEAFXxQRc='))
    ipn,icon_path = tempfile.mkstemp()
    with open(icon_path, 'wb') as icon_file:
        icon_file.write(icon)

    root.iconbitmap(default=icon_path)
    root.title(" ")
    root.geometry('{}x{}'.format(300, 275))

    # Add a grid which makes it easier to place the comboboxes
    mainframe = Frame(root)
    mainframe.grid(column=0,row=0, sticky=(N,W,E,S) )
    mainframe.columnconfigure(0, weight = 1)
    mainframe.rowconfigure(0, weight = 1)
    mainframe.pack(pady = 15, padx = 50)

    #pythonic way to create multiple boxes from dictionary.
    #first create function
    def packPopupMenu(choices,defaultOption,label):
        """
        function to create combobox in popup window
        adds choices to drop down menu, sets default value,
        adds the box to the grid then places a label directly above
        needed to adhere to DRY principle.
        """
        popupMenu = Combobox(mainframe, values=choices)
        popupMenu.set(defaultOption)
        popupMenu.configure(justify='center')
        popupMenu.grid(row = (i*2)+2, column =1)
        Label(mainframe, text=label).grid(row = (i*2)+1, column = 1)
        return popupMenu

    #second, create dictionary of options
    d = {
             0 : [list(range(2015,2025)),now.year,'Select Season'      ]
            ,1 : [list(range(1,28))     ,       7,'Select Round'       ]
            ,2 : [list(range(1,7))      ,       1,'Select Day of Round']
         }

    #create a list that gives us the name of the output of each box
    cbs = [packPopupMenu(*d[i]) for i in range(len(d))]

    def clickOk():
        """
        function will return the selected values of the comboboxes
        and get rid of the popup window when ok is clicked
        """

        global season, cr, pr, dor

        #subsequent program is expecting numbers and not strings
        season = int(cbs[0].get())
        cr     = int(cbs[1].get())
        dor    = int(cbs[2].get())
        pr     = int(cr) - 1

        root.destroy()

        return None

    ### link function to change dropdown
    ##tkvar.trace('w',change_dropdown)
    ##
    ##tkvar1.trace('w',change_dropdown)

    button = Button(root, text="OK", command=clickOk)
    #button.config(bg='ghost white')
    """
    this is just a list of default button styles that may come in handy later
        button['style'] = 'TButton'
        Widget class	        Style name
        Button	                TButton
        Checkbutton	            TCheckbutton
        Combobox	            TCombobox
        Entry	                TEntry
        Frame	                TFrame
        Label	                TLabel
        LabelFrame	            TLabelFrame
        Menubutton	            TMenubutton
        Notebook	            TNotebook
        PanedWindow	            TPanedwindow (not TPanedWindow!)
        Progressbar	            Horizontal.TProgressbar or Vertical.TProgressbar, depending on the orient option.
        Radiobutton	            TRadiobutton
        Scale	                Horizontal.TScale or Vertical.TScale, depending on the orient option.
        Scrollbar	            Horizontal.TScrollbar or Vertical.TScrollbar, depending on the orient option.
        Separator	            TSeparator
        Sizegrip	            TSizegrip
        Treeview	            Treeview (not TTreview!)
    """
    button.pack(side='bottom',padx=0,pady=30)

    #bring up popup window
    root.mainloop()

    #remove temporary file that is need for transparrent icon
    os.close(ipn)
    os.remove(icon_path)

    return season, cr, pr, dor