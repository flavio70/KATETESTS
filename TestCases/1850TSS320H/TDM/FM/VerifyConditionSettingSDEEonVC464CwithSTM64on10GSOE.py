#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description:To verify that, for each AUn path facility, SDEE is set for when it is used in cross-connection
:field Topology: 63
:field Dependency:NA
:field Lab: SVT
:field TPS: FM__5-2-70-32
:field RunSections: 10101
:field Author: tosima

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import *
import time
import math
from inspect import currentframe
from kateUsrLibs.tosima.FmLib import *

class Test(TestCase):
    '''
    this class implements the current test case behaviour by using
    the five methods (runSections):
        DUTSetUp: used for DUT configuration
        testSetup: used for Test Configuration
        testBody: used for main test pourposes
        testCleanUp: used to finalize test and clear the configuration
        DUTCleanUp: used for DUT cleanUp

        all these runSections can be either run or skipped using inline optional input parameters

        --DUTSet     Run the DUTs SetUp
        --testSet    Run the Test SetUp
        --testBody   Run the Test Main Body
        --testClean  Run the Test Clean Up
        --DUTClean   Run the DUTs Clean Up

        all runSections will be executed ifrunning Test without input parameters
    '''

    def dut_setup(self):
        '''
        DUT Setup section Implementation
        insert DUT SetUp code for your test below
        '''
        NE1.tl1.do("ACT-USER::admin:::Alcatel1;")

    def test_setup(self):
        '''
        test Setup Section implementation
        insert general SetUp code for your test below
        '''


    def test_body(self):
        '''
        test Body Section implementation
        insert Main body code for your test below
        '''
        global NE1_S1
                
        self.start_tps_block(NE1.id,"FM", "5-2-70-32")

        zq_temp  = TAG_RATE.split("_")
        zq_rate  = zq_temp[0]
        zq_board = zq_temp[1]
        
        print("\n*******************************************************************")
        print("\tSTRUCTURE {} TO 1xAU4{}C".format(zq_rate, zq_rate.replace("STM","")))
        print("*******************************************************************")
        #ED-STM4::STM4-1-1-6-3::::HOSTRUCT=1xAU44C
        #
        QS_1300_Change_STMn_Structure(self, NE1, zq_rate, NE1_S1, "1xAU464C")

        print("\n*******************************************************************")
        print("\tCHECK SECONDARY STATE IS NOT SDEE")
        print("*******************************************************************")
        # VERIFY SECONDARY STATE DOES NOT CONTAINS SDEE
        #
        QS_1000_Check_AU4_SST(self, NE1, zq_rate, NE1_S1, 1, "SDEE", False, "64C")
        
        print("\n*******************************************************************")
        print("\tCREATE VC4 CROSS-CONNECTIONS")
        print("*******************************************************************")
        # CREATE VC4 CROSS-CONNECTION
        # ENT-CRS-VC4:[TID]:FROM,TO:[CTAG]::[CCT]:[CKTID=]
        #
        
        QS_1100_Create_AU4_XC(self, NE1, zq_rate, NE1_S1, 1, 1, "1WAY", "64C")
        
        print("\n*******************************************************************")
        print("\tCHECK SECONDARY STATE IS SDEE")
        print("*******************************************************************")
        # VERIFY SECONDARY STATE CONTAINS SDEE
        #

        QS_1000_Check_AU4_SST(self, NE1, zq_rate, NE1_S1, 1, "SDEE", True, "64C")
        
        print("\n*******************************************************************")
        print("\tDELETE VC4 CROSS-CONNECTIONS")
        print("*******************************************************************")
        # DELETE VC4 CROSS-CONNECTION
        # DLT-CRS-VC4:[TID]:FROM,TO:[CTAG]::[CCT]:[CKTID=]
        #

        QS_1200_Delete_AU4_XC(self, NE1, zq_rate, NE1_S1, 1, 1, "1WAY", "64C")

        print("\n*******************************************************************")
        print("\tCHECK SECONDARY STATE IS NOT SDEE")
        print("*******************************************************************")
        # VERIFY SECONDARY STATE DOES NOT CONTAINS SDEE
        #

        QS_1000_Check_AU4_SST(self, NE1, zq_rate, NE1_S1, 1, "SDEE", False, "64C")


        print("\n*******************************************************************")
        print("\tSTRUCTURE {} BACK TO {}xAU4".format(zq_rate, zq_rate.replace("STM","")))
        print("*******************************************************************")
        #ED-STM4::STM4-1-1-6-3::::HOSTRUCT=1xAU44C
        #

        QS_1300_Change_STMn_Structure(self, NE1, zq_rate, NE1_S1, "64xAU4")

        
        self.stop_tps_block(NE1.id,"FM", "5-2-70-32")
 

    def test_cleanup(self):
        '''
        test Cleanup Section implementation
        insert CleanUp code for your test below
        '''


    def dut_cleanup(self):
        '''
        DUT CleanUp Section implementation
        insert DUT CleanUp code for your test below
        '''
        print('@DUT CleanUP')
        NE1.tl1.do("CANC-USER;")
        NE1.clean_up()


#Please don't change the code below#
if __name__ == "__main__":
    #initializing the Test object instance, do not remove
    CTEST = Test(__file__)

    #initializing all local variable and constants used by Test object
    NE1 = Eqpt1850TSS320('NE1', CTEST.kenvironment)
    NE1_S1=NE1.get_preset("S1")
    
    
    TAG_RATE="STM64_1P10GSOE"
    
    CTEST.add_eqpt(NE1)


    # Run Test main flow
    # Please don't touch this code
    CTEST.run()
