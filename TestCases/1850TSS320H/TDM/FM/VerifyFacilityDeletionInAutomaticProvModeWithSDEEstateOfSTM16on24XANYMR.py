#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description:This test is to verify the deletion of STMn facility that is a consequence of sub-module deletion.
:field Topology: 62
:field Dependency: NA
:field Lab: SVT
:field TPS: FM__5-1-9-20
:field RunSections: 10101
:field Author: tosima

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import *
import time
import math
from inspect import currentframe
from kateUsrLibs.tosima.FmLib import *


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

        all runSections will be executed if running Test without input parameters
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
       
        global NE1_S1
                
        self.start_tps_block(NE1.id,"FM", "5-1-9-20")

        zq_tmp = NE1_S1.split("-")
        zq_tmp.pop()
        NE1_S1 = "-".join(zq_tmp)
        zq_temp  = TAG_RATE.split("_")
        zq_rate  = zq_temp[0]
        zq_board = zq_temp[1]
        zq_mod_list = list()

        if (zq_board == E_10GSO) or \
            zq_board == E_10GSOE:
            zq_mod_type = "XFP"
            zq_mod = E_10GSO_MOD
            zq_mod_num = E_10GSO_MOD_NUM
            zq_range = 1

        if zq_board == E_10XANY10G:
            zq_mod_type = "XFP"
            zq_mod = E_10XANY10G_MOD
            zq_mod = E_10XANY10G_MOD_NUM
            zq_range = "1&&-{}".format(E_10XANY10G_MOD_NUM)

        if zq_board == E_24XANYMR:
            zq_mod_type = "SFP"
            zq_mod = E_24XANYMR_STMx_MOD
            zq_mod = E_24XANYMR_STMx_MOD_NUM
            zq_range = "1&&-{}".format(E_24XANYMR_STMx_MOD_NUM)

        if zq_board == E_10XANY:
            zq_mod_type = "SFP"
            zq_mod = E_10XANY_STMx_MOD
            zq_mod_num = E_10XANY_STMx_MOD_NUM
            zq_range = "1&&-{}".format(E_10XANY_STMx_MOD_NUM)

        if zq_board == E_MRSOE:
            zq_mod_type = "SFP"
            zq_mod = E_MRSOE_STMx_MOD
            zq_mod_num = E_MRSOE_STMx_MOD_NUM
            zq_range = "1&&-{}".format(E_MRSOE_STMx_MOD_NUM)

        if zq_rate == "STM1":
            zq_ss = "-11" 
            
        if zq_rate == "STM4":
            zq_ss = "-41" 

        if zq_rate == "STM16":
            zq_ss = "-161"

        if zq_rate == "STM64":
            zq_ss = "-641"

        zq_tl1_res=NE1.tl1.do("RTRV-EQPT::{}-{}-{};".format(zq_mod_type, NE1_S1, zq_range))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            for zq_i in zq_mod:
                zq_aid = zq_msg.get_cmd_aid_list()[zq_i-1]
                zq_attr_list = zq_msg.get_cmd_attr_values("{}".format(zq_aid))
                zq_act_type = 'NEQ'
                if zq_mod_type in str(zq_aid):
                    zq_act_type = zq_attr_list[0]['PROVISIONEDTYPE']
                    if zq_ss in zq_act_type:
                        zq_mod_list.append("{},{}".format(zq_aid,zq_act_type))
        
        dprint(zq_mod_list,2)
        
        if len(zq_mod_list) != 0:
            
            
            
            print("\n*******************************************************************")
            print("\tCHECK SECONDARY STATE IS NOT SDEE")
            print("*******************************************************************")
            # VERIFY SECONDARY STATE DOES NOT CONTAINS SDEE
            #
            for zq_i in zq_mod_list:
                zq_tmp=zq_i.split(",")
                zq_tmp=zq_tmp[0]
                zq_tmp=zq_tmp.split("-")
                zq_i=zq_tmp[4]
                zq_tl1_res=NE1.tl1.do("RTRV-{}::{}-{}-{};".format(zq_rate, zq_rate, NE1_S1, zq_i))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    zq_sst=zq_msg.get_cmd_sst("{}-{}-{}".format(zq_rate, NE1_S1, zq_i))
                    if ("SDEE" not in str(zq_sst)):
                        dprint("OK\t Initial SST is correct: {}".format(zq_sst),2)
                        self.add_success(NE1, 
                                         "SST VERIFY",
                                         "0.0", 
                                         "Initial SST is correct: {}".format(zq_sst))
                    else:
                        dprint("KO\t Initial SST is wrong: {}".format(zq_sst),2)
                        self.add_failure(NE1,
                                         "SST VERIFY",
                                         "0.0",
                                         "SST Verify Error",
                                         "Initial SST is wrong: {}".format(zq_sst)+QS_000_Print_Line_Function())
                else:
                    dprint("KO\t [RTRV-{}::{}-{}-{}] command failed.".format(zq_rate, zq_rate, NE1_S1, zq_i),2)
                    self.add_failure(NE1,
                                     "EQUIPMENT RETRIEVAL",
                                     "0.0",
                                     "Equipment Retrieval Error",
                                     "[RTRV-{}::{}-{}-{}] command failed.".format(zq_rate, zq_rate, NE1_S1, zq_i)+QS_000_Print_Line_Function())
    
            print("\n*******************************************************************")
            print("\tCREATE VC4 CROSS-CONNECTIONS")
            print("*******************************************************************")
            # CREATE VC4 CROSS-CONNECTION
            # ENT-CRS-VC4:[TID]:FROM,TO:[CTAG]::[CCT]:[CKTID=]
            #
            for zq_i in zq_mod_list:
                zq_tmp=zq_i.split(",")
                zq_tmp=zq_tmp[0]
                zq_tmp=zq_tmp.split("-")
                zq_i=zq_tmp[4]
                zq_from = "{}AU4-{}-{}-1".format(zq_rate, NE1_S1, zq_i)
                zq_to = "{}AU4-{}-{}-2".format(zq_rate, NE1_S1, zq_i)
                zq_cct = "2WAY"
                if zq_rate == "STM1":
                    zq_to = zq_from
                    zq_cct = "1WAY"
                zq_tl1_res=NE1.tl1.do("ENT-CRS-VC4::{},{}:::{};".format(zq_from, zq_to, zq_cct))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    dprint("OK\t Cross-connection from {} to {} creation successful".format(zq_from, zq_to),2)
                    self.add_success(NE1, 
                                     "CROSS-CONNECTION CREATION",
                                     "0.0", 
                                     "Cross-connection from {} to {} creation successful".format(zq_from, zq_to))
                else:
                    dprint("KO\t Cross-connection from {} to {} creation failed".format(zq_from, zq_to),2)
                    self.add_failure(NE1,
                                     "CROSS-CONNECTION CREATION",
                                     "0.0",
                                     "Cross-Connection Creation Error",
                                     "Cross-connection from {} to {} creation failed".format(zq_from, zq_to)+QS_000_Print_Line_Function())
    
            
            print("\n*******************************************************************")
            print("\tCHECK SECONDARY STATE IS SDEE")
            print("*******************************************************************")
            # VERIFY SECONDARY STATE CONTAINS SDEE
            #
            for zq_i in zq_mod_list:
                zq_tmp=zq_i.split(",")
                zq_tmp=zq_tmp[0]
                zq_tmp=zq_tmp.split("-")
                zq_i=zq_tmp[4]
                zq_tl1_res=NE1.tl1.do("RTRV-{}::{}-{}-{};".format(zq_rate, zq_rate, NE1_S1, zq_i))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    zq_sst=zq_msg.get_cmd_sst("{}-{}-{}".format(zq_rate, NE1_S1, zq_i))
                    if ("SDEE"  in str(zq_sst)):
                        dprint("OK\t SST is correct: {}".format(zq_sst),2)
                        self.add_success(NE1, 
                                         "SST VERIFY",
                                         "0.0", 
                                         "SST is correct: {}".format(zq_sst))
                    else:
                        dprint("KO\t SST is wrong: {}".format(zq_sst),2)
                        self.add_failure(NE1,
                                         "SST VERIFY",
                                         "0.0",
                                         "SST Verify Error",
                                         "SST is wrong: {}".format(zq_sst)+QS_000_Print_Line_Function())
                else:
                    dprint("KO\t [RTRV-{}::{}-{}-{}] command failed.".format(zq_rate, zq_rate, NE1_S1, zq_i),2)
                    self.add_failure(NE1,
                                     "EQUIPMENT RETRIEVAL",
                                     "0.0",
                                     "Equipment Retrieval Error",
                                     "[RTRV-{}::{}-{}-{}] command failed.".format(zq_rate, zq_rate, NE1_S1, zq_i)+QS_000_Print_Line_Function())
            
            print("\n*******************************************************************")
            print("\tVERIFY STM SUB-MODULE CANNOT BE DELETED WHEN SERVICE IS PROVIDED")
            print("*******************************************************************")
            for zq_i in zq_mod_list:
                zq_tmp=zq_i.split(",")
                zq_tmp=zq_tmp[0]
                zq_tmp=zq_tmp.split("-")
                zq_i=zq_tmp[4]
                zq_tl1_res=NE1.tl1.do("RMV-EQPT::{}-{}-{}:::FRCD;".format(zq_mod_type, NE1_S1, zq_i))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    dprint("OK\t {}-{}-{} correctly removed.".format(zq_mod_type, NE1_S1, zq_i),2)
                    self.add_success(NE1, 
                                     "EQUIPMENT REMOVAL",
                                     "0.0", 
                                     "{}-{}-{} correctly removed.".format(zq_mod_type, NE1_S1, zq_i))
                    zq_tl1_res=NE1.tl1.do("DLT-EQPT::{}-{}-{};".format(zq_mod_type, NE1_S1, zq_i),policy="DENY")
                    zq_msg=TL1message(NE1.tl1.get_last_outcome())
                    zq_cmd=zq_msg.get_cmd_status()
                    if zq_cmd == (True,'DENY'):
                        zq_error_frame = str(zq_msg.get_cmd_error_frame())
                        zq_res = ("SNVS" in zq_error_frame) and ("Equipment entity is in SDEE state" in zq_error_frame)
                        if zq_res:
                            dprint("OK\t {}-{}-{} correctly not deleted.".format(zq_mod_type, NE1_S1, zq_i),2)
                            self.add_success(NE1, 
                                             "EQUIPMENT DELETION",
                                             "0.0", 
                                             "{}-{}-{} correctly not deleted.".format(zq_mod_type, NE1_S1, zq_i))
                        else:
                            dprint("KO\t {}-{}-{} wrongly deleted.".format(zq_mod_type, NE1_S1, zq_i),2)
                            self.add_failure(NE1,
                                             "EQUIPMENT DELETION",
                                             "0.0",
                                             "Equipment Deletion Error",
                                             "{}-{}-{} wrongly deleted.".format(zq_mod_type, NE1_S1, zq_i)+QS_000_Print_Line_Function())
                    else:
                        dprint("KO\t [DLT-EQPT::{}-{}-{}] command failed".format(zq_mod_type, NE1_S1, zq_i),2)
                        self.add_failure(NE1,
                                         "EQUIPMENT DELETION",
                                         "0.0",
                                         "Equipment Deletion Error",
                                         "[DLT-EQPT::{}-{}-{}] command failed".format(zq_mod_type, NE1_S1, zq_i)+QS_000_Print_Line_Function())
    
                else:
                    dprint("KO\t [RMV-EQPT::{}-{}-{}:::FRCD] command failed.".format(zq_mod_type, NE1_S1, zq_i),2)
                    self.add_failure(NE1,
                                     "EQUIPMENT REMOVAL",
                                     "0.0",
                                     "Equipment Removal Error",
                                     "[RMV-EQPT::{}-{}-{}:::FRCD] command failed.".format(zq_mod_type, NE1_S1, zq_i)+QS_000_Print_Line_Function())
    
            
            print("\n*******************************************************************")
            print("\tDELETE VC4 CROSS-CONNECTIONS")
            print("*******************************************************************")
            # DELETE VC4 CROSS-CONNECTION
            # DLT-CRS-VC4:[TID]:FROM,TO:[CTAG]::[CCT]:[CKTID=]
            #
            for zq_i in zq_mod_list:
                zq_tmp=zq_i.split(",")
                zq_tmp=zq_tmp[0]
                zq_tmp=zq_tmp.split("-")
                zq_i=zq_tmp[4]
                zq_from = "{}AU4-{}-{}-1".format(zq_rate, NE1_S1, zq_i)
                zq_to = "{}AU4-{}-{}-2".format(zq_rate, NE1_S1, zq_i)
                zq_cct = "2WAY"
                if zq_rate == "STM1":
                    zq_to = zq_from
                    zq_cct = "1WAY"
                zq_tl1_res=NE1.tl1.do("DLT-CRS-VC4::{},{}:::{};".format(zq_from,zq_to,zq_cct))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    dprint("OK\t Cross-connection from {} to {} deletion successful".format(zq_from, zq_to),2)
                    self.add_success(NE1, 
                                     "CROSS-CONNECTION DELETION",
                                     "0.0", 
                                     "Cross-connection from {} to {} deletion successful".format(zq_from, zq_to))
                else:
                    dprint("KO\t Cross-connection from {} to {} deletion failed".format(zq_from, zq_to),2)
                    self.add_failure(NE1,
                                     "CROSS-CONNECTION DELETION",
                                     "0.0",
                                     "Cross-Connection Deletion Error",
                                     "Cross-connection from {} to {} deletion failed".format(zq_from, zq_to)+QS_000_Print_Line_Function())
    
            print("\n*******************************************************************")
            print("\tVERIFY STM SUB-MODULE CAN BE DELETED AFTER SERVICES ARE REMOVED")
            print("*******************************************************************")
            for zq_i in zq_mod_list:
                zq_tmp=zq_i.split(",")
                zq_tmp=zq_tmp[0]
                zq_tmp=zq_tmp.split("-")
                zq_i=zq_tmp[4]
                zq_tl1_res=NE1.tl1.do("DLT-EQPT::{}-{}-{};".format(zq_mod_type, NE1_S1, zq_i))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    dprint("OK\t {}-{}-{} correctly deleted.".format(zq_mod_type, NE1_S1, zq_i),2)
                    self.add_success(NE1, 
                                     "EQUIPMENT DELETION",
                                     "0.0", 
                                     "{}-{}-{} correctly deleted.".format(zq_mod_type, NE1_S1, zq_i))
                    print("\n*******************************************************************")
                    print("\tVERIFY STM IS OOS-AUMA,DSBLD&UAS")
                    print("*******************************************************************")
                    zq_tl1_res=NE1.tl1.do("RTRV-{}::{}-{}-{};".format(zq_rate, zq_rate, NE1_S1, zq_i))
                    zq_msg=TL1message(NE1.tl1.get_last_outcome())
                    zq_cmd=zq_msg.get_cmd_status()
                    if zq_cmd == (True,'COMPLD'):
                        zq_pst = zq_msg.get_cmd_pst("{}-{}-{}".format(zq_rate, NE1_S1, zq_i))
                        zq_sst = zq_msg.get_cmd_sst("{}-{}-{}".format(zq_rate, NE1_S1, zq_i))
                        if ("OOS-AUMA" in str(zq_pst)) and \
                           ("DSBLD" in str(zq_sst)) and \
                           ("UAS" in str(zq_sst)):
                            dprint("OK\t {}-{}-{} automatically deleted".format(zq_rate, NE1_S1, zq_i),2)
                            self.add_success(NE1, 
                                             "STMx DELETION",
                                             "0.0", 
                                             "{}-{}-{} automatically deleted".format(zq_rate, NE1_S1, zq_i))
                        else:
                            dprint("KO\t {}-{}-{} not automatically deleted.".format(zq_rate, NE1_S1, zq_i),2)
                            self.add_failure(NE1,
                                             "STMx DELETION",
                                             "0.0",
                                             "STMx Deletion Error",
                                             "{}-{}-{} not automatically deleted.".format(zq_rate, NE1_S1, zq_i)+QS_000_Print_Line_Function())
                    else:
                        dprint("KO\t [RTRV-{}::{}-{}-{}] command failed.".format(zq_rate, zq_rate, NE1_S1, zq_i),2)
                        self.add_failure(NE1,
                                         "EQUIPMENT RETRIEVAL",
                                         "0.0",
                                         "Equipment Retrieval Error",
                                         "[RTRV-{}::{}-{}-{}] command failed.".format(zq_rate, zq_rate, NE1_S1, zq_i)+QS_000_Print_Line_Function())
                else:
                    dprint("KO\t [DLT-EQPT::{}-{}-{}] command failed.".format(zq_mod_type, NE1_S1, zq_i),2)
                    self.add_failure(NE1,
                                     "EQUIPMENT DELETION",
                                     "0.0",
                                     "Equipment Deletion Error",
                                     "[DLT-EQPT::{}-{}-{}] command failed.".format(zq_mod_type, NE1_S1, zq_i)+QS_000_Print_Line_Function())
    
    
            print("\n*******************************************************************")
            print("\tPROVISION THE DELETED MODULES")
            print("*******************************************************************")
            for zq_i in zq_mod_list:
                zq_tmp=zq_i.split(",")
                zq_prov_type = zq_tmp[1]
                zq_tmp=zq_tmp[0]
                zq_tmp=zq_tmp.split("-")
                zq_i=zq_tmp[4]
                zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{}-{}::::PROVISIONEDTYPE={};".format(zq_mod_type, NE1_S1, zq_i, zq_prov_type))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                if zq_cmd == (True,'COMPLD'):
                    dprint("OK\t {}-{}-{} correctly equipped.".format(zq_mod_type, NE1_S1, zq_i),2)
                    self.add_success(NE1, 
                                     "EQUIPMENT PROVISIONING",
                                     "0.0", 
                                     "{}-{}-{} correctly equipped".format(zq_mod_type, NE1_S1, zq_i))
                else:
                    dprint("KO\t {}-{}-{} wrongly not equipped.".format(zq_mod_type, NE1_S1, zq_i),2)
                    self.add_failure(NE1,
                                     "EQUIPMENT PROVISIONING",
                                     "0.0",
                                     "Equipment Provisioning Error",
                                     "{}-{}-{} wrongly not equipped.".format(zq_mod_type, NE1_S1, zq_i)+QS_000_Print_Line_Function())
         
        else:
            dprint("KO\t No modules found [{}-{}-{}]".format(zq_mod_type, NE1_S1, zq_range),2)
            self.add_failure(NE1,
                             "VERIFY EQUIPPED MODULES",
                             "0.0",
                             "No modules found",
                             "No modules found [{}-{}-{}]".format(zq_mod_type, NE1_S1, zq_range)+QS_000_Print_Line_Function())
            
        self.stop_tps_block(NE1.id,"FM", "5-1-9-20")

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
    NE1_S1=NE1.get_preset("S1")
    
    
    TAG_RATE="STM16_24XANYMR"
    
    CTEST.add_eqpt(NE1)


    # Run Test main flow
    # Please don't touch this code
    CTEST.run()
