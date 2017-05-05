#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: test di prova
:field Topology: 54
:field Dependency:
:field Lab: SVT
:field TPS: CONN__5-0-0-0 
:field RunSections: 10000
:field Author: ippolf

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import *
import time


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
        self.start_tps_block(NE1.id,"CONN", "5-0-0-0")
        print('ciao')
        self.stop_tps_block(NE1.id,"CONN", "5-0-0-0")


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


#Please don't change the code below#
if __name__ == "__main__":
    #initializing the Test object instance, do not remove
    CTEST = Test(__file__)

    #initializing all local variable and constants used by Test object
    NE1 = Eqpt1850TSS320('NE1', CTEST.kenvironment)
    NE1_S1=NE1.get_preset("S1")
    
    
    TAG_RATE="STM1_MRSOE"
    
    CTEST.add_eqpt(NE1)


    # Run Test main flow
    # Please don't touch this code
    CTEST.run()
