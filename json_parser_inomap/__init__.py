# -*- coding: utf-8 -*-
"""
/***************************************************************************
 JsonParserInomap
                                 A QGIS plugin
 convert json into postgres
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-10-11
        copyright            : (C) 2023 by genesys
        email                : pramoddb@email.igenesys.com
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
    """Load JsonParserInomap class from file JsonParserInomap.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .json_parser_inomap import JsonParserInomap
    return JsonParserInomap(iface)
