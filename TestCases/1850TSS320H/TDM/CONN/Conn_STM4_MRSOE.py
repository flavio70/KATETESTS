#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: Test to verify all the Cross Connection checks in case of STM4 on MRSOE board
:field Topology: 44
:field Dependency:
:field Lab: 
:field TPS: CONN__5-3-3-38
:field TPS: CONN__5-3-4-38
:field TPS: CONN__5-3-26-38
:field TPS: CONN__5-3-28-38
:field TPS: CONN__5-3-6-38
:field TPS: CONN__5-3-3-40
:field TPS: CONN__5-3-28-40
:field TPS: CONN__5-3-26-40
:field TPS: CONN__5-3-4-40
:field RunSections: 11101
:field Author: luigir

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.instrumentONT     import InstrumentONT
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import *
from kateUsrLibs.luigir.conn_lib import *

import time
import sys

from email.utils import formatdate
from audioop import ratecv
from asyncio.tasks import sleep
from xdist.slavemanage import HostRSync
from inspect import currentframe


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
        NE1.tl1.event_collection_start()
        NE1.tl1.do("ACT-USER::admin:::Alcatel1;")
        print(NE1.tl1.get_last_outcome())
        
        SID = formatDate()
        cmd = "SET-SID:::::\"{}\";".format(SID)
        NE1.tl1.do(cmd)
        print(NE1.tl1.get_last_outcome())
        
        setup_result = setup_ONT_Conn(ONT1, ONT2, ONT1_P1, ONT2_P1, "STM4")
        if(setup_result == False):
            print("***** ONT5xx Setup ERROR")


    def test_setup(self):
        '''
        test Setup Section implementation
        insert general SetUp code for your test below
        '''
        slot = NE1_S1
        slot = slot[0:6]
        tl1_cmd = "RTRV-EQPT::MDL-" + slot + ";"
        res_tl1_cmd = NE1.tl1.do(tl1_cmd)
        if(res_tl1_cmd == True):
            tl1_string_out = NE1.tl1.get_last_outcome()
            tl1_msg_out = TL1message(tl1_string_out)
            aid_list = tl1_msg_out.get_cmd_aid_list()
            len = tl1_msg_out.get_cmd_response_size()
            aid = aid_list[0]
            k = aid.find("-")
            board = aid[0:k]
            board_type = "@@@@@  Board used:  [{}]".format(board)
            print(board_type)


    def test_body(self):
        '''
        test Body Section implementation
        insert Main body code for your test below
        '''       
        # Test CONN 2W - SPLIT - JOIN ; STM4, VC4, AU4
        self.start_tps_block(NE1.id,"CONN", "5-3-3-38")
        self.start_tps_block(NE1.id,"CONN", "5-3-28-38")
        self.start_tps_block(NE1.id,"CONN", "5-3-26-38")
        test_result = verify_conn_2w_split_join(self, NE1, ONT1, ONT2, ONT1_P1, ONT2_P1, "STM4", "VC4", "AU4", NE1_S1, NE1_S2)
        if(test_result == True):
            self.add_success(NE1, "CONN 5-3-3-38, 5-3-28-38, 5-3-26-38", "0", "Verify: CONN 2Way, SPLIT, JOIN - STM4, VC4, AU4 - MRSOE - TPS 5.3.3.38, 5-3-28-38, 5-3-26-38; PASSED")
            print("Verify: CONN 2Way, SPLIT, JOIN - STM4, VC4, AU4 - TPS 5.3.3.38, 5.3.28.38, 5.3.26.38; PASSED")
        else:
            self.add_failure(NE1, "CONN 5-3-3-37, 5-3-28-38, 5-3-26-38", "0", "Verify: CONN 2Way, SPLIT, JOIN - STM4, VC4, AU4 - MRSOE", "TPS 5-3-3-38, 5-3-28-38, 5-3-26-38; FAILED")
        print("Verify: CONN 2Way, SPLIT, JOIN - STM4, VC4, AU4 - TPS 5.3.3.38, 5.3.28.38, 5.3.26.38; FAILED")
        self.stop_tps_block(NE1.id,"CONN", "5-3-3-38")
        self.stop_tps_block(NE1.id,"CONN", "5-3-28-38")
        self.stop_tps_block(NE1.id,"CONN", "5-3-26-38")
        
        # Test CONN 1W; STM4, VC4, AU4
        self.start_tps_block(NE1.id,"CONN", "5-3-4-38")
        test_result = verify_conn_1w_tps534x(self, NE1, ONT1, ONT2, ONT1_P1, ONT2_P1, "STM4", "VC4", "AU4", NE1_S1, NE1_S2)
        if(test_result == True):
            self.add_success(NE1, "CONN 5-3-4-38", "0", "Verify: CONN 1Way - STM4, VC4, AU4 - MRSOE - TPS 5.3.4.38; PASSED")
            print("Verify: CONN 1Way - STM4, VC4, AU4 - TPS 5.3.4.38; PASSED")
        else:
            self.add_failure(NE1, "CONN 5-3-4-38", "0", "Verify: CONN 1Way - STM4, VC4, AU4 - MRSOE", "TPS 5.3.4.38 FAILED")
            print("Verify: CONN 1Way - STM4, VC4, AU4 - TPS 5.3.4.38; FAILED")
        self.stop_tps_block(NE1.id,"CONN", "5-3-4-38")
        
        # Test CONN Broadcast; STM4, VC4, AU4
        self.start_tps_block(NE1.id,"CONN", "5-3-6-38")
        test_result = verify_conn_br_tps536x(self, NE1, ONT1, ONT2, ONT1_P1, ONT2_P1, "STM4", "VC4", "AU4", NE1_S1, NE1_S2)
        if(test_result == True):
            self.add_success(NE1, "CONN 5-3-6-38", "0", "Verify: CONN Broadcast - STM4, VC4, AU4 - MRSOE - TPS 5.3.6.38; PASSED")
            print("Verify: CONN Broadcast - STM4, VC4, AU4 - TPS 5.3.6.38; PASSED")
        else:
            self.add_failure(NE1, "CONN 5-3-6-38", "0", "Verify: CONN Broadcast - STM4, VC4, AU4 - MRSOE", "TPS 5.3.4.38; FAILED")
            print("Verify: CONN Broadcast- STM4, VC4, AU4 - TPS 5.3.6.38; FAILED")
        self.stop_tps_block(NE1.id,"CONN", "5-3-6-38")
        
        # Test CONN 2W - SPLIT - JOIN; STM4, VC44C, AU44C
        self.start_tps_block(NE1.id,"CONN", "5-3-3-40")
        self.start_tps_block(NE1.id,"CONN", "5-3-28-40")
        self.start_tps_block(NE1.id,"CONN", "5-3-26-40")
        test_result = verify_conn_2w_split_join(self, NE1, ONT1, ONT2, ONT1_P1, ONT2_P1, "STM4", "VC44C", "AU44C", NE1_S1, NE1_S2)
        if(test_result == True):
            self.add_success(NE1, "CONN 5-3-3-40, 5-3-28-40, 5-3-26-40", "0", "Verify: CONN 2Way, SPLIT, JOIN - STM4, VC44C, AU44C -MRSOE - TPS 5.3.3.40, 5-3-28-40, 5-3-26-40; PASSED")
            print("Verify: CONN 2Way, SPLIT, JOIN - STM4, VC44C, AU44C - TPS 5.3.3.40, 5.3.28.40, 5.3.26.40; PASSED")
        else:
            self.add_failure(NE1, "CONN 5-3-3-40, 5-3-28-40, 5-3-26-40", "0", "Verify: CONN 2Way, SPLIT, JOIN - STM4, VC44C, AU44C - MRSOE", "TPS 5-3-3-40, 5-3-28-40, 5-3-26-40; FAILED")
            print("Verify: CONN 2Way, SPLIT, JOIN - STM4, VC44C, AU44C - TPS 5.3.3.40, 5.3.28.40, 5.3.26.40; FAILED")
        self.stop_tps_block(NE1.id,"CONN", "5-3-3-40")
        self.stop_tps_block(NE1.id,"CONN", "5-3-28-40")
        self.stop_tps_block(NE1.id,"CONN", "5-3-26-40")
        
        # Test CONN 1W; STM4, VC44C, AU44C
        self.start_tps_block(NE1.id, "CONN", "5-3-4-40")
        test_result = verify_conn_1w_tps534x(self, NE1, ONT1, ONT2, ONT1_P1, ONT2_P1, "STM4", "VC44C", "AU44C", NE1_S1, NE1_S2)
        if(test_result == True):
            self.add_success(NE1, "CONN 5-3-4-40", "0", "Verify: CONN 1Way - STM4, VC44C, AU44C - MRSOE - TPS 5.3.4.40; PASSED")
            print("Verify: CONN 1Way - STM4, VC44C, AU44C - TPS 5.3.4.40; PASSED")
        else:
            self.add_failure(NE1, "CONN 5-3-4-40", "0", "Verify: CONN 1Way - STM4, VC44C, AU44C - MRSOE", "TPS 5.3.4.40; FAILED")
            print("Verify: CONN 1Way - STM4, VC44C, AU44C - TPS 5.3.4.40; FAILED")
        self.stop_tps_block(NE1.id, "CONN", "5-3-4-40")


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
        NE1.tl1.event_collection_stop()
        NE1.tl1.do("CANC-USER;")
        ONT1.deinit_instrument(ONT1_P1)
        ONT2.deinit_instrument(ONT2_P1)



#Please don't change the code below#
if __name__ == "__main__":
    #initializing the Test object instance, do not remove
    CTEST = Test(__file__)

    #initializing all local variable and constants used by Test object
    NE1 = Eqpt1850TSS320('NE1', CTEST.kenvironment)
    NE1_S1=NE1.get_preset("S1")
    NE1_S2=NE1.get_preset("S2")
   
    ONT1=InstrumentONT('ONT1', CTEST.kenvironment)
    ONT1_P1="P1"

    ONT2=InstrumentONT('ONT2', CTEST.kenvironment)
    ONT2_P1="P1"
    
    TAG_RATE="STM4_MRSOE"
    
    CTEST.add_eqpt(NE1)
    CTEST.add_eqpt(ONT1)
    CTEST.add_eqpt(ONT2)

    # Run Test main flow
    # Please don't touch this code
    CTEST.run()
