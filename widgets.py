#! /home/creamop/miniconda3/bin/python

from PyQt5.QtWidgets import (QWidget , QPushButton, QFileDialog, QComboBox)
from PyQt5.QtCore import QSize

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from time import gmtime, strftime, localtime
import pylab


#custom function imports
from getfilelist import getfilelist
from makeroot import makeroot
from complete_tree import complete_tree
from trigrate import trigrate_chip
from trigrate import trigrate_channel

#UNUSED imports 
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
#from PyQt5.QtWidgets import (QLabel, QLineEdit, QApplication, QMessageBox,
#                             qApp, QGridLayout, QTextEdit, QHBoxLayout, QVBoxLayout,
#                             QLCDNumber, QSlider, QInputDialog, QSplitter, QDockWidget,
#                             QFrame, QMainWindow, QAction, QToolTip)
#import pyqtgraph as pg
#from PyQt5.QtGui import QFont, QStatusBar   
#from PyQt5.QtCore import QCoreApplication, QRect, Qt, pyqtSignal, QObject, 

#directories
app_dir = '/home/creamop/trigger_rate_app'
data_dir = '/data/cdps2/cream'
makeroot_path = '/home/creamop/L0data/'


#Global definitions to be used later
files = []
chip_select = 1
num_files = 0
chips = 40
events = 0
tree = 0
trigger_rate = None
time = None
start = ''
end = ''
last_year = 2030
first_year = 2015
strftime("%Y%m%d-000000", localtime())
current_year = strftime("%Y", localtime())
current_month = strftime("%m",localtime())
current_day = strftime("%d",localtime())
dates = [['%s'%first_year,'%s'%current_year],['01','%s'%current_month],['01','%s'%current_day]]

class yeardrop(QWidget): #This sets the year drop down menu for the app
        
    def __init__(self,se=None):
        super().__init__()
        if se == None:
            self.startend = '1'
        else:
            self.setstartend(sten=se)
        self.initUI(se=self.startend)
        
    def setstartend(self,sten=None): #this is used to determine if it is for start or end dates
        self.startend = sten
        
    def initUI(self,se=None): 
	#se is the StartEnd variable here and going forward (same as sten) (STard ENd)
	#this checks to see if it is a start or end date dropdown
        global current_year,first_year       
        yearlist = QComboBox(self)
        for i in range(first_year,last_year+1):
            yearlist.addItem("%d"%i)
        if self.startend == 'end':
            acy = int(current_year) - first_year
            yearlist.setCurrentIndex(acy)
        yearlist.activated[str].connect(self.onActivated)
	#connects selection of dropdown to onActivated function
            
    def onActivated(self, text): #this sets the correct dates in the date array
#        print(self.startend)
        if self.startend == 'start':
            dates[0][0] = text
#            print(dates)
        elif self.startend == 'end':
            dates[0][1] = text
#            print(dates)
        
class monthdrop(QWidget): #creates the month dropdown widget
    def __init__(self,se=None):
        super().__init__()
        if se == None:
            self.startend = '1'
        else:
            self.setstartend(sten=se)
        self.initUI(se=self.startend)

    def setstartend(self,sten=None):
        self.startend = sten
        
    def initUI(self,se=None):
        global current_month
        monthlist = QComboBox(self)
        for i in range(1,13):
            if i < 10:
                monthlist.addItem("0%d"%i)
            else:
                monthlist.addItem("%d"%i)
        if self.startend == 'end':
            monthlist.setCurrentIndex(int(current_month)-1)
        monthlist.activated[str].connect(self.onActivated) 
	#connects selection of dropdown to onActivated function

    def onActivated(self, text): #sets the date based on start or end
#        print(self.startend)
        if self.startend == 'start':
            dates[1][0] = text
#            print(dates)
        elif self.startend == 'end':
            dates[1][1] = text
#            print(dates)


class daydrop(QWidget): #day selection dropdown widget
    def __init__(self,se=None):
        super().__init__()
        if se == None:
            self.startend = '1'
        else:
            self.setstartend(sten=se)
        self.initUI(se=self.startend)

    def setstartend(self,sten=None):
        self.startend = sten
        
    def initUI(self,se=None):
        global current_day
        daylist = QComboBox(self)
        for i in range(1,10):
            daylist.addItem("0%d"%i)
        for i in range(10,32):
            daylist.addItem("%d"%i)
        if self.startend == 'end':
            daylist.setCurrentIndex(int(current_day)-1)
        daylist.activated[str].connect(self.onActivated)
	#connects selection of dropdown to onActivated function

    def onActivated(self, text):
#        print(self.startend)
        if self.startend == 'start':
            dates[2][0] = text
#            print(dates)
        elif self.startend == 'end':
            dates[2][1] = text
#            print(dates)
        
class chipdrop(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        chiplist = QComboBox(self)
        for i in range(1,41):
            chiplist.addItem("%d"%i)
        chiplist.activated[str].connect(self.chip_selection)
    def chip_selection(self, text):
        global chip_select
        chip_select = int(text)

class select_file(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self): 
	#this is the select file push button
        select_file = QPushButton('Select File',self)
        select_file.setToolTip('Select specific files to be used')
        select_file.clicked.connect(self.showDialog)
	#connects the select_file button click with the show_Dialog function 
        
    def showDialog(self):
	#this creates a file Dialog wigdet that opens to the data directory for ISSCREAM 
        global files,start,end, app_dir, data_dir, makeroot_path
        path = makeroot_path + '/cream'
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        fname = file_dialog.getOpenFileNames(self, 'Open files', directory=data_dir,filter='*.dat')
        if fname[0] != []: 
            #checks to maek sure that the dialog box was not closed 
            #without making a selection   
            num_files = len(fname[0])
            files = ['']*num_files
            for i in range(0,num_files):
                files[i] = fname[0][i] + ' '
            	#this is just to standardize this output with the getfilelist function
            
            os.chdir(makeroot_path)
            os.system('./list_override')
            os.chdir(path)
	#this writes the file list generated to the LIST file to be used by MAKEROOT
            file_list = open('LIST','w')
            file_list.writelines(["%s\n"%lines for lines in files])
            file_list.close()
            os.chdir(app_dir)
            
            numf = len(files)
            start = files[0][50:65]
            end = files[numf-1][50:65]
            
            
            get_tree_data()
        

class fullday(QWidget):
#full day button that gets the data for the day that is currently selected by the end date (current
# by default)
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        full_day = QPushButton('Full Day',self)
        full_day.clicked.connect(self.get) #connects click to the get function
        full_day.setToolTip('Gets the data and plots it for the entire day selected by end date/time')
        
    def get(self):
        global files, start, end
        start = '%s%s%s-000000'%(dates[0][1],dates[1][1],dates[2][1])
        end = '%s%s%s-235959'%(dates[0][1],dates[1][1],dates[2][1])
        files = getfilelist(start=start,end=end)
        
        numf = len(files)
        start = files[0][50:65]
        end = files[numf-1][50:65]

        get_tree_data()
        
        
class getdata(QWidget):
#this gets data for the days that are selected start default to 01/01/2015 and end to current date
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        get_data = QPushButton('Get Data',self)
        get_data.clicked.connect(self.get) #connects click to the get function 
        get_data.setToolTip('Gets the data and plots it for the date range selected')
        
    def get(self):
        global files, start, end
        start = '%s%s%s-000000'%(dates[0][0],dates[1][0],dates[2][0])
        end = '%s%s%s-235959'%(dates[0][1],dates[1][1],dates[2][1])
        files = getfilelist(start=start,end=end)
        numf = len(files)
        start = files[0][50:65]
        end = files[numf-1][50:65]
        get_tree_data()
        
class last(QWidget):
#this gets the data for the last file (2nd most recent one created in case the most reason is still 
#being written to. Uses end date as start search point (default current date)
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        last_file = QPushButton('Last File',self)
        last_file.clicked.connect(self.file) #connects click to file function
        last_file.setToolTip('This selects the last full .dat file that was created either on the date selected or if none selected most recent')
    
    def file(self):
        global files, start, end, current_year,current_month,current_day
        if dates == [['%s'%first_year,'%s'%current_year],['01','%s'%current_month],['01','%s'%current_day]]:
	#this checks to see if the dates selected are the defaults or not
#            end = strftime("%Y%m%d-000000", gmtime())
            files = getfilelist(last=1)
            end = files[0][50:65]
#            print('Most Recent File')
        else:
	#if defaults not selected it uses the selected dates
            start = '%s%s%s-000000'%(dates[0][0],dates[1][0],dates[2][0])
            end = '%s%s%s-235999'%(dates[0][0],dates[1][0],dates[2][0])
            files = getfilelist(start=start,end=end,last=1)

        get_tree_data()


        


def get_tree_data():
#this is the function that handles the data processing. 
#Once the file list is generated the get_tree_data function is called.

        global tree, events, num_files,files, start, end
        makeroot(files) #this bash script uses the file LIST and generates the approprate ROOT files
        tree = complete_tree(file_list=files)#this function reads in the ROOT file to a numpy array and returns it
        num_files = len(files)
        [trigger_rate,time,layer2asiic] = trigrate_chip(tree=tree,files=num_files) 
	#this function takes the tree and generates the trigger rate for each asiic chip
        events = len(tree)        
        plt.close(1) #closes any open figure previously incase the app was used already to generate a plot
        plt.figure(1)

        y_data = layer2asiic[:,0] #this is asiic list that is in the geometric location from top down
        y_data = y_data.astype(int) #this just makes it an int for display purposes
        x_data = trigger_rate[:,1]
        xdat = pd.Series.from_array(x_data) #generates the panda sereis to be used for plotting 

        this_manager = pylab.get_current_fig_manager() #this is just creating the manager object so the position of the plots can be manipulated
        this_manager.window.resize(600,800)

        ax = xdat.plot(kind='barh') #plots data as horizontal bar graph
	#formating:
        ax.set_title('Trigger Rate: %s -> %s'%(start,end))
        ax.set_xlabel('Events (Hz)')
        ax.set_ylabel('Layer')
        ax.set_xlim(0,20)
        ax.legend(['Asiic Chip'])
        ax.set_yticklabels(y_data)#creates the tick marks that are the layers
        for label in ax.yaxis.get_ticklabels()[1:40:2]:
	#this masks every second layer tick because there are two chips per layer
            label.set_visible(False)
        plt.gca().invert_yaxis() #makes the axis go from 40 up to zero for consistancy with CAL documentation
        rects = ax.patches
        
	#this is to mark each chip bar with which chip number it is (not sequential). Appears to the right of the bar.
        for rect, label in zip(rects, layer2asiic[:,1]):
            width = rect.get_width()
            ax.text(width + 0.8, rect.get_y() + rect.get_height() - 0.18, label, ha='right', va='center')
        
        plt.show()

class getchipdata(QWidget):
#this creates the button that gets the chip by chip individual channel trigger rates
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        get_chip_plot = QPushButton('Plot Chip Data',self)
        get_chip_plot.clicked.connect(self.call_chip) #connects to call_chip function
        get_chip_plot.setToolTip('Gets the data and plots it for the ASIIC Chip selected')
        
    def call_chip(self):
        getchip(self)

    
class nextchip(QWidget):
#creates a next chip button that gets the data for the next asiic chip
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        next_chip = QPushButton('>',self)
        next_chip.resize(QSize(20, 20))
        next_chip.clicked.connect(self.call_chip)
        next_chip.setToolTip('Next ASIIC Chip')
    def call_chip(self):
        getchip(self,nextc=0)

            
class previouschip(QWidget):
#creates a previous chip button that gets the ata for the previous asiic chip
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        next_chip = QPushButton('<',self)
        next_chip.clicked.connect(self.call_chip)
        next_chip.resize(QSize(20, 20))
        next_chip.setToolTip('Previous ASIIC Chip')
    def call_chip(self):
        getchip(self,previousc=0)           
        
def getchip(self,nextc=None,previousc=None):
#this gets the channel by channel trigger rate for a given asiic chip
    global tree, events, num_files,chip_select, start, end
    if events == 0:
        print('Please select a set of data first')
    if nextc == 0:
	#this varifies that you are not trying to increase the chip number past 39
        if chip_select < 40:
            chip_select += 1
            process_data(self)
        else:
#            print(chip_select)
            print()
            print('Chip number already at 40')
    elif previousc == 0:
	#varifies that you are not trying to deacrease chip number bellow 0
        if chip_select > 1:
            chip_select -= 1
            process_data(self)
        else:
            print()
            print('Chip number already at 1')
    else:
        process_data(self)
            
def process_data(self):
#this processes the data for channel by channel trigger rates for a single asiic chip
    global tree, events, num_files,chip_select, start, end
    [trigger_rate,time] = trigrate_channel(tree=tree,chip=chip_select,files=num_files)
    plt.close(2)
    plt.figure(2)
    plt.barh(trigger_rate[:,0],trigger_rate[:,1])
    plt.ylim(trigger_rate[0,0],trigger_rate[63,0])
    plt.xlim(0,100)
    this_manager = pylab.get_current_fig_manager()
    this_manager.window.move(1,1)
    plt.xlabel('Events (Hz)')
    plt.ylabel('Channel Number')
    plt.title('Asiic Chip %d Trigger Rate: %s -> %s'%(chip_select,start,end))
    plt.show()

        
        
        
        
