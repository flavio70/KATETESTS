#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: This test verifies the detection/clearance of RDI alarm on MVC4TU12 facilities
:field Topology: 5
:field Dependency:
:field Lab: SVT
:field TPS: FM__5-2-15-1
:field RunSections: 11111
:field Author: tosima

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.instrumentONT     import InstrumentONT
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import *
import time
import string
import math
from inspect import currentframe

E_RFI_NUM = 2
E_BLOCK_SIZE = 64

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


def QS_010_Create_HO_XC_Block(zq_run, zq_slot, zq_start_block, zq_block_size, zq_xc_list):
    '''
    # Create zq_block_size HO cross-connection between STM1AU4x and LOPOOL
    # 
    # 
    '''
    zq_i = zq_start_block
    while zq_i < (zq_start_block+zq_block_size):
        zq_tl1_res=NE1.tl1.do("ENT-CRS-VC4::STM64AU4-{}-{},LOPOOL-1-1-1;".format(zq_slot,zq_i))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_xc_list.append(''.join(zq_msg.get_cmd_aid_list()))
            zq_j = zq_xc_list.index(''.join(zq_msg.get_cmd_aid_list()))
            dprint("\nOK\tCross-connection creation successfull {}".format(zq_xc_list[zq_j]),2)
            zq_run.add_success(NE1, "Cross-connection creation successfull {}".format(zq_xc_list[zq_j]),"0.0", "Cross-connection creation successfull")
            
        else:
            if zq_cmd[1]== 'COMPLD':    
                dprint("\nKO\tCross-connection creation failed {}\n".format(zq_xc_list[zq_j]),2)
                zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "Cross-connection creation failure","TL1 command fail "+ QS_000_Print_Line_Function())
            else:
                dprint("\nKO\tTL1 Cross-connection command DENY\n",2)
        zq_i += 1
    return


def QS_020_Delete_HO_XC_Block(zq_run, zq_slot, zq_start_block, zq_block_size, zq_xc_list):

    zq_i = zq_start_block
    while zq_i < (zq_start_block+zq_block_size):
        zq_tl1_res=NE1.tl1.do("DLT-CRS-VC4::{};".format(zq_xc_list[zq_i]))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("\nOK\tCross-connection deletion successful {}".format(zq_xc_list[zq_i]),2)
            zq_run.add_success(NE1, "Cross-connection deletion successful {}".format(zq_xc_list[zq_i]),"0.0", "Cross-connection deletion successful")
        else:    
            dprint("\nKO\tCross-connection deletion failed {}".format(zq_xc_list[zq_i]),2)
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "Cross-connection deletion failure","TL1 command fail "+ QS_000_Print_Line_Function())
    
        zq_i += 1

    return


def QS_030_Create_LO_XC_Block(zq_run, zq_vc4_1, zq_vc4_2, zq_xc_list):
    
    zq_tu12_list=zq_xc_list[zq_vc4_1].split(',')
    zq_tu12_tmp1=zq_tu12_list[1].replace('MVC4','MVC4TU12')

    zq_tu12_list=zq_xc_list[zq_vc4_2].split(',')
    zq_tu12_tmp2=zq_tu12_list[1].replace('MVC4','MVC4TU12')

    for zq_j in range (1,4):
        for zq_k in range(1,8):                                        #zq_k=TU12 index
            for zq_m in range(1,4):
                zq_tu12_idx1=zq_tu12_tmp1+'-'+str(zq_j)+'-'+str(zq_k)+'-'+str(zq_m)
                zq_tu12_idx2=zq_tu12_tmp2+'-'+str(zq_j)+'-'+str(zq_k)+'-'+str(zq_m)
                zq_tl1_res=NE1.tl1.do("ENT-CRS-LOVC12::{},{}:::2WAY;".format(zq_tu12_idx1,zq_tu12_idx2))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                dprint(NE1.tl1.get_last_outcome(),1)
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    dprint("\nOK\tCross-connection successfully created from {} to {}".format(zq_tu12_idx1,zq_tu12_idx2),2)
                    zq_run.add_success(NE1, "Cross-connection creation successful {} to {}".format(zq_tu12_idx1,zq_tu12_idx2),"0.0", "Cross-connection creation successful")
    
                else:
                    dprint("\nKO\tCross-connection creation failed from {} to {}".format(zq_tu12_idx1,zq_tu12_idx2),2)
                    zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "Cross-connection creation failure","TL1 command fail "+ QS_000_Print_Line_Function())


    return


def QS_040_Modify_AU4_HO_Trace_Block(zq_run, zq_slot, zq_start_block, zq_block_size, zq_trace):
    '''
    # 
    # 
    '''
    zq_i = zq_start_block
    while zq_i < (zq_start_block+zq_block_size):
        zq_tl1_res=NE1.tl1.do("ED-AU4::STM64AU4-{}-{}::::TRCEXPECTED={},EGTRCEXPECTED={};".format(zq_slot,zq_i,zq_trace,zq_trace))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("\nOK\tHO Trace Identifier changed to {} for STM64AU4-{}-{}".format(zq_trace,zq_slot,zq_i),2)
            zq_run.add_success(NE1, "HO Trace Identifier changed to {} for STM64AU4-{}-{}".format(zq_trace,zq_slot,zq_i),"0.0", "HO Trace Identifier changed")

        else:
            dprint("\nKO\tHO Trace Identifier change failure for STM64AU4-{}-{}".format(zq_slot,zq_i),2)
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "HO Trace Identifier change failure for STM64AU4-{}-{}".format(zq_slot,zq_i),"TL1 command fail "+ QS_000_Print_Line_Function())

        zq_i += 1
    return


def QS_050_Modify_MVC4_HO_Trace_Block(zq_run, zq_slot, zq_start_block, zq_block_size, zq_trace):

    zq_i = zq_start_block
    while zq_i < (zq_start_block+zq_block_size):
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::TRC={},TRCEXPECTED={};".format(zq_slot,zq_i,zq_trace,zq_trace))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("\nOK\tHO Trace Identifier changed to {} for MVC4-{}-{}".format(zq_trace,zq_slot,zq_i),2)
            zq_run.add_success(NE1, "HO Trace Identifier changed to {} for MVC4-{}-{}".format(zq_trace,zq_slot,zq_i),"0.0", "HO Trace Identifier changed")

        else:
            dprint("\nKO\tHO Trace Identifier change failure for MVC4-{}-{}".format(zq_slot,zq_i),2)
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "HO Trace Identifier change failure for MVC4-{}-{}".format(zq_slot,zq_i),"TL1 command fail "+ QS_000_Print_Line_Function())
        zq_i += 1
    return


def QS_060_Delete_LO_XC_Block(zq_run, zq_vc4_1, zq_vc4_2, zq_xc_list):

    zq_tu12_list=zq_xc_list[zq_vc4_1].split(',')
    zq_tu12_tmp1=zq_tu12_list[1].replace('MVC4','MVC4TU12')

    zq_tu12_list=zq_xc_list[zq_vc4_2].split(',')
    zq_tu12_tmp2=zq_tu12_list[1].replace('MVC4','MVC4TU12')

    for zq_j in range (1,4):
        for zq_k in range(1,8):                                        #zq_k=TU12 index
            for zq_m in range(1,4):
                zq_tu12_idx1=zq_tu12_tmp1+'-'+str(zq_j)+'-'+str(zq_k)+'-'+str(zq_m)
                zq_tu12_idx2=zq_tu12_tmp2+'-'+str(zq_j)+'-'+str(zq_k)+'-'+str(zq_m)
                zq_tl1_res=NE1.tl1.do("DLT-CRS-LOVC12::{},{};".format(zq_tu12_idx1,zq_tu12_idx2))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                dprint(NE1.tl1.get_last_outcome(),1)
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    dprint("\nOK\tCross-connection successfully deleted from {} to {}".format(zq_tu12_idx1,zq_tu12_idx2),2)
                    zq_run.add_success(NE1, "Cross-connection successfully deleted from {} to {}".format(zq_tu12_idx1,zq_tu12_idx2),"0.0", "Cross-connection successfully deleted")
    
                else:
                    dprint("\nKO\tCross-connection deletion failed from {} to {}".format(zq_tu12_idx1,zq_tu12_idx2),2)
                    zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "Cross-connection deletion failed from {} to {}".format(zq_tu12_idx1,zq_tu12_idx2),"TL1 command fail "+ QS_000_Print_Line_Function())
    
    return



def QS_070_Enable_Disable_POM(zq_run, zq_mtx_slot, zq_vc4, zq_enadis):

    zq_tu12_idx="MVC4TU12-{}-{}".format(zq_mtx_slot,str(zq_vc4))
    for zq_j in range (1,4):
        for zq_m in range (1,8):
            for zq_l in range (1,4):
                zq_tl1_res=NE1.tl1.do("ED-TU12::{}-{}-{}-{}::::POM={},EGPOM={};".format(zq_tu12_idx, str(zq_j), str(zq_m), str(zq_l), zq_enadis, zq_enadis))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                dprint(NE1.tl1.get_last_outcome(),1)
                zq_cmd=zq_msg.get_cmd_status()
            
                if zq_cmd == (True,'COMPLD'):
                    dprint("\nOK\tPom and EGPOM setting to [{}] for {}-{}-{}-{} successful".format(zq_enadis, zq_tu12_idx, str(zq_j), str(zq_m), str(zq_l)),2)
                    zq_run.add_success(NE1, "Pom and EGPOM setting to [{}] for {}-{}-{} successful".format(zq_enadis, zq_tu12_idx, str(zq_j), str(zq_m), str(zq_l)),"0.0", "Pom and EGPOM setting")
            
                else:
                    dprint("\nKO\tPom and EGPOM setting to [{}] for {}-{}-{}-{} failed".format(zq_enadis, zq_tu12_idx, str(zq_j), str(zq_m), str(zq_l)),2)
                    zq_run.add_failure(NE1,  "TL1 COMMAND","0.0", "Pom and EGPOM setting to [{}] for {}-{}-{}-{} failed".format(zq_enadis, zq_tu12_idx, str(zq_j), str(zq_m), str(zq_l)),"TL1 command fail "+ QS_000_Print_Line_Function())
                
    return


def QS_90_Check_Lovc12_RFI(zq_run,zq_tu12,zq_man_exp,zq_type_exp,zq_dir_exp):

    zq_tl1_res=NE1.tl1.do("RTRV-COND-LOVC12::{}:::RFI;".format(zq_tu12))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    dprint(NE1.tl1.get_last_outcome(),1)
    if (zq_msg.get_cmd_response_size() == 0):
        dprint("KO\tRFI Condition verification failure for {} facility : Exp [{}] - Rcv [0]".format(zq_tu12, E_RFI_NUM),2)
        zq_run.add_failure(NE1,"RFI Condition verification failure for {} facility : Exp [{}] - Rcv [0]".format(zq_tu12, E_RFI_NUM),"0.0", "RFI Condition verification failure: Exp [{}] - Rcv [0]".format(E_RFI_NUM),"RFI CONDITION CHECK "+ QS_000_Print_Line_Function())
    else:
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_man = zq_msg.get_cmd_attr_value("{},LOVC12".format(zq_tu12), 2)
            zq_type = zq_msg.get_cmd_attr_value("{},LOVC12".format(zq_tu12), 6)
            zq_dir = zq_msg.get_cmd_attr_value("{},LOVC12".format(zq_tu12), 7)
            if (zq_man == zq_man_exp) and (zq_type == zq_type_exp) and (zq_dir == zq_dir_exp):
                dprint("OK\tRFI Condition verification successful for {} facility.".format(zq_tu12),2)
                zq_run.add_success(NE1, "RFI Condition verification successful for {} facility.".format(zq_tu12),"0.0", "RFI CONDITION CHECK")
            else:
                dprint("KO\tRFI Condition verification failure for {} facility.".format(zq_tu12),2)
                dprint("\t\tCOND: Exp [{}]  - Rcv [{}]".format(zq_man_exp,zq_man),2)
                dprint("\t\tTYPE: Exp [{}] - Rcv [{}]".format(zq_type_exp,zq_type),2)
                dprint("\t\tDIR : Exp [{}]  - Rcv [{}]".format(zq_dir_exp,zq_dir),2)
                zq_run.add_failure(NE1,"RFI Condition verification failure for {} facility : Exp: [{}-{}-{}] - Rcv [{}-{}-{}]".format(zq_tu12,zq_man_exp,zq_type_exp,zq_dir_exp,zq_man,zq_type,zq_dir),"0.0", "RFI Condition verification failure for {} facility : Exp: [{}-{}-{}] - Rcv [{}-{}-{}]".format(zq_man_exp,zq_type_exp,zq_dir_exp,zq_man,zq_type,zq_dir),"RFI CONDITION CHECK "+ QS_000_Print_Line_Function())
        
    return


def QS_100_Check_RDI(zq_run, zq_ONT_p1, zq_ONT_p2, zq_mtx_slot, zq_vc4_1, zq_vc4_2):

   
    for zq_j in range (1,2):
        for zq_m in range (1,2):
            for zq_l in range (1,2):
                zq_tu12_ch1="{}.{}.{}.{}".format(str(zq_vc4_1 % E_BLOCK_SIZE),str(zq_j),str(zq_m),str(zq_l))
                zq_tu12_ch2="{}.{}.{}.{}".format(str(zq_vc4_2 % E_BLOCK_SIZE),str(zq_j),str(zq_m),str(zq_l))

                zq_tu12_idx1="MVC4TU12-{}-{}-{}-{}-{}".format(zq_mtx_slot,str(zq_vc4_1),str(zq_j),str(zq_m),str(zq_l))
                zq_tu12_idx2="MVC4TU12-{}-{}-{}-{}-{}".format(zq_mtx_slot,str(zq_vc4_2),str(zq_j),str(zq_m),str(zq_l))

                ONT.get_set_rx_lo_measure_channel(zq_ONT_p1, zq_tu12_ch1)
                ONT.get_set_rx_lo_measure_channel(zq_ONT_p2, zq_tu12_ch2)
            
                ONT.get_set_tx_lo_measure_channel(zq_ONT_p1, zq_tu12_ch1)
                ONT.get_set_tx_lo_measure_channel(zq_ONT_p2, zq_tu12_ch2)
                
                ONT.get_set_alarm_insertion_mode(zq_ONT_p1, "LO", "CONT")
                ONT.get_set_alarm_insertion_mode(zq_ONT_p2, "LO", "CONT")
        
                ONT.get_set_alarm_insertion_type(zq_ONT_p1, "LPRDI")
                ONT.get_set_alarm_insertion_type(zq_ONT_p2, "LPRDI")
        
                ONT.get_set_alarm_insertion_activation(zq_ONT_p1,"LO","ON")
        
                time.sleep(10)
        
                QS_90_Check_Lovc12_RFI(zq_run,zq_tu12_idx1,"RFI","FEND","RCV")
                QS_90_Check_Lovc12_RFI(zq_run,zq_tu12_idx2,"RFI","FEND","TRMT")
                
                ONT.get_set_alarm_insertion_activation(zq_ONT_p1,"LO","OFF")
                ONT.get_set_alarm_insertion_activation(zq_ONT_p2,"LO","ON")
        
                time.sleep(10)
        
                QS_90_Check_Lovc12_RFI(zq_run,zq_tu12_idx1,"RFI","FEND","TRMT")
                QS_90_Check_Lovc12_RFI(zq_run,zq_tu12_idx2,"RFI","FEND","RCV")
            
                ONT.get_set_alarm_insertion_activation(zq_ONT_p2,"LO","OFF")
    
    
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
        ONT.init_instrument(ONT_P1)
        ONT.init_instrument(ONT_P2)


    def test_body(self):
        '''
        test Body Section implementation
        insert Main body code for your test below
        '''
        print("\n******************** START ********************")
        '''
        VERIFY DETECTION OF RFI CONDITION ALARM IN MVC4TU12 FACILITIES
        '''
        print("\n*******************************************************************")
        print("\n   VERIFY DETECTION OF RFI CONDITION ALARM IN MVC4TU12 FACILITIES  ")
        print("\n*******************************************************************")
        
        self.start_tps_block(NE1.id,"FM", "5-2-15-1")

        E_LO_MTX = "MXH60GLO"
        
        E_SLOT = ['2','3','4','5','6','7','8','12','13','14','15','16','17','18','19']
        E_HO_TI = 'X4F4E5420484F2D5452414345202020' #'ONT HO-TRACE   '

        E_VC4_1_1 = 34      # <64
        E_VC4_1_2 = 92      # 65<x<129
        E_VC4_2_1 = 189     # 128<x<193
        E_VC4_2_2 = 227     # 192<x<257
        E_VC4_3_1 = 289     # 256<x<321
        E_VC4_3_2 = 356     # 320<x<385
        
        zq_mtxlo_slot=NE1_M1
        NE1_stm64p1=NE1_S1
        NE1_stm64p2=NE1_S2
        zq_board_to_remove=list()
        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")


        '''
        Board equipment if not yet!
        '''
        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot), policy='DENY')
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'DENY'):
            print("Board already equipped")
        else:
            zq_filter=TL1check()
            zq_filter.add_pst("IS")
            zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
            NE1.tl1.do_until("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),zq_filter)

        '''
        Change MVC4 structure to 63xTU12 for preset VC4
        '''
        zq_filter=TL1check()
        zq_filter.add_field('LOSTRUCT', '63xTU12')
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_1_1))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_1_1),zq_filter)

        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_1_2))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_1_2),zq_filter)

        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_2_1))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_2_1),zq_filter)
        
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_2_2))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_2_2),zq_filter)
        
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_3_1))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_3_1),zq_filter)
        
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_3_2))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_3_2),zq_filter)


        '''
        Find 4 free slots and equip 4 x 1P10GSOE
        '''
        zq_filter=TL1check()
        zq_filter.add_pst("OOS-AU")
        zq_tl1_res=NE1.tl1.do("RTRV-EQPT::ALL;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_num=0
            zq_i = 0
            zq_aid_list=zq_msg.get_cmd_aid_list()
            while ((zq_i in range(0,len(zq_aid_list))) and (zq_num < 4)):
                if (('MDL' in zq_aid_list[zq_i]) and (''.join(zq_aid_list[zq_i]).count('-') == 3)):
                    zq_slot=''.join(zq_aid_list[zq_i])
                    zq_slot=zq_slot.split('-')
                    if (zq_slot[3] in E_SLOT):
                        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}::::PROVISIONEDTYPE=1P10GSOE;".format(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO')))
                        NE1.tl1.do_until("RTRV-EQPT::{};".format(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO')),zq_filter)
                        print('Board Equipped: {}'.format(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO')))
                        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-1::::PROVISIONEDTYPE=XI-641;".format(''.join(zq_aid_list[zq_i]).replace('MDL','XFP')))
                        zq_board_to_remove.append(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO'))
                        print('\tXFP equipped: {}-1'.format(''.join(zq_aid_list[zq_i]).replace('MDL','XFP')))
                        zq_num += 1
                zq_i += 1

            
        NE1_stm64p3 = (''.join(zq_board_to_remove[0]).replace('10GSO-',''))+'-1'
        NE1_stm64p4 = (''.join(zq_board_to_remove[1]).replace('10GSO-',''))+'-1'
        NE1_stm64p5 = (''.join(zq_board_to_remove[2]).replace('10GSO-',''))+'-1'
        NE1_stm64p6 = (''.join(zq_board_to_remove[3]).replace('10GSO-',''))+'-1'

        
        print("\n******************************************************************************")
        print("\n   CHECK RFI CONDITION ALARM FOR TWO MVC4TU12 FACILITIES IN 1st 128 BLOCK     ")
        print("\n******************************************************************************")
        '''
        CHECK RFI CONDITION ALARM FOR TWO MVC4TU12 FACILITIES IN FIRST 128 BLOCK 
        '''
        QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_040_Modify_AU4_HO_Trace_Block(self, NE1_stm64p1, (E_VC4_1_1 % E_BLOCK_SIZE), 1, E_HO_TI)
        QS_040_Modify_AU4_HO_Trace_Block(self, NE1_stm64p2, (E_VC4_1_2 % E_BLOCK_SIZE), 1, E_HO_TI)
        
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_1_1, 1, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_1_2, 1, E_HO_TI)
        
        QS_030_Create_LO_XC_Block(self, E_VC4_1_1, E_VC4_1_2, zq_xc_list)
        
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_1, "Y")
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_2, "Y")

        '''
        Configure both ONT ports to VC12 mapping
        '''
        ONT.get_set_tx_bit_rate(ONT_P1, "STM64")
        ONT.get_set_tx_bit_rate(ONT_P2, "STM64")
        
        ONT.get_set_rx_channel_mapping_size(ONT_P1, "VC12")
        ONT.get_set_rx_channel_mapping_size(ONT_P2, "VC12")
        
        ONT.get_set_tx_channel_mapping_size(ONT_P1, "VC12")
        ONT.get_set_tx_channel_mapping_size(ONT_P2, "VC12")

        ONT.get_set_laser_status(ONT_P1, "ON")
        ONT.get_set_laser_status(ONT_P2, "ON")

        ONT.get_set_clock_reference_source(ONT_P1, "RX")
        ONT.get_set_clock_reference_source(ONT_P2, "RX")
        
        ONT.get_set_background_channels_fill_mode(ONT_P1, "FIX")
        ONT.get_set_background_channels_fill_mode(ONT_P2, "FIX")

        QS_100_Check_RDI(self, "P1", "P2", zq_mtxlo_slot, E_VC4_1_1, E_VC4_1_2)

        QS_060_Delete_LO_XC_Block(self, E_VC4_1_1, E_VC4_1_2, zq_xc_list)

        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_1, "N")
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_2, "N")

        QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        print("\n******************************************************************************")
        print("\n   CHECK RFI CONDITION ALARM FOR TWO MVC4TU12 FACILITIES IN 2nd 128 BLOCK     ")
        print("\n******************************************************************************")
        '''
        CHECK RFI CONDITION ALARM FOR TWO MVC4TU12 FACILITIES IN SECOND 128 BLOCK 
        '''
        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")

        QS_010_Create_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p4, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_2_1, 1, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_2_2, 1, E_HO_TI)

        QS_030_Create_LO_XC_Block(self, E_VC4_2_1, E_VC4_2_2, zq_xc_list)
        
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_1, "Y")
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_2, "Y")

        QS_100_Check_RDI(self, "P1", "P2", zq_mtxlo_slot, E_VC4_2_1, E_VC4_2_2)
        
        QS_060_Delete_LO_XC_Block(self, E_VC4_2_1, E_VC4_2_2, zq_xc_list)

        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_1, "N")
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_2, "N")

        QS_020_Delete_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p4, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)
        
        print("\n******************************************************************************")
        print("\n   CHECK RFI CONDITION ALARM FOR TWO MVC4TU12 FACILITIES IN 3rd 128 BLOCK     ")
        print("\n******************************************************************************")
        '''
        CHECK RFI CONDITION ALARM FOR TWO MVC4TU12 FACILITIES IN THIRD 128 BLOCK 
        '''
        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")

        QS_010_Create_HO_XC_Block(self, NE1_stm64p5, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p6, 1, E_BLOCK_SIZE, zq_xc_list)
        
        QS_010_Create_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p4, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)
        
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_3_1, 1, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_3_2, 1, E_HO_TI)
        
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_1, "Y")
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_2, "Y")

        QS_030_Create_LO_XC_Block(self, E_VC4_3_1, E_VC4_3_2, zq_xc_list)
        
        QS_100_Check_RDI(self, "P1", "P2", zq_mtxlo_slot, E_VC4_3_1, E_VC4_3_2)

        QS_060_Delete_LO_XC_Block(self, E_VC4_3_1, E_VC4_3_2, zq_xc_list)

        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_1, "N")
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_2, "N")

        QS_020_Delete_HO_XC_Block(self, NE1_stm64p5, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p6, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        QS_020_Delete_HO_XC_Block(self, NE1_stm64p3, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p4, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)
        
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, E_BLOCK_SIZE*4+1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE*5+1, E_BLOCK_SIZE, zq_xc_list)

        '''
        Delete equipped 4 x 1P10GSO
        '''
        zq_filter=TL1check()
        zq_filter.add_pst("OOS-AUMA")
        for zq_i in range(0,len(zq_board_to_remove)):
            zq_tl1_res=NE1.tl1.do("RMV-EQPT::{}-1;".format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','XFP')))
            NE1.tl1.do_until("RTRV-EQPT::{}-1;".format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','XFP')),zq_filter)
            zq_tl1_res=NE1.tl1.do("DLT-EQPT::{}-1;".format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','XFP')))
            NE1.tl1.do_until("RTRV-EQPT::{}-1;".format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','MDL')),zq_filter)
            print('\tXFP Deleted: {}-1'.format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','MDL')))
            
            zq_tl1_res=NE1.tl1.do("RMV-EQPT::{};".format(''.join(zq_board_to_remove[zq_i])))
            NE1.tl1.do_until("RTRV-EQPT::{};".format(''.join(zq_board_to_remove[zq_i])),zq_filter)
            zq_tl1_res=NE1.tl1.do("DLT-EQPT::{};".format(''.join(zq_board_to_remove[zq_i])))
            NE1.tl1.do_until("RTRV-EQPT::{};".format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','MDL')),zq_filter)
            print('Board Deleted: {}'.format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','MDL')))

        '''
        Restore MVC4 structure to 3xTU3 for preset VC4
        '''
        zq_filter=TL1check()
        zq_filter.add_field('LOSTRUCT', '3xTU3')
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_1_1))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_1_1),zq_filter)

        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_1_2))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_1_2),zq_filter)

        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_2_1))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_2_1),zq_filter)
        
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_2_2))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_2_2),zq_filter)
        
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_3_1))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_3_1),zq_filter)
        
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_3_2))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_3_2),zq_filter)

        self.stop_tps_block(NE1.id,"FM", "5-2-15-1")

       
    def test_cleanup(self):
        '''
        test Cleanup Section implementation
        insert CleanUp code for your test below
        '''
        ONT.deinit_instrument(ONT_P1)
        ONT.deinit_instrument(ONT_P2)


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
    NE1_S1=NE1.get_preset("S1")
    NE1_S2=NE1.get_preset("S2")
    ONT=InstrumentONT('ONT1', CTEST.kenvironment)
    ONT_P1="P1"
    ONT_P2="P2"
    CTEST.add_eqpt(NE1)

    # Run Test main flow
    # Please don't touch this code
    CTEST.run()
    