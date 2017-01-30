#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: This test provides a method to verify the behavior of the validity  
:field Description: flag for the PM counters of MVC4 facilities, when counters are reset.
:field Description: The COMPL flag for current data and PRTL flag for first history entry are being checked.
:field Topology: 5
:field Dependency: NA
:field Lab: SVT
:field TPS: PM__5-5-17-1
:field TPS: PM__5-5-17-2
:field TPS: PM__5-5-15-1
:field TPS: PM__5-5-15-2
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

E_MAX_MVC4 = 384
E_LO_MTX = "MXH60GLO"
E_TIMEOUT = 20

E_RFI_NUM = 2
E_BLOCK_SIZE = 64        
E_WAIT = 10

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
                zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "Cross-connection creation failure " + QS_000_Print_Line_Function())
            else:
                dprint("\nKO\tTL1 Cross-connection command DENY\n",2)
                zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "TL1 Cross-connection command DENY " + QS_000_Print_Line_Function())
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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "Cross-connection deletion failed {} {}".format(zq_xc_list[zq_i],QS_000_Print_Line_Function()))
    
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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "Cross-connection creation failed from {}-{} to {}-{} {}".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j,QS_000_Print_Line_Function()))

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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", 
                                    "HO Trace Identifier change failure for STM64AU4-{}-{} {}".format(zq_slot,zq_i,QS_000_Print_Line_Function()))

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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", 
            "HO Trace Identifier change failure for MVC4-{}-{} {}".format(zq_slot,zq_i,QS_000_Print_Line_Function()))
        zq_i += 1
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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", 
                                    "Cross-connection deletion failed from {}-{} to {}-{} {}".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j,QS_000_Print_Line_Function()))

    return


def QS_070_Check_No_Alarm(zq_run, zq_ONT_p1, zq_ONT_p2, zq_vc4_ch1, zq_vc4_ch2):

    
    ONT.get_set_rx_lo_measure_channel(zq_ONT_p1, zq_vc4_ch1)
    ONT.get_set_rx_lo_measure_channel(zq_ONT_p2, zq_vc4_ch2)

    ONT.get_set_tx_lo_measure_channel(zq_ONT_p1, zq_vc4_ch1)
    ONT.get_set_tx_lo_measure_channel(zq_ONT_p2, zq_vc4_ch2)
    
    time.sleep(1)

    zq_res = False
    zq_alm1=ONT.retrieve_ho_lo_alarms(zq_ONT_p1)
    zq_alm2=ONT.retrieve_ho_lo_alarms(zq_ONT_p2)

    if zq_alm1[0] and zq_alm2[0]:
        if  len(zq_alm1[1]) == 0 and \
            len(zq_alm2[1]) == 0:
            dprint("\nOK\tPath is alarm free.",2)
            zq_run.add_success(NE1, "CHECK PATH ALARMS","0.0", "Path is alarm free")
            zq_res = True
        else:
            dprint("\nKO\tAlarms found on path: {}".format(zq_alm1[1]),2)
            dprint("\n\tAlarms found on path: {}".format(zq_alm2[1]),2)
            zq_run.add_failure(NE1, "CHECK PATH ALARMS","0.0", "PATH ALARMS FOUND"
                                  , "Path alarms found: {}-{} {}".format(zq_alm1[1],zq_alm2[1],QS_000_Print_Line_Function()))


    return  zq_res



def QS_080_Get_PM_Counter(zq_run, zq_vc4_idx, zq_counter_type, zq_locn, zq_period, zq_dir="RCV"):

    zq_counter = -1
    zq_tl1_res=NE1.tl1.do("RTRV-PM-VC4::{}:::{},0-UP,{},{},{};".format(zq_vc4_idx, zq_counter_type, zq_locn,zq_dir,zq_period))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        if zq_msg.get_cmd_response_size() != 0:
            zq_counter=zq_msg.get_cmd_attr_value("{},VC4".format(zq_vc4_idx), "2")

    return int(zq_counter[0])


def QS_090_Set_PM_Mode(zq_run, zq_vc4_idx, zq_locn, zq_mode, zq_period, zq_dir="RCV"):
    #Enable PM ALL 15-MIN and 1-DAY
    zq_tl1_res=NE1.tl1.do("SET-PMMODE-VC4::{}:::{},ALL,{},{}:TMPER={};".format(zq_vc4_idx, zq_locn, zq_mode, zq_dir,zq_period))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        dprint("OK\tPM set to {} for {}: [{}]-[{}]-[{}]".format(zq_mode, zq_vc4_idx,zq_locn,zq_dir,zq_period),2)
        zq_run.add_success(NE1, "TL1 Command","0.0", "PM set to {} for {}: [{}]-[{}]-[{}]".format(zq_mode, zq_vc4_idx,zq_locn,zq_dir,zq_period))
    else:
        dprint("KO\tPM NOT set to {} for {}: [{}]-[{}]-[{}]".format(zq_mode, zq_vc4_idx,zq_locn,zq_dir,zq_period),2)
        zq_run.add_failure(NE1, "TL1 Command","0.0", "TL1 Command not successful", 
                                "PM set to {} for {}: [{}]-[{}]-[{}] {}".format(zq_mode, zq_vc4_idx,zq_locn,zq_dir,zq_period,QS_000_Print_Line_Function()))

    return
    
def QS_100_Check_BBE_ES_SES_UAS(zq_run, 
                                zq_ONT_p1, 
                                zq_ONT_p2, 
                                zq_mtx_slot, 
                                zq_vc4_idx1, 
                                zq_vc4_idx2, 
                                zq_locn,
                                zq_period,
                                zq_dir,
                                zq_alm_type="",
                                zq_num_err="3000",
                                zq_num_err_free="64000"):

    ##################################################
    #Verify all counters are 0 when path is alarm free
    ##################################################
    if zq_period == "BOTH" or zq_period == "15-MIN":  
        zq_bbe = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"BBE-HOVC", zq_locn, "15-MIN")
        zq_es  = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"ES-HOVC", zq_locn, "15-MIN")
        zq_ses = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"SES-HOVC", zq_locn, "15-MIN")
        zq_uas = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"UAS-HOVC", zq_locn, "15-MIN")
        if zq_bbe == 0 and zq_es == 0 and zq_ses == 0 and zq_uas == 0:
            dprint("OK\tAll PM counter [{}]-[15-MIN] for {} are 0.".format(zq_locn, zq_vc4_idx1),2)
            zq_run.add_success(NE1, "PM Counter Reading","0.0", "All PM counter [{}]-[15-MIN] for {} are 0.".format(zq_locn, zq_vc4_idx1))
        else:
            zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", 
                                    "Some PM counter [{}]-[15-MIN] for {} not 0. {}".format(zq_locn, zq_vc4_idx1,QS_000_Print_Line_Function()))
            dprint("KO\tSome PM counter [{}]-[15-MIN] for {} not 0.".format(zq_locn, zq_vc4_idx1),2)
            dprint("\tPM counter BBE: {}".format(zq_bbe),2)
            dprint("\tPM counter  ES: {}".format(zq_es),2)
            dprint("\tPM counter SES: {}".format(zq_ses),2)
            dprint("\tPM counter UAS: {}".format(zq_uas),2)
    
    if zq_period == "BOTH" or zq_period == "1-DAY":
        if zq_locn == "BIDIR":
            zq_bbe_ne = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"BBE-HOVC-NE", zq_locn, "1-DAY")
            zq_bbe_fe = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"BBE-HOVC-FE", zq_locn, "1-DAY")
            zq_es_ne  = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"ES-HOVC-NE", zq_locn, "1-DAY")
            zq_es_fe  = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"ES-HOVC-FE", zq_locn, "1-DAY")
            zq_ses_ne = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"SES-HOVC-NE", zq_locn, "1-DAY")
            zq_ses_fe = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"SES-HOVC-FE", zq_locn, "1-DAY")
            zq_uas_bi = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"UAS-HOVC-BI", zq_locn, "1-DAY")
            if  zq_bbe_ne == 0 and \
                zq_bbe_fe == 0 and \
                zq_es_ne == 0 and \
                zq_es_fe == 0 and \
                zq_ses_ne == 0 and \
                zq_ses_fe == 0 and \
                zq_uas_bi == 0:
                dprint("OK\tAll PM counter [{}]-[1-DAY] for {} are 0.".format(zq_locn, zq_vc4_idx1),2)
                zq_run.add_success(NE1, "PM Counter Reading","0.0", "All PM counter [{}]-[1-DAY] for {} are 0.".format(zq_locn, zq_vc4_idx1))
                dprint("\tPM counter BBE: {}".format(zq_bbe_fe),2)
                dprint("\tPM counter  ES: {}".format(zq_es_ne),2)
                dprint("\tPM counter  ES: {}".format(zq_es_fe),2)
                dprint("\tPM counter SES: {}".format(zq_ses_ne),2)
                dprint("\tPM counter SES: {}".format(zq_ses_fe),2)
                dprint("\tPM counter UAS: {}".format(zq_uas_bi),2)
        
        else:  
            zq_bbe = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"BBE-HOVC", zq_locn, "1-DAY")
            zq_es  = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"ES-HOVC", zq_locn, "1-DAY")
            zq_ses = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"SES-HOVC", zq_locn, "1-DAY")
            zq_uas = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"UAS-HOVC", zq_locn, "1-DAY")
            if zq_bbe == 0 and zq_es == 0 and zq_ses == 0 and zq_uas == 0:
                dprint("OK\tAll PM counter [{}]-[1-DAY] for {} are 0.".format(zq_locn, zq_vc4_idx1),2)
                zq_run.add_success(NE1, "PM Counter Reading","0.0", "All PM counter [{}]-[1-DAY] for {} are 0.".format(zq_locn, zq_vc4_idx1))
            else:
                zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", 
                                        "Some PM counter [{}]-[1-DAY] for {} not 0. {}".format(zq_locn, zq_vc4_idx1,QS_000_Print_Line_Function()))
                dprint("KO\tSome PM counter [{}]-[1-DAY] for {} not 0.".format(zq_locn, zq_vc4_idx1),2)
                dprint("\tPM counter BBE: {}".format(zq_bbe),2)
                dprint("\tPM counter  ES: {}".format(zq_es),2)
                dprint("\tPM counter SES: {}".format(zq_ses),2)
                dprint("\tPM counter UAS: {}".format(zq_uas),2)
        
    
    ###################################################################
    # Insert B3 error continuous burst 
    ###################################################################
    ONT.get_set_error_insertion_mode(zq_ONT_p1, "HO", "BURST_CONT")
    ONT.get_set_num_errored_burst_frames(zq_ONT_p1, "HO", zq_num_err)
    ONT.get_set_num_not_errored_burst_frames(zq_ONT_p1, "HO", zq_num_err_free)
    ONT.get_set_error_insertion_type(zq_ONT_p1, zq_alm_type)
    ONT.get_set_error_activation(zq_ONT_p1, "HO", "ON")
    time.sleep(E_TIMEOUT)
    #time.sleep(E_TIMEOUT)
    if zq_locn == "BIDIR":
        ONT.get_set_error_insertion_type(zq_ONT_p1, "HPREI")
        time.sleep(E_TIMEOUT)
        #time.sleep(E_TIMEOUT)

    ONT.get_set_error_activation(zq_ONT_p1, "HO", "OFF")
    #time.sleep(E_TIMEOUT)
    
    ###################################################################
    #Verify BBE-ES-SES counters are incremented 
    ###################################################################
    if zq_period == "BOTH" or zq_period == "15-MIN":  
        zq_bbe = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"BBE-HOVC", zq_locn, "15-MIN")
        zq_es  = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"ES-HOVC", zq_locn, "15-MIN")
        zq_ses = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"SES-HOVC", zq_locn, "15-MIN")
        if zq_bbe != 0 and zq_es != 0 and zq_ses != 0:
            dprint("OK\tPM counter [{}]-[15-MIN] for {} were incremented.".format(zq_locn, zq_vc4_idx1),2)
            zq_run.add_success(NE1, "PM Counter Reading","0.0", "PM counter [{}]-[15-MIN] for {} were incremented.".format(zq_locn, zq_vc4_idx1))
        else:
            dprint("KO\tPM counter [{}]-[15-MIN] for {} are still 0.".format(zq_locn, zq_vc4_idx1),2)
            zq_run.add_failure(NE1, "PM Counter Reading", "0.0", 
                                    "PM Counter Reading", "PM counter [{}]-[15-MIN] for {} are still 0. {}".format(zq_locn, zq_vc4_idx1,QS_000_Print_Line_Function()))

        dprint("\tPM counter BBE: {}".format(zq_bbe),2)
        dprint("\tPM counter  ES: {}".format(zq_es),2)
        dprint("\tPM counter SES: {}".format(zq_ses),2)

    if zq_period == "BOTH" or zq_period == "1-DAY":  
        if zq_locn == "BIDIR":
            zq_bbe_ne = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"BBE-HOVC-NE", zq_locn, "1-DAY")
            zq_bbe_fe = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"BBE-HOVC-FE", zq_locn, "1-DAY")
            zq_es_ne  = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"ES-HOVC-NE", zq_locn, "1-DAY")
            zq_es_fe  = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"ES-HOVC-FE", zq_locn, "1-DAY")
            zq_ses_ne = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"SES-HOVC-NE", zq_locn, "1-DAY")
            zq_ses_fe = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"SES-HOVC-FE", zq_locn, "1-DAY")
            if  zq_bbe_ne != 0 and \
                zq_bbe_fe != 0 and \
                zq_es_ne != 0 and \
                zq_es_fe != 0 and \
                zq_ses_ne != 0 and \
                zq_ses_fe != 0: 
                dprint("OK\tPM counter [{}]-[1-DAY] for {} were incremented.".format(zq_locn, zq_vc4_idx1),2)
                zq_run.add_success(NE1, "PM Counter Reading","0.0", "PM counter [{}]-[1-DAY] for {} were incremented.".format(zq_locn, zq_vc4_idx1))
            else:
                dprint("KO\tSome PM counter [{}]-[1-DAY] for {} are still 0.".format(zq_locn, zq_vc4_idx1),2)
                zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", 
                                        "Some PM counter [{}]-[1-DAY] for {} are still 0. {}".format(zq_locn, zq_vc4_idx1,QS_000_Print_Line_Function()))

            dprint("\tPM counter BBE-NE: {}".format(zq_bbe_ne),2)
            dprint("\tPM counter BBE-FE: {}".format(zq_bbe_fe),2)
            dprint("\tPM counter  ES-NE: {}".format(zq_es_ne),2)
            dprint("\tPM counter  ES-FE: {}".format(zq_es_fe),2)
            dprint("\tPM counter SES-NE: {}".format(zq_ses_ne),2)
            dprint("\tPM counter SES-FE: {}".format(zq_ses_fe),2)
        
        else:  
            zq_bbe = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"BBE-HOVC", zq_locn, "1-DAY")
            zq_es  = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"ES-HOVC", zq_locn, "1-DAY")
            zq_ses = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"SES-HOVC", zq_locn, "1-DAY")
            if zq_bbe != 0 and zq_es != 0 and zq_ses != 0:
                dprint("OK\tPM counter [{}]-[1-DAY] for {} were incremented.".format(zq_locn, zq_vc4_idx1),2)
                zq_run.add_success(NE1, "PM Counter Reading","0.0", "PM counter [{}]-[1-DAY] for {} were incremented.".format(zq_locn, zq_vc4_idx1))
            else:
                dprint("KO\tPM counter [{}]-[1-DAY] for {} are still 0.".format(zq_locn, zq_vc4_idx1),2)
                zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", 
                                        "PM counter [{}]-[1-DAY] for {} are still 0. {}".format(zq_locn, zq_vc4_idx1,QS_000_Print_Line_Function()))

            dprint("\tPM counter BBE: {}".format(zq_bbe),2)
            dprint("\tPM counter  ES: {}".format(zq_es),2)
            dprint("\tPM counter SES: {}".format(zq_ses),2)

    
    ###################################################################
    # Insert B3 error continuous burst 
    ###################################################################
    # Exchange error frame number with error free number to detect UAS         
    ###################################################################
    ONT.get_set_num_errored_burst_frames(zq_ONT_p1, "HO", zq_num_err_free)
    ONT.get_set_num_not_errored_burst_frames(zq_ONT_p1, "HO", zq_num_err)
    ONT.get_set_error_insertion_type(zq_ONT_p1, zq_alm_type)
    ONT.get_set_error_activation(zq_ONT_p1, "HO", "ON")
    time.sleep(E_TIMEOUT)
    #time.sleep(E_TIMEOUT)
    if zq_locn == "BIDIR":
        ONT.get_set_error_insertion_type(zq_ONT_p1, "HPREI")
        time.sleep(E_TIMEOUT)
        #time.sleep(E_TIMEOUT)

    ONT.get_set_error_activation(zq_ONT_p1, "HO", "OFF")
    time.sleep(E_TIMEOUT)
    
    ###################################################################
    #Verify UAS counter is incremented 
    ###################################################################
    if zq_period == "BOTH" or zq_period == "15-MIN":  
        zq_uas = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"UAS-HOVC", zq_locn, "15-MIN")
        
        if zq_uas != 0:
            dprint("OK\tPM counter [{}]-[15-MIN] for {} were incremented.".format(zq_locn, zq_vc4_idx1),2)
            dprint("\tPM counter UAS: {}".format(zq_uas),2)
            zq_run.add_success(NE1, "PM Counter Reading","0.0", "PM counter [{}]-[15-MIN] for {} were incremented.".format(zq_locn, zq_vc4_idx1))
        else:
            zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", 
                                    "PM counter [{}]-[15-MIN] for {} are still 0. {}".format(zq_locn, zq_vc4_idx1,QS_000_Print_Line_Function()))
            dprint("KO\tPM counter [{}]-[15-MIN] for {} are still 0.".format(zq_locn, zq_vc4_idx1),2)
            dprint("\tPM counter UAS: {}".format(zq_uas),2)
        
    if zq_period == "BOTH" or zq_period == "1-DAY":
        if zq_locn == "BIDIR":  
            zq_uas_bi = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"UAS-HOVC-BI", zq_locn, "1-DAY")
            if zq_uas_bi != 0:
                dprint("OK\tPM counter [{}]-[1-DAY] for {} were incremented.".format(zq_locn, zq_vc4_idx1),2)
                dprint("\tPM counter UAS-BI: {}".format(zq_uas_bi),2)
                zq_run.add_success(NE1, "PM Counter Reading","0.0", "PM counter [{}]-[1-DAY] for {} were incremented.".format(zq_locn, zq_vc4_idx1))
            else:
                zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", 
                                        "PM counter [{}]-[1-DAY] for {} are still 0. {}".format(zq_locn, zq_vc4_idx1,QS_000_Print_Line_Function()))
                dprint("KO\tPM counter [{}]-[1-DAY] for {} are still 0.".format(zq_locn, zq_vc4_idx1),2)
                dprint("\tPM counter UAS-BI: {}".format(zq_uas_bi),2)
            
        else:
            zq_uas = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"UAS-HOVC", zq_locn, "1-DAY")
            
            if zq_uas != 0:
                dprint("OK\tPM counter [{}]-[1-DAY] for {} were incremented.".format(zq_locn, zq_vc4_idx1),2)
                dprint("\tPM counter UAS: {}".format(zq_uas),2)
                zq_run.add_success(NE1, "PM Counter Reading","0.0", "PM counter [{}]-[1-DAY] for {} were incremented.".format(zq_locn, zq_vc4_idx1))
            else:
                zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", 
                                        "PM counter [{}]-[1-DAY] for {} are still 0. {}".format(zq_locn, zq_vc4_idx1,QS_000_Print_Line_Function()))
                dprint("KO\tPM counter [{}]-[1-DAY] for {} are still 0.".format(zq_locn, zq_vc4_idx1),2)
                dprint("\tPM counter UAS: {}".format(zq_uas),2)
        
    return

def QS_120_Verify_PM_Counter_Zero(zq_run, zq_vc4_idx):

    zq_counter = 0
    zq_tl1_res=NE1.tl1.do("RTRV-PM-VC4::{}:::ALL,0-UP,ALL,ALL,BOTH,,,1,1;".format(zq_vc4_idx))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        if zq_msg.get_cmd_response_size() != 0:
            zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
            for zq_i in range(1,len(zq_temp_ary)-2):
                if zq_temp_ary[zq_i].find("{},VC4:".format(zq_vc4_idx)) > 0:
                    zq_counter_ary = zq_temp_ary[zq_i].split(",")
                    zq_aid = zq_counter_ary[0].replace("\"","")
                    zq_cnt = zq_counter_ary[1]
                    zq_cnt_val = int(zq_counter_ary[2])
                    zq_counter = zq_counter + zq_cnt_val
                    if zq_cnt_val != 0:
                        zq_counter = zq_counter + 1
                    dprint("\tPM Counter [{}] for [{}] is {}".format(zq_cnt, zq_aid, zq_cnt_val),2)
                    
    return int(zq_counter)


def QS_200_Verify_Validity_Flag(zq_run, zq_vc4_idx, zq_locn, zq_period, zq_val_flag_exp, zq_cnt_entry, zq_dir="RCV", zq_counter_type=""):

    zq_str = ""
    zq_res = False
    if zq_val_flag_exp == 'COMPL':
        zq_tl1_res=NE1.tl1.do("RTRV-PM-VC4::{}:::{},0-UP,{},{},{};".format(zq_vc4_idx, zq_counter_type, zq_locn, zq_dir, zq_period))
    else:
        if zq_period == '15-MIN':
            #RTRV-PM-VC4::MVC4-1-1-7-34:::,1-UP,ALL,RCV,15-MIN,,,ALL;
            zq_tl1_res=NE1.tl1.do("RTRV-PM-VC4::{}:::{},1-UP,{},{},{},,,ALL;".format(zq_vc4_idx, zq_counter_type, zq_locn, zq_dir, zq_period))
        else:
            #RTRV-PM-VC4::MVC4-1-1-7-34:::,1-UP,ALL,RCV,1-DAY,,,,ALL;
            zq_tl1_res=NE1.tl1.do("RTRV-PM-VC4::{}:::{},1-UP,{},{},{},,,,ALL;".format(zq_vc4_idx, zq_counter_type, zq_locn, zq_dir, zq_period))

    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        if zq_msg.get_cmd_response_size() != 0:
            zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
            for zq_i in range(1,len(zq_temp_ary)):
                if zq_temp_ary[zq_i].find("{},VC4".format(zq_vc4_idx)) > 0:
                    zq_cnt_ary = zq_temp_ary[zq_i].split(",")
                    zq_cnt_ary[2] = ""
                    zq_cnt_ary[7] = "" 
                    zq_cnt_ary[8] = ""
                    zq_cnt_ary[9] = ""
                    zq_val_flag = zq_cnt_ary[3] 
                    zq_sep = ","
                    zq_cnt_res = zq_sep.join(zq_cnt_ary)
                    zq_cnt_res = zq_cnt_res.replace("\"","")
                    zq_cnt_res = zq_cnt_res.replace(" ","")
                    if (zq_cnt_res == zq_cnt_entry): 
                        if (zq_val_flag == zq_val_flag_exp):
                            zq_res = True
                            dprint("OK\tValidity Flag [{}]".format(zq_cnt_entry),2)
                            zq_run.add_success(NE1, "PM Counter Validity Flag Check","0.0", "PM Counter Validity Flag Check successful [{}]".format(zq_cnt_entry))
                            break
                        else:
                            zq_res = False
                            dprint("KO\tValidity Flag [{}]".format(zq_cnt_entry),2)
                            zq_run.add_failure(NE1, "PM Counter Validity Flag Check", "0.0", "PM Counter Validity Flag Check", 
                                                    "PM Counter Validity Flag Check Fail [{}] {}".format(zq_cnt_entry,QS_000_Print_Line_Function()))
            
            if not zq_res:
                zq_str = zq_str + zq_cnt_entry        
                    
    return (zq_res,zq_str)
        

def QS_900_Set_Date(zq_run,zq_date,zq_time):

    zq_tl1_res=NE1.tl1.do("ED-DAT:::::{},{};".format(zq_date,zq_time))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        dprint("OK\tNE date & time changed to {} & {}".format(zq_date,zq_time),2)
        zq_run.add_success(NE1, "NE date & time changed to {} & {}".format(zq_date,zq_time),"0.0", "NE date & time changed to {} & {}".format(zq_date,zq_time))
    else:
        dprint("KO\tNE date & time change failure",2)
        zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "NE date & time change failure " + QS_000_Print_Line_Function())

    return

def QS_910_Wait_Quarter():
    
    zq_tl1_res=NE1.tl1.do("RTRV-HDR;")
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        zq_date_time=zq_msg.get_time_stamp()
        zq_time = zq_date_time[1]
        zq_min =  zq_date_time[1].split(":")
        #1 minuto e 1/2 in piu' rispetto allo scadere del quarto d'ora
        zq_wait = (15-(int(zq_min[1])%15)+1)*60 + 30  

    return(zq_wait)


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
        VERIFY BBE-ES-SES-UAS COUNTER FOR MVC4 FACILITIES
        '''
        print("\n*******************************************************************")
        print("\n   CONFIGURATION OF MVC4 AND LOVC3 CROSS-CONNECTION                ")
        print("\n*******************************************************************")
        
        self.start_tps_block(NE1.id,"PM","5-5-17-1")
        self.start_tps_block(NE1.id,"PM","5-5-17-2")
        self.start_tps_block(NE1.id,"PM","5-5-15-1")
        self.start_tps_block(NE1.id,"PM","5-5-15-2")

        E_LO_MTX = "MXH60GLO"
        E_HO_TI = 'X4F4E5420484F2D5452414345202020' #'ONT HO-TRACE   '
        E_SLOT = ['2','3','4','5','6','7','8','12','13','14','15','16','17','18','19']

        E_VC4_1_1 = 34      # <64
        E_VC4_1_2 = 92      # 65<x<129
        E_VC4_2_1 = 189     # 128<x<193
        E_VC4_2_2 = 227     # 192<x<257
        E_VC4_3_1 = 289     # 256<x<321
        E_VC4_3_2 = 356     # 320<x<385

        E_COND_AID_BK1 = "MVC4-{}-{}&&-{}".format(NE1_M1,str(E_BLOCK_SIZE*0+1),str(E_BLOCK_SIZE*2))
        E_COND_AID_BK2 = "MVC4-{}-{}&&-{}".format(NE1_M1,str(E_BLOCK_SIZE*2+1),str(E_BLOCK_SIZE*4))
        E_COND_AID_BK3 = "MVC4-{}-{}&&-{}".format(NE1_M1,str(E_BLOCK_SIZE*4+1),str(E_BLOCK_SIZE*6))
        
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
            zq_attr_list1=zq_msg.get_cmd_attr_values("{}-{}".format(E_LO_MTX, zq_mtxlo_slot))
            zq_attr_list2=zq_msg.get_cmd_attr_values("{}-{}".format("MDL", zq_mtxlo_slot))

            zq_attr_list1=zq_attr_list1[0]
            zq_attr_list2=zq_attr_list2[0]

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
                        print('*****************************************')
                        print('Board Equipped: {}'.format(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO')))
                        print('*****************************************')
                        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-1::::PROVISIONEDTYPE=XI-641;".format(''.join(zq_aid_list[zq_i]).replace('MDL','XFP')))
                        zq_board_to_remove.append(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO'))
                        print('*****************************************')
                        print('\tXFP equipped: {}-1'.format(''.join(zq_aid_list[zq_i]).replace('MDL','XFP')))
                        print('*****************************************')
                        zq_num += 1
                zq_i += 1

            
        NE1_stm64p3 = (''.join(zq_board_to_remove[0]).replace('10GSO-',''))+'-1'
        NE1_stm64p4 = (''.join(zq_board_to_remove[1]).replace('10GSO-',''))+'-1'
        NE1_stm64p5 = (''.join(zq_board_to_remove[2]).replace('10GSO-',''))+'-1'
        NE1_stm64p6 = (''.join(zq_board_to_remove[3]).replace('10GSO-',''))+'-1'
        
        print("\n******************************************************************************")
        print("\n   CHECK 2xMVC4 in FIRST BLOCK                                                ")
        print("\n******************************************************************************")

        #Delete ALL PM data for 15min/24hour
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/15m/*")
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/24h/*")
        
        '''
        CHECK FIRST 128 BLOCK of MVC4 
        '''
        QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_040_Modify_AU4_HO_Trace_Block(self, NE1_stm64p1, (E_VC4_1_1 % E_BLOCK_SIZE), 1, E_HO_TI)
        QS_040_Modify_AU4_HO_Trace_Block(self, NE1_stm64p2, (E_VC4_1_2 % E_BLOCK_SIZE), 1, E_HO_TI)
        
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_1_1, 1, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_1_2, 1, E_HO_TI)
        
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
        
        QS_900_Set_Date(self,"16-05-01", "01-00-00")

        print("\n******************************************************************************")
        print("\n       VERIFY VALIDITY FLAG LONG - 2xMVC4 in first block                       ")
        print("\n******************************************************************************")

        zq_vc4_ch1="{}.1.1.1".format(str(E_VC4_1_1 % E_BLOCK_SIZE))
        zq_vc4_ch2="{}.1.1.1".format(str(E_VC4_1_2 % E_BLOCK_SIZE))
         
        zq_vc4_idx1 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_1_1))
        zq_vc4_idx2 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_1_2)) 
    
        if QS_070_Check_No_Alarm(self, ONT_P1, ONT_P2, zq_vc4_ch1, zq_vc4_ch2):

            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "ON", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "ON", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "BIDIR", "ON", "1-DAY")
            

            if QS_120_Verify_PM_Counter_Zero(self, zq_vc4_idx1) == 0:
                dprint("OK\tAll PM counters are = 0",2)
                self.add_success(NE1, "PM counter reading","0.0", "All PM counters are = 0")
            else:
                dprint("KO\tSome PM counters are NOT = 0",2)
                self.add_failure(NE1, "PM counter reading","0.0", "PM counter reading", "Some PM counters are NOT = 0 " + QS_000_Print_Line_Function())

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","BOTH","RCV","HPBIP")
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","BOTH","RCV","HPREI")
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "BIDIR","1-DAY","RCV","HPBIP")
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "BIDIR","1-DAY","RCV","HPREI")

            #VERIFY FLAG IS COMPL
            zq_res = True
            zq_str = ""
            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]


            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]



            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC-NE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC-FE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC-NE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC-FE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC-NE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC-FE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC-BI,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]


            #WAIT QUARTER
            zq_wait = QS_910_Wait_Quarter()
            dprint("\tWaiting {} sec. for quarter.".format(zq_wait),2)
            time.sleep(zq_wait)


            #VERIFY FLAG IS PRTL FOR 15-MIN
            zq_res = True
            zq_str = ""
            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]


            #VERIFY FLAG IS PRTL FOR 24-HOUR
            QS_900_Set_Date(self,"16-05-01", "23-59-30")
            #WAIT 2 MINUTE TO BE SURE HISTORY ARE COLLECTED!
            time.sleep(120)

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]



            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC-NE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC-FE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC-NE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC-FE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC-NE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC-FE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:UAS-HOVC-BI,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]
            
            
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "DISABLED", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "DISABLED", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "BIDIR", "DISABLED", "1-DAY")

 
        QS_060_Delete_LO_XC_Block(self, E_VC4_1_1, E_VC4_1_2, zq_xc_list)
        
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        print("\n******************************************************************************")
        print("\n       VERIFY VALIDITY FLAG PRTL - 2xMVC4 in second block                      ")
        print("\n******************************************************************************")

        #Delete ALL PM data for 15min/24hour
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/15m/*")
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/24h/*")

        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")

        QS_010_Create_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p4, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_010_Create_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_2_1, 1, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, zq_mtxlo_slot, E_VC4_2_2, 1, E_HO_TI)
        
        QS_030_Create_LO_XC_Block(self, E_VC4_2_1, E_VC4_2_2, zq_xc_list)
        
        time.sleep(E_WAIT)

        QS_900_Set_Date(self,"16-05-01", "02-00-00")
        
        print("\n******************************************************************************")
        print("\n       VERIFY BBE-ES-SES-UAS COUNTER NEAR END 15-MIN/1-DAY                    ")
        print("\n******************************************************************************")

        zq_vc4_ch1="{}.1.1.1".format(str(E_VC4_2_1 % E_BLOCK_SIZE))
        zq_vc4_ch2="{}.1.1.1".format(str(E_VC4_2_2 % E_BLOCK_SIZE))
         
        zq_vc4_idx1 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_2_1))
        zq_vc4_idx2 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_2_2)) 
    
        if QS_070_Check_No_Alarm(self, ONT_P1, ONT_P2, zq_vc4_ch1, zq_vc4_ch2):

            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "ON", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "ON", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "BIDIR", "ON", "1-DAY")
            

            if QS_120_Verify_PM_Counter_Zero(self, zq_vc4_idx1) == 0:
                dprint("OK\tAll PM counters are = 0",2)
                self.add_success(NE1, "PM counter reading","0.0", "All PM counters are = 0")
            else:
                dprint("KO\tSome PM counters are NOT = 0",2)
                self.add_failure(NE1, "PM counter reading","0.0", "PM counter reading", "Some PM counters are NOT = 0 " + QS_000_Print_Line_Function())

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","BOTH","RCV","HPBIP")
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","BOTH","RCV","HPREI")
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "BIDIR","1-DAY","RCV","HPBIP")
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "BIDIR","1-DAY","RCV","HPREI")

            #VERIFY FLAG IS COMPL
            zq_res = True
            zq_str = ""
            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]


            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]



            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC-NE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC-FE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC-NE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC-FE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC-NE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC-FE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC-BI,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]


            #WAIT QUARTER
            zq_wait = QS_910_Wait_Quarter()
            dprint("\tWaiting {} sec. for quarter.".format(zq_wait),2)
            time.sleep(zq_wait)


            #VERIFY FLAG IS PRTL FOR 15-MIN
            zq_res = True
            zq_str = ""
            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]


            #VERIFY FLAG IS PRTL FOR 24-HOUR
            QS_900_Set_Date(self,"16-05-01", "23-59-30")
            #WAIT 2 MINUTE TO BE SURE HISTORY ARE COLLECTED!
            time.sleep(120)

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]



            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC-NE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC-FE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC-NE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC-FE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC-NE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC-FE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:UAS-HOVC-BI,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]
            
            
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "DISABLED", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "DISABLED", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "BIDIR", "DISABLED", "1-DAY")


        QS_060_Delete_LO_XC_Block(self, E_VC4_2_1, E_VC4_2_2, zq_xc_list)
        
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p4, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)

        
        print("\n******************************************************************************")
        print("\n       VERIFY VALIDITY FLAG PRTL - 2xMVC4 in third block                      ")
        print("\n******************************************************************************")

        #Delete ALL PM data for 15min/24hour
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/15m/*")
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/24h/*")

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
        
        QS_030_Create_LO_XC_Block(self, E_VC4_3_1, E_VC4_3_2, zq_xc_list)
        
        time.sleep(E_WAIT)

        QS_900_Set_Date(self,"16-05-01", "03-00-00")
        
        zq_vc4_ch1="{}.1.1.1".format(str(E_VC4_3_1 % E_BLOCK_SIZE))
        zq_vc4_ch2="{}.1.1.1".format(str(E_VC4_3_2 % E_BLOCK_SIZE))
         
        zq_vc4_idx1 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_3_1))
        zq_vc4_idx2 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_3_2)) 
    
        if QS_070_Check_No_Alarm(self, ONT_P1, ONT_P2, zq_vc4_ch1, zq_vc4_ch2):

            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "ON", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "ON", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "BIDIR", "ON", "1-DAY")
            

            if QS_120_Verify_PM_Counter_Zero(self, zq_vc4_idx1) == 0:
                dprint("OK\tAll PM counters are = 0",2)
                self.add_success(NE1, "PM counter reading","0.0", "All PM counters are = 0")
            else:
                dprint("KO\tSome PM counters are NOT = 0",2)
                self.add_failure(NE1, "PM counter reading","0.0", "PM counter reading", "Some PM counters are NOT = 0 " + QS_000_Print_Line_Function())

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","BOTH","RCV","HPBIP")
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","BOTH","RCV","HPREI")
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "BIDIR","1-DAY","RCV","HPBIP")
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "BIDIR","1-DAY","RCV","HPREI")

            #VERIFY FLAG IS COMPL
            zq_res = True
            zq_str = ""
            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]


            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC,,COMPL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]



            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC-NE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:BBE-HOVC-FE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC-NE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:ES-HOVC-FE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC-NE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:SES-HOVC-FE,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "BOTH", "COMPL", 
                                                  "{},VC4:UAS-HOVC-BI,,COMPL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]


            #WAIT QUARTER
            zq_wait = QS_910_Wait_Quarter()
            dprint("\tWaiting {} sec. for quarter.".format(zq_wait),2)
            time.sleep(zq_wait)


            #VERIFY FLAG IS PRTL FOR 15-MIN
            zq_res = True
            zq_str = ""
            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,NEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "15-MIN", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,FEND,RCV,15-MIN,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]


            #VERIFY FLAG IS PRTL FOR 24-HOUR
            QS_900_Set_Date(self,"16-05-01", "23-59-30")
            #WAIT 2 MINUTE TO BE SURE HISTORY ARE COLLECTED!
            time.sleep(120)

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,NEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:UAS-HOVC,,PRTL,FEND,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]



            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC-NE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:BBE-HOVC-FE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC-NE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:ES-HOVC-FE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC-NE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:SES-HOVC-FE,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]

            zq_temp = QS_200_Verify_Validity_Flag(self, zq_vc4_idx1, "ALL", "1-DAY", "PRTL", 
                                                  "{},VC4:UAS-HOVC-BI,,PRTL,BIDIR,RCV,1-DAY,,,".format(zq_vc4_idx1))
            zq_res = zq_res and zq_temp[0]
            zq_str = zq_str + zq_temp[1]
            
            
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "DISABLED", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "DISABLED", "BOTH")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "BIDIR", "DISABLED", "1-DAY")


        QS_060_Delete_LO_XC_Block(self, E_VC4_3_1, E_VC4_3_2, zq_xc_list)
        
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
            print('*****************************************')
            print('Board Deleted: {}'.format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','MDL')))
            print('*****************************************')


        self.stop_tps_block(NE1.id,"PM","5-5-17-1")
        self.stop_tps_block(NE1.id,"PM","5-5-17-2")
        self.stop_tps_block(NE1.id,"PM","5-5-15-1")
        self.stop_tps_block(NE1.id,"PM","5-5-15-2")


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
    