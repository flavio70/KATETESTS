#!/usr/bin/env python
'''
TestCase template for K@TE test developers

[DESCRIPTION]
    Put your test decription here
[DESCRIPTION]
[TOPOLOGY] 1 [TOPOLOGY]
[DEPENDENCY]
    Insert Test dependencies
[DEPENDENCY]
[LAB] Insert the lab referneces i.e. SW,SVT [LAB]
[TPS]
    insert here the Test mapping
[TPS]
[RUNSECTIONS]
    Insert here the sections developed in this test i.e.
    DUTSet,testSet,testBody,testClean,DutClean,all
[RUNSECTIONS]
[AUTHOR] ippolf [AUTHOR]

'''

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.instrumentONT     import InstrumentONT
#from katelibs.instrumentIXIA     import InstrumentIXIA
#from katelibs.instrumentSPIRENT  import InstrumentSPIRENT
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1 import TL1message
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

        all runSections will be executed if run Test without input parameters
    '''


    def dut_setup(self):
        '''
        DUT Setup section Implementation
        insert DUT SetUp code for your test below
        '''
        #NE1.tl1.do("ACT-USER::admin:::Alcatel1;")

        #NE1.tl1.do("CANC-USER;")

        NE1.tl1.do("ACT-USER::admin:::Alcatel1;")



    def test_setup(self):
        '''
        test Setup Section implementation
        insert general SetUp code for your test below
        '''
        #self.kenvironment.krepo.start_tps_block("EM", "1-2-3")

        ONT5xx.init_instrument("P1")
        ONT5xx.init_instrument("P2")


    def test_body(self):
        '''
        test Body Section implementation
        insert Main body code for your test below
        Try this test with the following command:
        ./Test1NE_Instrument_Ont506_only.py --testSet    --testBody  --testClean    
        '''
        '''
        print("\n\n\n\n\nTESTING ONT5xx SECTION START *************************************")
        #input("press enter to continue...\n")
        callResult = ONT5xx.get_set_measurement_time("P1", 1)
        print("ONT5xx.get_set_measurement_time result: [{}]".format(callResult))
        callResult = ONT5xx.start_measurement("P1")
        print("ONT5xx.start_measurement: [{}]".format(callResult))
        callResult = ONT5xx.get_set_rx_bit_rate("P1")
        print("ONT5xx.get_set_rx_bit_rate result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_rx_bit_rate("P1","STM1")
        print("ONT5xx.get_set_rx_bit_rate result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_clock_reference_source("P1")
        print("ONT5xx.get_set_clock_reference_source result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_clock_reference_source("P1","RX")
        print("ONT5xx.get_set_clock_reference_source result: [{}]".format(callResult))
        callResult = ONT5xx.retrieve_optical_alarms("P1")
        print("ONT5xx.retrieve_optical_alarms result: [{}]".format(callResult))
        #input("\n\npress enter to continue...\n")
        callResult = ONT5xx.retrieve_optical_alarms("P1")
        print("ONT5xx.retrieve_optical_alarms result: [{}]".format(callResult))
        #input("\n\npress enter to continue...\n")
        callResult = ONT5xx.retrieve_optical_alarms("P1")
        print("ONT5xx.retrieve_optical_alarms result: [{}]".format(callResult))
        #input("\n\npress enter to continue...\n")
        callResult = ONT5xx.retrieve_optical_alarms("P1")
        print("ONT5xx.retrieve_optical_alarms result: [{}]".format(callResult))
        #input("\n\npress enter to continue...\n")
        callResult = ONT5xx.retrieve_sdh_alarms("P1")
        print("ONT5xx.retrieve_optical_alarms result: [{}]".format(callResult))
        #input("\n\npress enter to continue...\n")
        #usercommand=input("\n\nInsert RAW command for check\n")
        #callResult = ONT5xx.cli_user_debug_command(usercommand,"P1")
        #print("ONT5xx.cli_user_debug_command result: [{}]".format(callResult))
        callResult = ONT5xx.retrieve_ho_alarms("P1")
        print("ONT5xx.retrieve_ho_alarms result: [{}]".format(callResult))
        callResult = ONT5xx.retrieve_lo_alarms("P1")
        print("ONT5xx.retrieve_lo_alarms result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_wavelenght("P1","W1310")
        print("ONT5xx.get_set_wavelenght result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_wavelenght("P1")
        print("ONT5xx.get_set_wavelenght result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_laser_status("P1","ON")
        print("ONT5xx.get_set_laser_status result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_laser_status("P1")
        print("ONT5xx.get_set_laser_status result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_rx_bit_rate("P1","STM16")
        print("ONT5xx.get_set_rx_bit_rate result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_tx_bit_rate("P1","STM16")
        print("ONT5xx.get_set_tx_bit_rate result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_rx_measure_channel("P1","1")
        print("ONT5xx.get_set_rx_measure_channel result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_rx_channel_mapping_size("P1","VC12")
        print("ONT5xx.get_set_rx_channel_mapping_size result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_rx_lo_measure_channel("P1","4")
        print("ONT5xx.get_set_rx_lo_measure_channel result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_alarm_insertion_type("P1","LOF")
        print("ONT5xx.get_set_alarm_insertion_type result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_alarmed_frames_number("P1","222")
        print("ONT5xx.get_set_alarmed_frames_number result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_not_alarmed_frames_number("P1","444")
        print("ONT5xx.get_set_not_alarmed_frames_number result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_alarm_activation("P1")
        print("ONT5xx.get_set_alarm_activation result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_alarm_activation("P1","OFF")
        print("ONT5xx.get_set_alarm_activation result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_alarm_insertion_mode("P1","BURST_CONT")
        print("ONT5xx.get_set_alarm_insertion_mode result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_alarm_insertion_type("P1")
        print("ONT5xx.get_set_alarm_insertion_type result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_num_errored_burst_frames("P1","7")
        print("ONT5xx.get_set_num_errored_burst_frames result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_num_not_errored_burst_frames("P1")
        print("ONT5xx.get_set_num_not_errored_burst_frames result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_num_not_errored_burst_frames("P1","300")
        print("ONT5xx.get_set_num_not_errored_burst_frames result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_error_activation("P1","ON")
        print("ONT5xx.get_set_error_activation result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_error_insertion_mode("P1","ONCE")
        print("ONT5xx.get_set_error_insertion_mode result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_error_insertion_type("P1","FAS")
        print("ONT5xx.get_set_error_insertion_type result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_error_insertion_type("P1","RSBIP")
        print("ONT5xx.get_set_error_insertion_type result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_tx_bit_rate("P1","STM16")
        print("ONT5xx.get_set_tx_bit_rate result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_tx_measure_channel("P1")
        print("ONT5xx.get_set_tx_measure_channel result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_tx_measure_channel("P1","7")
        print("ONT5xx.get_set_tx_measure_channel result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_rx_channel_mapping_size("P1","VC12")
        print("ONT5xx.get_set_rx_channel_mapping_size result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_tx_channel_mapping_size("P1","VC12")
        print("ONT5xx.get_set_tx_channel_mapping_size result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_rx_lo_measure_channel("P1","4")
        print("ONT5xx.get_set_rx_lo_measure_channel result: [{}]".format(callResult))
        callResult = ONT5xx.get_set_tx_lo_measure_channel("P1","5")
        print("ONT5xx.get_set_tx_lo_measure_channel result: [{}]".format(callResult))
        callResult = ONT5xx.retrieve_ho_alarms("P1")
        print("ONT5xx.retrieve_ho_alarms result: [{}]".format(callResult))
        callResult = ONT5xx.retrieve_lo_alarms("P1")
        print("ONT5xx.retrieve_lo_alarms result: [{}]".format(callResult))
        print("\n\n\n\n\nTESTING ONT5xx SECTION STOP **************************************")
        '''
        print("\n**************** START ****************")
        S1=NE1.get_preset("S1")
        S2=NE1.get_preset("S2")
        NE1.tl1.do("ED-AU4::STM1AU4-{}-1::::POM=Y,EGPOM=Y;".format(S1))
        NE1.tl1.do("ED-AU4::STM1AU4-{}-1::::POM=Y,EGPOM=Y;".format(S2))
        #time.sleep(5)
        
        ONT5xx.get_set_tx_bit_rate("P1", "STM1")
        ONT5xx.get_set_tx_bit_rate("P2", "STM1")
        
        ONT5xx.get_set_rx_channel_mapping_size("P1", "VC4")
        ONT5xx.get_set_rx_channel_mapping_size("P2", "VC4")
        
        ONT5xx.get_set_tx_channel_mapping_size("P1", "VC4")
        ONT5xx.get_set_tx_channel_mapping_size("P2", "VC4")

        ONT5xx.get_set_laser_status("P1", "ON")
        ONT5xx.get_set_laser_status("P2", "ON")

        zq_tl1_res=NE1.tl1.do("RTRV-COND-VC4::STM1AU4-{}-1:::UNEQ-P;".format(S1))
        print("zq_tl1_res = {}".format(zq_tl1_res))

        zq_msg=NE1.tl1.get_last_outcome()
        print("zq_msg = {}".format(zq_msg))

        zq_msg = TL1message(NE1.tl1.get_last_outcome())
        print(zq_msg.get_cmd_attr_value("1", 2))

        zq_tl1_res=NE1.tl1.do("RTRV-COND-VC4::STM1AU4-{}-1:::UNEQ-P;".format(S2))
        print("zq_tl1_res = {}".format(zq_tl1_res))

        zq_msg=NE1.tl1.get_last_outcome()
        print("zq_msg = {}".format(zq_msg))

        zq_msg = TL1message(NE1.tl1.get_last_outcome())
        print(zq_msg.get_cmd_attr_value("1", 2))

        zq_alm_ary = ONT5xx.retrieve_ho_alarms("P1")
        print("zq_alm_ary: [{}]".format(zq_alm_ary))
        
        zq_alm_ary = ONT5xx.retrieve_ho_alarms("P2")
        print("zq_alm_ary: [{}]".format(zq_alm_ary))

        NE1.tl1.do("ED-AU4::STM1AU4-{}-1::::POM=N,EGPOM=N;".format(S1))
        NE1.tl1.do("ED-AU4::STM1AU4-{}-1::::POM=N,EGPOM=N;".format(S2))
        print("\n**************** STOP ****************")
        


    def test_cleanup(self):
        '''
        test Cleanup Section implementation
        insert CleanUp code for your test below        '''
        ONT5xx.deinit_instrument("P1")
        ONT5xx.deinit_instrument("P2")



    def dut_cleanup(self):
        '''
        DUT CleanUp Section implementation
        insert DUT CleanUp code for your test below
        '''
        print('@DUT CleanUP')
        NE1.tl1.do("CANC-USER;")
        NE1.clean_up()
        #self.kenvironment.krepo.stop_tps_block("EM", "1-2-3")


#Please don't change the code below#
if __name__ == "__main__":
    #initializing the Test object instance, do not remove
    CTEST = Test(__file__)

    #initializing all local variable and constants used by Test object
    NE1 = Eqpt1850TSS320('NE1', CTEST.kenvironment)
    ONT5xx = InstrumentONT('ONT5xx', CTEST.kenvironment)
    
    # Run Test main flow
    # Please don't touch this code
    CTEST.run()

    ONT5xx.clean_up()
    
