#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: Verify PM data is not provided on non-existing VC4, VC4-4C, VC4-16C, VC4-64C    
:field Description: with STM64 facility on 10XANY10G
:field Topology: 42
:field Dependency:NA
:field Lab: SVT
:field TPS: PM__5-2-8-48
:field TPS: PM__5-2-8-49
:field TPS: PM__5-2-8-50
:field TPS: PM__5-2-8-51
:field RunSections: 11111
:field Author: ldelette 

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.instrumentONT     import InstrumentONT
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import *
import time
import string
import math

E_WAIT = 10
E_STM16 = "STM16"
E_STM4 = "STM4"
E_STM64 = "STM64"
E_POM = "Y"
E_EGPOM = "Y"

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

def QS_060_Create_HO_XC(zq_run, au_size,zq_from_xc,zq_to_xc):
    #Create a group of VCn 
        zq_tl1_res=NE1.tl1.do("ENT-CRS-{}::{},{}:::2WAY;".format(au_size,zq_from_xc,zq_to_xc))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tXC correctly created\n",2)
            zq_run.add_success(NE1, "TL1 Command","0.0", "XC correctly created")
        else:
            dprint("KO\tXC creation with a DENY message",2)
            zq_run.add_failure(NE1, "TL1 Command","0.0", "TL1 Command not successful", "XC creation with a DENY message")
        return
    
def QS_080_Get_PM_Counter_Check(zq_run,zq_issetmode,zq_isprov, NE1_stmnp1, zq_counter_type, zq_locn, zq_period, zq_dir,stm_size):
    # Get PM Counter values     
        zq_tl1_res=NE1.tl1.do("RTRV-PM-{}::{}:::{},0-UP,{},{},{};".format(stm_size,NE1_stmnp1, zq_counter_type, zq_locn,zq_dir,zq_period))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        zq_response_size=zq_msg.get_cmd_display_output_rows()
        if zq_isprov == "YES":
            if zq_cmd == (True,'COMPLD'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_run.add_success(NE1, "PM Counter Reading", "0.0", "RTRV-PM command correctly executed and registers are retrieved".format(NE1_stmnp1))
                    dprint("OK\tRTRV-PM command correctly executed and registers are retrieved.\n".format(NE1_stmnp1),2)
                else:
                    if zq_issetmode == "DISABLED":
                        zq_run.add_success(NE1, "PM Counter Reading", "0.0","RTRV-PM command correctly executed but no registers are retrieved because SETMODE is DISABLED".format(NE1_stmnp1))
                        dprint("OK\tRTRV-PM command correctly executed but no registers are retrieved because SETMODE is DISABLED.\n".format(NE1_stmnp1),2)
                    else:
                        zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", "RTRV-PM command with a COMPLD message but no registers are retrieved when SETMODE is NOT DISABLED".format(NE1_stmnp1))
                        dprint("KO\tRTRV-PM command with a COMPLD message but no registers are retrieved when SETMODE is NOT DISABLED.\n".format(NE1_stmnp1),2)        
        else:
            if zq_cmd == (True,'DENY'):
                if zq_msg.get_cmd_response_size() != 0:
                    zq_run.add_success(NE1, "PM Counter Reading", "0.0", "RTRV-PM command with a DENY message, AID wrong".format(NE1_stmnp1))
                    dprint("OK\tRTRV-PM command with a DENY message, AID wrong.\n".format(NE1_stmnp1),2)
            else:
                zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", "RTRV-PM command with a COMPLD message for an unprovided facility".format(NE1_stmnp1))
                dprint("KO\tRTRV-PM command with a COMPLD message for an unprovided facility.\n".format(NE1_stmnp1),2)        
            return

def QS_090_Set_PM_Mode(zq_run, NE1_stmnp1, zq_locn, zq_mode, zq_period, zq_dir,stm_size):
    #Enable PM ALL 15-MIN and 1-DAY
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-{}::{}:::{},ALL,{},{}:TMPER={};".format(stm_size,NE1_stmnp1, zq_locn, zq_mode, zq_dir,zq_period))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tPM set to {} for {}: [{}]-[{}]-[{}]\n".format(zq_mode, NE1_stmnp1,zq_locn,zq_dir,zq_period),2)
            zq_run.add_success(NE1, "TL1 Command","0.0", "PM set to {} for {}: [{}]-[{}]-[{}]".format(zq_mode, NE1_stmnp1,zq_locn,zq_dir,zq_period))
        else:
            dprint("KO\tPM NOT set to {} for {}: [{}]-[{}]-[{}]".format(zq_mode, NE1_stmnp1,zq_locn,zq_dir,zq_period),2)
            zq_run.add_failure(NE1, "TL1 Command","0.0", "TL1 Command not successful", "PM set to {} for {}: [{}]-[{}]-[{}]".format(zq_mode, NE1_stmnp1,zq_locn,zq_dir,zq_period))

        return
    
def QS_100_Check_PM_Mode(zq_run, NE1_stmnp1, zq_locn, zq_period, zq_dir,stm_size):
    #Retrieve PM MODE Status for 15-MIN and 1-DAY counter
        if zq_period == "BOTH":  
            zq_PMMODE_retrieve = QS_110_Get_PM_Mode_Status(zq_run, NE1_stmnp1,zq_locn, zq_period, zq_dir,stm_size)  
            b=0
            while b < len(zq_PMMODE_retrieve[0]):
                dprint("Location Counter is {}".format(zq_PMMODE_retrieve[2][int(b)]),2)
                dprint("Mode Type is {}".format(zq_PMMODE_retrieve[0][int(b)]),2)
                dprint("Time Period is {}".format(zq_PMMODE_retrieve[3][int(b)]),2)
                dprint("PM State is {}\n".format(zq_PMMODE_retrieve[1][int(b)]),2)
                b = b + 1   
        return
    
def QS_110_Get_PM_Mode_Status(zq_run, NE1_stmnp1, zq_locn, zq_period, zq_dir,stm_size):
        
        zq_output_retrieve_PM_state = []
        zq_timeperiod = []
        zq_location = []
        zq_modetype = []
        zq_PM_state = []
        zq_tl1_res=NE1.tl1.do("RTRV-PMMODE-{}::{}:::{},{}:TMPER={};".format(stm_size,NE1_stmnp1, zq_locn,zq_dir,zq_period))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        zq_response_size=zq_msg.get_cmd_display_output_rows()
        #for x in zq_response_size:
            #dprint("Values x {}".format(zq_response_size), 2)
        if zq_cmd == (True,'COMPLD'):
            if zq_msg.get_cmd_response_size() != 0:
                zq_run.add_success(NE1, "PM Counter Reading", "0.0", "RTRV-PMMODE command correctly executed".format(NE1_stmnp1))
                dprint("OK\tRTRV-PMMODE command correctly executed.\n".format(NE1_stmnp1),2)
                zq_location=zq_msg.get_cmd_attr_value("{}".format(NE1_stmnp1), "1")
                zq_PM_state=zq_msg.get_cmd_attr_value("{}".format(NE1_stmnp1), "PMSTATE")
                zq_modetype=zq_msg.get_cmd_attr_value("{}".format(NE1_stmnp1), "2")
                zq_timeperiod=zq_msg.get_cmd_attr_value("{}".format(NE1_stmnp1), "TMPER")       
        else:
                zq_run.add_failure(NE1, "PM Counter Reading", "0.0", "PM Counter Reading", "RTRV-PMMODE command with a DENY message".format(NE1_stmnp1))
                dprint("KO\tRTRV-PMMODE command with a DENY message.\n".format(NE1_stmnp1),2)
        zq_output_retrieve_PM_state = [zq_modetype, zq_PM_state, zq_location,zq_timeperiod]
        return zq_output_retrieve_PM_state
    
def QS_050_Delete_HO_XC(zq_run, au_size,zq_from_xc,zq_to_xc):
    #Create a group of VCn 
        zq_tl1_res=NE1.tl1.do("DLT-CRS-{}::{},{};".format(au_size,zq_from_xc,zq_to_xc))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tXC correctly deleted\n",2)
            zq_run.add_success(NE1, "TL1 Command","0.0", "XC correctly deleted")
        else:
            dprint("KO\tXC delete command with a DENY message",2)
            zq_run.add_failure(NE1, "TL1 Command","0.0", "TL1 Command not successful", "XC delete command with a DENY message")
        return
    
def QS_070_Setup_VC_Conc(zq_run, NE1_stmnp1,au4nc_size,rate_VC_conc,stm_rate):
    #Create a group of VCn 
        zq_tl1_res=NE1.tl1.do("ED-{}::{}-{}::::CMDMDE=FRCD,HOSTRUCT={}x{};".format(stm_rate,stm_rate,NE1_stmnp1,rate_VC_conc,au4nc_size))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tVC concatenation creation correctly completed\n",2)
            zq_run.add_success(NE1, "TL1 Command","0.0", "VC concatenation creation correctly completed")
        else:
            dprint("KO\tVC concatenation creation with a DENY message",2)
            zq_run.add_failure(NE1, "TL1 Command","0.0", "TL1 Command not successful", "VC concatenation creation with a DENY message")
        return
    
def QS_080_Set_PM_Mode_AUXXC(zq_run,vc4_nc_size, NE1_stmnp1, zq_locn, zq_mode, zq_period, zq_dir="ALL"):
    #Enable PM ALL 15-MIN and 1-DAY
        zq_tl1_res=NE1.tl1.do("SET-PMMODE-{}::{}:::{},ALL,{},{}:TMPER={};".format(vc4_nc_size,NE1_stmnp1, zq_locn, zq_mode, zq_dir,zq_period))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tPM set to {} for {}: [{}]-[{}]-[{}]\n".format(zq_mode, NE1_stmnp1,zq_locn,zq_dir,zq_period),2)
            zq_run.add_success(NE1, "TL1 Command","0.0", "PM set to {} for {}: [{}]-[{}]-[{}]".format(zq_mode, NE1_stmnp1,zq_locn,zq_dir,zq_period))
        else:
            dprint("KO\tPM NOT set to {} for {}: [{}]-[{}]-[{}]".format(zq_mode, NE1_stmnp1,zq_locn,zq_dir,zq_period),2)
            zq_run.add_failure(NE1, "TL1 Command","0.0", "TL1 Command not successful", "PM set to {} for {}: [{}]-[{}]-[{}]".format(zq_mode, NE1_stmnp1,zq_locn,zq_dir,zq_period))

        return
    
def QS_100_Edit_VCn_POM_EGPOM(zq_run,au4_nc_size, zq_stmn_idx1,zq_POM = "N",zq_EGPOM = "N"):
    #Enable or disable Path Overhead Monitoring in ingress and egress 
        zq_tl1_res=NE1.tl1.do("ED-{}::{}::::POM={},EGPOM={},CMDMDE=FRCD;".format(au4_nc_size,zq_stmn_idx1,zq_POM,zq_EGPOM))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tEdit AUn POM/EGPOM command correctly completed",2) 
            zq_run.add_success(NE1, "TL1 Command","0.0", "Edit AUn POM/EGPOM command correctly completed")
        else:
            dprint("KO\tEdit AUn POM/EGPOM command with a DENY message",2)
            zq_run.add_failure(NE1, "TL1 Command","0.0", "TL1 Command not successful", "Edit AUn POM/EGPOM command with a DENY message")
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
        ONT1.init_instrument(ONT1_P1)

    def test_body(self):
        '''
        test Body Section implementation
        insert Main body code for your test below
        '''
        print("\n******************** START ********************") 
        
        self.start_tps_block(NE1.id,"PM","5-2-8-48")
        
        E_MTX = "MXEC320"
        NE1_stmnp1 = NE1_S1
        NE1_stm64p1 =  NE1_S2
        E_HOAU4 = "AU4"
        E_HOVC4 = "VC4"
        TX_MEASURE_CH = "1"
        RX_MEASURE_CH = "1"
        zq_stmn_idx1 = "STM64{}-{}-{}".format(E_HOAU4,NE1_stmnp1,TX_MEASURE_CH)
        zq_stm64_idx2 = "STM64{}-{}-{}".format(E_HOAU4,NE1_stm64p1,RX_MEASURE_CH)
        
        '''
        Board equipment if not yet!
        '''
        
        zq_tl1_res=NE1.tl1.do("RTRV-EQPT::{}-1-1-10;".format(E_MTX))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_attr_list1=zq_msg.get_cmd_attr_values("{}-1-1-10".format(E_MTX))
            zq_attr_list2=zq_msg.get_cmd_attr_values("{}-1-1-10".format("MDL"))
            if zq_attr_list1[0] is not None:
                if zq_attr_list1[0]['PROVISIONEDTYPE']==E_MTX and zq_attr_list1[0]['ACTUALTYPE']==E_MTX:  #Board equipped 
                    print("Board already equipped")
                else:
                    zq_filter=TL1check()
                    zq_filter.add_pst("IS")
                    # zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-1-1-10;".format(E_MTX))
                    NE1.tl1.do_until("RTRV-EQPT::{}-1-1-10;".format(E_MTX),zq_filter)
            else:
                if zq_attr_list2[0] is not None:
                    if zq_attr_list2[0]['ACTUALTYPE']==E_MTX:  #Equip Board 
                        zq_filter=TL1check()
                        zq_filter.add_pst("IS")
                        # zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-1-1-10;".format(E_MTX))
                        NE1.tl1.do_until("RTRV-EQPT::{}-1-1-10;".format(E_MTX),zq_filter)
        
        print("\n******************************************************************************")
        print("\n CREATE STM-64 CROSS-CONNECTION ")
        print("\n******************************************************************************\n")
        
        QS_060_Create_HO_XC(self,E_HOVC4,zq_stmn_idx1,zq_stm64_idx2)
                        
        '''
        Configure ONT_P1 port to VC4 mapping
        '''
        ONT1.get_set_tx_bit_rate(ONT1_P1, E_STM64)
        
        ONT1.get_set_rx_bit_rate(ONT1_P1, E_STM64)
        
        ONT1.get_set_rx_channel_mapping_size(ONT1_P1, E_HOVC4)
        
        ONT1.get_set_tx_channel_mapping_size(ONT1_P1, E_HOVC4)
        
        ONT1.get_set_tx_measure_channel(ONT1_P1,TX_MEASURE_CH)
        
        ONT1.get_set_rx_measure_channel(ONT1_P1,RX_MEASURE_CH)
        
        ONT1.get_set_clock_reference_source(ONT1_P1, "RX")

        ONT1.get_set_laser_status(ONT1_P1, "ON")

        # ONT1.get_set_background_channels_fill_mode(ONT1_P1, "FIX")
        
        time.sleep(E_WAIT)
        
        zq_stm64_idx1 = "STM64-{}".format(NE1_stmnp1)
        
        stm_size = E_STM64
        
        print("\n******************************************************************************")
        print("\n VERIFY THAT FOR AN UNPROVISIONED STM64 FACILITY AID THE RTRV-PM COMMAND IS DENIED ")
        print("\n******************************************************************************\n")
        
        zq_isprov = "NO"
        zq_issetmode = "UNKNOWN"
        zq_stm64_idx1 = "STM64-{}".format("1-1-24-100")
        zq_locn = "ALL"
        zq_period = "BOTH"
        zq_counter_type = "ALL"
        zq_dir = "ALL"
            
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_stm64_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,stm_size)
        
        print("\n******************************************************************************")
        print("\n       SET PMMODE ON TO CREATE REGISTERS FOR STM64 FACILITIES                  ")
        print("\n******************************************************************************\n")
        
        zq_stm64_idx1 = "STM64-{}".format(NE1_stmnp1)
        
        QS_090_Set_PM_Mode(self, zq_stm64_idx1, "ALL", "ON", "BOTH","ALL",stm_size)
        
        print("\n******************************************************************************")
        print("\n       CHECK PMMODE STATE IS ON FOR STM64 REGISTERS                            ")
        print("\n******************************************************************************\n")
        
        QS_100_Check_PM_Mode(self, zq_stm64_idx1, "ALL", "BOTH","ALL",stm_size)
        
        print("\n******************************************************************************")
        print("\n VERIFY THAT FOR AN UNPROVISIONED STM64 FACILITY AID THE RTRV-PM COMMAND IS DENIED ")
        print("\n******************************************************************************\n")
        
        zq_isprov = "YES"
        zq_issetmode = "ON"
        zq_stm64_idx1 = "STM64-{}".format(NE1_stmnp1)
            
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_stm64_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,stm_size)
        
        print("\n******************************************************************************")
        print("\n SET PM MODE TO DISABLE AND VERIFY NO PARAMETERS ARE RETRIEVED FOR PM COUNTERS")
        print("\n******************************************************************************\n")
        
        QS_090_Set_PM_Mode(self, zq_stm64_idx1, "ALL", "DISABLED", "BOTH","ALL",stm_size)
        
        zq_isprov = "YES"
        zq_issetmode = "DISABLED"
        zq_stm64_idx1 = "STM64-{}".format(NE1_stmnp1)
        
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_stm64_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,stm_size)
        
        QS_050_Delete_HO_XC(self,E_HOVC4,zq_stmn_idx1,zq_stm64_idx2)
            
        self.stop_tps_block(NE1.id,"PM", "5-2-8-48")
        
        time.sleep(E_WAIT)
        
        self.start_tps_block(NE1.id,"PM","5-2-8-49")
        
        print("\n******************************************************************************")
        print("\nSETUP VC4-4C GROUP ON STM64 FACILITY USING ED-STM64 COMMAND AND CREATE CROSS-CONNECTION ")
        print("\n******************************************************************************\n")
        
        E_HOAU4NC = "AU44C"
        E_HOVC4NC = "VC44C"
        au4_nc_size = E_HOAU4NC
        vc4_nc_size = E_HOVC4NC
        stmrate = [E_STM16,E_STM64]
        rateVC4XC = [4,16,64]
        zq_au44c_idx1 = "{}{}-{}-{}".format(stmrate[1],au4_nc_size,NE1_stmnp1,TX_MEASURE_CH)
        zq_au44c_idx2 = "{}{}-{}-{}".format(stmrate[1],au4_nc_size,NE1_stm64p1,RX_MEASURE_CH)
        
        QS_070_Setup_VC_Conc(self, NE1_stmnp1,au4_nc_size,rateVC4XC[1],stmrate[1])
        
        QS_070_Setup_VC_Conc(self, NE1_stm64p1,au4_nc_size,rateVC4XC[1],stmrate[1])
        
        QS_060_Create_HO_XC(self,vc4_nc_size,zq_au44c_idx1,zq_au44c_idx2)
                        
        '''
        Configure ONT_P1 port to VC4 mapping
        '''
        
        ONT1.get_set_tx_bit_rate(ONT1_P1, E_STM64)
        
        ONT1.get_set_rx_bit_rate(ONT1_P1, E_STM64)
        
        ONT1.get_set_rx_channel_mapping_size(ONT1_P1, "VC4_4C")
        
        ONT1.get_set_tx_channel_mapping_size(ONT1_P1, "VC4_4C")
        
        ONT1.get_set_tx_measure_channel(ONT1_P1,TX_MEASURE_CH)
        
        ONT1.get_set_rx_measure_channel(ONT1_P1,RX_MEASURE_CH)
        
        ONT1.get_set_clock_reference_source(ONT1_P1, "RX")

        ONT1.get_set_laser_status(ONT1_P1, "ON")

        # ONT1.get_set_background_channels_fill_mode(ONT1_P1, "FIX")
        
        time.sleep(E_WAIT)
        
        print("\n******************************************************************************")
        print("\n VERIFY THAT FOR AN UNPROVISIONED STM64 FACILITY AID THE RTRV-PM COMMAND IS DENIED ")
        print("\n******************************************************************************\n")
        
        zq_isprov = "NO"
        zq_issetmode = "UNKNOWN"
        zq_au44c_idx1 = "{}{}-{}-{}".format(stmrate[1],au4_nc_size,"1-1-24-100",TX_MEASURE_CH)
        zq_locn = "ALL"
        zq_period = "BOTH"
        zq_counter_type = "ALL"
        zq_dir = "ALL"
            
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_au44c_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,vc4_nc_size)
        
        print("\n******************************************************************************")
        print("\n       SET PMMODE ON TO CREATE REGISTERS FOR STM64 VC4-4C FACILITIES                  ")
        print("\n******************************************************************************\n")
        
        zq_au44c_idx1 = "{}{}-{}-{}".format(stmrate[1],au4_nc_size,NE1_stmnp1,TX_MEASURE_CH)
             
        QS_100_Edit_VCn_POM_EGPOM(self,au4_nc_size,zq_au44c_idx1,E_POM, E_EGPOM)
        
        QS_080_Set_PM_Mode_AUXXC(self,vc4_nc_size,zq_au44c_idx1, "ALL", "ON", "BOTH")
        
        print("\n******************************************************************************")
        print("\n       CHECK PMMODE STATE IS ON FOR VC4-4C REGISTERS                            ")
        print("\n******************************************************************************\n")
        
        QS_100_Check_PM_Mode(self, zq_au44c_idx1, "ALL", "BOTH","ALL",vc4_nc_size)
        
        print("\n******************************************************************************")
        print("\n VERIFY THAT FOR AN UNPROVISIONED STM64 VC4-4C FACILITY AID THE RTRV-PM COMMAND IS DENIED ")
        print("\n******************************************************************************\n")
        
        zq_isprov = "YES"
        zq_issetmode = "ON"
            
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_au44c_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,vc4_nc_size)
        
        print("\n******************************************************************************")
        print("\n SET PM MODE TO DISABLE FOR STM64 VC4-4C AND VERIFY NO PARAMETERS ARE RETRIEVED FOR PM COUNTERS")
        print("\n******************************************************************************\n")
        
        QS_080_Set_PM_Mode_AUXXC(self,vc4_nc_size,zq_au44c_idx1, "ALL", "DISABLED", "BOTH")
        
        zq_isprov = "YES"
        zq_issetmode = "DISABLED"
        zq_stm64_idx1 = "STM64-{}".format(NE1_stmnp1)
        
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_au44c_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,vc4_nc_size)
        
        QS_050_Delete_HO_XC(self,E_HOVC4NC,zq_au44c_idx1,zq_au44c_idx2)
        
        au4_nc_size = "AU4"
            
        QS_070_Setup_VC_Conc(self, NE1_stmnp1,au4_nc_size,rateVC4XC[2],stmrate[1])
        
        QS_070_Setup_VC_Conc(self, NE1_stm64p1,au4_nc_size,rateVC4XC[2],stmrate[1])
        
        QS_090_Set_PM_Mode(self, zq_stm64_idx1, "ALL", "DISABLED", "BOTH","ALL",stm_size) 
       
        self.stop_tps_block(NE1.id,"PM", "5-2-8-49")
        
        self.start_tps_block(NE1.id,"PM","5-2-8-50")
        
        print("\n******************************************************************************")
        print("\nSETUP VC4-16C GROUP ON STM64 FACILITY USING ED-STM64 COMMAND AND CREATE CROSS-CONNECTION ")
        print("\n******************************************************************************\n")
        
        E_HOAU4NC = "AU416C"
        E_HOVC4NC = "VC416C"
        au4_nc_size = E_HOAU4NC
        vc4_nc_size = E_HOVC4NC
        stmrate = [E_STM16,E_STM64]
        rateVC4XC = [4,16,64,1]
        zq_au416c_idx1 = "{}{}-{}-{}".format(stmrate[1],E_HOAU4NC,NE1_stmnp1,TX_MEASURE_CH)
        zq_au416c_idx2 = "{}{}-{}-{}".format(stmrate[1],E_HOAU4NC,NE1_stm64p1,RX_MEASURE_CH)
        
        QS_070_Setup_VC_Conc(self, NE1_stmnp1,au4_nc_size,rateVC4XC[0],stmrate[1])
        
        QS_070_Setup_VC_Conc(self, NE1_stm64p1,au4_nc_size,rateVC4XC[0],stmrate[1])
        
        QS_060_Create_HO_XC(self,vc4_nc_size,zq_au416c_idx1,zq_au416c_idx2)
                        
        '''
        Configure ONT_P1 port to VC4 mapping
        '''
        
        ONT1.get_set_tx_bit_rate(ONT1_P1, E_STM64)
        
        ONT1.get_set_rx_bit_rate(ONT1_P1, E_STM64)
        
        ONT1.get_set_rx_channel_mapping_size(ONT1_P1, "VC4_16C")
        
        ONT1.get_set_tx_channel_mapping_size(ONT1_P1, "VC4_16C")
        
        ONT1.get_set_tx_measure_channel(ONT1_P1,TX_MEASURE_CH)
        
        ONT1.get_set_rx_measure_channel(ONT1_P1,RX_MEASURE_CH)
        
        ONT1.get_set_clock_reference_source(ONT1_P1, "RX")

        ONT1.get_set_laser_status(ONT1_P1, "ON")

        # ONT1.get_set_background_channels_fill_mode(ONT1_P1, "FIX")
        
        time.sleep(E_WAIT)
        
        print("\n******************************************************************************")
        print("\n VERIFY THAT FOR AN UNPROVISIONED STM64 FACILITY AID THE RTRV-PM COMMAND IS DENIED ")
        print("\n******************************************************************************\n")
        
        zq_isprov = "NO"
        zq_issetmode = "UNKNOWN"
        zq_au416c_idx1 = "{}{}-{}-{}".format(stmrate[1],au4_nc_size,"1-1-24-100",TX_MEASURE_CH)
        zq_locn = "ALL"
        zq_period = "BOTH"
        zq_counter_type = "ALL"
        zq_dir = "ALL"
            
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_au416c_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,vc4_nc_size)
        
        print("\n******************************************************************************")
        print("\n       SET PMMODE ON TO CREATE REGISTERS FOR STM64 VC4-16C FACILITIES                  ")
        print("\n******************************************************************************\n")
        
        zq_au416c_idx1 = "{}{}-{}-{}".format(stmrate[1],au4_nc_size,NE1_stmnp1,TX_MEASURE_CH)
             
        QS_100_Edit_VCn_POM_EGPOM(self,au4_nc_size,zq_au416c_idx1,E_POM, E_EGPOM)
        
        QS_080_Set_PM_Mode_AUXXC(self,vc4_nc_size,zq_au416c_idx1, "ALL", "ON", "BOTH")
        
        print("\n******************************************************************************")
        print("\n       CHECK PMMODE STATE IS ON FOR VC4-16C REGISTERS                            ")
        print("\n******************************************************************************\n")
        
        QS_100_Check_PM_Mode(self, zq_au416c_idx1, "ALL", "BOTH","ALL",vc4_nc_size)
        
        print("\n******************************************************************************")
        print("\n VERIFY THAT FOR AN UNPROVISIONED STM64 VC4-16C FACILITY AID THE RTRV-PM COMMAND IS DENIED ")
        print("\n******************************************************************************\n")
        
        zq_isprov = "YES"
        zq_issetmode = "ON"
            
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_au416c_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,vc4_nc_size)
        
        print("\n******************************************************************************")
        print("\n SET PM MODE TO DISABLE FOR STM64 VC4-16C AND VERIFY NO PARAMETERS ARE RETRIEVED FOR PM COUNTERS")
        print("\n******************************************************************************\n")
        
        QS_080_Set_PM_Mode_AUXXC(self,vc4_nc_size,zq_au416c_idx1, "ALL", "DISABLED", "BOTH")
        
        zq_isprov = "YES"
        zq_issetmode = "DISABLED"
        zq_stm64_idx1 = "STM64-{}".format(NE1_stmnp1)
        
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_au416c_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,vc4_nc_size)
        
        QS_050_Delete_HO_XC(self,E_HOVC4NC,zq_au416c_idx1,zq_au416c_idx2)
        
        au4_nc_size = "AU4"
            
        QS_070_Setup_VC_Conc(self, NE1_stmnp1,au4_nc_size,rateVC4XC[2],stmrate[1])
        
        QS_070_Setup_VC_Conc(self, NE1_stm64p1,au4_nc_size,rateVC4XC[2],stmrate[1])
        
        QS_090_Set_PM_Mode(self, zq_stm64_idx1, "ALL", "DISABLED", "BOTH","ALL",stm_size) 
       
        self.stop_tps_block(NE1.id,"PM", "5-2-8-50")
        
        self.start_tps_block(NE1.id,"PM","5-2-8-51")
        
        print("\n******************************************************************************")
        print("\nSETUP VC4-64C GROUP ON STM64 FACILITY USING ED-STM64 COMMAND AND CREATE CROSS-CONNECTION ")
        print("\n******************************************************************************\n")
        
        E_HOAU4NC = "AU464C"
        E_HOVC4NC = "VC464C"
        au4_nc_size = E_HOAU4NC
        vc4_nc_size = E_HOVC4NC
        stmrate = [E_STM16,E_STM64]
        rateVC4XC = [4,16,64,1]
        zq_au464c_idx1 = "{}{}-{}-{}".format(stmrate[1],E_HOAU4NC,NE1_stmnp1,TX_MEASURE_CH)
        zq_au464c_idx2 = "{}{}-{}-{}".format(stmrate[1],E_HOAU4NC,NE1_stm64p1,RX_MEASURE_CH)
        
        QS_070_Setup_VC_Conc(self, NE1_stmnp1,au4_nc_size,rateVC4XC[3],stmrate[1])
        
        QS_070_Setup_VC_Conc(self, NE1_stm64p1,au4_nc_size,rateVC4XC[3],stmrate[1])
        
        QS_060_Create_HO_XC(self,vc4_nc_size,zq_au464c_idx1,zq_au464c_idx2)
                        
        '''
        Configure ONT_P1 port to VC4 mapping
        '''
        
        ONT1.get_set_tx_bit_rate(ONT1_P1, E_STM64)
        
        ONT1.get_set_rx_bit_rate(ONT1_P1, E_STM64)
        
        ONT1.get_set_rx_channel_mapping_size(ONT1_P1, "VC4_64C")
        
        ONT1.get_set_tx_channel_mapping_size(ONT1_P1, "VC4_64C")
        
        ONT1.get_set_tx_measure_channel(ONT1_P1,TX_MEASURE_CH)
        
        ONT1.get_set_rx_measure_channel(ONT1_P1,RX_MEASURE_CH)
        
        ONT1.get_set_clock_reference_source(ONT1_P1, "RX")

        ONT1.get_set_laser_status(ONT1_P1, "ON")

        # ONT1.get_set_background_channels_fill_mode(ONT1_P1, "FIX")
        
        time.sleep(E_WAIT)
        
        print("\n******************************************************************************")
        print("\n VERIFY THAT FOR AN UNPROVISIONED STM64 VC4-64 FACILITY AID THE RTRV-PM COMMAND IS DENIED ")
        print("\n******************************************************************************\n")
        
        zq_isprov = "NO"
        zq_issetmode = "UNKNOWN"
        zq_au464c_idx1 = "{}{}-{}-{}".format(stmrate[1],au4_nc_size,"1-1-24-100",TX_MEASURE_CH)
        zq_locn = "ALL"
        zq_period = "BOTH"
        zq_counter_type = "ALL"
        zq_dir = "ALL"
            
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_au464c_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,vc4_nc_size)
        
        print("\n******************************************************************************")
        print("\n       SET PMMODE ON TO CREATE REGISTERS FOR STM64 VC4-64C FACILITIES                  ")
        print("\n******************************************************************************\n")
        
        zq_au464c_idx1 = "{}{}-{}-{}".format(stmrate[1],au4_nc_size,NE1_stmnp1,TX_MEASURE_CH)
             
        QS_100_Edit_VCn_POM_EGPOM(self,au4_nc_size,zq_au464c_idx1,E_POM, E_EGPOM)
        
        QS_080_Set_PM_Mode_AUXXC(self,vc4_nc_size,zq_au464c_idx1, "ALL", "ON", "BOTH")
        
        print("\n******************************************************************************")
        print("\n       CHECK PMMODE STATE IS ON FOR VC4-64C REGISTERS                            ")
        print("\n******************************************************************************\n")
        
        QS_100_Check_PM_Mode(self, zq_au464c_idx1, "ALL", "BOTH","ALL",vc4_nc_size)
        
        print("\n******************************************************************************")
        print("\n VERIFY THAT FOR AN UNPROVISIONED STM64 VC4-64C FACILITY AID THE RTRV-PM COMMAND IS DENIED ")
        print("\n******************************************************************************\n")
        
        zq_isprov = "YES"
        zq_issetmode = "ON"
            
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_au464c_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,vc4_nc_size)
        
        print("\n******************************************************************************")
        print("\n SET PM MODE TO DISABLE FOR STM64 VC4-64C AND VERIFY NO PARAMETERS ARE RETRIEVED FOR PM COUNTERS")
        print("\n******************************************************************************\n")
        
        QS_080_Set_PM_Mode_AUXXC(self,vc4_nc_size,zq_au464c_idx1, "ALL", "DISABLED", "BOTH")
        
        zq_isprov = "YES"
        zq_issetmode = "DISABLED"
        zq_stm64_idx1 = "STM64-{}".format(NE1_stmnp1)
        
        QS_080_Get_PM_Counter_Check(self,zq_issetmode,zq_isprov, zq_au464c_idx1,zq_counter_type, zq_locn, zq_period,zq_dir,vc4_nc_size)
        
        QS_050_Delete_HO_XC(self,E_HOVC4NC,zq_au464c_idx1,zq_au464c_idx2)
        
        au4_nc_size = "AU4"
            
        QS_070_Setup_VC_Conc(self, NE1_stmnp1,au4_nc_size,rateVC4XC[2],stmrate[1])
        
        QS_070_Setup_VC_Conc(self, NE1_stm64p1,au4_nc_size,rateVC4XC[2],stmrate[1])
        
        QS_090_Set_PM_Mode(self, zq_stm64_idx1, "ALL", "DISABLED", "BOTH","ALL",stm_size) 
       
        self.stop_tps_block(NE1.id,"PM", "5-2-8-51")
        
        def test_cleanup(self):
            '''
            test Cleanup Section implementation
            insert CleanUp code for your test below
            '''
        ONT1.deinit_instrument(ONT1_P1)

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
    NE1_S1=NE1.get_preset("S1")
    NE1_S2=NE1.get_preset("S2")
   
    ONT1=InstrumentONT('ONT1', CTEST.kenvironment)
    ONT1_P1="P1"
    
    TAG_RATE="STM64_10XANY10G"
    
    CTEST.add_eqpt(NE1)
    CTEST.add_eqpt(ONT1)

    # Run Test main flow
    # Please don't touch this code
    CTEST.run()
