#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: This test provides a method to enable the PM counter  
:field Description: mode ON/OFF for MVC4TU3 facilities.
:field Topology: 7
:field Dependency: NA
:field Lab: SVT
:field TPS: PM__5-5-3-1
:field TPS: PM__5-5-3-2
:field TPS: PM__5-5-3-3
:field TPS: PM__5-5-3-4
:field TPS: PM__5-5-3-5
:field TPS: PM__5-5-4-1
:field TPS: PM__5-5-4-2
:field RunSections: 10101
:field Author: tosima

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import *
import time
import string
import math

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
        zq_run.add_failure(NE1, "EVENTS COLLECTION","0.0", "MVC4TU3 with SST containing PMD exp.[{}] rcv.[{}]".format(str(zq_sst_counter_exp*3), zq_sst_counter),"MVC4TU3 SST mismatch")

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
        zq_run.add_failure(NE1, "EVENTS COLLECTION","0.0", "MVC4TU3 REPT DBCHG exp.[{}] rcv.[{}]".format(zq_report_exp*3, zq_dbchg_num),"MVC4TU3 REPT DBCHG mismatch")

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
                                          ,"PM COUNTER CHECK MISMATCH")
                    
                    
        if zq_check_zero:
            if zq_not_elapsed_counter == E_MAX_MVC4*3:
                dprint("OK\tPM counter {} time NOT increased for {} MVC4TU3s".format(zq_counter_type, zq_not_elapsed_counter),2)
                zq_run.add_success(NE1, "PM COUNTER CHECK","0.0"
                                      , "PM counter {} time NOT increased for {} MVC4TU3s".format(zq_counter_type, zq_not_elapsed_counter))
            else:
                dprint("KO\tPM counter {} time NOT increased for MVC4TU3s expected: {} ".format(zq_counter_type, E_MAX_MVC4*3),2)
                dprint("\tPM counter {} time NOT increased for MVC4TU3s received: {} ".format(zq_counter_type, zq_not_elapsed_counter),2)
                zq_run.add_failure(NE1, "PM COUNTER CHECK","0.0", "PM counter {} time NOT increased for MVC4TU3s exp.[{}] - rcv.[{}] ".format(zq_counter_type, E_MAX_MVC4*3,zq_not_elapsed_counter)
                                      ,"PM COUNTER CHECK MISMATCH")
        else:
            if zq_counter == E_MAX_MVC4*3:
                dprint("OK\tPM counter {} time increased for {} MVC4TU3s".format(zq_counter_type, zq_counter),2)
                zq_run.add_success(NE1, "PM COUNTER CHECK","0.0"
                                      , "PM counter {} time increased for {} MVC4TU3s".format(zq_counter_type, zq_counter))
            else:
                dprint("KO\tPM counter {} time increased for MVC4TU3s expected: {} ".format(zq_counter_type, E_MAX_MVC4*3),2)
                dprint("\tPM counter {} time increased for MVC4TU3s received: {} ".format(zq_counter_type, zq_counter),2)
                zq_run.add_failure(NE1, "PM COUNTER CHECK","0.0", "PM counter {} time increased for MVC4TU3s exp.[{}] - rcv.[{}] ".format(zq_counter_type, E_MAX_MVC4*3,zq_counter)
                                      ,"PM COUNTER CHECK MISMATCH")

    else:
        dprint("KO\tError retrieving PM counter {}.".format(zq_counter_type),2)
        zq_run.add_failure(NE1, "PM COUNTER CHECK","0.0", "Error retrieving PM counter {}.".format(zq_counter_type, E_MAX_MVC4*3,zq_counter)
                              ,"PM COUNTER CHECK")
        
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
                zq_run.add_failure(NE1,  "TL1 COMMAND","0.0", "Pom and EGPOM setting to [{}] for {}-{}-{} failed".format(zq_enadis,zq_mtxlo_slot,str(zq_i),str(zq_j)),"TL1 command fail")
    
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
        
        self.start_tps_block(NE1.id,"PM", "5-5-3-1")

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
        #zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::ALL,ALL,ON,ALL:TMPER=BOTH;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::NEND,ALL,ON,RCV:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::NEND,ALL,ON,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::NEND,ALL,ON,TRMT:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::NEND,ALL,ON,TRMT:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::FEND,ALL,ON,RCV:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::FEND,ALL,ON,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::FEND,ALL,ON,TRMT:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::FEND,ALL,ON,TRMT:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::BIDIR,ALL,ON,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        
        NE1.tl1.do_until("RTRV-TU3::MVC4TU3-{}-{}-3;".format(zq_mtxlo_slot,E_MAX_MVC4),zq_filter)
        time.sleep(E_TIMEOUT)

        NE1.tl1.event_collection_stop()

        QS_020_Verify_Report(self,zq_mtxlo_slot,E_MAX_MVC4,"A","MVC4TU3","SET-PMMODE","REPT DBCHG")        

        ########################################################
        # Verify 'PMD' is not present in MVC4TU3 SST 
        ########################################################

        QS_010_Verify_SST(self, zq_mtxlo_slot, 'PMD', 0) 

        print("******************************************************************")
        print("            VERIFY PM  NEND - RCV - 15 MIN      [mode ON]         ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::NEND,RCV:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                for zq_j in range (1,4):
                    zq_aid="MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot, str(zq_i),str(zq_j))
                    if QS_030_Verify_PM(zq_msg, zq_aid, "NEND", "RCV", "15-MIN", "ON"):
                        zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4*3:
            dprint("OK\tPM set to [NEND,RCV,15-MIN,ON] for {} MVC4TUs".format(zq_counter),2)
            self.add_success(NE1, "PM set to [NEND,RCV,15-MIN,ON] for {} MVC4TUs".format(zq_counter),"0.0" 
                                  , "PM set to [NEND,RCV,15-MIN,ON] for {} MVC4TUs".format(zq_counter))
        else:
            dprint("KO\tPM set to [NEND,RCV,15-MIN,ON] for {} MVC4TUs instead of {}".format(zq_counter, E_MAX_MVC4*3),2)
            self.add_failure(NE1,"PM set to [NEND,RCV,15-MIN,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3),"0.0"
                                  , "PM STATUS CHECK","PM set to [NEND,RCV,15-MIN,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3))

        print("******************************************************************")
        print("            VERIFY PM  NEND - TRMT - 15 MIN     [mode ON]         ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::NEND,TRMT:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                for zq_j in range (1,4):
                    zq_aid="MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot, str(zq_i),str(zq_j))
                    if QS_030_Verify_PM(zq_msg, zq_aid, "NEND", "TRMT", "15-MIN", "ON"):
                        zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4*3:
            dprint("OK\tPM set to [NEND,TRMT,15-MIN,ON] for {} MVC4TUs".format(zq_counter),2)
            self.add_success(NE1, "PM set to [NEND,TRMT,15-MIN,ON] for {} MVC4TUs".format(zq_counter),"0.0" 
                                  , "PM set to [NEND,TRMT,15-MIN,ON] for {} MVC4TUs".format(zq_counter))
        else:
            dprint("KO\tPM set to [NEND,TRMT,15-MIN,ON] for {} MVC4TUs instead of {}".format(zq_counter, E_MAX_MVC4*3),2)
            self.add_failure(NE1,"PM set to [NEND,TRMT,15-MIN,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3),"0.0"
                                  , "PM STATUS CHECK","PM set to [NEND,TRMT,15-MIN,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3))

        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS NEND-RCV-15-MIN          ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","NEND", "RCV", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","NEND", "RCV", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","NEND", "RCV", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","NEND", "RCV", "15-MIN")                
            
        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS NEND-TRMT-15-MIN         ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","NEND", "TRMT", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","NEND", "TRMT", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","NEND", "TRMT", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","NEND", "TRMT", "15-MIN")                
            
        self.stop_tps_block(NE1.id,"PM", "5-5-3-1")

        self.start_tps_block(NE1.id,"PM", "5-5-3-2")
        print("******************************************************************")
        print("            VERIFY PM  FEND - RCV - 15 MIN     [mode ON]          ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::FEND,RCV:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                for zq_j in range (1,4):
                    zq_aid="MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot, str(zq_i),str(zq_j))
                    if QS_030_Verify_PM(zq_msg, zq_aid, "FEND", "RCV", "15-MIN", "ON"):
                        zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4*3:
            dprint("OK\tPM set to [FEND,RCV,15-MIN,ON] for {} MVC4TUs".format(zq_counter),2)
            self.add_success(NE1, "PM set to [FEND,RCV,15-MIN,ON] for {} MVC4TUs".format(zq_counter),"0.0" 
                                  , "PM set to [FEND,RCV,15-MIN,ON] for {} MVC4TUs".format(zq_counter))
        else:
            dprint("KO\tPM set to [FEND,RCV,15-MIN,ON] for {} MVC4TUs instead of {}".format(zq_counter, E_MAX_MVC4*3),2)
            self.add_failure(NE1,"PM set to [FEND,RCV,15-MIN,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3),"0.0"
                                  , "PM STATUS CHECK","PM set to [FEND,RCV,15-MIN,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3))

        print("******************************************************************")
        print("            VERIFY PM  FEND - TRMT - 15 MIN     [mode ON]         ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::FEND,TRMT:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                for zq_j in range (1,4):
                    zq_aid="MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot, str(zq_i),str(zq_j))
                    if QS_030_Verify_PM(zq_msg, zq_aid, "FEND", "TRMT", "15-MIN", "ON"):
                        zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4*3:
            dprint("OK\tPM set to [FEND,TRMT,15-MIN,ON] for {} MVC4TUs".format(zq_counter),2)
            self.add_success(NE1, "PM set to [FEND,TRMT,15-MIN,ON] for {} MVC4TUs".format(zq_counter),"0.0" 
                                  , "PM set to [FEND,TRMT,15-MIN,ON] for {} MVC4TUs".format(zq_counter))
        else:
            dprint("KO\tPM set to [FEND,TRMT,15-MIN,ON] for {} MVC4TUs instead of {}".format(zq_counter, E_MAX_MVC4*3),2)
            self.add_failure(NE1,"PM set to [FEND,TRMT,15-MIN,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3),"0.0"
                                  , "PM STATUS CHECK","PM set to [FEND,TRMT,15-MIN,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3))

        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS FEND-RCV-15-MIN          ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","FEND", "RCV", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","FEND", "RCV", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","FEND", "RCV", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","FEND", "RCV", "15-MIN")                
            
        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS FEND-TRMT-15-MIN         ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","FEND", "TRMT", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","FEND", "TRMT", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","FEND", "TRMT", "15-MIN")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","FEND", "TRMT", "15-MIN")                

        self.stop_tps_block(NE1.id,"PM", "5-5-3-2")


        
        self.start_tps_block(NE1.id,"PM", "5-5-3-3")
        print("******************************************************************")
        print("            VERIFY PM  NEND - RCV - 1 DAY    [mode ON]            ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::NEND,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                for zq_j in range (1,4):
                    zq_aid="MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot, str(zq_i),str(zq_j))
                    if QS_030_Verify_PM(zq_msg, zq_aid, "NEND", "RCV", "1-DAY", "ON"):
                        zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4*3:
            dprint("OK\tPM set to [NEND,RCV,1-DAY,ON] for {} MVC4TUs".format(zq_counter),2)
            self.add_success(NE1, "PM set to [NEND,RCV,1-DAY,ON] for {} MVC4TUs".format(zq_counter),"0.0" 
                                  , "PM set to [NEND,RCV,1-DAY,ON] for {} MVC4TUs".format(zq_counter))
        else:
            dprint("KO\tPM set to [NEND,RCV,1-DAY,ON] for {} MVC4TUs instead of {}".format(zq_counter, E_MAX_MVC4*3),2)
            self.add_failure(NE1,"PM set to [NEND,RCV,1-DAY,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3),"0.0"
                                  , "PM STATUS CHECK","PM set to [NEND,RCV,1-DAY,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3))

        print("******************************************************************")
        print("           VERIFY PM  NEND - TRMT - 1 DAY    [mode ON]            ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::NEND,TRMT:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                for zq_j in range (1,4):
                    zq_aid="MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot, str(zq_i),str(zq_j))
                    if QS_030_Verify_PM(zq_msg, zq_aid, "NEND", "TRMT", "1-DAY", "ON"):
                        zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4*3:
            dprint("OK\tPM set to [NEND,TRMT,1-DAY,ON] for {} MVC4TUs".format(zq_counter),2)
            self.add_success(NE1, "PM set to [NEND,TRMT,1-DAY,ON] for {} MVC4TUs".format(zq_counter),"0.0" 
                                  , "PM set to [NEND,TRMT,1-DAY,ON] for {} MVC4TUs".format(zq_counter))
        else:
            dprint("KO\tPM set to [NEND,TRMT,1-DAY,ON] for {} MVC4TUs instead of {}".format(zq_counter, E_MAX_MVC4*3),2)
            self.add_failure(NE1,"PM set to [NEND,TRMT,1-DAY,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3),"0.0"
                                  , "PM STATUS CHECK","PM set to [NEND,TRMT,1-DAY,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3))

        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS NEND-RCV-1-DAY           ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","NEND", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","NEND", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","NEND", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","NEND", "RCV", "1-DAY")                
            
        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS NEND-TRMT-1-DAY          ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","NEND", "TRMT", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","NEND", "TRMT", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","NEND", "TRMT", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","NEND", "TRMT", "1-DAY")                
            
        self.stop_tps_block(NE1.id,"PM", "5-5-3-3")

        
        self.start_tps_block(NE1.id,"PM", "5-5-3-4")
        print("******************************************************************")
        print("            VERIFY PM  FEND - RCV - 1 DAY    [mode ON]            ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::FEND,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                for zq_j in range (1,4):
                    zq_aid="MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot, str(zq_i),str(zq_j))
                    if QS_030_Verify_PM(zq_msg, zq_aid, "FEND", "RCV", "1-DAY", "ON"):
                        zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4*3:
            dprint("OK\tPM set to [FEND,RCV,1-DAY,ON] for {} MVC4TUs".format(zq_counter),2)
            self.add_success(NE1, "PM set to [FEND,RCV,1-DAY,ON] for {} MVC4TUs".format(zq_counter),"0.0" 
                                  , "PM set to [FEND,RCV,1-DAY,ON] for {} MVC4TUs".format(zq_counter))
        else:
            dprint("KO\tPM set to [FEND,RCV,1-DAY,ON] for {} MVC4TUs instead of {}".format(zq_counter, E_MAX_MVC4*3),2)
            self.add_failure(NE1,"PM set to [FEND,RCV,1-DAY,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3),"0.0"
                                  , "PM STATUS CHECK","PM set to [FEND,RCV,1-DAY,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3))

        print("******************************************************************")
        print("           VERIFY PM  FEND - TRMT - 1 DAY    [mode ON]            ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::FEND,TRMT:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                for zq_j in range (1,4):
                    zq_aid="MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot, str(zq_i),str(zq_j))
                    if QS_030_Verify_PM(zq_msg, zq_aid, "FEND", "TRMT", "1-DAY", "ON"):
                        zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4*3:
            dprint("OK\tPM set to [FEND,TRMT,1-DAY,ON] for {} MVC4TUs".format(zq_counter),2)
            self.add_success(NE1, "PM set to [FEND,TRMT,1-DAY,ON] for {} MVC4TUs".format(zq_counter),"0.0" 
                                  , "PM set to [FEND,TRMT,1-DAY,ON] for {} MVC4TUs".format(zq_counter))
        else:
            dprint("KO\tPM set to [FEND,TRMT,1-DAY,ON] for {} MVC4TUs instead of {}".format(zq_counter, E_MAX_MVC4*3),2)
            self.add_failure(NE1,"PM set to [FEND,TRMT,1-DAY,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3),"0.0"
                                  , "PM STATUS CHECK","PM set to [FEND,TRMT,1-DAY,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3))
        
        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS FEND-RCV-1-DAY           ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","FEND", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","FEND", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","FEND", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","FEND", "RCV", "1-DAY")                
            
        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS FEND-TRMT-1-DAY          ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","FEND", "TRMT", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","FEND", "TRMT", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","FEND", "TRMT", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","FEND", "TRMT", "1-DAY")                

        self.stop_tps_block(NE1.id,"PM", "5-5-3-4")
        
        self.start_tps_block(NE1.id,"PM", "5-5-3-5")
        print("******************************************************************")
        print("            VERIFY PM  BIDIR - RCV - 1 DAY   [mode ON]            ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::BIDIR,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                for zq_j in range (1,4):
                    zq_aid="MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot, str(zq_i),str(zq_j))
                    if QS_030_Verify_PM(zq_msg, zq_aid, "BIDIR", "RCV", "1-DAY", "ON"):
                        zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4*3:
            dprint("OK\tPM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4TUs".format(zq_counter),2)
            self.add_success(NE1, "PM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4TUs".format(zq_counter),"0.0" 
                                  , "PM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4TUs".format(zq_counter))
        else:
            dprint("KO\tPM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4TUs instead of {}".format(zq_counter, E_MAX_MVC4*3),2)
            self.add_failure(NE1,"PM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3),"0.0"
                                  , "PM STATUS CHECK","PM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4TU3s instead of {}".format(zq_counter, E_MAX_MVC4*3))
        

        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS BIDIR-RCV-1-DAY          ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC-EG","BIDIR", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC-IN","BIDIR", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC-EG","BIDIR", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC-IN","BIDIR", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC-EG","BIDIR", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC-IN","BIDIR", "RCV", "1-DAY")                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC-BI","BIDIR", "RCV", "1-DAY")                
            

        self.stop_tps_block(NE1.id,"PM", "5-5-3-5")

        
        
        self.start_tps_block(NE1.id,"PM", "5-5-4-1")

        print("******************************************************************")
        print("     ENABLE PM NEND-FEND-BIDIR-RCV-TRMT-15-MIN-1-DAY  [mode OFF]  ")
        print("******************************************************************")
        NE1.tl1.event_collection_start()
        time.sleep(10)

        zq_filter=TL1check()
        zq_filter.add_sst("PMI")

        zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::ALL,ALL,OFF,ALL:TMPER=BOTH;".format(zq_mtxlo_slot, E_MAX_MVC4))
        NE1.tl1.do_until("RTRV-TU3::MVC4TU3-{}-{}-3;".format(zq_mtxlo_slot,E_MAX_MVC4),zq_filter)
        time.sleep(E_TIMEOUT)

        NE1.tl1.event_collection_stop()

        QS_020_Verify_Report(self,zq_mtxlo_slot,E_MAX_MVC4,"A","MVC4TU3","SET-PMMODE","REPT DBCHG")        

        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS NEND-RCV-15-MIN          ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","NEND", "RCV", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","NEND", "RCV", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","NEND", "RCV", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","NEND", "RCV", "15-MIN",True)                
            
        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS NEND-TRMT-15-MIN         ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","NEND", "TRMT", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","NEND", "TRMT", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","NEND", "TRMT", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","NEND", "TRMT", "15-MIN",True)                

        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS FEND-RCV-15-MIN          ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","FEND", "RCV", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","FEND", "RCV", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","FEND", "RCV", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","FEND", "RCV", "15-MIN",True)                
            
        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS FEND-TRMT-15-MIN         ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","FEND", "TRMT", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","FEND", "TRMT", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","FEND", "TRMT", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","FEND", "TRMT", "15-MIN",True)                

        self.stop_tps_block(NE1.id,"PM", "5-5-4-1")



        self.start_tps_block(NE1.id,"PM", "5-5-4-2")
        '''
        print("******************************************************************")
        print("            ENABLE PM  NEND - RCV - 1 DAY  [mode OFF]             ")
        print("******************************************************************")
        NE1.tl1.event_collection_start()

        zq_filter=TL1check()
        zq_filter.add_sst("FAF")

        zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::MVC4-{}-1&&-{}:::ALL,ALL,OFF,ALL:TMPER=BOTH;".format(zq_mtxlo_slot, E_MAX_MVC4))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_MAX_MVC4),zq_filter)
        time.sleep(E_TIMEOUT)

        NE1.tl1.event_collection_stop()

        QS_020_Verify_Report(self,zq_mtxlo_slot,E_MAX_MVC4,"A","MVC4","SET-PMMODE","REPT DBCHG")        

        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"NEND", "RCV", "1-DAY",True)                
		
        print("******************************************************************")
        print("            ENABLE PM  FEND - RCV - 1 DAY  [mode OFF]             ")
        print("******************************************************************")
        NE1.tl1.event_collection_start()

        zq_filter=TL1check()
        zq_filter.add_sst("FAF")

        zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::MVC4-{}-1&&-{}:::FEND,ALL,OFF,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_MAX_MVC4),zq_filter)
        time.sleep(E_TIMEOUT)

        NE1.tl1.event_collection_stop()

        QS_020_Verify_Report(self,zq_mtxlo_slot,E_MAX_MVC4,"A","MVC4","SET-PMMODE","REPT DBCHG")        

        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"FEND", "RCV", "1-DAY",True)                

        print("******************************************************************")
        print("            ENABLE PM  BIDIR - RCV - 1 DAY  [mode OFF]            ")
        print("******************************************************************")
        NE1.tl1.event_collection_start()

        zq_filter=TL1check()
        zq_filter.add_sst("PMI")

        zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::MVC4-{}-1&&-{}:::BIDIR,ALL,OFF,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_MAX_MVC4),zq_filter)
        time.sleep(E_TIMEOUT*4)

        NE1.tl1.event_collection_stop()

        QS_020_Verify_Report(self,zq_mtxlo_slot,E_MAX_MVC4,"A","MVC4","SET-PMMODE","REPT DBCHG")        

        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BIDIR", "RCV", "1-DAY",True)                
        '''
        
        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS NEND-RCV-1-DAY           ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","NEND", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","NEND", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","NEND", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","NEND", "RCV", "1-DAY",True)                
            
        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS NEND-TRMT-1-DAY          ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","NEND", "TRMT", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","NEND", "TRMT", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","NEND", "TRMT", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","NEND", "TRMT", "1-DAY",True)                
        
        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS FEND-RCV-1-DAY           ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","FEND", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","FEND", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","FEND", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","FEND", "RCV", "1-DAY",True)                
            
        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS FEND-TRMT-1-DAY          ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC","FEND", "TRMT", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC","FEND", "TRMT", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC","FEND", "TRMT", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC","FEND", "TRMT", "1-DAY",True)                

        print("******************************************************************")
        print("         VERIFY ELAPSED TIME PM COUNTERS BIDIR-RCV-1-DAY          ")
        print("******************************************************************")
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC-EG","BIDIR", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BBE-LOVC-IN","BIDIR", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC-EG","BIDIR", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"ES-LOVC-IN","BIDIR", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC-EG","BIDIR", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"SES-LOVC-IN","BIDIR", "RCV", "1-DAY",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"UAS-LOVC-BI","BIDIR", "RCV", "1-DAY",True)                

        self.stop_tps_block(NE1.id,"PM", "5-5-4-2")
        
        
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-LOVC3::MVC4TU3-{}-1&&-{}-1&&-3:::ALL,ALL,DISABLED,ALL:TMPER=BOTH;".format(zq_mtxlo_slot, E_MAX_MVC4))
        
        
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