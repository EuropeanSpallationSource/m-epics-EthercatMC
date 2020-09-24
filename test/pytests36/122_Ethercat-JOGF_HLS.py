#!/usr/bin/env python
#

import unittest
import os
import sys
from AxisMr import AxisMr
from AxisCom import AxisCom

###


class Test(unittest.TestCase):
    url_string = os.getenv("TESTEDMOTORAXIS")
    print(f"url_string={url_string}")

    axisCom = AxisCom(url_string, log_debug=True)
    axisMr = AxisMr(axisCom)

    # self.axisCom.put('-DbgStrToLOG', "Start " + os.path.basename(__file__)[0:20])

    hlm = axisCom.get(".HLM")
    llm = axisCom.get(".LLM")
    jvel = axisCom.get(".JVEL")

    margin = 1.1
    # motorRecord stops jogging 1 second before reaching HLM
    jog_start_pos = hlm - jvel - margin

    msta = int(axisCom.get(".MSTA"))
    velo = axisCom.get(".VELO")
    accl = axisCom.get(".ACCL")

    print(f"llm={llm:f} hlm={hlm:f} jog_start_pos={jog_start_pos:f}")

    # Make sure that motor is homed
    def test_TC_1221(self):
        tc_no = "1221"
        if not (self.msta & self.axisMr.MSTA_BIT_HOMED):
            self.axisMr.powerOnHomeAxis(tc_no)
            self.msta = int(self.axisCom.get(".MSTA"))
            self.assertNotEqual(
                0,
                self.msta & self.axisMr.MSTA_BIT_HOMED,
                "MSTA.homed (Axis is not homed)",
            )

    # high limit switch
    def test_TC_1222(self):
        if self.msta & self.axisMr.MSTA_BIT_HOMED:
            tc_no = "1222"
            print(f"{tc_no}")
            old_high_limit = self.axisCom.get(".HLM")
            old_low_limit = self.axisCom.get(".LLM")
            rdbd = self.axisCom.get(".RDBD")
            self.axisCom.put(".STOP", 1)
            # Go away from limit switch
            self.axisMr.moveWait(tc_no, self.jog_start_pos)
            destination = self.axisCom.get(".HLM")
            rbv = self.axisCom.get(".RBV")
            jvel = self.axisCom.get(".JVEL")
            timeout = self.axisMr.calcTimeOut(destination, jvel) * 2

            self.axisMr.setSoftLimitsOff(tc_no)

            self.axisMr.jogDirection(tc_no, 1)
            # Get values, check them later
            lvio = int(self.axisCom.get(".LVIO"))
            mstaE = int(self.axisCom.get(".MSTA"))
            # Go away from limit switch
            self.axisMr.moveWait(tc_no, old_high_limit - rdbd)
            print(f"{tc_no} msta={mstaE:x} lvio={int(lvio)}")

            self.axisMr.setSoftLimitsOn(old_low_limit, old_high_limit)

            self.assertEqual(
                0,
                mstaE & self.axisMr.MSTA_BIT_PROBLEM,
                "MSTA.Problem should not be set",
            )
            self.assertEqual(
                0, mstaE & self.axisMr.MSTA_BIT_MINUS_LS, "LLS should not be active"
            )
            self.assertNotEqual(
                0, mstaE & self.axisMr.MSTA_BIT_PLUS_LS, "HLS should be active"
            )
