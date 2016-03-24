#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: Verify the TIM-V alarm on MVC4TU3 facilities.
:field Topology: 5
:field Dependency:
:field Lab: SVT
:field TPS: FM__5-2-24-1
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
E_WAIT = 10


E_HO_TI  = 'X4F4E5420484F2D5452414345202020' #'ONT HO-TRACE   '
E_LO_TI  = 'X4F4E54204C4F2D5452414345202020' #'ONT LO-TRACE   '
E_BAD_TI = 'X4142434445464748494A4B4C202020' #'ABCDEFGHIJKL   '
E_DEF_TI = 'X000000000000000000000000000000' 


E_VC4_1_1 = 34      # <64
E_VC4_1_2 = 92      # 65<x<129
E_VC4_2_1 = 189     # 128<x<193
E_VC4_2_2 = 227     # 192<x<257
E_VC4_3_1 = 289     # 256<x<321
E_VC4_3_2 = 356     # 320<x<385


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


def QS_055_Modify_MVC4TU3_LO_Trace_Block(zq_run, zq_vc3, zq_trace):

    zq_tl1_res=NE1.tl1.do("ED-TU3::{}::::TRCEXPECTED={}, EGTRCEXPECTED={};".format(zq_vc3, zq_trace, zq_trace))
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


def QS_070_Enable_Disable_POM(zq_run, zq_mtx_slot, zq_vc4, zq_enadis):

    for zq_j in range (1,4):
        zq_tl1_res=NE1.tl1.do("ED-TU3::MVC4TU3-{}-{}-{}::::POM={},EGPOM={};".format(zq_mtx_slot, zq_vc4, zq_j, zq_enadis, zq_enadis))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
    
        if zq_cmd == (True,'COMPLD'):
            dprint("\nOK\tPOM and EGPOM setting to [{}] for MVC4TU3-{}-{}-{} successful".format(zq_enadis,zq_mtx_slot, zq_vc4, zq_j),2)
            zq_run.add_success(NE1, "POM and EGPOM setting to [{}] for MVC4TU3-{}-{}-{} successful".format(zq_enadis,zq_mtx_slot, zq_vc4, zq_j),"0.0", "POM and EGPOM setting")
    
        else:
            dprint("\nKO\tPOM and EGPOM setting to [{}] for MVC4TU3-{}-{}-{} failed".format(zq_enadis,zq_mtx_slot, zq_vc4, zq_j),2)
            zq_run.add_failure(NE1,  "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","POM and EGPOM setting to [{}] for MVC4TU3-{}-{}-{} failed".format(zq_enadis,zq_mtx_slot, zq_vc4, zq_j))
        
    return


def QS_075_Enable_Disable_TRCMON(zq_run, zq_vc4, zq_enadis):

    zq_tl1_res=NE1.tl1.do("ED-TU3::{}::::TRCMON={},EGTRCMON={};".format(zq_vc4, zq_enadis, zq_enadis))
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


def QS_80_Check_ONT_Alarm(zq_run, zq_ont_port, zq_alm_exp):

    ONT.start_measurement(zq_ont_port)
    time.sleep(E_WAIT)
    ONT.halt_measurement(zq_ont_port)
    zq_alm = ONT.retrieve_ho_lo_alarms(zq_ont_port)
    if zq_alm[0] == True:           #COMMAND IS OK
        if len(zq_alm[1]) == 0:     #NO ALARM FOUND
            if zq_alm_exp == "":    #NO ALARM EXPECTED AND NO ALARM FOUND
                dprint("OK\tNO Alarm found on ONT port {}".format(zq_ont_port),2)
                zq_run.add_success(NE1, "NO Alarm found on ONT port {}".format(zq_ont_port),"0.0", "ONT Alarm check")
                
            else:                   #NO ALARM EXPECTED BUT ALARM FOUND  
                dprint("KO\tAlarm found on ONT port {}:".format(zq_ont_port),2)
                dprint("\t\tAlarm: Exp [{}]  - Rcv [{}]".format("no alarm",zq_alm[1][0]),2)
                zq_run.add_failure(NE1,  "ONT Alarm check","0.0", "ONT Alarms check", "Alarm found on ONT port {}: Exp [{}]  - Rcv [{}]".format(zq_ont_port, "no alarm", zq_alm[1][0]))
                
        else:                       #ALARM FOUND
            if zq_alm[1][0] == zq_alm_exp:      #ALARM FOUND AND ALARM WAS EXPECTED
                dprint("OK\t{} Alarm found on ONT port {}".format(zq_alm_exp,zq_ont_port),2)
                zq_run.add_success(NE1, "{} Alarm found on ONT port {}".format(zq_alm_exp,zq_ont_port),"0.0", "ONT Alarm check")
            else:                               #ALARM FOUND BUT ALARM WAS NOT EXPECTED
                dprint("KO\tAlarm mismatch on ONT port {}:".format(zq_ont_port),2)
                dprint("\t\tAlarm: Exp [{}]  - Rcv [{}]".format(zq_alm_exp,zq_alm[1][0]),2)
                zq_run.add_failure(NE1,  "ONT Alarm check","0.0", "ONT Alarms check", "Alarm mismatch on ONT port {}: Exp [{}]  - Rcv [{}]".format(zq_ont_port, zq_alm_exp, zq_alm[1][0]))

    return

def QS_90_Check_MVC4TU3_Alarm(zq_run,zq_vc3,zq_man_exp,zq_type_exp,zq_dir_exp):

    zq_tl1_res=NE1.tl1.do("RTRV-COND-LOVC3::{}:::{},{},{};".format(str(zq_vc3),zq_man_exp,zq_type_exp,zq_dir_exp))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    dprint(NE1.tl1.get_last_outcome(),1)
    if (zq_msg.get_cmd_response_size() == 0):
        dprint("KO\t{} Condition verification failure for {} facility : Exp [{}] - Rcv [0]".format(zq_man_exp, zq_vc3, E_RFI_NUM),2)
        zq_run.add_failure(NE1,"{} Condition verification failure for {} facility : Exp [{}] - Rcv [0]".format(zq_man_exp, zq_vc3, E_RFI_NUM),"0.0", "SSF CONDITION CHECK","SSF Condition verification failure: Exp [{}] - Rcv [0]".format(E_RFI_NUM))
    else:
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_man = zq_msg.get_cmd_attr_value("{},LOVC3".format(zq_vc3), 2)
            zq_type = zq_msg.get_cmd_attr_value("{},LOVC3".format(zq_vc3), 6)
            zq_dir = zq_msg.get_cmd_attr_value("{},LOVC3".format(zq_vc3), 7)
            if (zq_man == zq_man_exp) and (zq_type == zq_type_exp) and (zq_dir == zq_dir_exp):
                dprint("OK\t{} Condition verification successful for {} facility [{}][{}][{}].".format(zq_man_exp,str(zq_vc3),zq_man,zq_type,zq_dir),2)
                zq_run.add_success(NE1, "{} Condition verification successful for {} facility [{}][{}][{}].".format(zq_man_exp,str(zq_vc3),zq_man,zq_type,zq_dir),"0.0", "{} CONDITION CHECK".format(zq_man_exp))
            else:
                dprint("KO\t{} Condition verification failure for {} facility.".format(zq_man_exp, str(zq_vc3)),2)
                dprint("\t\tCOND: Exp [{}]  - Rcv [{}]".format(zq_man_exp,zq_man),2)
                dprint("\t\tTYPE: Exp [{}] - Rcv [{}]".format(zq_type_exp,zq_type),2)
                dprint("\t\tDIR : Exp [{}]  - Rcv [{}]".format(zq_dir_exp,zq_dir),2)
                zq_run.add_failure(NE1,"{} Condition verification failure for {} facility : Exp: [{}-{}-{}] - Rcv [{}-{}-{}]".format(zq_man_exp, str(zq_vc3),zq_man_exp,zq_type_exp,zq_dir_exp,zq_man,zq_type,zq_dir),"0.0", "{} CONDITION CHECK".format(zq_man_exp),"{} Condition verification failure for {} facility : Exp: [{}-{}-{}] - Rcv [{}-{}-{}]".format(zq_man_exp, str(zq_vc3),zq_man_exp,zq_type_exp,zq_dir_exp,zq_man,zq_type,zq_dir))
        
    return


def QS_100_Check_TIM(zq_run, zq_ONT_p1, zq_ONT_p2, zq_mtx_slot, zq_vc4_1, zq_vc4_2):
    
    for zq_j in range(1,4):
        zq_tu3_ch1="{}.{}.1.1".format(str(zq_vc4_1 % E_BLOCK_SIZE),str(zq_j))
        zq_tu3_ch2="{}.{}.1.1".format(str(zq_vc4_2 % E_BLOCK_SIZE),str(zq_j))
         
        zq_tu3_idx1="MVC4TU3-{}-{}-{}".format(zq_mtx_slot,str(zq_vc4_1),str(zq_j))
        zq_tu3_idx2="MVC4TU3-{}-{}-{}".format(zq_mtx_slot,str(zq_vc4_2),str(zq_j))
    
        ONT.get_set_rx_lo_measure_channel(zq_ONT_p1, zq_tu3_ch1)
        ONT.get_set_rx_lo_measure_channel(zq_ONT_p2, zq_tu3_ch2)
    
        ONT.get_set_tx_lo_measure_channel(zq_ONT_p1, zq_tu3_ch1)
        ONT.get_set_tx_lo_measure_channel(zq_ONT_p2, zq_tu3_ch2)

        QS_075_Enable_Disable_TRCMON(zq_run, zq_tu3_idx1, "Y")
        QS_075_Enable_Disable_TRCMON(zq_run, zq_tu3_idx2, "Y")
        
        QS_055_Modify_MVC4TU3_LO_Trace_Block(zq_run, zq_tu3_idx1, E_LO_TI)
        QS_055_Modify_MVC4TU3_LO_Trace_Block(zq_run, zq_tu3_idx2, E_LO_TI)
        time.sleep(E_WAIT)
        time.sleep(E_WAIT)
        time.sleep(E_WAIT)

        #VERIFY INITIAL NOT ALARM CONDITION ON LOVC3
        #MVC4TU3-1-1-7-<MVC4>-1&&-3
        QS_150_Check_No_Alarm(zq_run,"MVC4TU3-{}-{}-1&&-3".format(zq_mtx_slot,str(zq_vc4_1)))
        QS_150_Check_No_Alarm(zq_run,"MVC4TU3-{}-{}-1&&-3".format(zq_mtx_slot,str(zq_vc4_2)))
        
        #Change expected string on TU3 so that TIM-V condition is raised on LOVC3
        QS_055_Modify_MVC4TU3_LO_Trace_Block(zq_run, zq_tu3_idx1, E_BAD_TI)
        QS_055_Modify_MVC4TU3_LO_Trace_Block(zq_run, zq_tu3_idx2, E_BAD_TI)
        time.sleep(E_WAIT)
        time.sleep(E_WAIT)
        time.sleep(E_WAIT)

        QS_90_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"TIM-V","NEND","RCV")
        QS_90_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx1,"TIM-V","NEND","TRMT")
        QS_90_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"TIM-V","NEND","RCV")
        QS_90_Check_MVC4TU3_Alarm(zq_run,zq_tu3_idx2,"TIM-V","NEND","TRMT")

        #Change TIM sent from ONT into the expected on TU3 so that LP-TIM alarm is raised on ONT ports
        ONT.get_set_tu_path_trace_tx_TR16_string(zq_ONT_p1,"ABCDEFGHIJKL   ")
        ONT.get_set_tu_path_trace_tx_TR16_string(zq_ONT_p2,"ABCDEFGHIJKL   ")

        QS_80_Check_ONT_Alarm(zq_run, zq_ONT_p1, "LP-TIM")
        QS_80_Check_ONT_Alarm(zq_run, zq_ONT_p2, "LP-TIM")

        #Restore original TIM sent from ONT into the expected on TU3 so that LP-TIM alarm cleared on ONT ports
        ONT.get_set_tu_path_trace_tx_TR16_string(zq_ONT_p1,"ONT LO-TRACE   ")
        ONT.get_set_tu_path_trace_tx_TR16_string(zq_ONT_p2,"ONT LO-TRACE   ")

        QS_075_Enable_Disable_TRCMON(zq_run, zq_tu3_idx1, "N")
        QS_075_Enable_Disable_TRCMON(zq_run, zq_tu3_idx2, "N")

        QS_055_Modify_MVC4TU3_LO_Trace_Block(zq_run, zq_tu3_idx1, E_DEF_TI)
        QS_055_Modify_MVC4TU3_LO_Trace_Block(zq_run, zq_tu3_idx2, E_DEF_TI)

        time.sleep(E_WAIT)
        time.sleep(E_WAIT)
        time.sleep(E_WAIT)

        QS_80_Check_ONT_Alarm(zq_run, zq_ONT_p1, "")
        QS_80_Check_ONT_Alarm(zq_run, zq_ONT_p2, "")

        QS_150_Check_No_Alarm(zq_run,"MVC4TU3-{}-{}-1&&-3".format(zq_mtx_slot,str(zq_vc4_1)))
        QS_150_Check_No_Alarm(zq_run,"MVC4TU3-{}-{}-1&&-3".format(zq_mtx_slot,str(zq_vc4_2)))
    
    
    return


def QS_150_Check_No_Alarm(zq_run,zq_vc3_range):

    zq_tl1_res=NE1.tl1.do("RTRV-COND-LOVC3::{};".format(zq_vc3_range))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    dprint(NE1.tl1.get_last_outcome(),1)
    if (zq_msg.get_cmd_response_size() == 0):
        dprint("OK\tPath is alarm free.",2)
        zq_run.add_success(NE1,"Path is alarm free.","0.0","CONDITION ALARMS CHECK")
    else:
        dprint("KO\tAlarms are present on path.",2)
        zq_run.add_failure(NE1,"Alarms are present on path.","0.0","CONDITION ALARMS CHECK","Alarms are present on path.")

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
        VERIFY DETECTION OF SSF/AIS/LOP CONDITION ALARM IN MVC4 FACILITIES
        '''
        print("\n***************************************************************************")
        print("\n   VERIFY DETECTION OF SSF/AIS/LOP CONDITION ALARM IN MVC4TU3 FACILITIES   ")
        print("\n***************************************************************************")
        
        self.start_tps_block(NE1.id,"FM", "5-2-24-1")

        E_LO_MTX = "MXH60GLO"
        E_SLOT = ['2','3','4','5','6','7','8','12','13','14','15','16','17','18','19']
        
        zq_mtxlo_slot=NE1_M1
        NE1_stm64p1=NE1_S1
        NE1_stm64p2=NE1_S2
        zq_board_to_remove=list()
        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")

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
        
        print("\n******************************************************************************")
        print("\n   CHECK SSF CONDITION ALARM FOR SIX MVC4TU3 FACILITIES IN 1st 128 BLOCK      ")
        print("\n******************************************************************************")
        '''
        CHECK FIRST 128 BLOCK of MVC4TU3 
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
        Configure both ONT ports to VC3 mapping
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
    
        time.sleep(E_WAIT)
        
        '''
        INITIAL CHECK NO ALARM PRESENT ON PATH AFTER HO CROSS-CONNECTIONS ARE CREATED 
        '''
        
        QS_100_Check_TIM(self, ONT_P1, ONT_P2, zq_mtxlo_slot, E_VC4_1_1, E_VC4_1_2)

        QS_060_Delete_LO_XC_Block(self, E_VC4_1_1, E_VC4_1_2, zq_xc_list)
        
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_1, "N")
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_1_2, "N")
        
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        print("\n******************************************************************************")
        print("\n   CHECK SSF CONDITION ALARM FOR SIX MVC4TU3 FACILITIES IN 2ND 128 BLOCK      ")
        print("\n******************************************************************************")
        '''
        CHECK SECOND 128 BLOCK of MVC4TU3 
        '''
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
        
        '''
        INITIAL CHECK NO ALARM PRESENT ON PATH AFTER HO CROSS-CONNECTIONS ARE CREATED 
        '''
        QS_100_Check_TIM(self, ONT_P1, ONT_P2, zq_mtxlo_slot, E_VC4_2_1, E_VC4_2_2)
        
        QS_060_Delete_LO_XC_Block(self, E_VC4_2_1, E_VC4_2_2, zq_xc_list)

        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_1, "N")
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_2_2, "N")

        QS_020_Delete_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p4, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)
        

        print("\n******************************************************************************")
        print("\n   CHECK SSF CONDITION ALARM FOR SIX MVC4TU3 FACILITIES IN 3ND 128 BLOCK      ")
        print("\n******************************************************************************")
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
        
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_3_1, 1, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_3_2, 1, E_HO_TI)
        
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_1, "Y")
        QS_070_Enable_Disable_POM(self, zq_mtxlo_slot, E_VC4_3_2, "Y")

        QS_030_Create_LO_XC_Block(self, E_VC4_3_1, E_VC4_3_2, zq_xc_list)
        
        time.sleep(E_WAIT)
        
        '''
        INITIAL CHECK NO ALARM PRESENT ON PATH AFTER HO CROSS-CONNECTIONS ARE CREATED 
        '''
        QS_100_Check_TIM(self, ONT_P1, ONT_P2, zq_mtxlo_slot, E_VC4_3_1, E_VC4_3_2)

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


        self.stop_tps_block(NE1.id,"FM", "5-2-24-1")
    
    
    
    
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