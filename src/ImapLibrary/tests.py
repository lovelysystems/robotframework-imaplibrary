##############################################################################
#
# Copyright (c) 2006-2012 Lovely Systems AG. All Rights Reserved.
#
# This software is subject to the provisions of the Lovely Visible Source
# License, Version 1.0 (LVSL).  A copy of the LVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
"""
__docformat__ = 'restructuredtext'

import unittest
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite, DocTestSuite

def uSuite(testfile, level=None):
    suite = doctest.DocFileSuite(
                testfile,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    if level is not None:
        suite.level = level
    return suite


def test_suite():
    s = unittest.TestSuite((
        uSuite('mail.txt', level=2),
        ))
    return s

