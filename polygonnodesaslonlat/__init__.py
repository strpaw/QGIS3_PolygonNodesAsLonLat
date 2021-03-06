# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PolygonNodesAsLonLat
                                 A QGIS plugin
 Show polygon nodes as longitue and lantiude
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-05-03
        copyright            : (C) 2020 by Paweł Strzelewicz
        email                : @
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PolygonNodesAsLonLat class from file PolygonNodesAsLonLat.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .polygon_node_as_lonlat import PolygonNodesAsLonLat
    return PolygonNodesAsLonLat(iface)
