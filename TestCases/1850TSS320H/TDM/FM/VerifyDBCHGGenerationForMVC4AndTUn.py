#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: Verify the DBCHG messages generation for each MVC4 and MVC4TUn facilities
:field Topology: 2 
:field Dependency:
:field Lab: SVT
:field TPS: FM__5-2-6-1
:field TPS: FM__5-2-6-2
:field TPS: FM__5-2-6-3
:field RunSections: 11111 
:field Author: tosima

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.instrumentONT     import InstrumentONT
#from katelibs.instrumentIXIA     import InstrumentIXIA
#from katelibs.instrumentSPIRENT  import InstrumentSPIRENT
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import * 
import time
from inspect import currentframe


def dprint(zq_str,zq_level):
    '''
    # print debug level:  0=no print
    #                     1=TL1 message response
    #                     2=OK/KO info 
    #                     4=execution info
    # can be used in combination, i.e.
    #                     3=TL1 message response+OK/KO info
    # 
    '''
    E_DPRINT = 6    
    
    if (E_DPRINT & zq_level):
        print(zq_str)
    return

def QS_000_Print_Line_Function(zq_gap=0):
    cf = currentframe()
    zq_line = cf.f_back.f_lineno + zq_gap
    zq_code = str(cf.f_back.f_code)
    zq_temp = zq_code.split(",")
    zq_function = zq_temp[0].split(" ")
    zq_res = "****** Line [{}] in function [{}]".format(zq_line,zq_function[2])
    
    return zq_res


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
        time.sleep(10)

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
        print("\n******************** START ********************")
        E_MAX_VC4=385
        E_LOA_MVC4=384
        E_LOA_MVC4TU3=E_LOA_MVC4*3
        E_LOA_MVC4TU12=E_LOA_MVC4TU3*21

        E_TIMEOUT=300
 
        E_LO_MTX = "MXH60GLO"
        
        self.start_tps_block(NE1.id,"FM", "5-2-6-1")
        zq_stm64_1=NE1.get_preset("S1")
        zq_mtxlo_slot=NE1.get_preset("M1")

        '''
        Board equipment if not yet!
        '''
        zq_tl1_res=NE1.tl1.do("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_attr_list1=zq_msg.get_cmd_attr_values("{}-{}".format(E_LO_MTX, zq_mtxlo_slot))
            zq_attr_list2=zq_msg.get_cmd_attr_values("{}-{}".format("MDL", zq_mtxlo_slot))
            if zq_attr_list1 is not None:
                if zq_attr_list1[0]['PROVISIONEDTYPE']==E_LO_MTX and zq_attr_list1[0]['ACTUALTYPE']==E_LO_MTX:  #Board equipped 
                    print("Board equipped then delete!")
                    zq_tl1_res=NE1.tl1.do("RMV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                    zq_tl1_res=NE1.tl1.do("DLT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                else:
                    NE1.tl1.event_collection_start()
                    time.sleep(10)
                    zq_filter=TL1check()
                    zq_filter.add_pst("IS")
                    zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                    NE1.tl1.do_until("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),zq_filter)
            else:
                if zq_attr_list2 is not None:
                    if zq_attr_list2[0]['ACTUALTYPE']==E_LO_MTX:  #Equip Board 
                        NE1.tl1.event_collection_start()
                        time.sleep(10)
                        zq_filter=TL1check()
                        zq_filter.add_pst("IS")
                        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                        NE1.tl1.do_until("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),zq_filter)


        
        '''        
        zq_tl1_res=NE1.tl1.do("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_attr_list=zq_msg.get_cmd_attr_values("{}-{}".format(E_LO_MTX, zq_mtxlo_slot))
            if zq_attr_list['PROVISIONEDTYPE']==E_LO_MTX and zq_attr_list['ACTUALTYPE']==E_LO_MTX:  #Board equipped then delete it!
                print("Board equipped then delete!")
                zq_tl1_res=NE1.tl1.do("RMV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                zq_tl1_res=NE1.tl1.do("DLT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
        '''
                        
        NE1.tl1.event_collection_start()
        time.sleep(10)

        zq_filter=TL1check()
        zq_filter.add_pst("IS")
        
        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
        NE1.tl1.do_until("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),zq_filter)
        
        zq_idx = 1
        zq_dbchg_num = 0
        zq_dbchg_tu3 = 0
        zq_dbchg_tu12 = 0
        zq_event_num=int(NE1.tl1.event_collection_size("A"))
        print("Number of event received: {}".format(zq_event_num))
        if zq_event_num > 0:
            for zq_elem in NE1.tl1.event_collection_get("A", aid="MVC4-{}-{}".format(zq_mtxlo_slot,"1&&-384"),cmd="ENT-PTF"):
                if zq_elem.get_eve_type() == 'REPT DBCHG':
                    zq_dbchg_num += 1
                        
            for zq_elem in NE1.tl1.event_collection_get("A", aid="MVC4TU3-{}-{}".format(zq_mtxlo_slot,"1&&-384-1&&-3"),cmd="ENT-TU3"):
                if zq_elem.get_eve_type() == 'REPT DBCHG':
                    zq_dbchg_tu3 += 1
        
        print("Number of MVC4 REPT DBCHG received: {}".format(zq_dbchg_num))
        print("Number of MVC4TU3 REPT DBCHG received: {}".format(zq_dbchg_tu3))

        if zq_dbchg_num == 1:
            dprint("OK\tNumber of MVC4 REPT DBCHG is correct: {}".format(zq_dbchg_num),2)
            self.add_success(NE1, "EVENTS COLLECTION","0.0", "Number of MVC4 REPT DBCHG is correct: {}".format(zq_dbchg_num))
        else:
            dprint("KO\tNumber of MVC4 REPT DBCHG expected: {}".format("1"),2)
            dprint("\tNumber of MVC4 REPT DBCHG received: {}".format(zq_dbchg_num),2)
            self.add_failure(NE1, "EVENTS COLLECTION","0.0", "MVC4 REPT DBCHG exp.[{}] rcv.[{}]".format("1", zq_dbchg_num),"MVC4 REPT DBCHG mismatch "+ QS_000_Print_Line_Function())

        self.stop_tps_block(NE1.id,"FM","5-2-6-1")
        

        self.start_tps_block(NE1.id,"FM", "5-2-6-2")
        
        if zq_dbchg_tu3 == 1:
            dprint("OK\tNumber of MVC4TU3 REPT DBCHG is correct: {}".format(zq_dbchg_tu3),2)
            self.add_success(NE1, "EVENTS COLLECTION","0.0", "Number of MVC4TU3 REPT DBCHG is correct: {}".format(zq_dbchg_tu3))
        else:
            dprint("KO\tNumber of MVC4TU3 REPT DBCHG expected: {}".format("1"),2)
            dprint("\tNumber of MVC4TU3 REPT DBCHG received: {}".format(zq_dbchg_tu3),2)
            self.add_failure(NE1, "EVENTS COLLECTION","0.0", "MVC4TU3 REPT DBCHG exp.[{}] rcv.[{}]".format("1",zq_dbchg_tu3),"MVC4TU3 REPT DBCHG mismatch "+ QS_000_Print_Line_Function())

        NE1.tl1.event_collection_stop()
        self.stop_tps_block(NE1.id,"FM","5-2-6-2")
        

        self.start_tps_block(NE1.id,"FM", "5-2-6-3")
        NE1.tl1.event_collection_start()
        time.sleep(10)
            
        for zq_i in range(1,E_MAX_VC4):
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=NORM,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,zq_i))
        
        
        if zq_event_num > 0:
            zq_exit=False
            for zq_i in range(1,E_TIMEOUT):
                if zq_exit:
                    break
                time.sleep(1)
                for zq_elem in NE1.tl1.event_collection_get("A", aid="MVC4TU12-{}-{}-{}".format(zq_mtxlo_slot,E_MAX_VC4-1,"3-7-3"),cmd="ENT-TU12"):
                    if zq_elem.get_eve_type() == 'REPT DBCHG':
                        print("Last MVC4TU12 created after {} seconds".format(zq_i))
                        zq_exit=True
        
        NE1.tl1.event_collection_stop()
        
        '''
        CHECK for 384 DLT-TU3 as consequence of MVVC4 structure to TU12
        '''
        zq_dbchg_tu3 = 0
        zq_event_num=int(NE1.tl1.event_collection_size("A"))
        if zq_event_num > 0:
            for zq_i in range(1,E_MAX_VC4):
                for zq_j in range(1,4):    
                    for zq_elem in NE1.tl1.event_collection_get("A", aid="MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot,zq_i,zq_j), cmd="DLT-TU3"):
                        if zq_elem.get_eve_type() == 'REPT DBCHG':
                            zq_dbchg_tu3 += 1
                            dprint("[{}]\r".format(zq_dbchg_tu3),2)
                        
            '''
            CHECK for 24192 ENT-TU12 as consequence of MVVC4 structure to TU12
            '''
            for zq_i in range(1,E_MAX_VC4):
                for zq_j in range(1,4):    
                    for zq_k in range (1,8):
                        for zq_m in range (1,4):
                            for zq_elem in NE1.tl1.event_collection_get("A", aid="MVC4TU12-{}-{}-{}-{}-{}".format(zq_mtxlo_slot,zq_i,zq_j,zq_k,zq_m), cmd="ENT-TU12"):
                                if zq_elem.get_eve_type() == 'REPT DBCHG':
                                    zq_dbchg_tu12 += 1
                                    dprint("[{}]\r".format(zq_dbchg_tu12),2)

        if zq_dbchg_tu3 == E_LOA_MVC4TU3:
            dprint("OK\tNumber of MVC4TU3 REPT DBCHG is correct: {}".format(zq_dbchg_tu3),2)
            self.add_success(NE1, "EVENTS COLLECTION","0.0", "Number of MVC4TU3 REPT DBCHG is correct: {}".format(zq_dbchg_tu3))
        else:
            dprint("KO\tNumber of MVC4TU3 REPT DBCHG expected: {}".format(E_LOA_MVC4TU3),2)
            dprint("\tNumber of MVC4TU3 REPT DBCHG received: {}".format(zq_dbchg_tu3),2)
            self.add_failure(NE1, "EVENTS COLLECTION","0.0", "MVC4TU3 REPT DBCHG exp.[{}] rcv.[{}]".format(E_LOA_MVC4TU3,zq_dbchg_tu3),"MVC4TU3 REPT DBCHG mismatch "+ QS_000_Print_Line_Function())


        if zq_dbchg_tu12 == E_LOA_MVC4TU12:
            dprint("OK\tNumber of MVC4TU12 REPT DBCHG is correct: {}".format(zq_dbchg_tu12),2)
            self.add_success(NE1, "EVENTS COLLECTION","0.0", "Number of MVC4TU12 REPT DBCHG is correct: {}".format(zq_dbchg_tu12))
        else:
            dprint("KO\tNumber of MVC4TU12 REPT DBCHG expected: {}".format(E_LOA_MVC4TU12),2)
            dprint("\tNumber of MVC4TU12 REPT DBCHG received: {}".format(zq_dbchg_tu12),2)
            self.add_failure(NE1, "EVENTS COLLECTION","0.0", "MVC4TU12 REPT DBCHG exp.[{}] rcv.[{}]".format(E_LOA_MVC4TU12,zq_dbchg_tu12),"MVC4TU12 REPT DBCHG mismatch "+ QS_000_Print_Line_Function())


        '''
        Delete board
        '''
        
        NE1.tl1.event_collection_start()
        time.sleep(10)
        
        zq_tl1_res=NE1.tl1.do("RMV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
        
        zq_tl1_res=NE1.tl1.do("DLT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
        
        zq_event_num=int(NE1.tl1.event_collection_size("A"))
        if zq_event_num > 0:
            zq_exit=False
            for zq_i in range(1,E_TIMEOUT):
                if zq_exit:
                    break
                time.sleep(1)
                for zq_elem in NE1.tl1.event_collection_get("A", aid="MDL-{}".format(zq_mtxlo_slot), cmd="CLEAR-FAULT-EQPT"):
                    if zq_elem.get_eve_type() == 'REPT DBCHG':
                        print("Last MVC4TU12 deleted after {} seconds".format(zq_i))
                        zq_exit=True

            if zq_exit:
                dprint("OK\tAll MVC4TU12 deleted",2)
                self.add_success(NE1, "EVENTS COLLECTION","0.0", "All MVC4TU12 deleted")
            else:
                dprint("KO\tDelete MVC4TU12 failed",2)
                self.add_failure(NE1, "EVENTS COLLECTION","0.0", "Delete MVC4TU12 failed","Some MVC4TU12 still exist "+ QS_000_Print_Line_Function())

        
        NE1.tl1.event_collection_stop()

        zq_dbchg_tu12 = 0
        for zq_i in range(1,E_MAX_VC4):
            for zq_j in range(1,4):    
                for zq_elem in NE1.tl1.event_collection_get("A", aid="MVC4TU12-{}-{}-{}-1&&-7-1&&-3".format(zq_mtxlo_slot,zq_i,zq_j), cmd="DLT-TU12"):
                    if zq_elem.get_eve_type() == 'REPT DBCHG':
                        zq_dbchg_tu12 += 1

        '''
        E_LOA_MVC4TU3 is CORRECT! Being grouped the number of DLT-TU12 is the same as the E_LOA_MVC4TU3 number! 
        '''
        if zq_dbchg_tu12 == E_LOA_MVC4TU3: 
            dprint("OK\tNumber of MVC4TU12 grouped REPT DBCHG is correct: {}".format(zq_dbchg_tu12),2)
            self.add_success(NE1, "EVENTS COLLECTION","0.0", "Number of MVC4TU12 grouped REPT DBCHG is correct: {}".format(zq_dbchg_tu12))
        else:
            dprint("KO\tNumber of MVC4TU12 grouped REPT DBCHG expected: {}".format(E_LOA_MVC4TU3),2)
            dprint("\tNumber of MVC4TU12 grouped REPT DBCHG received: {}".format(zq_dbchg_tu12),2)
            self.add_failure(NE1, "EVENTS COLLECTION","0.0", "MVC4TU12 grouped REPT DBCHG exp.[{}] rcv.[{}]".format(E_LOA_MVC4TU3,zq_dbchg_tu12),"MVC4TU12 REPT DBCHG mismatch "+ QS_000_Print_Line_Function())

        
        self.stop_tps_block(NE1.id,"FM","5-2-6-3")

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
    CTEST.add_eqpt(NE1)
    
    # Run Test main flow
    # Please don't touch this code
    CTEST.run()

