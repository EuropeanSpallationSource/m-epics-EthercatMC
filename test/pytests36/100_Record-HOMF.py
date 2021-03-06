#!/usr/bin/env python

#
# Test homing via EPICS motorRecord
#

import datetime
import unittest
import os
import sys
from AxisMr import AxisMr
from AxisCom import AxisCom

filnam = "100xx.py"

###


class Test(unittest.TestCase):
    url_string = os.getenv("TESTEDMOTORAXIS")
    print(
        f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {filnam} url_string={url_string}"
    )

    axisCom = AxisCom(url_string, log_debug=True)
    axisMr = AxisMr(axisCom)

    # Home the motor
    def test_TC_100(self):
        axisCom = self.axisCom
        axisMr = self.axisMr
        tc_no = "100"
        print(
            f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {filnam} {tc_no} Home the motor"
        )

        # Get values to be able calculate a timeout
        range_postion = axisCom.get(".HLM") - axisCom.get(".LLM")
        hvel = axisCom.get(".HVEL")
        accl = axisCom.get(".ACCL")
        msta = int(axisCom.get(".MSTA"))

        self.axisMr.setCNENandWait(tc_no, 1)
        # Calculate the timeout, based on the driving range
        if range_postion > 0 and hvel > 0:
            time_to_wait = 1 + 2 * range_postion / hvel + 2 * accl
        else:
            time_to_wait = 180

        # If we are sitting on the High limit switch, use HOMR
        if msta & axisMr.MSTA_BIT_PLUS_LS:
            axisCom.put(".HOMR", 1)
        else:
            axisCom.put(".HOMF", 1)
        axisMr.waitForStartAndDone(tc_no, time_to_wait)

        msta = int(axisCom.get(".MSTA"))
        self.assertNotEqual(
            0, msta & axisMr.MSTA_BIT_HOMED, "MSTA.homed (Axis has been homed)"
        )
