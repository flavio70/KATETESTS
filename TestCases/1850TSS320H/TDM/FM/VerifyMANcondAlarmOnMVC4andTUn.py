#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: This test verifies the reporting/clearing of MAN condition for MVC4,
:field Description: MVC4TU3 and MVC4TU12 facilities. For each block of 3x128 MVC4 one 
:field Description: facility of each type is chosen. On it the presence/absence of alarm is verified. 
:field Topology: 7
:field Dependency:
:field Lab: SVT
:field TPS: FM__5-2-10-1
:field TPS: FM__5-2-11-1
:field TPS: FM__5-2-12-1
:field RunSections: 10101
:field Author: tosima 

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import *
import time
import string
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
    E_DPRINT = 7    
    
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


def QS_010_No_MAN_presence(zq_run, zq_fac):

    zq_tl1_res=NE1.tl1.do("RTRV-COND-{}::ALL:::MAN;".format(zq_fac.upper()))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    dprint(NE1.tl1.get_last_outcome(),1)
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        zq_size=zq_msg.get_cmd_response_size()
        if zq_size == 0:
            dprint("OK\tNo MAN condition alarms found for M{}s".format(zq_fac.upper()),2)
            zq_run.add_success(NE1, "No MAN condition alarms found for M{}s".format(zq_fac.upper()),"0.0", "Alarm Check")
        else:
            dprint("KO\tCondition MAN Alarm found on some M{}s".format(zq_fac.upper()),2)
            zq_run.add_failure(NE1,"TL1 COMMAND","0.0", "Condition MAN Alarm found on some M{}s".format(zq_fac.upper()),"Alarms check "+ QS_000_Print_Line_Function())
            dprint(NE1.tl1.get_last_outcome(),2)

    return

def QS_020_Set_Fac_Status(zq_run, zq_slot, zq_fac_type, zq_fac_pos, zq_status):

    zq_filter=TL1check()
    if zq_status == 'OOS':
        zq_filter.add_pst(zq_status+"-MA")
    if zq_status == 'IS':
        zq_filter.add_pst(zq_status+"-NR")

    if zq_fac_type == "VC4":
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-1&&-384:::::{};".format(zq_slot, zq_status))
    else:
        if zq_fac_type == "LOVC3":
            zq_tl1_res=NE1.tl1.do("ED-TU3::MVC4TU3-{}-{}-1&&-3:::::{};".format(zq_slot, str(zq_fac_pos), zq_status))
        else:
            if zq_fac_type == "LOVC12":
                zq_tl1_res=NE1.tl1.do("ED-TU12::MVC4TU12-{}-{}-1&&-3-1&&-7-1&&-3:::::{};".format(zq_slot, str(zq_fac_pos), zq_status))
                
            
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    dprint(NE1.tl1.get_last_outcome(),1)
    zq_cmd=zq_msg.get_cmd_status()
    '''
    Wait for all FACILITIES status change reporting
    '''
    if zq_fac_type == "VC4":
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_slot, str(zq_fac_pos)),zq_filter)
    else:
        if zq_fac_type == "LOVC3":
            NE1.tl1.do_until("RTRV-TU3::MVC4TU3-{}-{}-3;".format(zq_slot, str(zq_fac_pos)),zq_filter)
        else:
            if zq_fac_type == "LOVC12":
                NE1.tl1.do_until("RTRV-TU12::MVC4TU12-{}-{}-3-7-3;".format(zq_slot, str(zq_fac_pos)),zq_filter)

    return zq_cmd


def QS_030_Verify_Fac_MAN_Alarm(zq_run, zq_cmd, zq_fac_type, zq_check_num):

    if zq_cmd == (True,'COMPLD'):
        zq_tl1_res=NE1.tl1.do("RTRV-COND-{}::ALL:::MAN;".format(zq_fac_type))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_man_nbr = 0
            zq_aid_list=zq_msg.get_cmd_aid_list()
            for zq_i in range(0, zq_check_num):
                zq_man = zq_msg.get_cmd_attr_value(zq_aid_list[zq_i], 2)
                if zq_man[0] == 'MAN':
                    zq_man_nbr += 1
                    dprint("zq_man_nbr:="+str(zq_man_nbr),1)
                    
        if zq_man_nbr == zq_check_num:
            dprint("OK\tMAN Condition verification successful for {} facility : Exp [{}] - Rcv [{}]".format(zq_fac_type, zq_check_num, zq_man_nbr),2)
            zq_run.add_success(NE1, "MAN Condition verification successful for {} facility : Exp [{}] - Rcv [{}]".format(zq_fac_type, zq_check_num, zq_man_nbr),"0.0", "MAN CONDITION CHECK")
        else:
            dprint("KO\tMAN Condition verification failure for {} facility : Exp [{}] - Rcv [{}]".format(zq_fac_type, zq_check_num, zq_man_nbr),2)
            zq_run.add_failure(NE1,"MAN Condition verification failure for {} facility : Exp [{}] - Rcv [{}]".format(zq_fac_type, zq_check_num, zq_man_nbr),"0.0", "MAN Condition verification failure: Exp [{}] - Rcv [{}]".format(E_MAX_VC4,zq_man_nbr),"MAN CONDITION CHECK "+ QS_000_Print_Line_Function())
            
    else:
        zq_run.add_failure(NE1,"TL1 COMMAND","0.0", "TL1 COMMAND FAILURE","TL1 COMMAND "+ QS_000_Print_Line_Function())
        dprint("TL1 COMMAND FAILURE",2)
        dprint(NE1.tl1.get_last_outcome(),1)

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
        VERIFY DETECTION OF MAN CONDITION ALARM FOR MVC4 FACILITIES
        '''
        print("\n*******************************************************************")
        print("\n    VERIFY DETECTION OF MAN CONDITION ALARM FOR MVC4 FACILITIES    ")
        print("\n*******************************************************************")
        
        self.start_tps_block(NE1.id,"FM", "5-2-10-1")

        E_LO_MTX = "MXH60GLO"

        E_MAX_VC4 = 384
        E_VC3_X_VC4 = 3
        E_VC12_X_VC4 = 63

        E_VC4_1 = 87      # <129
        E_VC4_2 = 199      # 129<x<257
        E_VC4_3 = 289     # 256<x<385

        zq_mtxlo_slot = NE1_M1
        
        
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

        #Verify no MAN alarm condition is present
        QS_010_No_MAN_presence(self, "VC4")
                
        #Set all MVC4 to OOS status and verifies all MAN condition are reported
        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "VC4", E_MAX_VC4, "OOS")
        time.sleep(30)
        QS_030_Verify_Fac_MAN_Alarm(self, zq_cmd, "VC4", E_MAX_VC4)

        #Set all MVC4 to IS status and verifies all MAN condition are cleared
        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "VC4", E_MAX_VC4, "IS")
        QS_010_No_MAN_presence(self, "VC4")

        self.stop_tps_block(NE1.id,"FM", "5-2-10-1")

        '''
        VERIFY DETECTION OF MAN CONDITION ALARM FOR MVC4TU3 FACILITIES
        '''
        print("\n*******************************************************************")
        print("\n   VERIFY DETECTION OF MAN CONDITION ALARM FOR MVC4TU3 FACILITIES  ")
        print("\n   OF MVC4: {}-{}-{}                                               ".format(E_VC4_1,E_VC4_2,E_VC4_3))
        print("\n*******************************************************************")
        self.start_tps_block(NE1.id,"FM", "5-2-11-1")

        #Verify no MAN alarm condition is present
        QS_010_No_MAN_presence(self, "LOVC3")
        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC3", E_VC4_1, "OOS")
        QS_030_Verify_Fac_MAN_Alarm(self, zq_cmd, "LOVC3", E_VC3_X_VC4)
        #Set MVC4TU3 to IS status and verifies all MAN condition are cleared
        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC3", E_VC4_1, "IS")
        QS_010_No_MAN_presence(self, "LOVC3")

        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC3", E_VC4_2, "OOS")
        QS_030_Verify_Fac_MAN_Alarm(self, zq_cmd, "LOVC3", E_VC3_X_VC4)
        #Set all MVC4TU3 to IS status and verifies all MAN condition are cleared
        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC3", E_VC4_2, "IS")
        QS_010_No_MAN_presence(self, "LOVC3")

        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC3", E_VC4_3, "OOS")
        QS_030_Verify_Fac_MAN_Alarm(self, zq_cmd, "LOVC3", E_VC3_X_VC4)
        #Set all MVC4TU3 to IS status and verifies all MAN condition are cleared
        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC3", E_VC4_3, "IS")
        QS_010_No_MAN_presence(self, "LOVC3")

        self.stop_tps_block(NE1.id,"FM", "5-2-11-1")

        '''
        VERIFY DETECTION OF MAN CONDITION ALARM FOR MVC4TU12 FACILITIES
        '''
        print("\n*******************************************************************")
        print("\n   VERIFY DETECTION OF MAN CONDITION ALARM FOR MVC4TU12 FACILITIES ")
        print("\n   OF MVC4: {}-{}-{}                                               ".format(E_VC4_1,E_VC4_2,E_VC4_3))
        print("\n*******************************************************************")
        self.start_tps_block(NE1.id,"FM", "5-2-12-1")
        '''
        Change 3xMVC4 structure to 63xTU12
        '''
        zq_filter=TL1check()
        zq_filter.add_field('LOSTRUCT', '63xTU12')
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_1))
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_2))
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,E_VC4_3))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_3),zq_filter)

        #Verify no MAN alarm condition is present
        QS_010_No_MAN_presence(self, "LOVC12")
        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC12", E_VC4_1, "OOS")
        QS_030_Verify_Fac_MAN_Alarm(self, zq_cmd, "LOVC12", E_VC12_X_VC4)
        #Set MVC4TU3 to IS status and verifies all MAN condition are cleared
        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC12", E_VC4_1, "IS")
        QS_010_No_MAN_presence(self, "LOVC12")

        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC12", E_VC4_2, "OOS")
        QS_030_Verify_Fac_MAN_Alarm(self, zq_cmd, "LOVC12", E_VC12_X_VC4)
        #Set all MVC4TU3 to IS status and verifies all MAN condition are cleared
        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC12", E_VC4_2, "IS")
        QS_010_No_MAN_presence(self, "LOVC12")

        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC12", E_VC4_3, "OOS")
        QS_030_Verify_Fac_MAN_Alarm(self, zq_cmd, "LOVC12", E_VC12_X_VC4)
        #Set all MVC4TU3 to IS status and verifies all MAN condition are cleared
        zq_cmd = QS_020_Set_Fac_Status(self, zq_mtxlo_slot, "LOVC12", E_VC4_3, "IS")
        QS_010_No_MAN_presence(self, "LOVC12")

        '''
        Change 3xMVC4 structure back to 3xTU3
        '''
        zq_filter=TL1check()
        zq_filter.add_field('LOSTRUCT', '3xTU3')
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_1))
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_2))
        zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mtxlo_slot,E_VC4_3))
        NE1.tl1.do_until("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,E_VC4_3),zq_filter)


        self.stop_tps_block(NE1.id,"FM", "5-2-12-1")




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