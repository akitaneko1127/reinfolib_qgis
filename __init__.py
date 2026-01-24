# -*- coding: utf-8 -*-
"""
ReinfoLib for QGIS - Real Estate Information Library Plugin

This plugin provides access to Japan's Real Estate Information Library API
provided by the Ministry of Land, Infrastructure, Transport and Tourism (MLIT).

Copyright (C) 2024 Link Field
Email: info@linkfield.co.jp

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""


def classFactory(iface):
    """Load ReinfoLibPlugin class from file reinfolib_plugin.

    Args:
        iface: A QGIS interface instance.

    Returns:
        ReinfoLibPlugin: The plugin instance.
    """
    from .reinfolib_plugin import ReinfoLibPlugin
    return ReinfoLibPlugin(iface)
