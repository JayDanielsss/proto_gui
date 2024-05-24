#This is the main program for the proto_gui for spinquest
#May 2023
#Jay

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from DataOrganizer import DataOrganizer
from hitDisplay import HitDisplay
import pyqtgraph as pg
import calc
import numpy as np
from scipy.optimize import curve_fit

# Define a class for our main window that inherits from QMainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        



    def initUI(self):
        # Set the window title
        self.setWindowTitle("Proto_Gui_SpinQuest")
        # Set the window dimensions (width, height)
        self.setGeometry(100, 100, 800, 600)
        # Create a central widget and set it as the central widget for the main window
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout(central_widget)

        # Create a QTabWidget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create and add the scatter plot tab
        self.plot_tab()


        layout = QVBoxLayout(self)  # Initialize the layout with the widget as parent
        self.plot_widget = pg.PlotWidget()  # Create the plot widget
        layout.addWidget(self.plot_widget)  # Add the plot widget to the layout



        pg.setConfigOptions(antialias=True)

        
    def plot_tab(self):
        plot_tab = QWidget()
        self.tabs.addTab(plot_tab, "Plots")
        plot_layout = QVBoxLayout(plot_tab)

        # Create the plot widgets
        self.plot_widget_1 = pg.PlotWidget()
        self.plot_widget_2 = pg.PlotWidget()
        

        plot_layout.addWidget(self.plot_widget_1)
        plot_layout.addWidget(self.plot_widget_2)
        
        # Create the plot widgets
        self.plot_widget_vtx = pg.PlotWidget()
        self.plot_widget_vty = pg.PlotWidget()
        self.plot_widget_vtz = pg.PlotWidget()

        plot_layout.addWidget(self.plot_widget_vtx)
        plot_layout.addWidget(self.plot_widget_vty)
        plot_layout.addWidget(self.plot_widget_vtz)

        # Initialize DataOrganizer
        self.organizer = DataOrganizer()
        self.organizer.organizeData()

        # Call the method to create and add the scatter plot
        self.hit_display()
        self.invariant_mass_display()
        self.vertex_per_spill()
  

    def hit_display(self):
        ith_event = 0
        elementid, detectorid, selectedEvents, sid, hits, eventID, track = self.organizer.grab_HitInfo()
        hitmatrices = HitDisplay()
        scatter_raw = hitmatrices.Raw_Hit(elementid, detectorid, selectedEvents, sid, eventID, ith_event)
        scatter_cluster = hitmatrices.Cluster_Hit(hits, selectedEvents, sid, eventID, ith_event)
        scatter_mup, scatter_mum = hitmatrices.Track_Hits(selectedEvents, sid, eventID, track, ith_event)
        
        # Clear the plot widget before drawing new data
        self.plot_widget_1.clear()
        # Add the scatter plot items to the plot widget
        self.plot_widget_1.addItem(scatter_raw)
        self.plot_widget_1.addItem(scatter_cluster)
        self.plot_widget_1.addItem(scatter_mup)
        self.plot_widget_1.addItem(scatter_mum)
        print("Hit Display plotted")


    def invariant_mass_display(self):
        mom = self.organizer.grab_mom()
        invar_mass = []
        mass = calc.calcVariables(mom)

        jpsi_mass = 3.0969  # J/psi mass in GeV
        psiprime_mass = 3.6861  # Psi prime mass in GeV

        # Create a histogram item
        histogram_item = pg.PlotDataItem()

        # Generate the histogram
        hist, bin_edges = np.histogram(mass, bins=np.linspace(0, 10.0, 101))

        # Plot the histogram
        histogram_item.setData(x=bin_edges, y=hist, stepMode=True, fillLevel=0, brush='b')

        # Set labels and title
        self.plot_widget_2.setLabel('left', 'Frequency')
        self.plot_widget_2.setLabel('bottom', 'Value')
        self.plot_widget_2.setTitle('Histogram Example')

        # Add the histogram item to the plot widget
        self.plot_widget_2.addItem(histogram_item)

    def vertex_per_spill(self):
        vtx, vty, vtz, sid, EventID = self.organizer.grab_Vertex()
       # Create histogram items for vtx, vty, vtz
        hist_vtx = pg.PlotDataItem()
        hist_vty = pg.PlotDataItem()
        hist_vtz = pg.PlotDataItem()

        hist_vtx_data, bin_edges_vtx = np.histogram(vtx, bins=50)
        hist_vty_data, bin_edges_vty = np.histogram(vty, bins=50)
        hist_vtz_data, bin_edges_vtz = np.histogram(vtz, bins=50)

        hist_vtx.setData(x=bin_edges_vtx, y=hist_vtx_data, stepMode=True, fillLevel=0, brush='r')
        hist_vty.setData(x=bin_edges_vty, y=hist_vty_data, stepMode=True, fillLevel=0, brush='g')
        hist_vtz.setData(x=bin_edges_vtz, y=hist_vtz_data, stepMode=True, fillLevel=0, brush='b')

        # Add histograms to the plot widgets
        self.plot_widget_vtx.addItem(hist_vtx)
        self.plot_widget_vty.addItem(hist_vty)
        self.plot_widget_vtz.addItem(hist_vtz)


         
    
         

# Main execution
if __name__ == "__main__":
    # Create an instance of QApplication
    app = QApplication(sys.argv)

    # Create an instance of our MainWindow class
    main_window = MainWindow()

    # Show the main window
    main_window.show()

    # Enter the application's main loop
    sys.exit(app.exec_())