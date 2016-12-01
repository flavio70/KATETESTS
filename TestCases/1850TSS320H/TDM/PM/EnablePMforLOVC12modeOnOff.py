#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: This test verifies the SST of MVC4TU12 facility when  
:field Description: setting the PM mode ON/OFF. It checks the presence of
:field Description: PMD/SGEO for 1152 MVC4TU12, and for each counter the
:field Description: increment of elapsed time (ON) or the not increment (OFF)
:field Description: WARNING: for time constraint reason only 63 TU12 for each
:field Description: bank is checked.
:field Topology: 7
:field Dependency: NA
:field Lab: SVT
:field TPS: PM__5-5-3-6
:field TPS: PM__5-5-3-7
:field TPS: PM__5-5-3-8
:field TPS: PM__5-5-3-9
:field TPS: PM__5-5-3-10
:field TPS: PM__5-5-4-3
:field TPS: PM__5-5-4-4
:field RunSections: 10101
:field Author: tosima

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.instrumentONT     import InstrumentONT
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import *
import time
from inspect import currentframe

E_BLOCK_SIZE = 64
E_MAX_MVC4 = 384
E_LO_MTX = "MXH60GLO"
E_TIMEOUT = 60


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


def QS_010_Verify_SST(zq_run, zq_mtxlo_slot, zq_sst_exp, zq_sst_counter_exp):
    
    zq_tl1_res=NE1.tl1.do("RTRV-TU3::MVC4TU3-{}-1&&-384-1&&-3;".format(zq_mtxlo_slot))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    zq_sst_counter=0
    if zq_cmd == (True,'COMPLD'):
        for zq_i in range(1,E_MAX_MVC4+1):
            for zq_j in range(1,4):
                zq_sst=zq_msg.get_cmd_sst("MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot, str(zq_i),str(zq_j)))
                if zq_sst_exp in zq_sst:
                    zq_sst_counter = zq_sst_counter+1

    if (zq_sst_counter == (zq_sst_counter_exp*3)):
        dprint("OK\tNumber of MVC4TU3 with SST containing PMD is correct: {}".format(zq_sst_counter),2)
        zq_run.add_success(NE1, "EVENTS COLLECTION","0.0", "Number of MVC4TU3 with SST containing PMD is correct: {}".format(zq_sst_counter))
    else:
        dprint("KO\tNumber of MVC4TU3 with SST containing PMD expected: {}".format(str(zq_sst_counter_exp*3)),2)
        dprint("\tNumber of MVC4TU3 with SST containing PMD received: {}".format(zq_sst_counter),2)
        zq_run.add_failure(NE1, "EVENTS COLLECTION","0.0", "MVC4TU3 with SST containing PMD exp.[{}] rcv.[{}]".format(str(zq_sst_counter_exp*3), zq_sst_counter),
        "MVC4TU3 with SST containing PMD exp.[{}] rcv.[{}] {}".format(str(zq_sst_counter_exp*3),zq_sst_counter,QS_000_Print_Line_Function()))

    return

def QS_020_Verify_Report(zq_run,zq_mtxlo_slot,zq_report_exp,zq_marker,zq_aid,zq_cmd,zq_report_type):     

    zq_idx = 1
    zq_dbchg_num = 0
    zq_event_num=int(NE1.tl1.event_collection_size("A"))
    print("Number of event received: {}".format(zq_event_num))
    if zq_event_num > 0:
        for zq_idx in range(1,zq_report_exp+1):
            for zq_j in range(1,4):
                zq_elem = NE1.tl1.event_collection_get(zq_marker, aid="{}-{}-{}-{}".format(zq_aid,zq_mtxlo_slot,str(zq_idx),str(zq_j)), cmd=zq_cmd)
                if len(zq_elem) != 0:
                    if zq_elem[0]._TL1message__m_coded['S_VMM'] == zq_report_type:
                        zq_dbchg_num += 1
            
    if zq_dbchg_num == zq_report_exp*3:
        dprint("OK\tNumber of MVC4TU3 REPT DBCHG is correct: {}".format(zq_dbchg_num),2)
        zq_run.add_success(NE1, "EVENTS COLLECTION","0.0", "Number of MVC4TU3 REPT DBCHG is correct: {}".format(zq_dbchg_num))
    else:
        dprint("KO\tNumber of MVC4TU3 REPT DBCHG expected: {}".format(zq_report_exp*3),2)
        dprint("\tNumber of MVC4TU3 REPT DBCHG received: {}".format(zq_dbchg_num),2)
        zq_run.add_failure(NE1, "EVENTS COLLECTION","0.0", "MVC4TU3 REPT DBCHG exp.[{}] rcv.[{}]".format(zq_report_exp*3,zq_dbchg_num),"MVC4TU3 REPT DBCHG exp.[{}] rcv.[{}] {}".format(zq_report_exp*3,zq_dbchg_num,QS_000_Print_Line_Function()))

    return

def QS_030_Verify_PM(zq_msg, zq_aid, zq_locn_exp, zq_dir_exp, zq_period_exp, zq_pmstate_exp):

    zq_res = False
    zq_locn=zq_msg.get_cmd_attr_value(zq_aid, "1")
    zq_pmstate=zq_msg.get_cmd_attr_value(zq_aid, "PMSTATE")
    zq_dir = zq_msg.get_cmd_attr_value(zq_aid, "DIRN")
    zq_period=zq_msg.get_cmd_attr_value(zq_aid, "TMPER")
    
    if  zq_locn == zq_locn_exp and \
        zq_dir == zq_dir_exp and \
        zq_period == zq_period_exp and \
        zq_pmstate == zq_pmstate_exp:
        
        zq_res = True
        
    
    return zq_res

def QS_040_Get_PM_Time(zq_run, zq_mtxlo_slot, zq_counter_type, zq_locn, zq_dir, zq_period):

    zq_time_list=list()
    #zq_tmp = "UAS-LOVC"
    #if zq_locn == "BIDIR":
    #    zq_tmp = zq_tmp + "-BI"
    for zq_i in range(1,E_MAX_MVC4+1):
        for zq_j in range (1,4):
            zq_tl1_res=NE1.tl1.do("RTRV-PM-LOVC3::MVC4TU3-{}-{}-{}:::{},0-UP,{},{},{};".format(zq_mtxlo_slot, str(zq_i),str(zq_j),zq_counter_type, zq_locn,zq_dir,zq_period))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_time_str=zq_msg.get_cmd_attr_value("MVC4TU3-{}-{}-{},LOVC3".format(zq_mtxlo_slot, str(zq_i),str(zq_j)), "9")
                    zq_sec_ary = zq_time_str.split("-")
                    zq_time_list.append("{}#MVC4TU3-{}-{}-{},LOVC3:{}-{}-{}-{}".format(zq_sec_ary[2],zq_mtxlo_slot, str(zq_i),str(zq_j),zq_counter_type, zq_locn,zq_dir,zq_period))
                    print("{}".format(zq_sec_ary[2]),end='\r')
            
    return zq_time_list


def QS_050_Check_PM_Time(zq_run,zq_mtxlo_slot, zq_counter_type, zq_locn, zq_dir, zq_period, zq_check_zero=False):

    zq_counter=0
    zq_not_elapsed_counter=0
    zq_time1= QS_040_Get_PM_Time(zq_run, zq_mtxlo_slot, zq_counter_type, zq_locn, zq_dir, zq_period)
    zq_time2= QS_040_Get_PM_Time(zq_run, zq_mtxlo_slot, zq_counter_type, zq_locn, zq_dir, zq_period)
    if len(zq_time1)!= 0 and \
       len(zq_time2)!= 0:
        zq_range = len(zq_time1)
        if zq_range > len(zq_time2):
            zq_range = len(zq_time2)
            
        for zq_i in range(1,zq_range+1):
            zq_tempo1_ary = zq_time1[zq_i-1].split("#") 
            zq_tempo2_ary = zq_time2[zq_i-1].split("#") 
            
            zq_tempo1 =  zq_tempo1_ary[0]
            zq_tempo2 =  zq_tempo2_ary[0]
                        
            if abs(int(zq_tempo2)-int(zq_tempo1)) != 0:
                zq_counter=zq_counter+1
            else:
                zq_not_elapsed_counter=zq_not_elapsed_counter+1

                if zq_check_zero:
                    dprint("OK\tElapsed Time not increased for {} ".format(zq_tempo1_ary[1]),2)
                    zq_run.add_failure(NE1, "PM COUNTER CHECK","0.0", "PM counter {} time not increased for {} ".format(zq_counter_type,zq_tempo1_ary[1])
                                          ,"PM COUNTER CHECK MISMATCH")
                else:
                    dprint("KO\tElapsed Time not increased for {} ".format(zq_tempo1_ary[1]),2)
                    zq_run.add_failure(NE1, "PM COUNTER CHECK","0.0", "PM counter {} time NOT increased for {} ".format(zq_counter_type,zq_tempo1_ary[1])
                                          ,"PM counter {} time NOT increased for {} {}".format(zq_counter_type,zq_tempo1_ary[1],QS_000_Print_Line_Function()))
                    
                    
        if zq_check_zero:
            if zq_not_elapsed_counter == E_MAX_MVC4*3:
                dprint("OK\tPM counter {} time NOT increased for {} MVC4TU3s".format(zq_counter_type, zq_not_elapsed_counter),2)
                zq_run.add_success(NE1, "PM COUNTER CHECK","0.0"
                                      , "PM counter {} time NOT increased for {} MVC4TU3s".format(zq_counter_type, zq_not_elapsed_counter))
            else:
                dprint("KO\tPM counter {} time NOT increased for MVC4TU3s expected: {} ".format(zq_counter_type, E_MAX_MVC4*3),2)
                dprint("\tPM counter {} time NOT increased for MVC4TU3s received: {} ".format(zq_counter_type, zq_not_elapsed_counter),2)
                zq_run.add_failure(NE1, "PM COUNTER CHECK","0.0", "PM counter {} time NOT increased for MVC4TU3s exp.[{}] - rcv.[{}] ".format(zq_counter_type, E_MAX_MVC4*3,zq_not_elapsed_counter)
                                      ,"PM counter {} time NOT increased for MVC4TU3s exp.[{}] - rcv.[{}] {}".format(zq_counter_type, E_MAX_MVC4*3,zq_not_elapsed_counter,QS_000_Print_Line_Function()))
        else:
            if zq_counter == E_MAX_MVC4*3:
                dprint("OK\tPM counter {} time increased for {} MVC4TU3s".format(zq_counter_type, zq_counter),2)
                zq_run.add_success(NE1, "PM COUNTER CHECK","0.0"
                                      , "PM counter {} time increased for {} MVC4TU3s".format(zq_counter_type, zq_counter))
            else:
                dprint("KO\tPM counter {} time increased for MVC4TU3s expected: {} ".format(zq_counter_type, E_MAX_MVC4*3),2)
                dprint("\tPM counter {} time increased for MVC4TU3s received: {} ".format(zq_counter_type, zq_counter),2)
                zq_run.add_failure(NE1, "PM COUNTER CHECK","0.0", "PM counter {} time increased for MVC4TU3s exp.[{}] - rcv.[{}] ".format(zq_counter_type, E_MAX_MVC4*3,zq_counter)
                                      ,"PM counter {} time increased for MVC4TU3s exp.[{}] - rcv.[{}] ".format(zq_counter_type, E_MAX_MVC4*3,zq_counter,QS_000_Print_Line_Function()))

    else:
        dprint("KO\tError retrieving PM counter {}.".format(zq_counter_type),2)
        zq_run.add_failure(NE1, "PM COUNTER CHECK","0.0", "Error retrieving PM counter {}.".format(zq_counter_type, E_MAX_MVC4*3,zq_counter)
                              ,"Error retrieving PM counter {}.".format(zq_counter_type, E_MAX_MVC4*3,zq_counter,QS_000_Print_Line_Function()))
        
    return 


def QS_070_Enable_Disable_POM(zq_run, zq_range, zq_mtxlo_slot,zq_enadis):

    for zq_i in range(1,zq_range+1):
        for zq_j in range(1,4):
            zq_tl1_res=NE1.tl1.do("ED-TU3::MVC4TU3-{}-{}-{}::::POM={},EGPOM={};".format(zq_mtxlo_slot,str(zq_i),str(zq_j),zq_enadis,zq_enadis))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            dprint(NE1.tl1.get_last_outcome(),1)
            zq_cmd=zq_msg.get_cmd_status()
        
            if zq_cmd == (True,'COMPLD'):
                dprint("\nOK\tPom and EGPOM setting to [{}] for {}-{}-{} successful".format(zq_enadis,zq_mtxlo_slot,str(zq_i),str(zq_j)),2)
                zq_run.add_success(NE1, "Pom and EGPOM setting to [{}] for {}-{}-{} successful".format(zq_enadis,zq_mtxlo_slot,str(zq_i),str(zq_j)),"0.0", "Pom and EGPOM setting")
        
            else:
                dprint("\nKO\tPom and EGPOM setting to [{}] for {}-{}-{} failed".format(zq_enadis,zq_mtxlo_slot,str(zq_i),str(zq_j)),2)
                zq_run.add_failure(NE1,  "TL1 COMMAND","0.0", "Pom and EGPOM setting to [{}] for {}-{}-{} failed".format(zq_enadis,zq_mtxlo_slot,str(zq_i),str(zq_j)),
                                         "Pom and EGPOM setting to [{}] for {}-{}-{} failed {}".format(zq_enadis,zq_mtxlo_slot,str(zq_i),str(zq_j),QS_000_Print_Line_Function()))
    
    return


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
        print("\n******************** START ********************")
        '''
        '''
        
        self.start_tps_block(NE1.id,"PM", "5-5-3-6")
        self.stop_tps_block(NE1.id,"PM","5-5-3-6")

        self.start_tps_block(NE1.id,"PM", "5-5-3-7")
        self.stop_tps_block(NE1.id,"PM","5-5-3-7")

        self.start_tps_block(NE1.id,"PM", "5-5-3-8")
        self.stop_tps_block(NE1.id,"PM","5-5-3-8")

        self.start_tps_block(NE1.id,"PM", "5-5-3-9")
        self.stop_tps_block(NE1.id,"PM","5-5-3-9")

        self.start_tps_block(NE1.id,"PM", "5-5-3-10")
        self.stop_tps_block(NE1.id,"PM","5-5-3-10")

        self.start_tps_block(NE1.id,"PM", "5-5-4-3")
        self.stop_tps_block(NE1.id,"PM","5-5-4-3")

        self.start_tps_block(NE1.id,"PM", "5-5-4-4")
        self.stop_tps_block(NE1.id,"PM","5-5-4-4")

        zq_mtxlo_slot=NE1_M1

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
                if zq_attr_list1['PROVISIONEDTYPE']==E_LO_MTX and zq_attr_list1['ACTUALTYPE']==E_LO_MTX:  #Board equipped 
                    print("Board already equipped")
                else:
                    zq_filter=TL1check()
                    zq_filter.add_pst("IS")
                    zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                    NE1.tl1.do_until("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),zq_filter)
            else:
                if zq_attr_list2 is not None:
                    if zq_attr_list2['ACTUALTYPE']==E_LO_MTX:  #Equip Board 
                        zq_filter=TL1check()
                        zq_filter.add_pst("IS")
                        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                        NE1.tl1.do_until("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),zq_filter)


        print("******************************************************************")
        print("                 VERIFY SST of MVC4TU3 contains PMD               ")
        print("******************************************************************")
        QS_070_Enable_Disable_POM(self, E_MAX_MVC4, zq_mtxlo_slot, "Y")
        
        QS_010_Verify_SST(self, zq_mtxlo_slot, 'PMD', E_MAX_MVC4) 
            

        NE1.tl1.event_collection_start()
        time.sleep(10)

        zq_filter=TL1check()
        zq_filter.add_sst("SGEO")
        
        print("******************************************************************")
        print("     ENABLE PM NEND-FEND-BIDIR-RCV-TRMT-15-MIN-1-DAY   [mode ON]  ")
        print("******************************************************************")
 

 
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
    NE1_M1=NE1.get_preset("M1")
    CTEST.add_eqpt(NE1)

    # Run Test main flow
    # Please don't touch this code
    CTEST.run()
    