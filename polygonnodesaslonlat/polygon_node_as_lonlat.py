# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PolygonNodesAsLonLat
                                 A QGIS plugin
 Show polygon nodes as longitue and lantiude
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-05-03
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Paweł Strzelewicz
        email                : @
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
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMessageBox, QWidget
from qgis.core import *

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .polygon_node_as_lonlat_dialog import PolygonNodesAsLonLatDialog
import os.path
import datetime
from .aviation_gis_toolkit.angle import *



class PolygonNodesAsLonLat:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.lyr_name = None
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PolygonNodesAsLonLat_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PolygonNodesAsLonLatDialog()
        self.dlg.pushButtonShowNodeCoord.clicked.connect(self.show_node_coordinates)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&PolygonNodesAsLonLat')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PolygonNodesAsLonLat')
        self.toolbar.setObjectName(u'PolygonNodesAsLonLat')

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
        return QCoreApplication.translate('PolygonNodesAsLonLat', message)


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
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/polygon_node_as_lonlat/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'PolygonNodesAsLonLat'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&PolygonNodesAsLonLat'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    @staticmethod
    def gen_name():
        """ Generates name for memory layer base on timestamp in format:
        YYYYY_MMM_DDD_HHMM.ssssss, e.g.: 2020_Apr_Wed_1622.000001. """
        timestamp = datetime.datetime.now()
        return timestamp.strftime('%Y_%b_%a_%H%M.%f')

    @staticmethod
    def create_memory_lyr(lyr_name):
        """ Create temporary 'memory' layer to store results of calculations.
        :param lyr_name: string, layer name
        :return mem_lyr: created memory layer
        """
        mem_lyr = QgsVectorLayer('Point?crs=epsg:4326', lyr_name, 'memory')
        prov = mem_lyr.dataProvider()
        mem_lyr.startEditing()
        prov.addAttributes([QgsField("COORD_DMS", QVariant.String)])
        mem_lyr.commitChanges()
        QgsProject.instance().addMapLayer(mem_lyr)

        mem_lyr.setLabelsEnabled(True)
        mem_lyr_settings = QgsPalLayerSettings()
        mem_lyr_settings.isExpression = True
        mem_lyr_settings.fieldName = "COORD_DMS"
        lyr_set = QgsVectorLayerSimpleLabeling(mem_lyr_settings)
        mem_lyr.setLabelsEnabled(True)
        mem_lyr.setLabeling(lyr_set)
        mem_lyr.triggerRepaint()

        return mem_lyr

    def add_node(self, lyr, point, attributes):
        lyr = self.iface.activeLayer()
        prov = lyr.dataProvider()
        feat = QgsFeature()
        feat.setGeometry(point)
        feat.setAttributes(attributes)
        prov.addFeatures([feat])

    def show_node_coordinates(self):
        """ Creates point layer for nodes for chosen polygon and shows label with coordinates. """
        canvas = self.iface.mapCanvas()
        clayer = canvas.currentLayer()
        if clayer is None:
            QMessageBox.critical(QWidget(), "Message", "No active layer.")
        else:
            angle_tool = Angle()
            if self.lyr_name:
                lyr = QgsProject.instance().mapLayersByName(self.lyr_name)[0]
                self.iface.setActiveLayer(lyr)
            else:
                self.lyr_name = self.gen_name()
                lyr = self.create_memory_lyr(self.lyr_name)

            # Geometry must be Polygon
            if clayer.wkbType() == QgsWkbTypes.Polygon:
                if clayer.selectedFeatureCount() != 1:
                    QMessageBox.critical(QWidget(), "Message", "Select one polygon.")
            elif clayer.wkbType() == QgsWkbTypes.MultiPolygon:
                if clayer.selectedFeatureCount() != 1:
                    QMessageBox.critical(QWidget(), "Message", "{} polygons selected.\n"
                                                               "Select one polygon.".format(clayer.selectedFeatureCount()))

                else:
                    lyr.startEditing()
                    selected_polygon = clayer.selectedFeatures()[0]
                    geom = selected_polygon.geometry()
                    for vertex in geom.vertices():
                        # Convert DD to DMS format
                        lon_dms = angle_tool.dd_to_dms_string(vertex.x(), AT_LON, ang_format=AF_DMSH_SEP_SYMBOLS)
                        lat_dms = angle_tool.dd_to_dms_string(vertex.y(), AT_LAT, ang_format=AF_DMSH_SEP_SYMBOLS)
                        coord = '{} {}'.format(lon_dms, lat_dms)
                        self.add_node(lyr, vertex, [coord])
                    lyr.commitChanges()
                    geom_wkt = selected_polygon.geometry().asWkt()
                    self.dlg.plainTextEdit.appendPlainText(geom_wkt)
        # Set active layer previously selected polygon layer
        self.iface.setActiveLayer(clayer)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
