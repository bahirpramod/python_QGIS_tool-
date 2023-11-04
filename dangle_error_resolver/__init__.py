# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DangleErrorResolver
                                 A QGIS plugin
 This plugin is used for dangle error resolver
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-12-28
        copyright            : (C) 2022 by Genesys
        email                : nurjahansh@email.igenesys.com
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
    """Load DangleErrorResolver class from file DangleErrorResolver.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .dangle_error_resolver import DangleErrorResolver
    return DangleErrorResolver(iface)