#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: This test provides a method to verify the arise of TCA alarms  
:field Description: when the MVC4 PM counters for MVC4 cross the threshold of a previously
:field Description: created TCA profile. It is also verified the clearing of the alarm
:field Description: when a NULL TCA profile is associated to the MVC4. At least the arise of
:field Description: alarm when previous profile is applied again.
:field Topology: 5
:field Dependency: NA
:field Lab: SVT
:field TPS: PM__5-5-25-1
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
from ipaddress import ip_address
from inspect import currentframe

'''
    MonitorType    Location    Direction    Threshold Level Clear    15-Minute Threshold    1-Day Threshold
    ES-HOVC         NEND        TRMT            20                      180                      1500
                                RCV             20                      180                      1500
                    FEND        TRMT            20                      180                      1500
                                RCV             20                      180                      1500
    SES-HOVC        NEND        TRMT             0                       15                        20
                                RCV              0                       15                        20
                    FEND        TRMT             0                       15                        20
                                RCV              0                       15                        20
    BBE-HOVC        NEND        TRMT           200                    36000                     48000
                                RCV            200                    36000                     48000
                    FEND        TRMT           200                    36000                     48000
                                RCV            200                    36000                     48000
'''


E_MAX_MVC4 = 384
E_LO_MTX = "MXH60GLO"
E_TIMEOUT = 20

E_RFI_NUM = 2
E_BLOCK_SIZE = 64        
E_WAIT = 10

# TCA THREHOLD VALUES FOR ALARM ARISE
E_BBE_HOVC_15_ON = 6000 
E_ES_HOVC_15_ON  = 25
E_SES_HOVC_15_ON = 2

E_BBE_HOVC_24_ON = 6000 
E_ES_HOVC_24_ON  = 25
E_SES_HOVC_24_ON = 2

# TCA THREHOLD VALUES FOR ALARM CLEAR
E_BBE_HOVC_15_OFF = 200 
E_ES_HOVC_15_OFF  = 20 
E_SES_HOVC_15_OFF = 0 

E_BBE_HOVC_24_OFF = 200 
E_ES_HOVC_24_OFF  = 20 
E_SES_HOVC_24_OFF = 0 



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
                zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "Cross-connection creation failure")
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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "Cross-connection deletion failure")
    
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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "Cross-connection creation failure")

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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "HO Trace Identifier change failure for STM64AU4-{}-{}".format(zq_slot,zq_i))

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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "HO Trace Identifier change failure for MVC4-{}-{}".format(zq_slot,zq_i))
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
            zq_run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL", "Cross-connection deletion failed from {}-{} to {}-{}".format(zq_tu3_idx1,zq_j,zq_tu3_idx2,zq_j))

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
                                  , "Path alarms found: {}-{}".format(zq_alm1[1],zq_alm2[1]))


    return  zq_res



def QS_080_Get_PM_Counter(zq_run, zq_vc4_idx, zq_counter_type, zq_locn, zq_period, zq_dir="RCV"):

    zq_counter = -1
    zq_tl1_res=NE1.tl1.do("RTRV-PM-VC4::{}:::{},0-UP,{},{},{};".format(zq_vc4_idx, zq_counter_type, zq_locn,zq_dir,zq_period))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        if zq_msg.get_cmd_response_size() != 0:
            zq_counter=zq_msg.get_cmd_attr_value("{},VC4".format(zq_vc4_idx), "2")

    return int(zq_counter)


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
        zq_run.add_failure(NE1, "TL1 Command","0.0", "TL1 Command not successful", "PM set to {} for {}: [{}]-[{}]-[{}]".format(zq_mode, zq_vc4_idx,zq_locn,zq_dir,zq_period))

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
            zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", "Some PM counter [{}]-[15-MIN] for {} not 0.".format(zq_locn, zq_vc4_idx1))
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
                zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", "Some PM counter [{}]-[1-DAY] for {} not 0.".format(zq_locn, zq_vc4_idx1))
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
    time.sleep(20)
    zq_tca_bbe = False
    zq_tca_es  = False
    zq_tca_ses = False
    for zq_i in range(1,80):
        time.sleep(20)
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
                zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", "PM counter [{}]-[15-MIN] for {} are still 0.".format(zq_locn, zq_vc4_idx1))
    
            dprint("\tPM counter BBE: {}".format(zq_bbe),2)
            dprint("\tPM counter  ES: {}".format(zq_es),2)
            dprint("\tPM counter SES: {}".format(zq_ses),2)
            
            if (int(zq_bbe) >= E_BBE_HOVC_15_ON) and (not zq_tca_bbe):
                zq_tca_bbe = True
                dprint("BBE threshold 15-MIN reached...check TCA Alarm presence",2)
                QS_150_Check_TCA(zq_run,zq_vc4_idx1,"WR","T-BBE-HOVC-15-MIN","NSA",zq_locn,zq_dir)

            if (int(zq_es) >= E_ES_HOVC_15_ON) and (not zq_tca_es):
                zq_tca_es = True
                dprint("ES  threshold 15-MIN reached...check TCA Alarm presence",2)
                QS_150_Check_TCA(zq_run,zq_vc4_idx1,"WR","T-ES-HOVC-15-MIN","NSA",zq_locn,zq_dir)
                
            if (int(zq_ses) >= E_SES_HOVC_15_ON) and (not zq_tca_ses):
                zq_tca_ses = True
                dprint("SES  threshold 15-MIN reached...check TCA Alarm presence",2)
                QS_150_Check_TCA(zq_run,zq_vc4_idx1,"WR","T-SES-HOVC-15-MIN","NSA",zq_locn,zq_dir)
                
    
        if zq_period == "BOTH" or zq_period == "1-DAY":  
            zq_bbe = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"BBE-HOVC", zq_locn, "1-DAY")
            zq_es  = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"ES-HOVC", zq_locn, "1-DAY")
            zq_ses = QS_080_Get_PM_Counter(zq_run, zq_vc4_idx1,"SES-HOVC", zq_locn, "1-DAY")
            if zq_bbe != 0 and zq_es != 0 and zq_ses != 0:
                dprint("OK\tPM counter [{}]-[1-DAY] for {} were incremented.".format(zq_locn, zq_vc4_idx1),2)
                zq_run.add_success(NE1, "PM Counter Reading","0.0", "PM counter [{}]-[1-DAY] for {} were incremented.".format(zq_locn, zq_vc4_idx1))
            else:
                dprint("KO\tPM counter [{}]-[1-DAY] for {} are still 0.".format(zq_locn, zq_vc4_idx1),2)
                zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", "PM counter [{}]-[1-DAY] for {} are still 0.".format(zq_locn, zq_vc4_idx1))
    
            dprint("\tPM counter BBE: {}".format(zq_bbe),2)
            dprint("\tPM counter  ES: {}".format(zq_es),2)
            dprint("\tPM counter SES: {}".format(zq_ses),2)

            if (int(zq_bbe) >= E_BBE_HOVC_24_ON) and (not zq_tca_bbe):
                zq_tca_bbe = True
                dprint("BBE threshold 1-DAY reached...check TCA Alarm presence",2)
                QS_150_Check_TCA(zq_run,zq_vc4_idx1,"WR","T-BBE-HOVC-1-DAY","NSA",zq_locn,zq_dir)

            if (int(zq_es) >= E_ES_HOVC_24_ON) and (not zq_tca_es):
                zq_tca_es = True
                dprint("ES  threshold 1-DAY reached...check TCA Alarm presence",2)
                QS_150_Check_TCA(zq_run,zq_vc4_idx1,"WR","T-ES-HOVC-1-DAY","NSA",zq_locn,zq_dir)
                
            if (int(zq_ses) >= E_SES_HOVC_24_ON) and (not zq_tca_ses):
                zq_tca_ses = True
                dprint("SES  threshold 1-DAY reached...check TCA Alarm presence",2)
                QS_150_Check_TCA(zq_run,zq_vc4_idx1,"WR","T-SES-HOVC-1-DAY","NSA",zq_locn,zq_dir)

        if zq_tca_bbe and zq_tca_es and zq_tca_ses:
            dprint("All TCA alarms set after {} min".format(zq_i*20//60),2)
            break  
        
            
    ONT.get_set_error_activation(zq_ONT_p1, "HO", "OFF")
    

    return

def QS_150_Check_TCA(zq_run,
                     zq_vc4_idx,
                     zq_cond_code,
                     zq_cond_type,
                     zq_sev,
                     zq_locn,
                     zq_dir):

    # RTRV-ALM-VC4:[TID]:AID:[CTAG]::[NTFCNCDE],[CONDTYPE],[SRVEFF],[LOCN],[DIRN]
    zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{}:::{},{},{},{},{};".format(zq_vc4_idx, zq_cond_code, zq_cond_type, zq_sev, zq_locn, zq_dir))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        if zq_msg.get_cmd_response_size() == 1:
            dprint("OK\tPM Check TCA successful for {}: [{}]-[{}]-[{}]-[{}]-[{}]".format(zq_vc4_idx, zq_cond_code, zq_cond_type, zq_sev, zq_locn, zq_dir),2)
            zq_run.add_success(NE1, "TL1 Command","0.0", "PM Check TCA successful for {}: [{}]-[{}]-[{}]-[{}-[{}]]".format(zq_vc4_idx, zq_cond_code, zq_cond_type, zq_sev, zq_locn, zq_dir))
        else:
            zq_run.add_failure(NE1, "TL1 Command", "0.0", "TL1 Command", "PM TCA Fail for {}: [{}]-[{}]-[{}]-[{}]-[{}]".format(zq_vc4_idx, zq_cond_code, zq_cond_type, zq_sev, zq_locn, zq_dir))
            dprint("KO\tPM Check TCA fail for {}: [{}]-[{}]-[{}]-[{}]-[{}]".format(zq_vc4_idx, zq_cond_code, zq_cond_type, zq_sev, zq_locn, zq_dir),2)
    else:
        zq_run.add_failure(NE1, "TL1 Command", "0.0", "TL1 Command", "PM TCA Retrieve Command Fail for {}: [{}]-[{}]-[{}]-[{}]-[{}]".format(zq_vc4_idx, zq_cond_code, zq_cond_type, zq_sev, zq_locn, zq_dir))
        dprint("KO\tPM TCA Retrieve Command Fail for {}: [{}]-[{}]-[{}]-[{}]-[{}]".format(zq_vc4_idx, zq_cond_code, zq_cond_type, zq_sev, zq_locn, zq_dir),2)

    return


def QS_160_Verify_TCA_Alarm(zq_run, zq_temp_ary, zq_vc4_idx, zq_alm_exp):

    zq_str = ""
    zq_res = False
    for zq_i in range(1,len(zq_temp_ary)):
        if zq_temp_ary[zq_i].find("{}".format(zq_vc4_idx)) > 0:
            #zq_temp_ary[zq_i] = zq_temp_ary[zq_i].replace("\"","")
            #zq_temp_ary[zq_i] = zq_temp_ary[zq_i].replace(" ","")
            zq_alm_ary = zq_temp_ary[zq_i].split(",")
            zq_alm_ary[4] = "" 
            zq_alm_ary[5] = ""
            zq_sep = ","
            zq_TCA_alm = zq_sep.join(zq_alm_ary)
            zq_TCA_alm = zq_TCA_alm.replace("\"","")
            zq_TCA_alm = zq_TCA_alm.replace(" ","")
            if zq_TCA_alm == zq_alm_exp:
                zq_res = True
                break
            else:
                zq_res = False
    
    if not zq_res:
        zq_str = zq_str + zq_alm_exp        
            
    return (zq_res,zq_str)


def QS_900_Set_Date(zq_date,zq_time):

    zq_tl1_res=NE1.tl1.do("ED-DAT:::::{},{};".format(zq_date,zq_time))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        dprint("OK\tNE date & time changed to {} & {}".format(zq_date,zq_time),2)
    else:
        dprint("KO\tNE date & time change failure",2)

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
        VERIFY BBE-ES-SES-UAS COUNTER FOR MVC4 FACILITIES
        '''
        print("\n*******************************************************************")
        print("\n   CONFIGURATION OF MVC4 AND LOVC3 CROSS-CONNECTION                ")
        print("\n*******************************************************************")
        
        self.start_tps_block(NE1.id,"PM","5-5-25-1")

        E_LO_MTX = "MXH60GLO"
        E_HO_TI = 'X4F4E5420484F2D5452414345202020' #'ONT HO-TRACE   '
        E_SLOT = ['2','3','4','5','6','7','8','12','13','15','16','17','18','19']

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
        CREATE TCA PROFILE "AD HOC" TO FASTER TEST EXECUTION
        '''
        zq_tl1_res=NE1.tl1.do("ENT-TH-PROF:::::VC4:DFLT=N,USERLABEL=TCAAutomtest;")

        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::NEND,:MONTYPE-TMPER=ES-HOVC-15-MIN,THLEV={},DIRN=RCV;".format(E_ES_HOVC_15_ON))
        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::NEND,:MONTYPE-TMPER=ES-HOVC-1-DAY,THLEV={},DIRN=RCV;".format(E_ES_HOVC_24_ON))
        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::FEND,:MONTYPE-TMPER=ES-HOVC-15-MIN,THLEV={},DIRN=RCV;".format(E_ES_HOVC_15_ON))
        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::FEND,:MONTYPE-TMPER=ES-HOVC-1-DAY,THLEV={},DIRN=RCV;".format(E_ES_HOVC_24_ON))
        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::NEND,:MONTYPE-TMPER=SES-HOVC-15-MIN,THLEV={},DIRN=RCV;".format(E_SES_HOVC_15_ON))
        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::NEND,:MONTYPE-TMPER=SES-HOVC-1-DAY,THLEV={},DIRN=RCV;".format(E_SES_HOVC_24_ON))
        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::FEND,:MONTYPE-TMPER=SES-HOVC-15-MIN,THLEV={},DIRN=RCV;".format(E_SES_HOVC_15_ON))
        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::FEND,:MONTYPE-TMPER=SES-HOVC-1-DAY,THLEV={},DIRN=RCV;".format(E_SES_HOVC_24_ON))
        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::NEND,:MONTYPE-TMPER=BBE-HOVC-15-MIN,THLEV={},DIRN=RCV;".format(E_BBE_HOVC_15_ON))
        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::NEND,:MONTYPE-TMPER=BBE-HOVC-1-DAY,THLEV={},DIRN=RCV;".format(E_BBE_HOVC_24_ON))
        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::FEND,:MONTYPE-TMPER=BBE-HOVC-15-MIN,THLEV={},DIRN=RCV;".format(E_BBE_HOVC_15_ON))
        zq_tl1_res=NE1.tl1.do("ED-TH-PROF::THPVC4-2:::FEND,:MONTYPE-TMPER=BBE-HOVC-1-DAY,THLEV={},DIRN=RCV;".format(E_BBE_HOVC_24_ON))
        
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
                        print("**************************************")
                        print('Board Equipped: {}'.format(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO')))
                        print("**************************************")
                        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-1::::PROVISIONEDTYPE=XI-641;".format(''.join(zq_aid_list[zq_i]).replace('MDL','XFP')))
                        zq_board_to_remove.append(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO'))
                        print("**************************************")
                        print('\tXFP equipped: {}-1'.format(''.join(zq_aid_list[zq_i]).replace('MDL','XFP')))
                        print("**************************************")
                        zq_num += 1
                zq_i += 1

            
        NE1_stm64p3 = (''.join(zq_board_to_remove[0]).replace('10GSO-',''))+'-1'
        NE1_stm64p4 = (''.join(zq_board_to_remove[1]).replace('10GSO-',''))+'-1'
        NE1_stm64p5 = (''.join(zq_board_to_remove[2]).replace('10GSO-',''))+'-1'
        NE1_stm64p6 = (''.join(zq_board_to_remove[3]).replace('10GSO-',''))+'-1'
        
        print("\n******************************************************************************")
        print("\n   CHECK 2xMVC4 in FIRST BLOCK                                                ")
        print("\n******************************************************************************")

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
        
        QS_900_Set_Date("16-05-01", "01-00-00")

        zq_vc4_ch1="{}.1.1.1".format(str(E_VC4_1_1 % E_BLOCK_SIZE))
        zq_vc4_ch2="{}.1.1.1".format(str(E_VC4_1_2 % E_BLOCK_SIZE))
         
        zq_vc4_idx1 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_1_1))
        zq_vc4_idx2 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_1_2)) 

        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx1))
        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx2))
        

        if QS_070_Check_No_Alarm(self, ONT_P1, ONT_P2, zq_vc4_ch1, zq_vc4_ch2):

            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA NEAR END 15-MIN                                  ")
            print("\n******************************************************************************")

            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "ON", "15-MIN")
            
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","15-MIN","RCV","HPBIP","14000","64000")
            
           
            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA FAR END 15-MIN                                   ")
            print("\n******************************************************************************")
    
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "ON", "15-MIN")

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","15-MIN","RCV","HPREI","14000","64000")


            print("\n******************************************************************************")
            print("\n       Verify 15-MIN TCA Alarms presence (2xT-BBE,2xT-ES,2xT-SES)             ")
            print("\n******************************************************************************")
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-15-MIN,NSA,05-01,01-02-22,NEND,RCV,15,15,15-MIN"
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-15-MIN,NSA,05-01,01-14-59,FEND,RCV,15,15,15-MIN"
            
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        dprint("OK\tAll 15-MIN Near/Far End TCA Alarms are present",2)
                        self.add_success(NE1, "TCA Alarms","0.0", "All 15-MIN Near/Far End TCA Alarms are present")
                    else:
                        dprint("KO\tFollowing 15-MIN TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN TCA Alarms are missing:\r\n".format(zq_str))
                        

            print("\n***************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO NULL -> TCA ALARMS DISAPPEAR                 ")
            print("\n***************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx2))

            zq_tca_cleared = False
            for zq_i in range(1,180):
                time.sleep(10)
                zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    if zq_msg.get_cmd_response_size() == 0:
                        zq_tca_ttc = zq_i*10//60
                        dprint("\tTCA Alarms cleared after {} min".format(zq_tca_ttc),2)
                        if zq_tca_ttc <= 30:
                            dprint("OK\tTCA Alarms cleared after TCA profile change",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "TCA Alarms cleared after TCA profile change")
                            zq_tca_cleared = True
                        else:
                            dprint("KO\tTCA Alarms NOT cleared after TCA profile change",2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "TCA Alarms NOT cleared after TCA profile change")
                        break

            
            print("\n******************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO TCAAutomtest -> TCA ALARMS APPEAR AGAIN         ")
            print("\n******************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx2))

            time.sleep(10)
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        if zq_tca_cleared:
                            dprint("OK\tAll 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "All 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present")
                        else:
                            dprint("KO\tFollowing 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present".format(zq_str),2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present")
                    else:
                        dprint("KO\tFollowing 15-MIN TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN TCA Alarms are missing:\r\n".format(zq_str))



            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "DISABLED", "15-MIN")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "DISABLED", "15-MIN")

            
            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA NEND 1-DAY                                       ")
            print("\n******************************************************************************")
    
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "ON", "1-DAY")

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","1-DAY","RCV","HPBIP","14000","64000")


            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA FEND 1-DAY                                       ")
            print("\n******************************************************************************")
    
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "ON", "1-DAY")

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","1-DAY","RCV","HPREI","14000","64000")


            print("\n******************************************************************************")
            print("\n       Verify 1-DAY TCA Alarms presence (2xT-BBE,2xT-ES,2xT-SES)              ")
            print("\n******************************************************************************")
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-1-DAY,NSA,05-01,01-02-22,NEND,RCV,20,20,1-DAY"
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-1-DAY,NSA,05-01,01-14-59,FEND,RCV,20,20,1-DAY"
            
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        dprint("OK\tAll 1-DAY Near/Far End TCA Alarms are present",2)
                        self.add_success(NE1, "TCA Alarms","0.0", "All 1-DAY Near/Far End TCA Alarms are present")
                    else:
                        dprint("KO\tFollowing 1-DAY TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 1-DAY TCA Alarms are missing:\r\n".format(zq_str))
                        

            print("\n***************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO NULL -> TCA ALARMS DISAPPEAR                 ")
            print("\n***************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx2))

            zq_tca_cleared = False
            for zq_i in range(1,180):
                time.sleep(10)
                zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    if zq_msg.get_cmd_response_size() == 0:
                        zq_tca_ttc = zq_i*10//60
                        dprint("\tTCA Alarms cleared after {} min".format(zq_tca_ttc),2)
                        if zq_tca_ttc <= 30:
                            dprint("OK\tTCA Alarms cleared after TCA profile change",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "TCA Alarms cleared after TCA profile change")
                            zq_tca_cleared = True
                        else:
                            dprint("KO\tTCA Alarms NOT cleared after TCA profile change",2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "TCA Alarms NOT cleared after TCA profile change")
                        break

            print("\n******************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO TCAAutomtest -> TCA ALARMS APPEAR AGAIN         ")
            print("\n******************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx2))

            time.sleep(10)
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        if zq_tca_cleared:
                            dprint("OK\tAll 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "All 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present")
                        else:
                            dprint("KO\tFollowing 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present".format(zq_str),2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present")
                    else:
                        dprint("KO\tFollowing 15-MIN TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN TCA Alarms are missing:\r\n".format(zq_str))
                        

            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "DISABLED", "1-DAY")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "DISABLED", "1-DAY")

        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-SYSDFLT;".format(zq_vc4_idx1))
        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-SYSDFLT;".format(zq_vc4_idx2))
 
        QS_060_Delete_LO_XC_Block(self, E_VC4_1_1, E_VC4_1_2, zq_xc_list)
        
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        print("\n******************************************************************************")
        print("\n   CHECK 2xMVC4 in SECOND BLOCK                                               ")
        print("\n******************************************************************************")

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

        QS_900_Set_Date("16-05-01", "02-00-00")
        
        print("\n******************************************************************************")
        print("\n       VERIFY BBE-ES-SES-UAS COUNTER NEAR END 15-MIN/1-DAY                    ")
        print("\n******************************************************************************")

        zq_vc4_ch1="{}.1.1.1".format(str(E_VC4_2_1 % E_BLOCK_SIZE))
        zq_vc4_ch2="{}.1.1.1".format(str(E_VC4_2_2 % E_BLOCK_SIZE))
         
        zq_vc4_idx1 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_2_1))
        zq_vc4_idx2 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_2_2)) 
    
        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx1))
        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx2))
        
        if QS_070_Check_No_Alarm(self, ONT_P1, ONT_P2, zq_vc4_ch1, zq_vc4_ch2):

            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA NEAR END 15-MIN                                  ")
            print("\n******************************************************************************")

            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "ON", "15-MIN")
            
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","15-MIN","RCV","HPBIP","14000","64000")
            
           
            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA FAR END 15-MIN                                   ")
            print("\n******************************************************************************")
    
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "ON", "15-MIN")

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","15-MIN","RCV","HPREI","14000","64000")


            print("\n******************************************************************************")
            print("\n       Verify 15-MIN TCA Alarms presence (2xT-BBE,2xT-ES,2xT-SES)             ")
            print("\n******************************************************************************")
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-15-MIN,NSA,05-01,01-02-22,NEND,RCV,15,15,15-MIN"
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-15-MIN,NSA,05-01,01-14-59,FEND,RCV,15,15,15-MIN"
            
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        dprint("OK\tAll 15-MIN Near/Far End TCA Alarms are present",2)
                        self.add_success(NE1, "TCA Alarms","0.0", "All 15-MIN Near/Far End TCA Alarms are present")
                    else:
                        dprint("KO\tFollowing 15-MIN TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN TCA Alarms are missing:\r\n".format(zq_str))
                        

            print("\n***************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO NULL -> TCA ALARMS DISAPPEAR                 ")
            print("\n***************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx2))

            zq_tca_cleared = False
            for zq_i in range(1,180):
                time.sleep(10)
                zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    if zq_msg.get_cmd_response_size() == 0:
                        zq_tca_ttc = zq_i*10//60
                        dprint("\tTCA Alarms cleared after {} min".format(zq_tca_ttc),2)
                        if zq_tca_ttc <= 30:
                            dprint("OK\tTCA Alarms cleared after TCA profile change",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "TCA Alarms cleared after TCA profile change")
                            zq_tca_cleared = True
                        else:
                            dprint("KO\tTCA Alarms NOT cleared after TCA profile change",2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "TCA Alarms NOT cleared after TCA profile change")
                        break

            
            print("\n******************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO TCAAutomtest -> TCA ALARMS APPEAR AGAIN         ")
            print("\n******************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx2))

            time.sleep(10)
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        if zq_tca_cleared:
                            dprint("OK\tAll 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "All 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present")
                        else:
                            dprint("KO\tFollowing 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present".format(zq_str),2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present")
                    else:
                        dprint("KO\tFollowing 15-MIN TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN TCA Alarms are missing:\r\n".format(zq_str))



            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "DISABLED", "15-MIN")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "DISABLED", "15-MIN")

            
            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA NEND 1-DAY                                       ")
            print("\n******************************************************************************")
    
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "ON", "1-DAY")

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","1-DAY","RCV","HPBIP","14000","64000")


            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA FEND 1-DAY                                       ")
            print("\n******************************************************************************")
    
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "ON", "1-DAY")

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","1-DAY","RCV","HPREI","14000","64000")


            print("\n******************************************************************************")
            print("\n       Verify 1-DAY TCA Alarms presence (2xT-BBE,2xT-ES,2xT-SES)              ")
            print("\n******************************************************************************")
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-1-DAY,NSA,05-01,01-02-22,NEND,RCV,20,20,1-DAY"
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-1-DAY,NSA,05-01,01-14-59,FEND,RCV,20,20,1-DAY"
            
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        dprint("OK\tAll 1-DAY Near/Far End TCA Alarms are present",2)
                        self.add_success(NE1, "TCA Alarms","0.0", "All 1-DAY Near/Far End TCA Alarms are present")
                    else:
                        dprint("KO\tFollowing 1-DAY TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 1-DAY TCA Alarms are missing:\r\n".format(zq_str))
                        

            print("\n***************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO NULL -> TCA ALARMS DISAPPEAR                 ")
            print("\n***************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx2))

            zq_tca_cleared = False
            for zq_i in range(1,180):
                time.sleep(10)
                zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    if zq_msg.get_cmd_response_size() == 0:
                        zq_tca_ttc = zq_i*10//60
                        dprint("\tTCA Alarms cleared after {} min".format(zq_tca_ttc),2)
                        if zq_tca_ttc <= 30:
                            dprint("OK\tTCA Alarms cleared after TCA profile change",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "TCA Alarms cleared after TCA profile change")
                            zq_tca_cleared = True
                        else:
                            dprint("KO\tTCA Alarms NOT cleared after TCA profile change",2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "TCA Alarms NOT cleared after TCA profile change")
                        break

            print("\n******************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO TCAAutomtest -> TCA ALARMS APPEAR AGAIN         ")
            print("\n******************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx2))

            time.sleep(10)
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        if zq_tca_cleared:
                            dprint("OK\tAll 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "All 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present")
                        else:
                            dprint("KO\tFollowing 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present".format(zq_str),2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present")
                    else:
                        dprint("KO\tFollowing 15-MIN TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN TCA Alarms are missing:\r\n".format(zq_str))
                        

            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "DISABLED", "1-DAY")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "DISABLED", "1-DAY")

        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-SYSDFLT;".format(zq_vc4_idx1))
        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-SYSDFLT;".format(zq_vc4_idx2))

        QS_060_Delete_LO_XC_Block(self, E_VC4_2_1, E_VC4_2_2, zq_xc_list)
        
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p4, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        QS_020_Delete_HO_XC_Block(self, NE1_stm64p1, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1_stm64p2, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)

        
        print("\n******************************************************************************")
        print("\n   CHECK 2xMVC4 in THIRD BLOCK                                                ")
        print("\n******************************************************************************")

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

        QS_900_Set_Date("16-05-01", "03-00-00")
        
        zq_vc4_ch1="{}.1.1.1".format(str(E_VC4_3_1 % E_BLOCK_SIZE))
        zq_vc4_ch2="{}.1.1.1".format(str(E_VC4_3_2 % E_BLOCK_SIZE))
         
        zq_vc4_idx1 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_3_1))
        zq_vc4_idx2 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_3_2)) 
    
        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx1))
        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx2))

        if QS_070_Check_No_Alarm(self, ONT_P1, ONT_P2, zq_vc4_ch1, zq_vc4_ch2):

            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA NEAR END 15-MIN                                  ")
            print("\n******************************************************************************")

            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "ON", "15-MIN")
            
            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","15-MIN","RCV","HPBIP","14000","64000")
            
           
            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA FAR END 15-MIN                                   ")
            print("\n******************************************************************************")
    
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "ON", "15-MIN")

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","15-MIN","RCV","HPREI","14000","64000")


            print("\n******************************************************************************")
            print("\n       Verify 15-MIN TCA Alarms presence (2xT-BBE,2xT-ES,2xT-SES)             ")
            print("\n******************************************************************************")
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-15-MIN,NSA,05-01,01-02-22,NEND,RCV,15,15,15-MIN"
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-15-MIN,NSA,05-01,01-14-59,FEND,RCV,15,15,15-MIN"
            
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        dprint("OK\tAll 15-MIN Near/Far End TCA Alarms are present",2)
                        self.add_success(NE1, "TCA Alarms","0.0", "All 15-MIN Near/Far End TCA Alarms are present")
                    else:
                        dprint("KO\tFollowing 15-MIN TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN TCA Alarms are missing:\r\n".format(zq_str))
                        

            print("\n***************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO NULL -> TCA ALARMS DISAPPEAR                 ")
            print("\n***************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx2))

            zq_tca_cleared = False
            for zq_i in range(1,180):
                time.sleep(10)
                zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    if zq_msg.get_cmd_response_size() == 0:
                        zq_tca_ttc = zq_i*10//60
                        dprint("\tTCA Alarms cleared after {} min".format(zq_tca_ttc),2)
                        if zq_tca_ttc <= 30:
                            dprint("OK\tTCA Alarms cleared after TCA profile change",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "TCA Alarms cleared after TCA profile change")
                            zq_tca_cleared = True
                        else:
                            dprint("KO\tTCA Alarms NOT cleared after TCA profile change",2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "TCA Alarms NOT cleared after TCA profile change")
                        break

            
            print("\n******************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO TCAAutomtest -> TCA ALARMS APPEAR AGAIN         ")
            print("\n******************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx2))

            time.sleep(10)
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1,
                                                      "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,NEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_BBE_HOVC_15_ON,E_BBE_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_ES_HOVC_15_ON,E_ES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-15-MIN,NSA,,,FEND,RCV,{},{},15-MIN".format(zq_vc4_idx1,E_SES_HOVC_15_ON,E_SES_HOVC_15_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        if zq_tca_cleared:
                            dprint("OK\tAll 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "All 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present")
                        else:
                            dprint("KO\tFollowing 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present".format(zq_str),2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present")
                    else:
                        dprint("KO\tFollowing 15-MIN TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN TCA Alarms are missing:\r\n".format(zq_str))



            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "DISABLED", "15-MIN")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "DISABLED", "15-MIN")

            
            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA NEND 1-DAY                                       ")
            print("\n******************************************************************************")
    
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "ON", "1-DAY")

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","1-DAY","RCV","HPBIP","14000","64000")


            print("\n******************************************************************************")
            print("\n       VERIFY BBE-ES-SES TCA FEND 1-DAY                                       ")
            print("\n******************************************************************************")
    
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "ON", "1-DAY")

            QS_100_Check_BBE_ES_SES_UAS(self, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","1-DAY","RCV","HPREI","14000","64000")


            print("\n******************************************************************************")
            print("\n       Verify 1-DAY TCA Alarms presence (2xT-BBE,2xT-ES,2xT-SES)              ")
            print("\n******************************************************************************")
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-1-DAY,NSA,05-01,01-02-22,NEND,RCV,20,20,1-DAY"
            #MVC4-1-1-7-34,VC4:WR,T-SES-HOVC-1-DAY,NSA,05-01,01-14-59,FEND,RCV,20,20,1-DAY"
            
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        dprint("OK\tAll 1-DAY Near/Far End TCA Alarms are present",2)
                        self.add_success(NE1, "TCA Alarms","0.0", "All 1-DAY Near/Far End TCA Alarms are present")
                    else:
                        dprint("KO\tFollowing 1-DAY TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 1-DAY TCA Alarms are missing:\r\n".format(zq_str))
                        

            print("\n***************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO NULL -> TCA ALARMS DISAPPEAR                 ")
            print("\n***************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-NULL;".format(zq_vc4_idx2))

            zq_tca_cleared = False
            for zq_i in range(1,180):
                time.sleep(10)
                zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    if zq_msg.get_cmd_response_size() == 0:
                        zq_tca_ttc = zq_i*10//60
                        dprint("\tTCA Alarms cleared after {} min".format(zq_tca_ttc),2)
                        if zq_tca_ttc <= 30:
                            dprint("OK\tTCA Alarms cleared after TCA profile change",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "TCA Alarms cleared after TCA profile change")
                            zq_tca_cleared = True
                        else:
                            dprint("KO\tTCA Alarms NOT cleared after TCA profile change",2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "TCA Alarms NOT cleared after TCA profile change")
                        break

            print("\n******************************************************************************")
            print("\n   CHANGE MVC4 TCA PROFILE TO TCAAutomtest -> TCA ALARMS APPEAR AGAIN         ")
            print("\n******************************************************************************")
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx1))
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=TCAAutomtest;".format(zq_vc4_idx2))

            time.sleep(10)
            zq_tl1_res=NE1.tl1.do("RTRV-ALM-VC4::{};".format(zq_vc4_idx1))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_temp_ary = zq_msg._TL1message__m_plain.split("\r\n")
                    zq_res = True
                    zq_str = "" 
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON))
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,NEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-BBE-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_BBE_HOVC_24_ON,E_BBE_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-ES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_ES_HOVC_24_ON,E_ES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 
                    
                    zq_tmp = QS_160_Verify_TCA_Alarm(self, zq_temp_ary, zq_vc4_idx1, 
                                                     "{},VC4:WR,T-SES-HOVC-1-DAY,NSA,,,FEND,RCV,{},{},1-DAY".format(zq_vc4_idx1,E_SES_HOVC_24_ON,E_SES_HOVC_24_ON)) 
                    zq_res = zq_res and zq_tmp[0]
                    zq_str = zq_str + zq_tmp[1] 

                    if zq_res:
                        if zq_tca_cleared:
                            dprint("OK\tAll 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present",2)
                            self.add_success(NE1, "TCA Alarms","0.0", "All 15-MIN Near/Far End TCA Alarms were CLEARED and are NOW present")
                        else:
                            dprint("KO\tFollowing 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present".format(zq_str),2)
                            self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN Near/Far End TCA Alarms were NOT CLEARED and are present")
                    else:
                        dprint("KO\tFollowing 15-MIN TCA Alarms are missing:\r\n".format(zq_str),2)
                        self.add_failure(NE1, "TCA Alarms", "0.0", "TCA Alarms", "Following 15-MIN TCA Alarms are missing:\r\n".format(zq_str))
                        

            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "NEND", "DISABLED", "1-DAY")
            QS_090_Set_PM_Mode(self, zq_vc4_idx1, "FEND", "DISABLED", "1-DAY")

        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-SYSDFLT;".format(zq_vc4_idx1))
        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::TCAprof=LBL-THPVC4-SYSDFLT;".format(zq_vc4_idx2))

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
            print("**************************************")
            print('\tXFP Deleted: {}-1'.format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','MDL')))
            print("**************************************")
            
            zq_tl1_res=NE1.tl1.do("RMV-EQPT::{};".format(''.join(zq_board_to_remove[zq_i])))
            NE1.tl1.do_until("RTRV-EQPT::{};".format(''.join(zq_board_to_remove[zq_i])),zq_filter)
            zq_tl1_res=NE1.tl1.do("DLT-EQPT::{};".format(''.join(zq_board_to_remove[zq_i])))
            NE1.tl1.do_until("RTRV-EQPT::{};".format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','MDL')),zq_filter)
            print("**************************************")
            print('Board Deleted: {}'.format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','MDL')))
            print("**************************************")

        zq_tl1_res=NE1.tl1.do("DLT-TH-PROF::THPVC4-2:;")
        
        self.stop_tps_block(NE1.id,"PM","5-5-25-1")


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
    