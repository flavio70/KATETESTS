#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: This test provides a method to enable the PM counter  
:field Description: mode ON/OFF for MVC4 facilities.
:field Topology: 7
:field Dependency: NA
:field Lab: SVT
:field TPS: PM__5-5-1-1
:field TPS: PM__5-5-1-2
:field TPS: PM__5-5-1-3
:field TPS: PM__5-5-1-4
:field TPS: PM__5-5-1-5
:field TPS: PM__5-5-2-1
:field TPS: PM__5-5-2-2
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
from inspect import currentframe

E_MAX_MVC4 = 384
E_LO_MTX = "MXH60GLO"
E_TIMEOUT = 20

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
    
    zq_tl1_res=NE1.tl1.do("RTRV-PTF::MVC4-{}-1&&-384::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    zq_sst_counter=0
    if zq_cmd == (True,'COMPLD'):
        for zq_i in range(1,zq_sst_counter_exp+1):
            zq_sst=zq_msg.get_cmd_sst("MVC4-{}-{}".format(zq_mtxlo_slot, zq_i))
            if zq_sst_exp in zq_sst[0]:
                zq_sst_counter = zq_sst_counter+1

    if zq_sst_counter == zq_sst_counter_exp:
        dprint("OK\tNumber of MVC4 with SST containing PMD is correct: {}".format(zq_sst_counter),2)
        zq_run.add_success(NE1, "EVENTS COLLECTION","0.0", "Number of MVC4 with SST containing PMD is correct: {}".format(zq_sst_counter))
    else:
        dprint("KO\tNumber of MVC4 with SST containing PMD expected: {}".format(str(zq_sst_counter_exp)),2)
        dprint("\tNumber of MVC4 with SST containing PMD received: {}".format(zq_sst_counter),2)
        zq_run.add_failure(NE1, "EVENTS COLLECTION","0.0", "MVC4 with SST containing PMD exp.[{}] rcv.[{}]".format(str(zq_sst_counter_exp), zq_sst_counter),
                                "MVC4 with SST containing PMD exp.[{}] rcv.[{}] {}".format(str(zq_sst_counter_exp),zq_sst_counter,QS_000_Print_Line_Function()))

    return

def QS_020_Verify_Report(zq_run,zq_mtxlo_slot,zq_report_exp,zq_marker,zq_aid,zq_cmd,zq_report_type):     

    zq_idx = 1
    zq_dbchg_num = 0
    zq_event_num=int(NE1.tl1.event_collection_size("A"))
    print("Number of event received: {}".format(zq_event_num))
    if zq_event_num > 0:
        for zq_idx in range(1,zq_report_exp+1):
            zq_elem = NE1.tl1.event_collection_get(zq_marker, aid="{}-{}-{}".format(zq_aid,zq_mtxlo_slot,str(zq_idx)), cmd=zq_cmd)
            if len(zq_elem) != 0:
                if zq_elem[0]._TL1message__m_coded['S_VMM'] == zq_report_type:
                    zq_dbchg_num += 1
            
    if zq_dbchg_num == zq_report_exp:
        dprint("OK\tNumber of MVC4 REPT DBCHG is correct: {}".format(zq_dbchg_num),2)
        zq_run.add_success(NE1, "EVENTS COLLECTION","0.0", "Number of MVC4 REPT DBCHG is correct: {}".format(zq_dbchg_num))
    else:
        dprint("KO\tNumber of MVC4 REPT DBCHG expected: {}".format(zq_report_exp),2)
        dprint("\tNumber of MVC4 REPT DBCHG received: {}".format(zq_dbchg_num),2)
        zq_run.add_failure(NE1, "EVENTS COLLECTION","0.0", "MVC4 REPT DBCHG exp.[{}] rcv.[{}]".format(zq_report_exp, zq_dbchg_num),
                                "MVC4 REPT DBCHG exp.[{}] rcv.[{}] {}".format(zq_report_exp, zq_dbchg_num,QS_000_Print_Line_Function()))

    return

def QS_030_Verify_PM(zq_msg, zq_aid, zq_locn_exp, zq_dir_exp, zq_period_exp, zq_pmstate_exp):

    zq_res = False
    zq_locn=zq_msg.get_cmd_attr_value(zq_aid, "1")
    zq_pmstate=zq_msg.get_cmd_attr_value(zq_aid, "PMSTATE")
    zq_dir = zq_msg.get_cmd_attr_value(zq_aid, "DIRN")
    zq_period=zq_msg.get_cmd_attr_value(zq_aid, "TMPER")
    
    if  zq_locn[0] == zq_locn_exp and \
        zq_dir[0] == zq_dir_exp and \
        zq_period[0] == zq_period_exp and \
        zq_pmstate[0] == zq_pmstate_exp:
        
        zq_res = True
        
    
    return zq_res

def QS_040_Get_PM_Time(zq_run, zq_mtxlo_slot, zq_locn, zq_dir, zq_period):

    zq_time_list=list()
    zq_tmp = "UAS-HOVC"
    if zq_locn == "BIDIR":
        zq_tmp = zq_tmp + "-BI"
    for zq_i in range(1,E_MAX_MVC4+1):
        zq_tl1_res=NE1.tl1.do("RTRV-PM-VC4::MVC4-{}-{}:::{},0-UP,{},{},{};".format(zq_mtxlo_slot, str(zq_i),zq_tmp, zq_locn,zq_dir,zq_period))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            if zq_msg.get_cmd_response_size() != 0:
                zq_time_str=zq_msg.get_cmd_attr_value("MVC4-{}-{},VC4".format(zq_mtxlo_slot, str(zq_i)), "9")
                zq_sec_ary = zq_time_str[0].split("-")
                zq_time_list.append(zq_sec_ary[2])
            
    return zq_time_list

def QS_050_Check_PM_Time(zq_run,zq_mtxlo_slot, zq_locn, zq_dir, zq_period, zq_check_zero=False):

    zq_counter=0
    zq_not_elapsed_counter=0
    zq_time1= QS_040_Get_PM_Time(zq_run, zq_mtxlo_slot, zq_locn, zq_dir, zq_period)
    zq_time2= QS_040_Get_PM_Time(zq_run, zq_mtxlo_slot, zq_locn, zq_dir, zq_period)
    if len(zq_time1)!= 0 and \
       len(zq_time2)!= 0:
        zq_range = len(zq_time1)
        if zq_range > len(zq_time2):
            zq_range = len(zq_time2)
            
        for zq_i in range(1,zq_range+1):
            if abs(int(zq_time2[zq_i-1])-int(zq_time1[zq_i-1])) != 0:
                zq_counter=zq_counter+1
            else:
                zq_not_elapsed_counter=zq_not_elapsed_counter+1
        
        if zq_check_zero:
            if zq_not_elapsed_counter == E_MAX_MVC4:
                dprint("OK\tPM counter time NOT increased for {} MVC4s".format(zq_not_elapsed_counter),2)
                zq_run.add_success(NE1, "PM COUNTER CHECK","0.0"
                                      , "PM counter time NOT increased for {} MVC4s".format(zq_not_elapsed_counter))
            else:
                dprint("KO\tPM counter time NOT increased for MVC4s expected: {} ".format(E_MAX_MVC4),2)
                dprint("\tPM counter time NOT increased for MVC4s received: {} ".format(zq_not_elapsed_counter),2)
                zq_run.add_failure(NE1, "PM COUNTER CHECK","0.0", "PM counter time NOT increased for MVC4s exp.[{}] - rcv.[{}] ".format(E_MAX_MVC4,zq_not_elapsed_counter)
                                      ,"PM counter time NOT increased for MVC4s exp.[{}] - rcv.[{}] {}".format(E_MAX_MVC4,zq_not_elapsed_counter,QS_000_Print_Line_Function()))
        else:
            if zq_counter == E_MAX_MVC4:
                dprint("OK\tPM counter time increased for {} MVC4s".format(zq_counter),2)
                zq_run.add_success(NE1, "PM COUNTER CHECK","0.0"
                                      , "PM counter time increased for {} MVC4s".format(zq_counter))
            else:
                dprint("KO\tPM counter time increased for MVC4s expected: {} ".format(E_MAX_MVC4),2)
                dprint("\tPM counter time increased for MVC4s received: {} ".format(zq_counter),2)
                zq_run.add_failure(NE1, "PM COUNTER CHECK","0.0", "PM counter time increased for MVC4s exp.[{}] - rcv.[{}] ".format(E_MAX_MVC4,zq_counter)
                                      ,"PM counter time increased for MVC4s exp.[{}] - rcv.[{}] {}".format(E_MAX_MVC4,zq_counter,QS_000_Print_Line_Function()))

    else:
        dprint("KO\tError retrieving PM counter.",2)
        zq_run.add_failure(NE1, "PM COUNTER CHECK","0.0", "Error retrieving PM counter."
                              ,"Error retrieving PM counter. {}".format(QS_000_Print_Line_Function()))
        
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
        
        self.start_tps_block(NE1.id,"PM", "5-5-1-1")

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
            if zq_attr_list1[0] is not None:
                if zq_attr_list1[0]['PROVISIONEDTYPE']==E_LO_MTX and zq_attr_list1[0]['ACTUALTYPE']==E_LO_MTX:  #Board equipped 
                    print("Board already equipped")
                else:
                    zq_filter=TL1check()
                    zq_filter.add_pst("IS")
                    zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                    NE1.tl1.do_until("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),zq_filter)
            else:
                if zq_attr_list2[0] is not None:
                    if zq_attr_list2[0]['ACTUALTYPE']==E_LO_MTX:  #Equip Board 
                        zq_filter=TL1check()
                        zq_filter.add_pst("IS")
                        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                        NE1.tl1.do_until("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),zq_filter)


        print("******************************************************************")
        print("                 VERIFY SST of MVC4 contains PMD                  ")
        print("******************************************************************")

        QS_010_Verify_SST(self, zq_mtxlo_slot, 'PMD', E_MAX_MVC4) 
            

        NE1.tl1.event_collection_start()
        time.sleep(10)

        zq_filter=TL1check()
        zq_filter.add_sst("FAF")
        
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::MVC4-{}-1&&-{}:::NEND,ALL,ON,RCV:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_MAX_MVC4),zq_filter)
        time.sleep(E_TIMEOUT)

        NE1.tl1.event_collection_stop()

        QS_020_Verify_Report(self,zq_mtxlo_slot,E_MAX_MVC4,"A","MVC4","SET-PMMODE","REPT DBCHG")        

        ########################################################
        # Verify 'PMD' is not present in MVC4 SST 
        ########################################################

        QS_010_Verify_SST(self, zq_mtxlo_slot, 'PMD', 0) 

        print("******************************************************************")
        print("            ENABLE PM  NEND - RCV - 15 MIN      [mode ON]         ")
        print("******************************************************************")

        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-VC4::MVC4-{}-1&&-{}:::NEND,RCV:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                zq_aid="MVC4-{}-{}".format(zq_mtxlo_slot, str(zq_i))
                if QS_030_Verify_PM(zq_msg, zq_aid, "NEND", "RCV", "15-MIN", "ON"):
                    zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4:
            dprint("OK\tPM set to [NEND,RCV,15-MIN,ON] for {} MVC4s".format(zq_counter),2)
            self.add_success(NE1, "PM set to [NEND,RCV,15-MIN,ON] for {} MVC4s".format(zq_counter),"0.0" 
                                  , "PM set to [NEND,RCV,15-MIN,ON] for {} MVC4s".format(zq_counter))
        else:
            dprint("KO\tPM set to [NEND,RCV,15-MIN,ON] for {} MVC4s instead of {}".format(zq_counter, E_MAX_MVC4),2)
            self.add_failure(NE1,"PM set to [NEND,RCV,15-MIN,ON] for {} MVC4s instead of {}".format(zq_counter, E_MAX_MVC4),"0.0"
                                ,"PM STATUS CHECK","PM set to [NEND,RCV,15-MIN,ON] for {} MVC4s instead of {} {}".format(zq_counter,E_MAX_MVC4,QS_000_Print_Line_Function()))

        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"NEND", "RCV", "15-MIN")                
            
        self.stop_tps_block(NE1.id,"PM", "5-5-1-1")
 
        self.start_tps_block(NE1.id,"PM", "5-5-1-2")
        print("******************************************************************")
        print("            ENABLE PM  FEND - RCV - 15 MIN     [mode ON]          ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::MVC4-{}-1&&-{}:::FEND,ALL,ON,RCV:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-VC4::MVC4-{}-1&&-{}:::FEND,RCV:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                zq_aid="MVC4-{}-{}".format(zq_mtxlo_slot, str(zq_i))
                if QS_030_Verify_PM(zq_msg, zq_aid, "FEND", "RCV", "15-MIN", "ON"):
                    zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4:
            dprint("OK\tPM set to [FEND,RCV,15-MIN,ON] for {} MVC4s".format(zq_counter),2)
            self.add_success(NE1, "PM set to [FEND,RCV,15-MIN,ON] for {} MVC4s".format(zq_counter),"0.0" 
                                  , "PM set to [FEND,RCV,15-MIN,ON] for {} MVC4s".format(zq_counter))
        else:
            dprint("KO\tPM set to [FEND,RCV,15-MIN,ON] for {} MVC4s instead of {}".format(zq_counter, E_MAX_MVC4),2)
            self.add_failure(NE1,"PM set to [FEND,RCV,15-MIN,ON] for {} MVC4s instead of {}".format(zq_counter, E_MAX_MVC4),"0.0"
                                ,"PM STATUS CHECK","PM set to [FEND,RCV,15-MIN,ON] for {} MVC4s instead of {} {}".format(zq_counter, E_MAX_MVC4,QS_000_Print_Line_Function()))

        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"FEND", "RCV", "15-MIN")                

        self.stop_tps_block(NE1.id,"PM", "5-5-1-2")
        
        
        self.start_tps_block(NE1.id,"PM", "5-5-1-3")
        print("******************************************************************")
        print("            ENABLE PM  NEND - RCV - 1 DAY    [mode ON]            ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::MVC4-{}-1&&-{}:::NEND,ALL,ON,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-VC4::MVC4-{}-1&&-{}:::NEND,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                zq_aid="MVC4-{}-{}".format(zq_mtxlo_slot, str(zq_i))
                if QS_030_Verify_PM(zq_msg, zq_aid, "NEND", "RCV", "1-DAY", "ON"):
                    zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4:
            dprint("OK\tPM set to [NEND,RCV,1-DAY,ON] for {} MVC4s".format(zq_counter),2)
            self.add_success(NE1, "PM set to [NEND,RCV,1-DAY,ON] for {} MVC4s".format(zq_counter),"0.0" 
                                  , "PM set to [NEND,RCV,1-DAY,ON] for {} MVC4s".format(zq_counter))
        else:
            dprint("KO\tPM set to [NEND,RCV,1-DAY,ON] for {} MVC4s instead of {}".format(zq_counter, E_MAX_MVC4),2)
            self.add_failure(NE1,"PM set to [NEND,RCV,1-DAY,ON] for {} MVC4s instead of {}".format(zq_counter, E_MAX_MVC4),"0.0"
                                ,"PM STATUS CHECK","PM set to [NEND,RCV,1-DAY,ON] for {} MVC4s instead of {} {}".format(zq_counter,E_MAX_MVC4,QS_000_Print_Line_Function()))
            
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"NEND", "RCV", "1-DAY")                

        self.stop_tps_block(NE1.id,"PM", "5-5-1-3")
 
        self.start_tps_block(NE1.id,"PM", "5-5-1-4")
        print("******************************************************************")
        print("            ENABLE PM  FEND - RCV - 1 DAY    [mode ON]            ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::MVC4-{}-1&&-{}:::FEND,ALL,ON,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-VC4::MVC4-{}-1&&-{}:::FEND,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                zq_aid="MVC4-{}-{}".format(zq_mtxlo_slot, str(zq_i))
                if QS_030_Verify_PM(zq_msg, zq_aid, "FEND", "RCV", "1-DAY", "ON"):
                    zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4:
            dprint("OK\tPM set to [FEND,RCV,1-DAY,ON] for {} MVC4s".format(zq_counter),2)
            self.add_success(NE1, "PM set to [FEND,RCV,1-DAY,ON] for {} MVC4s".format(zq_counter),"0.0" 
                                  , "PM set to [FEND,RCV,1-DAY,ON] for {} MVC4s".format(zq_counter))
        else:
            dprint("KO\tPM set to [FEND,RCV,1-DAY,ON] for {} MVC4s instead of {}".format(zq_counter, E_MAX_MVC4),2)
            self.add_failure(NE1,"PM set to [FEND,RCV,1-DAY,ON] for {} MVC4s instead of {}".format(zq_counter, E_MAX_MVC4),"0.0"
                                ,"PM STATUS CHECK","PM set to [FEND,RCV,1-DAY,ON] for {} MVC4s instead of {} {}".format(zq_counter,E_MAX_MVC4,QS_000_Print_Line_Function()))

        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"FEND", "RCV", "1-DAY")                

        self.stop_tps_block(NE1.id,"PM", "5-5-1-4")
        

        self.start_tps_block(NE1.id,"PM", "5-5-1-5")
        print("******************************************************************")
        print("            ENABLE PM  BIDIR - RCV - 1 DAY   [mode ON]            ")
        print("******************************************************************")
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::MVC4-{}-1&&-{}:::BIDIR,ALL,ON,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        time.sleep(E_TIMEOUT)
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-VC4::MVC4-{}-1&&-{}:::BIDIR,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_counter = 0
            for zq_i in range(1,E_MAX_MVC4+1):
                zq_aid="MVC4-{}-{}".format(zq_mtxlo_slot, str(zq_i))
                if QS_030_Verify_PM(zq_msg, zq_aid, "BIDIR", "RCV", "1-DAY", "ON"):
                    zq_counter = zq_counter+1

        if zq_counter == E_MAX_MVC4:
            dprint("OK\tPM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4s".format(zq_counter),2)
            self.add_success(NE1, "PM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4s".format(zq_counter),"0.0" 
                                  , "PM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4s".format(zq_counter))
        else:
            dprint("KO\tPM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4s instead of {}".format(zq_counter, E_MAX_MVC4),2)
            self.add_failure(NE1,"PM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4s instead of {}".format(zq_counter, E_MAX_MVC4),"0.0"
                                ,"PM STATUS CHECK","PM set to [BIDIR,RCV,1-DAY,ON] for {} MVC4s instead of {} {}".format(zq_counter, E_MAX_MVC4,QS_000_Print_Line_Function()))

        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"BIDIR", "RCV", "1-DAY")                

        self.stop_tps_block(NE1.id,"PM", "5-5-1-5")
        
        
        self.start_tps_block(NE1.id,"PM", "5-5-2-1")
        print("******************************************************************")
        print("         ENABLE PM  NEND,FEND,BIDIR - RCV - 15 MIN [mode OFF]     ")
        print("******************************************************************")
        NE1.tl1.event_collection_start()

        zq_filter=TL1check()
        zq_filter.add_sst("FAF")

        zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::MVC4-{}-1&&-{}:::ALL,ALL,OFF,RCV:TMPER=15-MIN;".format(zq_mtxlo_slot, E_MAX_MVC4))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_MAX_MVC4),zq_filter)
        time.sleep(E_TIMEOUT)

        NE1.tl1.event_collection_stop()

        QS_020_Verify_Report(self,zq_mtxlo_slot,E_MAX_MVC4,"A","MVC4","SET-PMMODE","REPT DBCHG")        

        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"NEND", "RCV", "15-MIN",True)                
        QS_050_Check_PM_Time(self, zq_mtxlo_slot,"FEND", "RCV", "15-MIN",True)                
                   
        
        self.stop_tps_block(NE1.id,"PM", "5-5-2-1")
        
        

        self.start_tps_block(NE1.id,"PM", "5-5-2-2")
        print("******************************************************************")
        print("            ENABLE PM  NEND - RCV - 1 DAY  [mode OFF]             ")
        print("******************************************************************")
        NE1.tl1.event_collection_start()

        zq_filter=TL1check()
        zq_filter.add_sst("FAF")

        zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::MVC4-{}-1&&-{}:::NEND,ALL,OFF,RCV:TMPER=1-DAY;".format(zq_mtxlo_slot, E_MAX_MVC4))
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
        
        
        self.stop_tps_block(NE1.id,"PM", "5-5-2-2")
        
        
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::MVC4-1-1-7-1&&-384:::ALL,ALL,DISABLED,RCV:TMPER=BOTH;")
        
        
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
    