#This is the main program for the proto_gui for spinquest
#May 2023
#Jay

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget
from PyQt5.QtCore import QTimer
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
        
        # # Create the plot widgets
        self.plot_widget_vtx = pg.PlotWidget()
        self.plot_widget_vty = pg.PlotWidget()
        self.plot_widget_vtz = pg.PlotWidget()

        plot_layout.addWidget(self.plot_widget_vtx)
        plot_layout.addWidget(self.plot_widget_vty)
        plot_layout.addWidget(self.plot_widget_vtz)

        # Initialize DataOrganizer
        self.organizer = DataOrganizer()
        self.organizer.organizeData()

        # Initialize event index
        self.ith_event = 0

        # Setup a timer to call hit_display repeatedly
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hit_display)
        self.timer.start(1000)  # Call hit_display every 1000 milliseconds (1 second)

        # Call the method to create and add the scatter plot
        self.hit_display()
        self.invariant_mass_display()
        self.vertex_per_spill()
  

    def hit_display(self):
        if self.ith_event >= 40:
            self.timer.stop()  # Stop the timer after 10 iterations
            return
        elementid, detectorid, selectedEvents, sid, hits, eventID, track = self.organizer.grab_HitInfo()
        hitmatrices = HitDisplay()
        scatter_raw = hitmatrices.Raw_Hit(elementid, detectorid, selectedEvents, sid, eventID, self.ith_event)
        scatter_cluster = hitmatrices.Cluster_Hit(hits, selectedEvents, sid, eventID, self.ith_event)
        scatter_mup, scatter_mum = hitmatrices.Track_Hits(selectedEvents, sid, eventID, track, self.ith_event)
        
        # Clear the plot widget before drawing new data
        self.plot_widget_1.clear()
        # Add the scatter plot items to the plot widget
        self.plot_widget_1.addItem(scatter_raw)
        self.plot_widget_1.addItem(scatter_cluster)
        self.plot_widget_1.addItem(scatter_mup)
        self.plot_widget_1.addItem(scatter_mum)

        # Set the y-axis limit to 0, 201
        self.plot_widget_1.setYRange(0, 201)
        print("Hit Display plotted")

        # Advance the event index
        self.ith_event += 1


    def invariant_mass_display(self):
        mom = self.organizer.grab_mom()
        invar_mass = []
        mass = calc.calcVariables(mom)[0]

        jpsi_mass = 3.0969  # J/psi mass in GeV
        psiprime_mass = 3.6861  # Psi prime mass in GeV

        def gaussian(x, amplitude, mean, stddev):
            return amplitude * np.exp(-((x - mean) / stddev) ** 2 / 2)
        # Create a histogram item
        histogram_item = pg.PlotDataItem()

        # Generate the histogram
        hist, bin_edges = np.histogram(mass, bins=np.linspace(0, 10.0, 101))

        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        fit_range = (bin_centers < 3.3)
        initial_guess = [max(hist), jpsi_mass, 0.1]

        x_fit_data = bin_centers[fit_range]
        y_fit_data = hist[fit_range]

        params, covariance = curve_fit(gaussian, x_fit_data, y_fit_data, p0=initial_guess)
        mean_fit, width_fit = params[1], abs(params[2])
        print(f"Mean of the Gaussian fit: {mean_fit:.3f} GeV")
        print(f"Width (sigma) of the Gaussian fit: {width_fit:.3f} GeV")

        # Plot the histogram
        histogram_item.setData(x=bin_edges, y=hist, stepMode=True, fillLevel=0, brush='b')

        # Set labels and title
        self.plot_widget_2.setLabel('left', 'Frequency')
        self.plot_widget_2.setLabel('bottom', 'Value')
        self.plot_widget_2.setTitle('Histogram Example')

        # Add the histogram item to the plot widget
        self.plot_widget_2.addItem(histogram_item)

        # Add vertical lines for jpsi_mass and psiprime_mass
        jpsi_line = pg.InfiniteLine(pos=jpsi_mass, angle=90, pen=pg.mkPen('r', style=pg.QtCore.Qt.DashLine))
        psiprime_line = pg.InfiniteLine(pos=psiprime_mass, angle=90, pen=pg.mkPen('g', style=pg.QtCore.Qt.DashLine))

        self.plot_widget_2.addItem(jpsi_line)
        self.plot_widget_2.addItem(psiprime_line)
         # Add the labels to the lines
        jpsi_label = pg.TextItem(text='J/psi Mass', color='r', anchor=(0.5, 0))
        psiprime_label = pg.TextItem(text='psi Mass', color='g', anchor=(0.5, 0))

        # Adjust the label positions
        jpsi_label.setPos(jpsi_mass, 6)  # Adjust the y-coordinate as needed
        psiprime_label.setPos(psiprime_mass, 5)  # Adjust the y-coordinate as needed

        self.plot_widget_2.addItem(jpsi_label)
        self.plot_widget_2.addItem(psiprime_label)

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