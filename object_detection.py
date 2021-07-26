# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ObjectDetection
                                 A QGIS plugin
 This plugin can be used to train and test object detection models on satellite imagery.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-06-26
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Centre for Development of Advanced Computing, Pune
        email                : rshindihatti@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

# Import threading
from threading import *

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .object_detection_dialog import ObjectDetectionDialog
import os.path

import pathlib

import shutil
import numpy as np

# Import labelImg
from .labelImg.labelImg import *

# Import preprocessing
from .preprocess import *


class ObjectDetection:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ObjectDetection_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Object Detection')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        
        #clippings_path
        self.clippings_path = ""

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ObjectDetection', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/object_detection/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Train and test object detection models.'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Object Detection'),
                action)
            self.iface.removeToolBarIcon(action)

    # function to show the clippings in the scroll area
    def show_clippings(self):
        url = self.trainImagesPath
        
        self.i=0
        self.j=0
    
        self.files_it = iter([os.path.join(url, file) for file in os.listdir(url)])

        self._timer = QtCore.QTimer(interval=2)
        self._timer.timeout.connect(self.on_timeout)
        self._timer.start()
    
    # used in show_clippings()
    def on_timeout(self):
        try:
            file = next(self.files_it)
            pixmap = QPixmap(file)
            self.add_pixmap(pixmap)
        except StopIteration:
            self._timer.stop()

    # function to add pixmap to the layout
    def add_pixmap(self, pixmap):
    
        if not pixmap.isNull():
            pixmap_resized = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)
            label = QLabel(pixmap=pixmap_resized)
            self.dlg.gridLayout.addWidget(label, self.i, self.j)
            self.j = (self.j+1) % 11
            if(self.j==0):
                self.i = self.i+1

    # function to select the training image
    def select_training_image(self):
        filename, _ = QFileDialog.getOpenFileName(self.dlg, "", "", '*.tiff, *.tif')
        self.filename = filename
        self.dlg.lineEditInputImage.setText(filename)

    '''def clippingThread(self):
        t1 = Thread(target = self.clip_image)
        t1.start()'''

    def createTrainTestSplit(self):
        self.testImagesPath = os.path.join(self.dataset_path, "test")
        self.trainImagesPath = os.path.join(self.dataset_path, "train")
    
        source = self.clippings_path
        dest = self.testImagesPath
        files = os.listdir(source)
        
        if(self.testSplitPercentage>0):
            pathlib.Path(self.testImagesPath).mkdir(0o755, parents=True, exist_ok=True)
        
            i=0
            length = len(files)
            for f in files:
                
                # progress bar increment
                i+=1
                progress = self.dlg.progressBarClip.value() + ((i/length) * 20)
                self.dlg.progressBarClip.setValue(progress)
                
                if np.random.rand(1) < self.testSplitPercentage/100:
                    shutil.move(source + '/'+ f, dest + '/'+ f)
        else:
            progress = 100
            self.dlg.progressBarClip.setValue(progress)
        
        os.rename(source, self.trainImagesPath)

    # function to clip the image
    def clip_image(self):
    
        self.dlg.statusLabel.setText("Perfoming checks...")
        self.datasetName = self.dlg.lineEditDatasetName.text()
        plugin_directory = sys.path[0]
        self.dataset_path = os.path.join(plugin_directory, "plugins/object_detection/workspace/data", self.datasetName)
        self.clippings_path = os.path.join(plugin_directory, "plugins/object_detection/workspace/data", self.datasetName, "images")  
             
        if self.datasetName == "":
            self.dlg.error_dialog = QErrorMessage()
            self.dlg.error_dialog.showMessage('Please enter dataset name.')
            return
        elif not self.filename:
            self.dlg.error_dialog = QErrorMessage()
            self.dlg.error_dialog.showMessage('Please select an input file.')
            return
        elif os.path.exists(self.clippings_path): 
            self.dlg.error_dialog = QErrorMessage()
            self.dlg.error_dialog.showMessage('The detector already exists. Please provide a new detector name.')
            self.dlg.lineEditDatasetName.setText("") 
            return 
            
        self.dlg.statusLabel.setText("Creating directories...")    
        pathlib.Path(self.clippings_path).mkdir(0o755, parents=True, exist_ok=True)
        self.dlg.pushButtonCreateClippings.setEnabled(False)
        
        self.dlg.statusLabel.setText("Clipping the image...")
        geoTransform, projection = create_jpg_clippings(self.filename, self.clippings_path, self.dlg.progressBarClip)
        
        # create training and testing sets
        self.dlg.statusLabel.setText("Splitting the images into testing and training sets...")
        self.createTrainTestSplit()
        
        self.dlg.statusLabel.setText("Dataset created...")
        self.dlg.pushButtonCreateClippings.setText("Done!")
        
        # enable annotation and preparation buttons
        self.dlg.pushButtonAnnotate.setEnabled(True)
        self.dlg.pushButtonPreparation.setEnabled(True)
               
        # show clippings in the scroll view
        self.show_clippings()
        

    # function to open labelImg
    def open_label_img(self):
        win = MainWindow(self.clippings_path,
                     "",
                     self.clippings_path)
        win.show()

    # Dialog to annotate images
    def open_annotation_dialog(self):
        

    def display_slider_value(self):
        self.trainSplitPercentage = self.dlg.horizontalSliderSplit.value()
        self.testSplitPercentage = 100 - self.trainSplitPercentage
        self.dlg.trainTestLabel.setText("Train = " + str(self.trainSplitPercentage) + "% | Test = " + str(self.testSplitPercentage) + "%")

    # Create all the necessary files for training.
    def prepare_dataset_for_training(self):
        dest = self.dataset_path
        name = self.datasetName
    
        # Create dataset_name.names file
        src = str(os.path.join(self.trainImagesPath, "classes.txt"))
        destNames = str(os.path.join(dest, name + ".names"))
        shutil.copyfile(src, destNames)
        
        # Create training.txt file
        
        # Create testing.txt file
        
        # Create dataset_name.data file

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = ObjectDetectionDialog()
            self.dlg.setWindowFlags(Qt.WindowShadeButtonHint)
            self.filename = ""
        else: 
            self.dlg.lineEditInputImage.setText("")
            self.dlg.lineEditDatasetName.setText("") 
            self.dlg.pushButtonCreateClippings.setText("Create Clippings")
            self.dlg.pushButtonCreateClippings.setEnabled(True)
            self.dlg.pushButtonAnnotate.setEnabled(False)
            self.dlg.pushButtonPreparation.setEnabled(False)
            progressBarClip.setValue(0)
            self.dlg.horizontalSliderSplit.setValue(100)
            
        self.dlg.horizontalSliderSplit.setValue(100)
        self.display_slider_value()
        self.dlg.show()
           
        self.dlg.toolButtonData.clicked.connect(self.select_training_image)
        self.dlg.pushButtonCreateClippings.clicked.connect(self.clip_image)
        self.dlg.pushButtonAnnotate.clicked.connect(self.open_annotation_dialog)
        self.dlg.pushButtonPreparation.clicked.connect(self.prepare_dataset_for_training)
        
        self.dlg.horizontalSliderSplit.valueChanged.connect(self.display_slider_value)
        
        self.dlg.pushButtonAnnotate.setEnabled(False)
        self.dlg.pushButtonPreparation.setEnabled(False)
        
        
            
            
    
        
        
        
        
            