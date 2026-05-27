# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'christoph.ratke@agdoit.com'
__date__ = '2026-01-04'
__copyright__ = 'Copyright 2026, Christoph Ratke'

import unittest

from qgis.PyQt.QtWidgets import QDialog

from ofe_planning_dialog import OFEPlanningDialog

from utilities import get_qgis_app
QGIS_APP = get_qgis_app()


class OFEPlanningDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = OFEPlanningDialog(None, None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_cancel(self):
        """Test we can close the dialog."""
        self.dialog.close()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)

if __name__ == "__main__":
    suite = unittest.makeSuite(OFEPlanningDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

