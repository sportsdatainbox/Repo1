from subprocess import Popen
import subprocess
import webbrowser
import Tkinter
import tkMessageBox
import sys
import base64, zlib, os, tempfile
import checkLog

def winProb(season,dor,rnd):
    """
    Used to run the SAS progam - "&season AFL build.sas"
    The function creates a popup window which can be used to help the user
    validate whether or not the data collection process has executed correctly
    This function also has the ability to check the log of the SAS program
    """
    print '\nRun SAS data build:'
    #call the SAS data build
    subprocess.call([
                      'C:/Program Files/SASHome/SASFoundation/9.3/sas.exe'
                     ,'-config'  , 'C:/Program Files/SASHome/SASFoundation/9.3/nls/en/sasv9.cfg'
                     ,'-sysin'   ,'D:/AFL/Model/%s AFL build.sas'                        % season
                     ,'-log'     ,'D:/AFL/Model/Data/Logs/log - build %s round %s.txt'   % (season,rnd)
                     ,'-print'   ,'D:/AFL/Model/Data/Logs/print - build %s round %s.txt' % (season,rnd)
                     ,'-sysparm', '%s %s %s'                                             % (rnd,dor,season)
                     ])

    #function to generate popup box that asks if log is acceptable.(check win prob log)
    def cwpl():
        global resLog
        print '  > check log:'
        checkLog.path('D:/AFL/Model/Data/Logs/log - build %s round %s.txt' % (season,rnd))
        resLog = tkMessageBox.askyesno(title='Log', message='Acceptable?')
        if resLog != True:
            epmb = tkMessageBox.showerror(title='Check the program', message='Click to exit')
            puw.destroy()
        if 'resVal' in globals():
            puw.destroy()
        return None

    #function to generate popup box that asks if data validation was passed. (check data validation)
    def cdv():
        global resVal
        webbrowser.open('D:/AFL/Model/Data/Validation/body.html')
        print '  > check validation:'
        resVal = tkMessageBox.askyesno(title='Validation', message='Passed?')
        if resVal != True:
            resVal = tkMessageBox.showerror(title='Data Validation Failed', message='Click to exit')
            puw.destroy()
        else:
            print '    > passed'
        if 'resLog' in globals():
            puw.destroy()
        return None

    #create popup window (with TK icon removed), change the title to none, alter the size of the popup, create button, and pack / place
    icon = zlib.decompress(base64.b64decode('eJxjYGAEQgEBBiDJwZDBy'
        'sAgxsDAoAHEQCEGBQaIOAg4sDIgACMUj4JRMApGwQgF/ykEAFXxQRc='))
    ipn,icon_path = tempfile.mkstemp()
    with open(icon_path, 'wb') as icon_file:
        icon_file.write(icon)

    puw = Tkinter.Tk()
    puw.wm_title("")
    puw.geometry('{}x{}'.format(350, 100))
    puw.iconbitmap(default=icon_path)
    ##puw.overrideredirect(1)

    #generate 3 buttons within the popup windown that have different function (shown above)
    b3 = Tkinter.Button(puw, command=puw.destroy,bg='ghost white',text="Quit", width=42)
    b3.pack(side='bottom',padx=0.5,pady=0.5)

    b1 = Tkinter.Button(puw,command = cwpl,bg='ghost white',text = "Click to Check Log",height = 4, width = 20)
    b1.pack(side='left',padx=1,pady=0.5)

    b2 = Tkinter.Button(puw,command = cdv,bg='ghost white',text = "Click to Open Validation",height = 4, width = 20)
    b2.pack(side='right',padx=1,pady=0.5)

    #bring up the popup window
    puw.mainloop()

    #remove temporary file that is need for transparrent icon
    os.close(ipn)
    os.remove(icon_path)

    #error checking - stop the program from proceeding to automatic betting
    if 'resLog' in globals():
        if resLog != True:
            sys.exit('*** SAS data build needs further investigation ***')
    if 'resVal' in globals():
        if resVal != True:
            sys.exit('*** Validation FAILED ***')

    return None

def betSize(season,dor,rnd):
    """
    Used to run the SAS progam - "&season AFL bets.sas"
    The function creates a popup window which can be used to help the user
    validate whether or not the bets have been generated correctly
    This function also has the ability to check the log of the SAS program
    """
    print '\nRun SAS bets progam:'
    subprocess.call([
                          'C:/Program Files/SASHome/SASFoundation/9.3/sas.exe'
                         ,'-config'  , 'C:/Program Files/SASHome/SASFoundation/9.3/nls/en/sasv9.cfg'
                         ,'-sysin'   ,'D:/AFL/Model/2018 AFL bets.sas'
                         ,'-log'     ,'D:/AFL/Model/Data/Logs/log - bets %s round %s.txt'   % (season,rnd)
                         ,'-print'   ,'D:/AFL/Model/Data/Logs/print - bets %s round %s.txt' % (season,rnd)
                         ,'-sysparm', '%s %s %s'                                            % (rnd,dor,season)
                         ])

    #function to generate popup box that asks if log is acceptable.(check bet size log)
    def cbsl():
        global resLog
        print '  > check log:'
        checkLog.path('D:/AFL/Model/Data/Logs/log - bets %s round %s.txt' % (season,rnd))
        resLog = tkMessageBox.askyesno(title='Log', message='Acceptable?')
        if resLog != True:
            epmb = tkMessageBox.showerror(title='Check the program', message='Click to exit')
            puw.destroy()
        return None

    #function to generate popup box that asks if betfair bets are valid. (check betfair bets)
    def cbb():
        global autoBetBetfair
        print '  > open Betfair bets'
        p = Popen('D:/AFL/Model/Data/CSVs/Bets/%s/betfair_%s_%s_%s.csv' % (season,season,rnd,dor), shell=True)
        autoBetBetfair = tkMessageBox.askyesno(title='Betfair', message='Place Bets Automatically?')
        if autoBetBetfair != True:
            autoBetBetfair = tkMessageBox.showwarning(title='', message='Enter bets manually')
            puw.destroy()
        return None

    #function to generate popup box that asks if tab bets are valid. (check tab bets)
    def ctb():
        print '  > open TAB bets'
        p = Popen('D:/AFL/Model/Data/CSVs/Bets/%s/tab_%s_%s_%s.csv' % (season,season,rnd,dor), shell=True)
        t = tkMessageBox.showinfo(title='TAB', message='Click to proceed')
        return None

    #create popup window (with TK icon removed), change the title to none, alter the size of the popup, create button, and pack / place
    icon = zlib.decompress(base64.b64decode('eJxjYGAEQgEBBiDJwZDBy'
        'sAgxsDAoAHEQCEGBQaIOAg4sDIgACMUj4JRMApGwQgF/ykEAFXxQRc='))
    ipn,icon_path = tempfile.mkstemp()
    with open(icon_path, 'wb') as icon_file:
        icon_file.write(icon)

    puw = Tkinter.Tk()
    puw.wm_title("")
    puw.geometry('{}x{}'.format(515, 100))
    puw.iconbitmap(default=icon_path)
    ##puw.overrideredirect(1)

    #generate 4 buttons within the popup windown that have different function (shown above)
    b4 = Tkinter.Button(puw, command=puw.destroy,bg='ghost white',text="Quit", width=42)
    b4.pack(side='bottom',padx=0.5,pady=0.5)

    b1 = Tkinter.Button(puw,command = cbsl,bg='ghost white',text = "Check Log",height = 4, width = 20)
    b1.pack(side='left',padx=0.5,pady=0.5)

    b2 = Tkinter.Button(puw,command = cbb,bg='ghost white',text = "Check Betfair Bets",height = 4, width = 20)
    b2.pack(side='left',padx=0.5,pady=0.5)

    b3 = Tkinter.Button(puw,command = ctb,bg='ghost white',text = "Check TAB Bets",height = 4, width = 20)
    b3.pack(side='left',padx=0.5,pady=0.5)

    #bring up the popup window
    puw.mainloop()

    #remove temporary file that is need for transparrent icon
    os.close(ipn)
    os.remove(icon_path)

    #error checking to avoid automatic betting
    if 'autoBetBetfair' in globals():
        if autoBetBetfair != True:
                sys.exit('*** Bets will not be processed automatically ***')
    if 'resLog' in globals():
        if resLog != True:
            sys.exit('*** SAS bet sizes needs further investigation ***')

    return None