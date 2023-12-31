# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutoSolveSharpAngle
                                 A QGIS plugin
 Need to create smooth data wherever there is Notches. Tolerance- Restriction basis
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-03-28
        copyright            : (C) 2023 by Genesys
        email                : pramoddb@email.igenesys.com; 
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
    """Load AutoSolveSharpAngle class from file AutoSolveSharpAngle.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Auto_Solve_Sharp_Angle import AutoSolveSharpAngle
    return AutoSolveSharpAngle(iface)
