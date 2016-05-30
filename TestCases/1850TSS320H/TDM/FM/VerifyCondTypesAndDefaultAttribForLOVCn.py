#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: Verify the condition types and factory default attributes
:field Description: for LOVCn according to the asap profile selected and table.5.1
:field Description: of TPS doc. MXH60GLO 
:field Description: The check is performed on 6 TU3s (2 for each 128 bank) and 
:field Description: other 6 TU12s (2 for each 128 bank). 
:field Topology: 5
:field Dependency:
:field Lab: SVT
:field TPS: FM__5-2-31-1
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

E_RFI_NUM = 1
E_BLOCK_SIZE = 64        
E_TU3_RANGE = 2
E_WAIT = 10

E_NO_BER = 8000

#Timeout for do_until TL1 command
E_TIMEOUT = 1800

#ASAP PROFILES
E_ASAP_LOVC3_0 = 'LBL-ASAPLOVC3-None'
E_ASAP_LOVC3_1 = 'LBL-ASAPLOVC3-SYSDFLT'
E_ASAP_LOVC3_2 = 'LBL-ASAPLOVC3-NotPrimary'
E_ASAP_LOVC3_3 = 'LBL-ASAPLOVC3-FerfAis'
E_ASAP_LOVC3_4 = 'LBL-ASAPLOVC3-ALL'

E_ASAP_LOVC12_0 = 'LBL-ASAPLOVC12-None'
E_ASAP_LOVC12_1 = 'LBL-ASAPLOVC12-SYSDFLT'
E_ASAP_LOVC12_2 = 'LBL-ASAPLOVC12-NotPrimary'
E_ASAP_LOVC12_3 = 'LBL-ASAPLOVC12-FerfAis'
E_ASAP_LOVC12_4 = 'LBL-ASAPLOVC12-ALL'

E_HO_TI  = 'X4F4E5420484F2D5452414345202020' #'ONT HO-TRACE   '
E_LO_TI  = 'X4F4E54204C4F2D5452414345202020' #'ONT LO-TRACE   '
E_BAD_TI = 'X4142434445464748494A4B4C202020' #'ABCDEFGHIJKL   '
E_DEF_TI = 'X000000000000000000000000000000' 

#CHANGE THIS LISTS TO RANGE IN MORE LOVC12, ACCORDING TO SDH SPECIFICATION
#TUG3 range from 1..3
#TUG2 range from 1..7
#TU12 range from 1..3
E_TUG3 = [1]
E_TUG2 = [1]
E_TU12 = [1]

zq_asaplovc12_1_list=list()
zq_asaplovc12_2_list=list()
zq_asaplovc12_3_list=list()
zq_asaplovc12_4_list=list()

zq_asaplovc3_1_list=list()
zq_asaplovc3_2_list=list()
zq_asaplovc3_3_list=list()
zq_asaplovc3_4_list=list()


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


def QS_005_Check_Cond_Absence(zq_run, zq_fac, zq_container):

    zq_tl1_res=NE1.tl1.do("RTRV-COND-{}::{};".format(zq_fac.upper(),zq_container))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    dprint(NE1.tl1.get_last_outcome(),1)
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        zq_size=zq_msg.get_cmd_response_size()
        if zq_size == 0:
            dprint("OK\tNo condition alarms found for {}".format(zq_container),2)
            zq_run.add_success(NE1, "No condition alarms found for {}".format(zq_container),"0.0", "Alarm Check")
        else:
            dprint("KO\tCondition Alarm found on some {}".format(zq_container),2)
            zq_run.add_failure(NE1,"TL1 COMMAND","0.0", "Condition Alarm found on some {}".format(zq_container),"Alarms check")
            dprint(NE1.tl1.get_last_outcome(),2)

    return


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
                zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","Cross-connection creation failure")
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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","Cross-connection deletion failure")
    
        zq_i += 1

    return


def QS_030_Create_LO_XC_Block(zq_run, zq_vc4_1, zq_vc4_2, zq_xc_list):
    
    zq_tu3_list=zq_xc_list[zq_vc4_1].split(',')
    zq_tu3_idx1=zq_tu3_list[1].replace('MVC4','MVC4TU3')

    zq_tu3_list=zq_xc_list[zq_vc4_2].split(',')
    zq_tu3_idx2=zq_tu3_list[1].replace('MVC4','MVC4TU3')

    for zq_j in range (1,4):
        zq_tl1_res=NE1.tl1.do("ENT-CRS-LOVC3::{}-{},{}-{}:::2WAY;".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("\nOK\tCross-connection successfully created from {}-{} to {}-{}".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j),2)
            zq_run.add_success(NE1, "Cross-connection creation successful {}-{} to {}-{}".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j),"0.0", "Cross-connection creation successful")

        else:
            dprint("\nKO\tCross-connection creation failed from {}-{} to {}-{}".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j),2)
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","Cross-connection creation failure")

    return


def QS_035_Create_LO_XC_Block(zq_run, zq_vc4_1, zq_vc4_2, zq_xc_list):
    
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
                    zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "Cross-connection creation failure","TL1 command fail")


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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMAND FAIL","HO Trace Identifier change failure for STM64AU4-{}-{}".format(zq_slot,zq_i))

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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMAND FAIL","HO Trace Identifier change failure for MVC4-{}-{}".format(zq_slot,zq_i))
        zq_i += 1
    return


def QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_vc3, zq_trace):

    if 'TU3' in zq_vc3:
        zq_tl1_res=NE1.tl1.do("ED-TU3::{}::::TRCEXPECTED={}, EGTRCEXPECTED={};".format(zq_vc3, zq_trace, zq_trace))
    else:
        zq_tl1_res=NE1.tl1.do("ED-TU12::{}::::TRCEXPECTED={}, EGTRCEXPECTED={};".format(zq_vc3, zq_trace, zq_trace))

    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        dprint("\nOK\tLO Trace Identifier changed to {} for {}".format(zq_trace, zq_vc3),2)
        zq_run.add_success(NE1, "LO Trace Identifier changed to {} for {}".format(zq_trace, zq_vc3),"0.0", "LO Trace Identifier changed")

    else:
        dprint("\nKO\tLO Trace Identifier change failure for {}".format(zq_vc3),2)
        zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMAND FAIL","LO Trace Identifier change failure for {}".format(zq_vc3))
    
    return


def QS_060_Delete_LO_XC_Block(zq_run, zq_vc4_1, zq_vc4_2, zq_xc_list):

    zq_tu3_list=zq_xc_list[zq_vc4_1].split(',')
    zq_tu3_idx1=zq_tu3_list[1].replace('MVC4','MVC4TU3')

    zq_tu3_list=zq_xc_list[zq_vc4_2].split(',')
    zq_tu3_idx2=zq_tu3_list[1].replace('MVC4','MVC4TU3')

    for zq_j in range (1,4):
        zq_tl1_res=NE1.tl1.do("DLT-CRS-LOVC3::{}-{},{}-{};".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("\nOK\tCross-connection successfully deleted from {}-{} to {}-{}".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j),2)
            zq_run.add_success(NE1, "Cross-connection successfully deleted from {}-{} to {}-{}".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j),"0.0", "Cross-connection successfully deleted")

        else:
            dprint("\nKO\tCross-connection deletion failed from {}-{} to {}-{}".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j),2)
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","Cross-connection deletion failed from {}-{} to {}-{}".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j))

    return

def QS_065_Delete_LO_XC_Block(zq_run, zq_vc4_1, zq_vc4_2, zq_xc_list):

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
                    zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "Cross-connection deletion failed from {} to {}".format(zq_tu12_idx1,zq_tu12_idx2))
    
    return


def QS_070_Enable_Disable_POM(zq_run, zq_mtx_slot, zq_vc4, zq_enadis):

    for zq_j in range (1,4):
        zq_tl1_res=NE1.tl1.do("ED-TU3::MVC4TU3-{}-{}-{}::::POM={},EGPOM={};".format(zq_mtx_slot, zq_vc4, zq_j, zq_enadis, zq_enadis))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
    
        if zq_cmd == (True,'COMPLD'):
            dprint("\nOK\tPom and EGPOM setting to [{}] for MVC4TU3-{}-{}-{} successful".format(zq_enadis,zq_mtx_slot, zq_vc4, zq_j),2)
            zq_run.add_success(NE1, "Pom and EGPOM setting to [{}] for MVC4TU3-{}-{}-{} successful".format(zq_enadis,zq_mtx_slot, zq_vc4, zq_j),"0.0", "Pom and EGPOM setting")
    
        else:
            dprint("\nKO\tPom and EGPOM setting to [{}] for MVC4TU3-{}-{}-{} failed".format(zq_enadis,zq_mtx_slot, zq_vc4, zq_j),2)
            zq_run.add_failure(NE1,  "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","Pom and EGPOM setting to [{}] for MVC4TU3-{}-{}-{} failed".format(zq_enadis,zq_mtx_slot, zq_vc4, zq_j))
        
    return

def QS_075_Enable_Disable_TRCMON(zq_run, zq_vc4, zq_enadis):

    if 'TU3' in zq_vc4:
        zq_tl1_res=NE1.tl1.do("ED-TU3::{}::::TRCMON={},EGTRCMON={};".format(zq_vc4, zq_enadis, zq_enadis))
    else:
        zq_tl1_res=NE1.tl1.do("ED-TU12::{}::::TRCMON={},EGTRCMON={};".format(zq_vc4, zq_enadis, zq_enadis))
        
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    dprint(NE1.tl1.get_last_outcome(),1)
    zq_cmd=zq_msg.get_cmd_status()

    if zq_cmd == (True,'COMPLD'):
        dprint("\nOK\tTRCMON and EGTRCMON setting to [{}] for {} successful".format(zq_enadis, zq_vc4),2)
        zq_run.add_success(NE1, "TRCMON and EGTRCMON setting to [{}] for {} successful".format(zq_enadis, zq_vc4),"0.0", "TRCMON and EGTRCMON setting")

    else:
        dprint("\nKO\tTRCMON and EGTRCMON setting to [{}] for {} failed".format(zq_enadis, zq_vc4),2)
        zq_run.add_failure(NE1,  "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","TRCMON and EGTRCMON setting to [{}] for {} failed".format(zq_enadis, zq_vc4))
    
    return


def QS_077_Enable_Disable_POM(zq_run, zq_mtx_slot, zq_vc4, zq_enadis):

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
                    zq_run.add_failure(NE1,  "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "Pom and EGPOM setting to [{}] for {}-{}-{}-{} failed".format(zq_enadis, zq_tu12_idx, str(zq_j), str(zq_m), str(zq_l)))
                
    return


def QS_080_Set_Alm_Prof(zq_run,zq_fac_idx,zq_alm_prof):

    if 'TU3' in zq_fac_idx:
        zq_tl1_res=NE1.tl1.do("ED-TU3::{}::::ALMPROF={};".format(zq_fac_idx, zq_alm_prof))
    else:
        zq_tl1_res=NE1.tl1.do("ED-TU12::{}::::ALMPROF={};".format(zq_fac_idx, zq_alm_prof))
        
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    dprint(NE1.tl1.get_last_outcome(),1)
    zq_cmd=zq_msg.get_cmd_status()

    if zq_cmd == (True,'COMPLD'):
        dprint("\nOK\tAlarm Profile successfully changed to [{}] for {}".format(zq_alm_prof,zq_fac_idx),2)
        zq_run.add_success(NE1, "Alarm Profile successfully changed to [{}] for {}".
                           format(zq_alm_prof,zq_fac_idx),"0.0", "Alarm Profile setting")

    else:
        dprint("\nKO\tAlarm Profile changing to [{}] for {} failed".format(zq_alm_prof,zq_fac_idx),2)
        zq_run.add_failure(NE1,  "TL1 COMMAND","0.0", 
                           "TL1 COMMAND FAIL","Alarm Profile changing to [{}] for {} failed".format(zq_alm_prof,zq_fac_idx))

    return


def QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_pst):

    zq_filter=TL1check()
    zq_filter.add_pst(zq_pst)
    zq_tl1_res=NE1.tl1.do_until("RTRV-TU3::MVC4TU3-{}-{}-{};".format(zq_slot, zq_vc4_1, zq_j), zq_filter,timeout=E_TIMEOUT)
    if zq_tl1_res:
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tPrimary Status successful changed to {} for MVC4TU3-{}-{}-{} facility.".format(zq_pst, zq_slot, zq_vc4_1, zq_j),2)
            zq_run.add_success(NE1, "Primary Status successful changed to {} for MVC4TU3-{}-{}-{} facility.".format(zq_pst, zq_slot, zq_vc4_1, zq_j),"0.0", "PRIMARY STATUS CHECK")
        else:
            dprint("KO\tPrimary Status wrong for MVC4TU3-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j),2)
            zq_run.add_failure(NE1,"Primary Status wrong for MVC4TU3-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j),"0.0", "PRIMARY STATUS CHECK","Primary Status wrong for MVC4TU3-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j))
    else:
        dprint("KO\tTL1 Command Timeout retrieving MVC4TU3-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j),2)
        zq_run.add_failure(NE1,"TL1 Command Timeout retrieving MVC4TU3-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j),"0.0", "TL1 COMMAND","TL1 Command Timeout retrieving MVC4TU3-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j))
        
    return


def QS_092_Set_FAC_pst(zq_run, zq_fac, zq_pst):

    if 'TU3' in zq_fac:
        zq_tl1_res=NE1.tl1.do("ED-TU3::{}:::::{};".format(zq_fac, zq_pst))
    else:
        zq_tl1_res=NE1.tl1.do("ED-TU12::{}:::::{};".format(zq_fac, zq_pst))

    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        dprint("\nOK\tPrimary status changing to {} for {}".format(zq_pst, zq_fac),2)
        zq_run.add_success(NE1, "Primary status changing to {} for {}".format(zq_pst, zq_fac),"0.0", "Primary Status Changing")

    else:
        dprint("\nKO\tPrimary status changing to {} for {} failed".format(zq_pst, zq_fac),2)
        zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMAND FAIL","Primary status changing to {} for {} failed"
                           .format(zq_pst, zq_fac))
    
    return


def QS_095_Check_MVC4TU3_Alarm(zq_run,zq_vc3,zq_man_exp,zq_prio_exp,zq_sa_nsa_exp,zq_type_exp,zq_dir_exp,zq_asap_list):

    zq_asap_str = "{},{},{},{},{}".format(zq_man_exp,zq_prio_exp,zq_sa_nsa_exp,zq_type_exp,zq_dir_exp)
    zq_asap_found=False
    for zq_i in range(0,len(zq_asap_list)):
        if zq_asap_list[zq_i] == zq_asap_str:
            zq_asap_found = True
            dprint("OK\t[{}] found in current ASAP profile".format(zq_asap_str),2)
            zq_run.add_success(NE1, "[{}] found in current ASAP profile".format(zq_asap_str),"0.0", "ASAP PROFILE CHECK")
            break
        
    if zq_asap_found == True:
        zq_tl1_res=NE1.tl1.do("RTRV-COND-LOVC3::{}:::{},,{};".format(str(zq_vc3),zq_man_exp,zq_dir_exp))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        if (zq_msg.get_cmd_response_size() == 0):
            dprint("KO\t{} Condition verification failure for {} facility : Exp [{}] - Rcv [0]".format(zq_man_exp, zq_vc3, E_RFI_NUM),2)
            zq_run.add_failure(NE1,"{} Condition verification failure for {} facility : Exp [{}] - Rcv [0]".format(zq_man_exp, zq_vc3, E_RFI_NUM),"0.0", "SSF CONDITION CHECK","SSF Condition verification failure: Exp [{}] - Rcv [0]".format(E_RFI_NUM))
        else:
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                zq_prio = zq_msg.get_cmd_attr_value("{},LOVC3".format(zq_vc3), 1)
                zq_man = zq_msg.get_cmd_attr_value("{},LOVC3".format(zq_vc3), 2)
                zq_sa_nsa = zq_msg.get_cmd_attr_value("{},LOVC3".format(zq_vc3), 3)
                zq_type = zq_msg.get_cmd_attr_value("{},LOVC3".format(zq_vc3), 6)
                zq_dir = zq_msg.get_cmd_attr_value("{},LOVC3".format(zq_vc3), 7)
                if (zq_man == zq_man_exp) and \
                   (zq_type == zq_type_exp) and \
                   (zq_dir == zq_dir_exp) and \
                   (zq_sa_nsa == zq_sa_nsa_exp) and \
                   (zq_prio == zq_prio_exp):
                    dprint("OK\t{} Condition verification successful for {} facility.".format(zq_man_exp, str(zq_vc3)),2)
                    zq_run.add_success(NE1, "{} Condition verification successful for {} facility.".
                                       format(zq_man_exp, str(zq_vc3)),"0.0", "{} CONDITION CHECK".format(zq_man_exp))
                    dprint("\t\tCOND: Exp [{}]  - Rcv [{}]".format(zq_prio_exp,zq_prio),2)
                    dprint("\t\tTYPE: Exp [{}] - Rcv [{}]".format(zq_man_exp,zq_man),2)
                    dprint("\t\tDIR : Exp [{}]  - Rcv [{}]".format(zq_sa_nsa_exp,zq_sa_nsa),2)
                    dprint("\t\tTYPE: Exp [{}] - Rcv [{}]".format(zq_type_exp,zq_type),2)
                    dprint("\t\tDIR : Exp [{}]  - Rcv [{}]".format(zq_dir_exp,zq_dir),2)
                else:
                    dprint("KO\t{} Condition verification failure for {} facility.".format(zq_man_exp, str(zq_vc3)),2)
                    dprint("\t\tCOND: Exp [{}]  - Rcv [{}]".format(zq_prio_exp,zq_prio),2)
                    dprint("\t\tTYPE: Exp [{}] - Rcv [{}]".format(zq_man_exp,zq_man),2)
                    dprint("\t\tDIR : Exp [{}]  - Rcv [{}]".format(zq_sa_nsa_exp,zq_sa_nsa),2)
                    dprint("\t\tTYPE: Exp [{}] - Rcv [{}]".format(zq_type_exp,zq_type),2)
                    dprint("\t\tDIR : Exp [{}]  - Rcv [{}]".format(zq_dir_exp,zq_dir),2)
                    zq_run.add_failure(NE1,"{} Condition verification failure for {} facility : Exp: [{}-{}-{}-{}-{}] - Rcv [{}-{}-{}-{}-{}]".
                                       format(zq_man_exp, str(zq_vc3),zq_prio_exp,zq_man_exp,zq_sa_nsa_exp,zq_type_exp,zq_dir_exp,zq_prio,zq_man,zq_sa_nsa,zq_type,zq_dir),"0.0","{} CONDITION CHECK".
                                       format(zq_man_exp),"{} Condition verification failure for {} facility : Exp: [{}-{}-{}-{}-{}] - Rcv [{}-{}-{}-{}-{}]".
                                       format(zq_man_exp, str(zq_vc3),zq_prio_exp,zq_man_exp,zq_sa_nsa_exp,zq_type_exp,zq_dir_exp,zq_prio,zq_man,zq_sa_nsa,zq_type,zq_dir))
    else:
        dprint("KO\t[{}] NOT found in current ASAP profile".format(zq_asap_str),2)
        zq_run.add_failure(NE1,"[{}] NOT found in current ASAP profile".format(zq_asap_str),"0.0", "ASAP PROFILE CHECK","[{}] found in current ASAP profile".format(zq_asap_str))
            
    return




def QS_100_Check_Cond_Attr(zq_run, 
                       zq_ont_p1, 
                       zq_ont_p2, 
                       zq_slot, 
                       zq_vc4_1, 
                       zq_vc4_2):

    global zq_asaplovc12_1_list, zq_asaplovc12_2_list, zq_asaplovc12_3_list,zq_asaplovc12_4_list
    global zq_asaplovc3_1_list, zq_asaplovc3_2_list, zq_asaplovc3_3_list, zq_asaplovc3_4_list
    

    for zq_j in range (1,E_TU3_RANGE):
        zq_tu3_idx1="MVC4TU3-{}-{}-{}".format(zq_slot,str(zq_vc4_1),str(zq_j))
        zq_tu3_idx2="MVC4TU3-{}-{}-{}".format(zq_slot,str(zq_vc4_2),str(zq_j))

        zq_tu3_ch1="{}.{}.1.1".format(str(zq_vc4_1 % E_BLOCK_SIZE),str(zq_j))
        zq_tu3_ch2="{}.{}.1.1".format(str(zq_vc4_2 % E_BLOCK_SIZE),str(zq_j))

        ONT.get_set_rx_lo_measure_channel(zq_ont_p1, zq_tu3_ch1)
        ONT.get_set_rx_lo_measure_channel(zq_ont_p2, zq_tu3_ch2)
    
        ONT.get_set_tx_lo_measure_channel(zq_ont_p1, zq_tu3_ch1)
        ONT.get_set_tx_lo_measure_channel(zq_ont_p2, zq_tu3_ch2)
    
        ONT.get_set_error_rate(zq_ont_p1, "LO", "1E-3")
        ONT.get_set_error_rate(zq_ont_p2, "LO", "1E-3")

        ONT.get_set_error_insertion_type(zq_ont_p1, "LPBIP")
        ONT.get_set_error_insertion_type(zq_ont_p2, "LPBIP")

        ###############################################################################################
        ###############################################################################################
        #                                       EBER check 
        ###############################################################################################
        ###############################################################################################
        ONT.get_set_error_activation(zq_ont_p1, "LO", "ON")

        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "OOS-AU")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")
        
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"EBER","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"EBER","NR","SA","NEND","TRMT",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"EBER","MJ","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"EBER","MJ","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc3_4_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"EBER","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc3_4_list)
        
        ONT.get_set_error_activation(zq_ont_p1, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)

        ONT.get_set_error_activation(zq_ont_p2, "LO", "ON")

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "OOS-AU")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"EBER","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"EBER","NR","SA","NEND","TRMT",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"EBER","MJ","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"EBER","MJ","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc3_4_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"EBER","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc3_4_list)
        
        ONT.get_set_error_activation(zq_ont_p2, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)

        ###############################################################################################
        ###############################################################################################
        #                                       SDBER check 
        ###############################################################################################
        ###############################################################################################
        #
        ONT.get_set_error_rate(zq_ont_p1, "LO", "1E-6")
        ONT.get_set_error_rate(zq_ont_p2, "LO", "1E-6")

        ONT.get_set_error_activation(zq_ont_p1, "LO", "ON")

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-ANR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SDBER","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SDBER","NR","SA","NEND","TRMT",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SDBER","MN","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SDBER","MN","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SDBER","MN","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc3_4_list)
        
        ONT.get_set_error_activation(zq_ont_p1, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)

        ONT.get_set_error_activation(zq_ont_p2, "LO", "ON")

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-ANR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        
        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SDBER","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SDBER","NR","SA","NEND","TRMT",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SDBER","MN","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SDBER","MN","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SDBER","MN","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc3_4_list)
        
        ONT.get_set_error_activation(zq_ont_p2, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)

        ###############################################################################################
        ###############################################################################################
        #                                       AIS-V & SSF-V check 
        ###############################################################################################
        ###############################################################################################

        ONT.get_set_alarm_insertion_type(zq_ont_p1, "TUAIS")
        ONT.get_set_alarm_insertion_type(zq_ont_p2, "TUAIS")
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "ON")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "OOS-AU")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SSF-V","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SSF-V","NR","SA","NEND","TRMT",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SSF-V","NR","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SSF-V","NR","SA","NEND","TRMT",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SSF-V","MJ","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SSF-V","MJ","SA","NEND","TRMT",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"AIS-V","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SSF-V","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SSF-V","MJ","SA","NEND","TRMT",zq_asaplovc3_4_list)
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)

        ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "ON")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "OOS-AU")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")

        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SSF-V","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SSF-V","NR","SA","NEND","TRMT",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SSF-V","NR","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SSF-V","NR","SA","NEND","TRMT",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SSF-V","MJ","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SSF-V","MJ","SA","NEND","TRMT",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"AIS-V","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"SSF-V","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"SSF-V","MJ","SA","NEND","TRMT",zq_asaplovc3_4_list)
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)


        ###############################################################################################
        ###############################################################################################
        #                                       LOP-V check 
        ###############################################################################################
        ###############################################################################################

        ONT.get_set_alarm_insertion_type(zq_ont_p1, "TULOP")
        ONT.get_set_alarm_insertion_type(zq_ont_p2, "TULOP")
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "ON")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "OOS-AU")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"LOP-V","NR","SA","NEND","RCV",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)

        ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "ON")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "OOS-AU")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")

        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"LOP-V","NR","SA","NEND","RCV",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)

    
        ###############################################################################################
        ###############################################################################################
        #                                       TIM-V check 
        ###############################################################################################
        ###############################################################################################
    
        QS_075_Enable_Disable_TRCMON(zq_run, zq_tu3_idx1, "Y")
        QS_075_Enable_Disable_TRCMON(zq_run, zq_tu3_idx2, "Y")
        
        QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu3_idx1, E_LO_TI)
        QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu3_idx2, E_LO_TI)
        time.sleep(E_WAIT)
        time.sleep(E_WAIT)
        time.sleep(E_WAIT)

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)

        #Change expected string on TU3 so that TIM-V condition is raised on LOVC3
        QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu3_idx1, E_BAD_TI)
        QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu3_idx2, E_BAD_TI)
        time.sleep(E_WAIT)
        time.sleep(E_WAIT)
        time.sleep(E_WAIT)
        
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "OOS-AU")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "OOS-AU")

        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"TIM-V","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"TIM-V","NR","SA","NEND","TRMT",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"TIM-V","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"TIM-V","NR","SA","NEND","TRMT",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc3_4_list)
        
        #Restore Default ASAP profile
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)

        #SET TI as expected
        QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu3_idx1, E_LO_TI)
        QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu3_idx2, E_LO_TI)
        time.sleep(E_WAIT)
        time.sleep(E_WAIT)
        time.sleep(E_WAIT)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)

        #RESTORE default TI on TU3s
        QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu3_idx1, E_DEF_TI)
        QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu3_idx2, E_DEF_TI)

        #DISABLE TCMON (default)
        QS_075_Enable_Disable_TRCMON(zq_run, zq_tu3_idx1, "N")
        QS_075_Enable_Disable_TRCMON(zq_run, zq_tu3_idx2, "N")

        ###############################################################################################
        ###############################################################################################
        #                                       UNEQ-V check 
        ###############################################################################################
        ###############################################################################################

        ONT.get_set_alarm_insertion_type(zq_ont_p1, "LPUNEQ")
        ONT.get_set_alarm_insertion_type(zq_ont_p2, "LPUNEQ")
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "ON")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "OOS-AU")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"UNEQ-V","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"UNEQ-V","NR","SA","NEND","TRMT",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc3_4_list)
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)

        ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "ON")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "OOS-AU")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")

        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"UNEQ-V","NR","SA","NEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"UNEQ-V","NR","SA","NEND","TRMT",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc3_4_list)
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)


        ###############################################################################################
        ###############################################################################################
        #                                       RFI check 
        ###############################################################################################
        ###############################################################################################

        ONT.get_set_alarm_insertion_type(zq_ont_p1, "LPRDI")
        ONT.get_set_alarm_insertion_type(zq_ont_p2, "LPRDI")
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "ON")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")
        time.sleep(E_WAIT)
        
        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"RFI","NR","SA","FEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"RFI","NR","SA","FEND","TRMT",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"RFI","NR","SA","FEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"RFI","NR","SA","FEND","TRMT",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"RFI","NR","SA","FEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"RFI","NR","SA","FEND","TRMT",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"RFI","WR","SA","FEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"RFI","WR","SA","FEND","TRMT",zq_asaplovc3_4_list)
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)
        time.sleep(E_WAIT)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)

        ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "ON")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        time.sleep(E_WAIT)

        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"RFI","NR","SA","FEND","RCV",zq_asaplovc3_1_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"RFI","NR","SA","FEND","TRMT",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"RFI","NR","SA","FEND","RCV",zq_asaplovc3_2_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"RFI","NR","SA","FEND","TRMT",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"RFI","NR","SA","FEND","RCV",zq_asaplovc3_3_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"RFI","NR","SA","FEND","TRMT",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"RFI","WR","SA","FEND","RCV",zq_asaplovc3_4_list)
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"RFI","WR","SA","FEND","TRMT",zq_asaplovc3_4_list)
        
        ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "OFF")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)
        time.sleep(E_WAIT)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)


        ###############################################################################################
        ###############################################################################################
        #                                       MAN check 
        ###############################################################################################
        ###############################################################################################
        #SET FACILITY to OOS
        QS_092_Set_FAC_pst(zq_run,zq_tu3_idx1,"OOS")

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "OOS-MA")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")
        time.sleep(E_WAIT)
        
        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"MAN","NR","SA","NEND","RCV",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"MAN","NR","SA","NEND","RCV",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"MAN","NR","SA","NEND","RCV",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"MAN","NR","SA","NEND","RCV",zq_asaplovc3_4_list)
        
        #SET FACILITY to IS
        QS_092_Set_FAC_pst(zq_run,zq_tu3_idx1,"IS")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)
        time.sleep(E_WAIT)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)

        #SET FACILITY to OOS
        QS_092_Set_FAC_pst(zq_run,zq_tu3_idx2,"OOS")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "OOS-MA")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")
        time.sleep(E_WAIT)

        #ALMPROF=LBL-ASAPLOVC3-SYSDFLT level1
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"MAN","NR","SA","NEND","RCV",zq_asaplovc3_1_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_2)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_2)
        
        #ALMPROF=LBL-ASAPLOVC3-NotPrimary level2
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"MAN","NR","SA","NEND","RCV",zq_asaplovc3_2_list)
        
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_3)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_3)
        
        #ALMPROF=LBL-ASAPLOVC3-FerfAis level3
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"MAN","NR","SA","NEND","RCV",zq_asaplovc3_3_list)

        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_4)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_4)
        
        #ALMPROF=LBL-ASAPLOVC3-ALL level4
        QS_095_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"MAN","NR","SA","NEND","RCV",zq_asaplovc3_4_list)
        
        #SET FACILITY to IS
        QS_092_Set_FAC_pst(zq_run,zq_tu3_idx2,"IS")
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx2,E_ASAP_LOVC3_1)
        QS_080_Set_Alm_Prof(zq_run,zq_tu3_idx1,E_ASAP_LOVC3_1)
        time.sleep(E_WAIT)

        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, "IS-NR")
        QS_090_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, "IS-NR")

        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx2)
        QS_005_Check_Cond_Absence(zq_run, "LOVC3", zq_tu3_idx1)
    

    
    return


def QS_150_Check_No_Alarm(zq_run,zq_vc_range):

    if 'TU3' in zq_vc_range:
        zq_tl1_res=NE1.tl1.do("RTRV-COND-LOVC3::{};".format(zq_vc_range))
    else:
        zq_tl1_res=NE1.tl1.do("RTRV-COND-LOVC12::{};".format(zq_vc_range))
        
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    dprint(NE1.tl1.get_last_outcome(),1)
    if (zq_msg.get_cmd_response_size() == 0):
        dprint("OK\tPath is alarm free.",2)
        zq_run.add_success(NE1,"Path is alarm free.","0.0","CONDITION ALARMS CHECK")
    else:
        dprint("KO\tAlarms are present on path.",2)
        zq_run.add_failure(NE1,"Alarms are present on path.","0.0","CONDITION ALARMS CHECK","Alarms are present on path.")

    return

def QS_200_Fill_ASAP_List(zq_run,zq_asap_userlabel):

    zq_tl1_res=NE1.tl1.do("RTRV-ASAP-PROF::::::USERLABEL={};".format(zq_asap_userlabel))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        zq_asap_list = list()
        zq_len=len(zq_msg._TL1message__m_coded['R_BODY_OK'])
        for zq_i in range(1,zq_len):
            zq_field1=zq_msg._TL1message__m_coded['R_BODY_OK'][str(zq_i)]['VALUE'][1]
            zq_field2=zq_msg._TL1message__m_coded['R_BODY_OK'][str(zq_i)]['VALUE'][2]
            zq_field3=zq_msg._TL1message__m_coded['R_BODY_OK'][str(zq_i)]['VALUE'][3]
            zq_field4=zq_msg._TL1message__m_coded['R_BODY_OK'][str(zq_i)]['VALUE'][4]
            zq_field5=zq_msg._TL1message__m_coded['R_BODY_OK'][str(zq_i)]['VALUE'][5]
            zq_temp=zq_field1+','+zq_field2+','+zq_field3+','+zq_field4+','+zq_field5
            zq_asap_list.append(zq_temp)
        dprint("OK\tASAP profile [{}] successfully retrieved".format(zq_asap_userlabel),2)
        zq_run.add_success(NE1,"ASAP profile [{}] successfully retrieved".format(zq_asap_userlabel),"0.0","TL1 COMMAND")
    else:
        dprint("KO\tError retrieving ASAP profile: {}".format(zq_asap_userlabel),2)
        zq_run.add_failure(NE1,"Error retrieving ASAP profile: {}".format(zq_asap_userlabel),"0.0","TL1 COMMAND","Error retrieving ASAP profile: {}".format(zq_asap_userlabel))
    return(zq_asap_list)


def QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l, zq_pst):

    zq_filter=TL1check()
    zq_filter.add_pst(zq_pst)
    zq_tl1_res=NE1.tl1.do_until("RTRV-TU12::MVC4TU12-{}-{}-{}-{}-{};".format(zq_slot, zq_vc4_1, zq_j, zq_k, zq_l), zq_filter,timeout=E_TIMEOUT)
    if zq_tl1_res:
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tPrimary Status successful changed to {} for MVC4TU12-{}-{}-{}-{}-{} facility.".format(zq_pst, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l),2)
            zq_run.add_success(NE1, "Primary Status successful changed to {} for MVC4TU12-{}-{}-{}-{}-{} facility.".format(zq_pst, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l),"0.0", "PRIMARY STATUS CHECK")
        else:
            dprint("KO\tPrimary Status wrong for MVC4TU12-{}-{}-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j, zq_k, zq_l),2)
            zq_run.add_failure(NE1,"Primary Status wrong for MVC4TU12-{}-{}-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j, zq_k, zq_l),"0.0", "PRIMARY STATUS CHECK","Primary Status wrong for MVC4TU12-{}-{}-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j, zq_k, zq_l))
    else:
        dprint("KO\tTL1 Command Timeout retrieving MVC4TU12-{}-{}-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j, zq_k, zq_l),2)
        zq_run.add_failure(NE1,"TL1 Command Timeout retrieving MVC4TU12-{}-{}-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j, zq_k, zq_l),"0.0", "TL1 COMMAND","TL1 Command Timeout retrieving MVC4TU12-{}-{}-{}-{}-{} facility.".format(zq_slot, zq_vc4_1, zq_j, zq_k, zq_l))
        
    return


def QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_vc3,zq_man_exp,zq_prio_exp,zq_sa_nsa_exp,zq_type_exp,zq_dir_exp,zq_asap_list):

    zq_asap_str = "{},{},{},{},{}".format(zq_man_exp,zq_prio_exp,zq_sa_nsa_exp,zq_type_exp,zq_dir_exp)
    zq_asap_found=False
    for zq_i in range(0,len(zq_asap_list)):
        if zq_asap_list[zq_i] == zq_asap_str:
            zq_asap_found = True
            dprint("OK\t[{}] found in current ASAP profile".format(zq_asap_str),2)
            zq_run.add_success(NE1, "[{}] found in current ASAP profile".format(zq_asap_str),"0.0", "ASAP PROFILE CHECK")
            break
        
    if zq_asap_found == True:
        zq_tl1_res=NE1.tl1.do("RTRV-COND-LOVC12::{}:::{},,{};".format(str(zq_vc3),zq_man_exp,zq_dir_exp))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        if (zq_msg.get_cmd_response_size() == 0):
            dprint("KO\t{} Condition verification failure for {} facility : Exp [{}] - Rcv [0]".format(zq_man_exp, zq_vc3, E_RFI_NUM),2)
            zq_run.add_failure(NE1,"{} Condition verification failure for {} facility : Exp [{}] - Rcv [0]".format(zq_man_exp, zq_vc3, E_RFI_NUM),"0.0", "SSF CONDITION CHECK","SSF Condition verification failure: Exp [{}] - Rcv [0]".format(E_RFI_NUM))
        else:
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                zq_prio = zq_msg.get_cmd_attr_value("{},LOVC12".format(zq_vc3), 1)
                zq_man = zq_msg.get_cmd_attr_value("{},LOVC12".format(zq_vc3), 2)
                zq_sa_nsa = zq_msg.get_cmd_attr_value("{},LOVC12".format(zq_vc3), 3)
                zq_type = zq_msg.get_cmd_attr_value("{},LOVC12".format(zq_vc3), 6)
                zq_dir = zq_msg.get_cmd_attr_value("{},LOVC12".format(zq_vc3), 7)
                if (zq_man == zq_man_exp) and \
                   (zq_type == zq_type_exp) and \
                   (zq_dir == zq_dir_exp) and \
                   (zq_sa_nsa == zq_sa_nsa_exp) and \
                   (zq_prio == zq_prio_exp):
                    dprint("OK\t{} Condition verification successful for {} facility.".format(zq_man_exp, str(zq_vc3)),2)
                    zq_run.add_success(NE1, "{} Condition verification successful for {} facility.".
                                       format(zq_man_exp, str(zq_vc3)),"0.0", "{} CONDITION CHECK".format(zq_man_exp))
                    dprint("\t\tCOND: Exp [{}]  - Rcv [{}]".format(zq_prio_exp,zq_prio),2)
                    dprint("\t\tTYPE: Exp [{}] - Rcv [{}]".format(zq_man_exp,zq_man),2)
                    dprint("\t\tDIR : Exp [{}]  - Rcv [{}]".format(zq_sa_nsa_exp,zq_sa_nsa),2)
                    dprint("\t\tTYPE: Exp [{}] - Rcv [{}]".format(zq_type_exp,zq_type),2)
                    dprint("\t\tDIR : Exp [{}]  - Rcv [{}]".format(zq_dir_exp,zq_dir),2)
                else:
                    dprint("KO\t{} Condition verification failure for {} facility.".format(zq_man_exp, str(zq_vc3)),2)
                    dprint("\t\tCOND: Exp [{}]  - Rcv [{}]".format(zq_prio_exp,zq_prio),2)
                    dprint("\t\tTYPE: Exp [{}] - Rcv [{}]".format(zq_man_exp,zq_man),2)
                    dprint("\t\tDIR : Exp [{}]  - Rcv [{}]".format(zq_sa_nsa_exp,zq_sa_nsa),2)
                    dprint("\t\tTYPE: Exp [{}] - Rcv [{}]".format(zq_type_exp,zq_type),2)
                    dprint("\t\tDIR : Exp [{}]  - Rcv [{}]".format(zq_dir_exp,zq_dir),2)
                    zq_run.add_failure(NE1,"{} Condition verification failure for {} facility : Exp: [{}-{}-{}-{}-{}] - Rcv [{}-{}-{}-{}-{}]".
                                       format(zq_man_exp, str(zq_vc3),zq_prio_exp,zq_man_exp,zq_sa_nsa_exp,zq_type_exp,zq_dir_exp,zq_prio,zq_man,zq_sa_nsa,zq_type,zq_dir),"0.0","{} CONDITION CHECK".
                                       format(zq_man_exp),"{} Condition verification failure for {} facility : Exp: [{}-{}-{}-{}-{}] - Rcv [{}-{}-{}-{}-{}]".
                                       format(zq_man_exp, str(zq_vc3),zq_prio_exp,zq_man_exp,zq_sa_nsa_exp,zq_type_exp,zq_dir_exp,zq_prio,zq_man,zq_sa_nsa,zq_type,zq_dir))
    else:
        dprint("KO\t[{}] NOT found in current ASAP profile".format(zq_asap_str),2)
        zq_run.add_failure(NE1,"[{}] NOT found in current ASAP profile".format(zq_asap_str),"0.0", "ASAP PROFILE CHECK","[{}] found in current ASAP profile".format(zq_asap_str))
            
    return





def QS_1000_Check_Cond_Attr(zq_run, 
                            zq_ont_p1, 
                            zq_ont_p2, 
                            zq_slot, 
                            zq_vc4_1, 
                            zq_vc4_2):

    global zq_asaplovc12_1_list, zq_asaplovc12_2_list, zq_asaplovc12_3_list,zq_asaplovc12_4_list
    global zq_asaplovc3_1_list, zq_asaplovc3_2_list, zq_asaplovc3_3_list, zq_asaplovc3_4_list
    

    for zq_j in E_TUG3:
        for zq_k in E_TUG2:
                for zq_l in E_TU12:
                    zq_tu12_idx1="MVC4TU12-{}-{}-{}-{}-{}".format(zq_slot,str(zq_vc4_1),str(zq_j),str(zq_k),str(zq_l))
                    zq_tu12_idx2="MVC4TU12-{}-{}-{}-{}-{}".format(zq_slot,str(zq_vc4_2),str(zq_j),str(zq_k),str(zq_l))

                    zq_tu12_ch1="{}.{}.{}.{}".format(str(zq_vc4_1 % E_BLOCK_SIZE),str(zq_j),str(zq_k),str(zq_l))
                    zq_tu12_ch2="{}.{}.{}.{}".format(str(zq_vc4_2 % E_BLOCK_SIZE),str(zq_j),str(zq_k),str(zq_l))
            
                    ONT.get_set_rx_lo_measure_channel(zq_ont_p1, zq_tu12_ch1)
                    ONT.get_set_rx_lo_measure_channel(zq_ont_p2, zq_tu12_ch2)
                
                    ONT.get_set_tx_lo_measure_channel(zq_ont_p1, zq_tu12_ch1)
                    ONT.get_set_tx_lo_measure_channel(zq_ont_p2, zq_tu12_ch2)
                
                    ONT.get_set_error_rate(zq_ont_p1, "LO", "1E-3")
                    ONT.get_set_error_rate(zq_ont_p2, "LO", "1E-3")
            
                    ONT.get_set_error_insertion_type(zq_ont_p1, "LPBIP")
                    ONT.get_set_error_insertion_type(zq_ont_p2, "LPBIP")
            
                    ###############################################################################################
                    ###############################################################################################
                    #                                       EBER check 
                    ###############################################################################################
                    ###############################################################################################
                    ONT.get_set_error_activation(zq_ont_p1, "LO", "ON")
            
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"OOS-AU")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
                    
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"EBER","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"EBER","NR","SA","NEND","TRMT",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"EBER","MJ","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"EBER","MJ","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc12_4_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"EBER","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc12_4_list)
                    
                    ONT.get_set_error_activation(zq_ont_p1, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
            
                    ONT.get_set_error_activation(zq_ont_p2, "LO", "ON")
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"OOS-AU")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"EBER","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"EBER","NR","SA","NEND","TRMT",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"EBER","MJ","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"EBER","MJ","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc12_4_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"EBER","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"EBER","MJ","SA","NEND","TRMT",zq_asaplovc12_4_list)
                    
                    ONT.get_set_error_activation(zq_ont_p2, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
            
                    ###############################################################################################
                    ###############################################################################################
                    #                                       SDBER check 
                    ###############################################################################################
                    ###############################################################################################
                    #
                    ONT.get_set_error_rate(zq_ont_p1, "LO", "1E-6")
                    ONT.get_set_error_rate(zq_ont_p2, "LO", "1E-6")
            
                    ONT.get_set_error_activation(zq_ont_p1, "LO", "ON")
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l, "IS-ANR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l, "IS-NR")
            
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SDBER","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SDBER","NR","SA","NEND","TRMT",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SDBER","MN","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SDBER","MN","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SDBER","MN","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc12_4_list)
                    
                    ONT.get_set_error_activation(zq_ont_p1, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l, "IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l, "IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
            
                    ONT.get_set_error_activation(zq_ont_p2, "LO", "ON")
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-ANR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SDBER","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SDBER","NR","SA","NEND","TRMT",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SDBER","MN","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SDBER","MN","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SDBER","MN","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SDBER","MN","SA","NEND","TRMT",zq_asaplovc12_4_list)
                    
                    ONT.get_set_error_activation(zq_ont_p2, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
            
                    ###############################################################################################
                    ###############################################################################################
                    #                                       TIM-V & SSF-V check 
                    ###############################################################################################
                    ###############################################################################################
            
                    ONT.get_set_alarm_insertion_type(zq_ont_p1, "TUAIS")
                    ONT.get_set_alarm_insertion_type(zq_ont_p2, "TUAIS")
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "ON")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"OOS-AU")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
            
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SSF-V","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SSF-V","NR","SA","NEND","TRMT",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SSF-V","NR","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SSF-V","NR","SA","NEND","TRMT",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SSF-V","MJ","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SSF-V","MJ","SA","NEND","TRMT",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"AIS-V","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SSF-V","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SSF-V","MJ","SA","NEND","TRMT",zq_asaplovc12_4_list)
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
            
                    ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "ON")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"OOS-AU")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
            
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SSF-V","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SSF-V","NR","SA","NEND","TRMT",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SSF-V","NR","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SSF-V","NR","SA","NEND","TRMT",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"AIS-V","NR","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SSF-V","MJ","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SSF-V","MJ","SA","NEND","TRMT",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"AIS-V","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"SSF-V","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"SSF-V","MJ","SA","NEND","TRMT",zq_asaplovc12_4_list)
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
            
            
                    ###############################################################################################
                    ###############################################################################################
                    #                                       LOP-V check 
                    ###############################################################################################
                    ###############################################################################################
            
                    ONT.get_set_alarm_insertion_type(zq_ont_p1, "TULOP")
                    ONT.get_set_alarm_insertion_type(zq_ont_p2, "TULOP")
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "ON")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"OOS-AU")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
            
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"LOP-V","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
            
                    ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "ON")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"OOS-AU")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
            
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"LOP-V","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"LOP-V","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
            
                
                    ###############################################################################################
                    ###############################################################################################
                    #                                       TIM-V check 
                    ###############################################################################################
                    ###############################################################################################
                
                    QS_075_Enable_Disable_TRCMON(zq_run, zq_tu12_idx1, "Y")
                    QS_075_Enable_Disable_TRCMON(zq_run, zq_tu12_idx2, "Y")
                    
                    QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu12_idx1, E_LO_TI)
                    QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu12_idx2, E_LO_TI)
                    time.sleep(E_WAIT)
                    time.sleep(E_WAIT)
                    time.sleep(E_WAIT)
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
            
                    #Change expected string on TU3 so that TIM-V condition is raised on LOVC12
                    QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu12_idx1, E_BAD_TI)
                    QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu12_idx2, E_BAD_TI)
                    time.sleep(E_WAIT)
                    time.sleep(E_WAIT)
                    time.sleep(E_WAIT)
                    
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"OOS-AU")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"OOS-AU")
            
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"TIM-V","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"TIM-V","NR","SA","NEND","TRMT",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"TIM-V","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"TIM-V","NR","SA","NEND","TRMT",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"TIM-V","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"TIM-V","MJ","SA","NEND","TRMT",zq_asaplovc12_4_list)
                    
                    #Restore Default ASAP profile
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
            
                    #SET TI as expected
                    QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu12_idx1, E_LO_TI)
                    QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu12_idx2, E_LO_TI)
                    time.sleep(E_WAIT)
                    time.sleep(E_WAIT)
                    time.sleep(E_WAIT)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
            
                    #RESTORE default TI on TU3s
                    QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu12_idx1, E_DEF_TI)
                    QS_055_Modify_MVC4TUn_LO_Trace_Block(zq_run, zq_tu12_idx2, E_DEF_TI)
            
                    #DISABLE TCMON (default)
                    QS_075_Enable_Disable_TRCMON(zq_run, zq_tu12_idx1, "N")
                    QS_075_Enable_Disable_TRCMON(zq_run, zq_tu12_idx2, "N")
            
                    ###############################################################################################
                    ###############################################################################################
                    #                                       UNEQ-V check 
                    ###############################################################################################
                    ###############################################################################################
            
                    ONT.get_set_alarm_insertion_type(zq_ont_p1, "LPUNEQ")
                    ONT.get_set_alarm_insertion_type(zq_ont_p2, "LPUNEQ")
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "ON")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"OOS-AU")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
            
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"UNEQ-V","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"UNEQ-V","NR","SA","NEND","TRMT",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc12_4_list)
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
            
                    ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "ON")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"OOS-AU")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
            
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"UNEQ-V","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"UNEQ-V","NR","SA","NEND","TRMT",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"UNEQ-V","MJ","SA","NEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"UNEQ-V","MJ","SA","NEND","TRMT",zq_asaplovc12_4_list)
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
            
            
                    ###############################################################################################
                    ###############################################################################################
                    #                                       RFI check 
                    ###############################################################################################
                    ###############################################################################################
            
                    ONT.get_set_alarm_insertion_type(zq_ont_p1, "LPRDI")
                    ONT.get_set_alarm_insertion_type(zq_ont_p2, "LPRDI")
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "ON")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
                    time.sleep(E_WAIT)
                    
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"RFI","NR","SA","FEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"RFI","NR","SA","FEND","TRMT",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"RFI","NR","SA","FEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"RFI","NR","SA","FEND","TRMT",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"RFI","NR","SA","FEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"RFI","NR","SA","FEND","TRMT",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"RFI","WR","SA","FEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"RFI","WR","SA","FEND","TRMT",zq_asaplovc12_4_list)
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p1, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
                    time.sleep(E_WAIT)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
            
                    ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "ON")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    time.sleep(E_WAIT)
            
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"RFI","NR","SA","FEND","RCV",zq_asaplovc12_1_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"RFI","NR","SA","FEND","TRMT",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"RFI","NR","SA","FEND","RCV",zq_asaplovc12_2_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"RFI","NR","SA","FEND","TRMT",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"RFI","NR","SA","FEND","RCV",zq_asaplovc12_3_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"RFI","NR","SA","FEND","TRMT",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"RFI","WR","SA","FEND","RCV",zq_asaplovc12_4_list)
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"RFI","WR","SA","FEND","TRMT",zq_asaplovc12_4_list)
                    
                    ONT.get_set_alarm_insertion_activation(zq_ont_p2, "LO", "OFF")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
                    time.sleep(E_WAIT)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
    
                    ###############################################################################################
                    ###############################################################################################
                    #                                       MAN check 
                    ###############################################################################################
                    ###############################################################################################
                    #SET FACILITY to OOS
                    QS_092_Set_FAC_pst(zq_run,zq_tu12_idx1,"OOS")
    
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"OOS-MA")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
                    time.sleep(E_WAIT)
                    
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"MAN","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"MAN","NR","SA","NEND","RCV",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"MAN","NR","SA","NEND","RCV",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx1,"MAN","NR","SA","NEND","RCV",zq_asaplovc12_4_list)
                    
                    #SET FACILITY to IS
                    QS_092_Set_FAC_pst(zq_run,zq_tu12_idx1,"IS")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
                    time.sleep(E_WAIT)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
            
                    #SET FACILITY to OOS
                    QS_092_Set_FAC_pst(zq_run,zq_tu12_idx2,"OOS")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"OOS-MA")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
                    time.sleep(E_WAIT)
            
                    #ALMPROF=LBL-ASAPLOVC12-SYSDFLT level1
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"MAN","NR","SA","NEND","RCV",zq_asaplovc12_1_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_2)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_2)
                    
                    #ALMPROF=LBL-ASAPLOVC12-NotPrimary level2
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"MAN","NR","SA","NEND","RCV",zq_asaplovc12_2_list)
                    
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_3)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_3)
                    
                    #ALMPROF=LBL-ASAPLOVC12-FerfAis level3
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"MAN","NR","SA","NEND","RCV",zq_asaplovc12_3_list)
            
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_4)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_4)
                    
                    #ALMPROF=LBL-ASAPLOVC12-ALL level4
                    QS_0950_Check_MVC4TU12_Alarm(zq_run,zq_tu12_idx2,"MAN","NR","SA","NEND","RCV",zq_asaplovc12_4_list)
                    
                    #SET FACILITY to IS
                    QS_092_Set_FAC_pst(zq_run,zq_tu12_idx2,"IS")
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx2,E_ASAP_LOVC12_1)
                    QS_080_Set_Alm_Prof(zq_run,zq_tu12_idx1,E_ASAP_LOVC12_1)
                    time.sleep(E_WAIT)
            
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_2, zq_j, zq_k, zq_l,"IS-NR")
                    QS_0900_Check_FAC_pst(zq_run, zq_slot, zq_vc4_1, zq_j, zq_k, zq_l,"IS-NR")
            
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx2)
                    QS_005_Check_Cond_Absence(zq_run, "LOVC12", zq_tu12_idx1)
    
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
        global zq_asaplovc12_1_list, zq_asaplovc12_2_list, zq_asaplovc12_3_list,zq_asaplovc12_4_list
        global zq_asaplovc3_1_list, zq_asaplovc3_2_list, zq_asaplovc3_3_list, zq_asaplovc3_4_list

        print("\n******************** START ********************")
        '''
        VERIFY DETECTION OF SSF/AIS/LOP CONDITION ALARM IN MVC4 FACILITIES
        '''
        print("\n******************************************************************")
        print("\n   VERIFY DETECTION OF SDBER CONDITION ALARM IN MVC4TU3 FACILITIES")
        print("\n******************************************************************")
        
        self.start_tps_block(NE1.id,"FM", "5-2-31-1")

        E_VC3_EXE = False
        E_VC12_EXE = True

        E_LO_MTX = "MXH60GLO"
        E_HO_TI = 'X4F4E5420484F2D5452414345202020' #'ONT HO-TRACE   '
        E_SLOT = ['2','3','4','5','6','7','8','12','13','14','15','16','17','18','19']

        #MVC4 for 6 TU3s
        E_VC4_1_1 = 34      # <64
        E_VC4_1_2 = 92      # 65<x<129
        E_VC4_2_1 = 189     # 128<x<193
        E_VC4_2_2 = 227     # 192<x<257
        E_VC4_3_1 = 289     # 256<x<321
        E_VC4_3_2 = 356     # 320<x<385

        #MVC4TU3-1-1-7-<MVC4>-1&&-3
        E_COND_AID_BK1_1 = "MVC4TU3-{}-{}-1&&-3".format(NE1_M1,str(E_VC4_1_1))
        E_COND_AID_BK1_2 = "MVC4TU3-{}-{}-1&&-3".format(NE1_M1,str(E_VC4_1_2))
        E_COND_AID_BK2_1 = "MVC4TU3-{}-{}-1&&-3".format(NE1_M1,str(E_VC4_2_1))
        E_COND_AID_BK2_2 = "MVC4TU3-{}-{}-1&&-3".format(NE1_M1,str(E_VC4_2_2))
        E_COND_AID_BK3_1 = "MVC4TU3-{}-{}-1&&-3".format(NE1_M1,str(E_VC4_3_1))
        E_COND_AID_BK3_2 = "MVC4TU3-{}-{}-1&&-3".format(NE1_M1,str(E_VC4_3_2))
        
        #MVC4 for 6 TU12s
        E_VC4_1_3 = 17      # <64
        E_VC4_1_4 = 105     # 65<x<129
        E_VC4_2_3 = 156     # 128<x<193
        E_VC4_2_4 = 220     # 192<x<257
        E_VC4_3_3 = 300     # 256<x<321
        E_VC4_3_4 = 333     # 320<x<385

        #MVC4TU12-1-1-7-<MVC4>-1&&-3-1&&-7-1&&-3
        E_COND_AID_BK1_3 = "MVC4TU12-{}-{}-1&&-3-1&&-7-1&&-3".format(NE1_M1,str(E_VC4_1_3))
        E_COND_AID_BK1_4 = "MVC4TU12-{}-{}-1&&-3-1&&-7-1&&-3".format(NE1_M1,str(E_VC4_1_4))
        E_COND_AID_BK2_3 = "MVC4TU12-{}-{}-1&&-3-1&&-7-1&&-3".format(NE1_M1,str(E_VC4_2_3))
        E_COND_AID_BK2_4 = "MVC4TU12-{}-{}-1&&-3-1&&-7-1&&-3".format(NE1_M1,str(E_VC4_2_4))
        E_COND_AID_BK3_3 = "MVC4TU12-{}-{}-1&&-3-1&&-7-1&&-3".format(NE1_M1,str(E_VC4_3_3))
        E_COND_AID_BK3_4 = "MVC4TU12-{}-{}-1&&-3-1&&-7-1&&-3".format(NE1_M1,str(E_VC4_3_4))
        
        zq_mtxlo_slot=NE1_M1
        NE1_stm64p1=NE1_S1
        NE1_stm64p2=NE1_S2
        zq_board_to_remove=list()
        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")
        
        zq_asaplovc3_1_list = QS_200_Fill_ASAP_List(self,E_ASAP_LOVC3_1)
        zq_asaplovc3_2_list = QS_200_Fill_ASAP_List(self,E_ASAP_LOVC3_2)
        zq_asaplovc3_3_list = QS_200_Fill_ASAP_List(self,E_ASAP_LOVC3_3)
        zq_asaplovc3_4_list = QS_200_Fill_ASAP_List(self,E_ASAP_LOVC3_4)
        
        zq_asaplovc12_1_list = QS_200_Fill_ASAP_List(self,E_ASAP_LOVC12_1)
        zq_asaplovc12_2_list = QS_200_Fill_ASAP_List(self,E_ASAP_LOVC12_2)
        zq_asaplovc12_3_list = QS_200_Fill_ASAP_List(self,E_ASAP_LOVC12_3)
        zq_asaplovc12_4_list = QS_200_Fill_ASAP_List(self,E_ASAP_LOVC12_4)

        '''
        Board equipment if not yet!
        '''
        zq_tl1_res=NE1.tl1.do("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_attr_list=zq_msg.get_cmd_attr_values("{}-{}".format(E_LO_MTX, zq_mtxlo_slot))
            if zq_attr_list['PROVISIONEDTYPE']==E_LO_MTX and zq_attr_list['ACTUALTYPE']==E_LO_MTX:  #Board equipped 
                print("Board already equipped")
            else:
                zq_filter=TL1check()
                zq_filter.add_pst("IS")
                zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                NE1.tl1.do_until("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),zq_filter)


        
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
        
        if E_VC3_EXE:        
            print("\n*****************************************************************************************************")
            print("\n   CHECK AIS_V/EBER/LOP-V/MAN/RFI/SDBER/SSF-V/TIM-V/UNEQ-V for MVC4TU3 FACILITIES IN 1st 128 BLOCK   ")
            print("\n*****************************************************************************************************")
            '''
            #CHECK FIRST 128 BLOCK of MVC4TU3 
            '''
            QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)
    
            QS_040_Modify_AU4_HO_Trace_Block(self, NE1_stm64p1, (E_VC4_1_1 % E_BLOCK_SIZE), 1, E_HO_TI)
            QS_040_Modify_AU4_HO_Trace_Block(self, NE1_stm64p2, (E_VC4_1_2 % E_BLOCK_SIZE), 1, E_HO_TI)
            
            QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_1_1, 1, E_HO_TI)
            QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_1_2, 1, E_HO_TI)
            
            QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_1, "Y")
            QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_2, "Y")
    
    
            QS_030_Create_LO_XC_Block(self, E_VC4_1_1, E_VC4_1_2, zq_xc_list)
    
            '''
            #Configure both ONT ports to VC3 mapping
            '''
            ONT.get_set_tx_bit_rate(ONT_P1, "STM64")
            ONT.get_set_tx_bit_rate(ONT_P2, "STM64")
            
            ONT.get_set_rx_channel_mapping_size(ONT_P1, "VC3")
            ONT.get_set_rx_channel_mapping_size(ONT_P2, "VC3")
            
            ONT.get_set_tx_channel_mapping_size(ONT_P1, "VC3")
            ONT.get_set_tx_channel_mapping_size(ONT_P2, "VC3")
    
            ONT.get_set_laser_status(ONT_P1, "ON")
            ONT.get_set_laser_status(ONT_P2, "ON")
    
            ONT.get_set_clock_reference_source(ONT_P1, "RX")
            ONT.get_set_clock_reference_source(ONT_P2, "RX")
    
            ONT.get_set_background_channels_fill_mode(ONT_P1, "FIX")
            ONT.get_set_background_channels_fill_mode(ONT_P2, "FIX")
        
            #EBER parameter setting
            ONT.get_set_error_insertion_mode(ONT_P1, "LO", "RATE")
            ONT.get_set_error_insertion_mode(ONT_P2, "LO", "RATE")
    
            #Alarm parameter setting
            ONT.get_set_alarm_insertion_mode(ONT_P1, "LO", "CONT")
            ONT.get_set_alarm_insertion_mode(ONT_P2, "LO", "CONT")
            
    
            time.sleep(E_WAIT)
            time.sleep(E_WAIT)
            
            '''
            #INITIAL CHECK NO ALARM PRESENT ON PATH AFTER HO CROSS-CONNECTIONS ARE CREATED 
            '''
            QS_150_Check_No_Alarm(self,E_COND_AID_BK1_1)
            QS_150_Check_No_Alarm(self,E_COND_AID_BK1_2)
            
            QS_100_Check_Cond_Attr(self, ONT_P1, ONT_P2, zq_mtxlo_slot, E_VC4_1_1, E_VC4_1_2)
    
            QS_060_Delete_LO_XC_Block(self, E_VC4_1_1, E_VC4_1_2, zq_xc_list)
            
            QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_1, "N")
            QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_2, "N")
            
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)
    
            print("\n*****************************************************************************************************")
            print("\n   CHECK AIS_V/EBER/LOP-V/MAN/RFI/SDBER/SSF-V/TIM-V/UNEQ-V for MVC4TU3 FACILITIES IN 2nd 128 BLOCK   ")
            print("\n*****************************************************************************************************")
    
            zq_xc_list=list()
            zq_xc_list.append("EMPTY,EMPTY")
    
            QS_010_Create_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_010_Create_HO_XC_Block(self, NE1_stm64p4, 1, E_BLOCK_SIZE, zq_xc_list)
    
            QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)
    
            QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_2_1, 1, E_HO_TI)
            QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_2_2, 1, E_HO_TI)
    
            QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_1, "Y")
            QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_2, "Y")
    
            QS_030_Create_LO_XC_Block(self, E_VC4_2_1, E_VC4_2_2, zq_xc_list)
     
            time.sleep(E_WAIT)
            time.sleep(E_WAIT)
            
            '''
            #INITIAL CHECK NO ALARM PRESENT ON PATH AFTER HO CROSS-CONNECTIONS ARE CREATED 
            '''
            QS_150_Check_No_Alarm(self,E_COND_AID_BK2_1)
            QS_150_Check_No_Alarm(self,E_COND_AID_BK2_2)
            
            QS_100_Check_Cond_Attr(self, ONT_P1, ONT_P2, zq_mtxlo_slot, E_VC4_2_1, E_VC4_2_2)
           
            QS_060_Delete_LO_XC_Block(self, E_VC4_2_1, E_VC4_2_2, zq_xc_list)
    
            QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_1, "N")
            QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_2, "N")
    
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p4, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)
    
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)
            
            print("\n*****************************************************************************************************")
            print("\n   CHECK AIS_V/EBER/LOP-V/MAN/RFI/SDBER/SSF-V/TIM-V/UNEQ-V for MVC4TU3 FACILITIES IN 3rd 128 BLOCK   ")
            print("\n*****************************************************************************************************")
    
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
            
            time.sleep(E_WAIT)
            time.sleep(E_WAIT)
    
            QS_150_Check_No_Alarm(self,E_COND_AID_BK3_1)
            QS_150_Check_No_Alarm(self,E_COND_AID_BK3_2)
            
            QS_100_Check_Cond_Attr(self, ONT_P1, ONT_P2, zq_mtxlo_slot, E_VC4_3_1, E_VC4_3_2)
    
            QS_060_Delete_LO_XC_Block(self, E_VC4_3_1, E_VC4_3_2, zq_xc_list)
    
            QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_1, "N")
            QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_2, "N")
    
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p5, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p6, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)
    
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p3, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p4, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)
            
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, E_BLOCK_SIZE*4+1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE*5+1, E_BLOCK_SIZE, zq_xc_list)

        if E_VC12_EXE:
            '''
            Change MVC4 structure to 63xTU12 for preset MVC4
            '''
            zq_filter=TL1check()
            zq_filter.add_field('LOSTRUCT', '63xTU12')
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_1_3))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_1_3),zq_filter)
    
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_1_4))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_1_4),zq_filter)
    
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_2_3))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_2_3),zq_filter)
            
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_2_4))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_2_4),zq_filter)
            
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_3_3))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_3_3),zq_filter)
            
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_3_4))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_3_4),zq_filter)
    
    
            print("\n******************************************************************************************************")
            print("\n   CHECK AIS_V/EBER/LOP-V/MAN/RFI/SDBER/SSF-V/TIM-V/UNEQ-V for MVC4TU12 FACILITIES IN 1st 128 BLOCK   ")
            print("\n******************************************************************************************************")
            '''
            CHECK FIRST 128 BLOCK of MVC4TU12
            '''
            zq_xc_list=list()
            zq_xc_list.append("EMPTY,EMPTY")
    
            QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)
    
            QS_040_Modify_AU4_HO_Trace_Block(self, NE1_stm64p1, (E_VC4_1_3 % E_BLOCK_SIZE), 1, E_HO_TI)
            QS_040_Modify_AU4_HO_Trace_Block(self, NE1_stm64p2, (E_VC4_1_4 % E_BLOCK_SIZE), 1, E_HO_TI)
            
            QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_1_3, 1, E_HO_TI)
            QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_1_4, 1, E_HO_TI)
            
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_3, "Y")
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_4, "Y")
    
    
            QS_035_Create_LO_XC_Block(self, E_VC4_1_3, E_VC4_1_4, zq_xc_list)
    
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
        
            #EBER parameter setting
            ONT.get_set_error_insertion_mode(ONT_P1, "LO", "RATE")
            ONT.get_set_error_insertion_mode(ONT_P2, "LO", "RATE")
    
            #Alarm parameter setting
            ONT.get_set_alarm_insertion_mode(ONT_P1, "LO", "CONT")
            ONT.get_set_alarm_insertion_mode(ONT_P2, "LO", "CONT")
            
    
            time.sleep(E_WAIT)
            time.sleep(E_WAIT)
            
            '''
            INITIAL CHECK NO ALARM PRESENT ON PATH AFTER HO CROSS-CONNECTIONS ARE CREATED 
            '''
            QS_150_Check_No_Alarm(self,E_COND_AID_BK1_3)
            QS_150_Check_No_Alarm(self,E_COND_AID_BK1_4)
            
            QS_1000_Check_Cond_Attr(self, ONT_P1, ONT_P2, zq_mtxlo_slot, E_VC4_1_3, E_VC4_1_4)
    
            QS_065_Delete_LO_XC_Block(self, E_VC4_1_3, E_VC4_1_4, zq_xc_list)
            
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_3, "N")
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_4, "N")
            
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)
    
            print("\n******************************************************************************************************")
            print("\n   CHECK AIS_V/EBER/LOP-V/MAN/RFI/SDBER/SSF-V/TIM-V/UNEQ-V for MVC4TU12 FACILITIES IN 2nd 128 BLOCK   ")
            print("\n******************************************************************************************************")
    
            zq_xc_list=list()
            zq_xc_list.append("EMPTY,EMPTY")
    
            QS_010_Create_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_010_Create_HO_XC_Block(self, NE1_stm64p4, 1, E_BLOCK_SIZE, zq_xc_list)
    
            QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)
    
            QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_2_3, 1, E_HO_TI)
            QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_2_4, 1, E_HO_TI)
    
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_3, "Y")
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_4, "Y")
    
            QS_035_Create_LO_XC_Block(self, E_VC4_2_3, E_VC4_2_4, zq_xc_list)
     
            time.sleep(E_WAIT)
            time.sleep(E_WAIT)
            
            '''
            INITIAL CHECK NO ALARM PRESENT ON PATH AFTER HO CROSS-CONNECTIONS ARE CREATED 
            '''
            QS_150_Check_No_Alarm(self,E_COND_AID_BK2_3)
            QS_150_Check_No_Alarm(self,E_COND_AID_BK2_4)
            
            QS_1000_Check_Cond_Attr(self, ONT_P1, ONT_P2, zq_mtxlo_slot, E_VC4_2_3, E_VC4_2_4)
           
            QS_065_Delete_LO_XC_Block(self, E_VC4_2_3, E_VC4_2_4, zq_xc_list)
    
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_3, "N")
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_4, "N")
    
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p4, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)
    
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)
            
            print("\n******************************************************************************************************")
            print("\n   CHECK AIS_V/EBER/LOP-V/MAN/RFI/SDBER/SSF-V/TIM-V/UNEQ-V for MVC4TU12 FACILITIES IN 3rd 128 BLOCK   ")
            print("\n******************************************************************************************************")
    
            zq_xc_list=list()
            zq_xc_list.append("EMPTY,EMPTY")
    
            QS_010_Create_HO_XC_Block(self, NE1_stm64p5, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_010_Create_HO_XC_Block(self, NE1_stm64p6, 1, E_BLOCK_SIZE, zq_xc_list)
            
            QS_010_Create_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_010_Create_HO_XC_Block(self, NE1_stm64p4, 1, E_BLOCK_SIZE, zq_xc_list)
    
            QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)
            
            QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_3_3, 1, E_HO_TI)
            QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_3_4, 1, E_HO_TI)
            
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_3, "Y")
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_4, "Y")
    
            QS_035_Create_LO_XC_Block(self, E_VC4_3_3, E_VC4_3_4, zq_xc_list)
            
            time.sleep(E_WAIT)
            time.sleep(E_WAIT)
    
            QS_150_Check_No_Alarm(self,E_COND_AID_BK3_3)
            QS_150_Check_No_Alarm(self,E_COND_AID_BK3_4)
            
            QS_1000_Check_Cond_Attr(self, ONT_P1, ONT_P2, zq_mtxlo_slot, E_VC4_3_3, E_VC4_3_4)
    
            QS_065_Delete_LO_XC_Block(self, E_VC4_3_3, E_VC4_3_4, zq_xc_list)
    
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_3, "N")
            QS_077_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_4, "N")
    
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p5, 1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p6, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)
    
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p3, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p4, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)
            
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, E_BLOCK_SIZE*4+1, E_BLOCK_SIZE, zq_xc_list)
            QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE*5+1, E_BLOCK_SIZE, zq_xc_list)
    
            '''
            Restore MVC4 structure to 3xTU3 for preset MVC4
            '''
            zq_filter=TL1check()
            zq_filter.add_field('LOSTRUCT', '3xTU3')
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_1_3))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_1_3),zq_filter)
    
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_1_4))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_1_4),zq_filter)
    
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_2_3))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_2_3),zq_filter)
            
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_2_4))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_2_4),zq_filter)
            
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_3_3))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_3_3),zq_filter)
            
            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_3_4))
            NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_3_4),zq_filter)
    


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


        self.stop_tps_block(NE1.id,"FM", "5-2-31-1")
    

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
    