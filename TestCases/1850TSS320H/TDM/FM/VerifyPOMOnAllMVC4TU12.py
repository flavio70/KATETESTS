#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: Check that when enabling and disabling POM and EGPOM on MVC4TU12
:field Description: no alarms/errors are generating on SDH. All 384x3x21=24192 TU12s 
:field Description: are verified. 
:field Description: S1 and S2 port on NE must be STM64
:field Topology: 5 
:field Dependency: NA
:field Lab: SVT
:field TPS: FM__8-1-4-1
:field RunSections: 11111 
:field Author: tosima

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.instrumentONT     import InstrumentONT
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import *
import time
import math
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


def QS_030_Create_LO_XC_Block(zq_run, zq_start_block, zq_block_size, zq_xc_list):
    
    zq_i = zq_start_block
    while zq_i < (zq_start_block+zq_block_size):
        zq_tu12_list=zq_xc_list[zq_i].split(',')
        zq_tu12_tmp1=zq_tu12_list[1].replace('MVC4','MVC4TU12')

        zq_tu12_list=zq_xc_list[zq_i+zq_block_size].split(',')
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

        zq_i += 1

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



def QS_060_Delete_LO_XC_Block(zq_run, zq_start_block, zq_block_size, zq_xc_list):

    zq_i = zq_start_block
    while zq_i < (zq_start_block+zq_block_size):
        zq_tu12_list=zq_xc_list[zq_i].split(',')
        zq_tu12_tmp1=zq_tu12_list[1].replace('MVC4','MVC4TU12')

        zq_tu12_list=zq_xc_list[zq_i+zq_block_size].split(',')
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
        
        zq_i += 1
    
    return


def QS_070_Enable_Disable_POM(zq_run, zq_tu12,zq_enadis):

    zq_tl1_res=NE1.tl1.do("ED-TU12::{}::::POM={},EGPOM={};".format(zq_tu12,zq_enadis,zq_enadis))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    dprint(NE1.tl1.get_last_outcome(),1)
    zq_cmd=zq_msg.get_cmd_status()

    if zq_cmd == (True,'COMPLD'):
        dprint("\nOK\tPom and EGPOM setting to [{}] for {} successful".format(zq_enadis,zq_tu12),2)
        zq_run.add_success(NE1, "Pom and EGPOM setting to [{}] for {} successful".format(zq_enadis,zq_tu12),"0.0", "Pom and EGPOM setting")

    else:
        dprint("\nKO\tPom and EGPOM setting to [{}] for {} failed".format(zq_enadis,zq_tu12),2)
        zq_run.add_failure(NE1, "TL1 COMMAND","0.0","Pom and EGPOM setting to [{}] for {} failed".format(zq_enadis,zq_tu12),"TL1 command fail "+ QS_000_Print_Line_Function())
    
    return


def QS_100_Check_POM_Block(zq_run, zq_ONT_p1, zq_ONT_p2, zq_mtx_slot, zq_start_block, zq_block_size):
    
    zq_i = zq_start_block
    zq_k = 1
    while zq_i < (zq_start_block+zq_block_size):
        for zq_j in range (1,4):
            zq_tu12_idx1="MVC4TU12-{}-{}-{}".format(zq_mtx_slot,str(zq_i),str(zq_j))
            zq_tu12_idx2="MVC4TU12-{}-{}-{}".format(zq_mtx_slot,str(zq_i+zq_block_size),str(zq_j))

            for zq_m in range (1,8):
                for zq_l in range (1,4):
                    zq_tu12_ch="{}.{}.{}.{}".format(str(zq_k),str(zq_j),str(zq_m),str(zq_l))
                    ONT.get_set_rx_lo_measure_channel(zq_ONT_p1, zq_tu12_ch)
                    ONT.get_set_rx_lo_measure_channel(zq_ONT_p2, zq_tu12_ch)
                    
                    ONT.get_set_tx_lo_measure_channel(zq_ONT_p1, zq_tu12_ch)
                    ONT.get_set_tx_lo_measure_channel(zq_ONT_p2, zq_tu12_ch)
                    
                    ONT.start_measurement("P1")
                    ONT.start_measurement("P2")

                   
                    QS_070_Enable_Disable_POM(zq_run, "{}-{}-{}".format(zq_tu12_idx1,str(zq_m),str(zq_l)),"Y")
                    QS_070_Enable_Disable_POM(zq_run, "{}-{}-{}".format(zq_tu12_idx2,str(zq_m),str(zq_l)),"Y")
            
                    time.sleep(1)
            
                    QS_070_Enable_Disable_POM(zq_run, "{}-{}-{}".format(zq_tu12_idx1,str(zq_m),str(zq_l)),"N")
                    QS_070_Enable_Disable_POM(zq_run, "{}-{}-{}".format(zq_tu12_idx2,str(zq_m),str(zq_l)),"N")
            
                    ONT.halt_measurement("P1")
                    ONT.halt_measurement("P2")
            
                    zq_alm_p1=ONT.retrieve_ho_lo_alarms("P1")
                    zq_alm_p2=ONT.retrieve_ho_lo_alarms("P2")
                    if zq_alm_p1[0] == True:
                        if len(zq_alm_p1[1]) == 0:
                            dprint("OK\tAlarm not found when enabling/disabling POM",2)
                            zq_run.add_success(NE1, "Alarm not found when enabling/disabling POM","0.0", "Alarms check")
                        else:
                            dprint("KO\tAlarm found on ONT port {} when enabling/disabling POM: {}".format(zq_ONT_p1, zq_alm_p1[1]),2)
                            zq_run.add_failure(NE1,  "TL1 COMMAND","0.0", "Alarm found on ONT port {} when enabling/disabling POM: {}".format(zq_ONT_p1, zq_alm_p1[1]),"Alarms check "+ QS_000_Print_Line_Function())
        
                    if zq_alm_p2[0] == True:
                        if len(zq_alm_p2[1]) == 0:
                            dprint("OK\tAlarm not found when enabling/disabling POM",2)
                            zq_run.add_success(NE1, "Alarm not found when enabling/disabling POM","0.0", "Alarms check")
                        else:
                            dprint("KO\tAlarm found on ONT port {} when enabling/disabling POM: {}".format(zq_ONT_p2, zq_alm_p2[1]),2)
                            zq_run.add_failure(NE1,  "TL1 COMMAND","0.0", "Alarm found on ONT port {} when enabling/disabling POM: {}".format(zq_ONT_p2, zq_alm_p2[1]),"Alarms check "+ QS_000_Print_Line_Function())
        
            
        zq_i += 1
        zq_k += 1

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
        self.start_tps_block(NE1.id,"FM", "8-1-4-1")

        ONT.init_instrument("P1")
        ONT.init_instrument("P2")


    def test_body(self):
        '''
        test Body Section implementation
        insert Main body code for your test below
        '''
        print("\n******************** START ********************")
        '''
        Retrieve parameters from preset
        '''
        E_LO_MTX = "MXH60GLO"
        
        E_SLOT = ['2','3','4','5','6','7','8','12','13','14','15','16','17','18','19']
        E_BLOCK_SIZE = 64
        E_HO_TI = 'X4F4E5420484F2D5452414345202020' #'ONT HO-TRACE   '
        
        zq_mtxlo_slot=NE1.get_preset("M1")
        NE1_stm64p1=NE1.get_preset("S1")
        NE1_stm64p2=NE1.get_preset("S2")
        #ONT_P1="P1"
        #ONT_P2="P2"
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
        Change 384xMVC4 structure to 63xTU12
        '''
        zq_filter=TL1check()
        zq_filter.add_field('LOSTRUCT', '63xTU12')
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-1&&-384::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-384::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot),zq_filter)

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
        
        '''
        CHECK FIRST 128 BLOCK of MVC4/TU3 
        '''
        QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_040_Modify_AU4_HO_Trace_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, E_HO_TI)
        QS_040_Modify_AU4_HO_Trace_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, E_HO_TI)
        
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, 1, E_BLOCK_SIZE, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_BLOCK_SIZE*1+1, E_BLOCK_SIZE, E_HO_TI)
        
        
        QS_030_Create_LO_XC_Block(self, 1, E_BLOCK_SIZE, zq_xc_list)
        
        '''
        Configure both ONT ports to VC3 mapping
        '''
        ONT.get_set_tx_bit_rate("P1", "STM64")
        ONT.get_set_tx_bit_rate("P2", "STM64")
        
        ONT.get_set_rx_channel_mapping_size("P1", "VC12")
        ONT.get_set_rx_channel_mapping_size("P2", "VC12")
        
        ONT.get_set_tx_channel_mapping_size("P1", "VC12")
        ONT.get_set_tx_channel_mapping_size("P2", "VC12")

        ONT.get_set_laser_status("P1", "ON")
        ONT.get_set_laser_status("P2", "ON")

        ONT.get_set_clock_reference_source("P1", "RX")
        ONT.get_set_clock_reference_source("P2", "RX")

                
        QS_100_Check_POM_Block(self, "P1", "P2", zq_mtxlo_slot, 1, E_BLOCK_SIZE)

        
        QS_060_Delete_LO_XC_Block(self, 1, E_BLOCK_SIZE, zq_xc_list)



        QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        '''
        CHECK SECOND 128 BLOCK of MVC4/TU3 
        '''
        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")

        QS_010_Create_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p4, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, E_HO_TI)
        
        QS_030_Create_LO_XC_Block(self, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
        
        QS_100_Check_POM_Block(self, "P1", "P2", zq_mtxlo_slot, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE)
        
        QS_060_Delete_LO_XC_Block(self, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
        
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p4, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)
        

        '''
        CHECK THIRD 128 BLOCK of MVC4/TU3 
        '''
        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")

        QS_010_Create_HO_XC_Block(self, NE1_stm64p5, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p6, 1, E_BLOCK_SIZE, zq_xc_list)
        
        QS_010_Create_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p4, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)
        
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_BLOCK_SIZE*4+1, E_BLOCK_SIZE, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_BLOCK_SIZE*5+1, E_BLOCK_SIZE, E_HO_TI)
        
        QS_030_Create_LO_XC_Block(self, E_BLOCK_SIZE*4+1, E_BLOCK_SIZE, zq_xc_list)
        
        #QS_100_Check_POM_Block(self, "P1", "P2", zq_mtxlo_slot, E_BLOCK_SIZE*4+1, E_BLOCK_SIZE)

        QS_060_Delete_LO_XC_Block(self, E_BLOCK_SIZE*4+1, E_BLOCK_SIZE, zq_xc_list)

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
        Restore 384xMVC4 structure to 3xTU3
        '''
        zq_filter=TL1check()
        zq_filter.add_field("LOSTRUCT", "3xTU3")
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-1&&-384::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-384::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot),zq_filter)


        self.stop_tps_block(NE1.id,"FM", "8-1-4-1")



    def test_cleanup(self):
        '''
        test Cleanup Section implementation
        insert CleanUp code for your test below
        '''
        ONT.deinit_instrument("P1")
        ONT.deinit_instrument("P2")


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