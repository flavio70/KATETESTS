#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: Verify the retrieving of LOPOOL information when MVC4 are
:field Description: UNUSED, USEDBYHOCC and USEDBYLOVCGMEM and CONSTATE parameter 
:field Description: in RTRV-LOPOOL command is set to ALL, UNUSED, USEDBYHOCC
:field Topology: 8 
:field Dependency:
:field Lab: SVT
:field TPS: FM__5-2-7-1
:field RunSections: 10101 
:field Author: tosima

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.instrumentONT     import InstrumentONT
#from katelibs.instrumentIXIA     import InstrumentIXIA
#from katelibs.instrumentSPIRENT  import InstrumentSPIRENT
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import * 
import time
import math


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
        E_MAX_VC4=65
        E_LOA_MVC4=56
        E_LOA_MVC4TU3=E_LOA_MVC4*3
        E_LOA_MVC4TU12=E_LOA_MVC4TU3*21

        E_START_VC4=1
        E_VCGVC4_MAXMBR = 20
        E_START_VC3 = E_START_VC4 + E_VCGVC4_MAXMBR + 5
        E_VCGVC3_MAXMBR = 10
        E_START_VC12 = E_START_VC3 + E_VCGVC3_MAXMBR + 5
        E_VCGVC12_MAXMBR = 63

        E_HO_CONN = E_VCGVC4_MAXMBR +1  #connections are 1 less !
        
        E_TIMEOUT=180
        
        E_LO_MTX = "MXH60GLO"
        '''
        Retrieve parameters from preset
        '''
        self.start_tps_block(NE1.id,"FM", "5-2-7-1")
        zq_stm64_1=NE1.get_preset("S1")
        zq_mtxlo_slot=NE1.get_preset("M1")
        zq_pp10ms_slot=NE1.get_preset("MS1")
        
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
        Verify all MVC4 are UNUSED
        '''
        zq_tl1_res=NE1.tl1.do("RTRV-LOPOOL;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_unused_num = 0
            for zq_i in range(1,E_MAX_VC4):
                zq_mvc4_use=zq_msg.get_cmd_attr_value("MVC4-{}-{}".format(zq_mtxlo_slot,zq_i), "CONSTATE")
                if zq_mvc4_use == 'UNUSED':
                    zq_unused_num +=1
                
            if zq_unused_num == E_LOA_MVC4:
                dprint("OK\tAll MVC4 are UNUSED",2)
                self.add_success(NE1, "MVC4 CONSTATE","0.0", "All MVC4 are UNUSED")
            else:
                dprint("KO\tNot all MVC4 are UNUSED",2)
                self.add_failure(NE1, "MVC4 CONSTATE","0.0", "Not all MVC4 are UNUSED","Not all MVC4 are UNUSED")
            
                
        '''
        Create VCGVC4 group with E_VCGVC4_MAXMBR and verify again all MVC4 are still UNUSED
        '''
        zq_tl1_res=NE1.tl1.do("ENT-VCG::VCG-{}-{}::::MAXMBR={},VCGTYPE=VC4;".format(zq_pp10ms_slot,E_START_VC4,E_VCGVC4_MAXMBR))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tVCG-{}-{} group with {} members created".format(zq_pp10ms_slot,E_START_VC4,E_VCGVC4_MAXMBR),2)
            self.add_success(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group with {} member created".format(zq_pp10ms_slot,E_START_VC4,E_VCGVC4_MAXMBR))
            
            zq_tl1_res=NE1.tl1.do("RTRV-LOPOOL;")
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            dprint(NE1.tl1.get_last_outcome(),1)
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                dprint("OK\tLOPOOL successfully retrieved",2)
                self.add_success(NE1, "LOPOOL successfully retrieved","0.0", "LOPOOL successfully retrieved")
                zq_unused_num = 0
                for zq_i in range(1,E_MAX_VC4):
                    zq_mvc4_use=zq_msg.get_cmd_attr_value("MVC4-{}-{}".format(zq_mtxlo_slot,zq_i), "CONSTATE")
                    if zq_mvc4_use == 'UNUSED':
                        zq_unused_num +=1
                    
                if zq_unused_num == E_LOA_MVC4:
                    dprint("OK\tAll MVC4 are UNUSED",2)
                    self.add_success(NE1, "MVC4 CONSTATE","0.0", "All MVC4 are UNUSED")
                else:
                    dprint("KO\tNot all MVC4 are UNUSED",2)
                    self.add_failure(NE1, "MVC4 CONSTATE","0.0", "Not all MVC4 are UNUSED","Not all MVC4 are UNUSED")
            else:
                dprint("KO\tLOPOOL retrieve failure",2)
                self.add_failure(NE1, "TL1 COMMAND","0.0", "LOPOOL retrieve failure", "LOPOOL retrieve failure")
        
        else:        
            dprint("KO\tVCG-{}-{} group with {} member creation failed".format(zq_pp10ms_slot,E_START_VC4,E_VCGVC4_MAXMBR),2)
            self.add_failure(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group with {} member creation failed".format(zq_pp10ms_slot,E_START_VC4,E_VCGVC4_MAXMBR),"TL1 command fail")
        
        
        '''
        Create E_HO_CONN VC4 cross-connection and verify MVC4 are USEDBYHOCC 
        '''
        
        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")
        for zq_i in range (1,E_HO_CONN):
            zq_tl1_res=NE1.tl1.do("ENT-CRS-VC4::STM64AU4-{}-{},LOPOOL-1-1-1;".format(zq_stm64_1,zq_i))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                zq_xc_list.append(''.join(zq_msg.get_cmd_aid_list()))
                dprint("OK\tCross-connection creation successfull {}".format(zq_xc_list[zq_i]),2)
                self.add_success(NE1, "Cross-connection creation successfull {}".format(zq_xc_list[zq_i]),"0.0", "Cross-connection creation successfull")
            else:
                dprint("KO\tCross-connection creation failure",2)
                self.add_failure(NE1, "TL1 COMMAND","0.0", "Cross-connection creation failure","TL1 command fail")
                
        
        '''
        Create VCGVC3 group with E_VCGVC3_MAXMBR and verify that (E_VCGVC3_MAXMBR div 3) MVC4 are USEDBYLOVCGMEM 
        '''
        zq_tl1_res=NE1.tl1.do("ENT-VCG::VCG-{}-{}::::MAXMBR={},VCGTYPE=LOVC3;".format(zq_pp10ms_slot,E_START_VC3,E_VCGVC3_MAXMBR))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tVCG-{}-{} group with {} members created".format(zq_pp10ms_slot,E_START_VC3,E_VCGVC3_MAXMBR),2)
            self.add_success(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group with {} member created".format(zq_pp10ms_slot,E_START_VC4,E_VCGVC4_MAXMBR))
        else:
            dprint("KO\tVCG-{}-{} group with {} member creation failed".format(zq_pp10ms_slot,E_START_VC4,E_VCGVC4_MAXMBR),2)
            self.add_failure(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group with {} member creation failed".format(zq_pp10ms_slot,E_START_VC4,E_VCGVC4_MAXMBR),"TL1 command fail")

        '''
        Create VCGVC12 group with E_VCGVC12_MAXMBR and verify that (E_VCGVC12_MAXMBR div 63) MVC4 are USEDBYLOVCGMEM 
        '''
        zq_tl1_res=NE1.tl1.do("ENT-VCG::VCG-{}-{}::::MAXMBR={},VCGTYPE=LOVC12;".format(zq_pp10ms_slot,E_START_VC12,E_VCGVC12_MAXMBR))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tVCG-{}-{} group with {} members created".format(zq_pp10ms_slot,E_START_VC12,E_VCGVC12_MAXMBR),2)
            self.add_success(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group with {} member created".format(zq_pp10ms_slot,E_START_VC12,E_VCGVC12_MAXMBR))
        else:
            dprint("KO\tVCG-{}-{} group with {} member creation failed".format(zq_pp10ms_slot,E_START_VC12,E_VCGVC12_MAXMBR),2)
            self.add_failure(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group with {} member creation failed".format(zq_pp10ms_slot,E_START_VC12,E_VCGVC12_MAXMBR),"TL1 command fail")


        '''
        Check MVC4 are in the correct CONSTATE when retrieved with ALL parameter:
        '''
        zq_tl1_res=NE1.tl1.do("RTRV-LOPOOL::::::CONSTATE=ALL;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_unused_num = 0
            zq_usedbyhocc_num = 0
            zq_usedbylovcgmem_num = 0
            for zq_i in range(1,E_MAX_VC4):
                zq_mvc4_use=zq_msg.get_cmd_attr_value("MVC4-{}-{}".format(zq_mtxlo_slot,zq_i), "CONSTATE")
                if zq_mvc4_use == 'UNUSED':
                    zq_unused_num +=1
                if zq_mvc4_use == 'USEDBYHOCC':
                    zq_usedbyhocc_num +=1
                if zq_mvc4_use == 'USEDBYLOVCGMEM':
                    zq_usedbylovcgmem_num +=1
            
            zq_mvc4_num=zq_unused_num+zq_usedbyhocc_num+zq_usedbylovcgmem_num
            if zq_mvc4_num == E_LOA_MVC4:
                dprint("OK\tAll MVC4 are reported",2)
                self.add_success(NE1, "MVC4 CONSTATE ALL","0.0", "All MVC4 are reported")
            else:
                dprint("KO\tNot all MVC4 are reported",2)
                self.add_failure(NE1, "MVC4 CONSTATE ALL","0.0", "Not all MVC4 are reported","Not all MVC4 are reported")
            
            '''
            Check number of USEDBYLOVCGMEM MVC4:
            expected value=E_VCGVC3_MAXMBR*21+E_VCGVC12_MAXMBR) // 63
            '''
            if (zq_usedbylovcgmem_num == math.ceil(((E_VCGVC3_MAXMBR*21+E_VCGVC12_MAXMBR) / 63))):
                dprint("OK\tMVC4 in CONSTATE=USEDBYLOVCGMEM is correct",2)
                self.add_success(NE1, "MVC4 CONSTATE CHECK","0.0", "MVC4 in CONSTATE=USEDBYLOVCGMEM is correct")
            else:
                dprint("KO\tMVC4 in USEDBYLOVCGMEM exp: {} ".format(((E_VCGVC3_MAXMBR*21+E_VCGVC12_MAXMBR) // 63)),2)
                dprint("\tMVC4 in USEDBYLOVCGMEM act: {} ".format(zq_usedbylovcgmem_num),2)
                self.add_failure(NE1, "MVC4 CONSTATE CHECK","0.0", "MVC4 in CONSTATE=USEDBYLOVCGMEM is wrong","MVC4 in CONSTATE=USEDBYLOVCGMEM is wrong")
                
            '''
            Check number of USEDBYHOCC MVC4:
            expected value=E_HO_CONN-1
            '''
            if zq_usedbyhocc_num == E_HO_CONN -1:
                dprint("OK\tMVC4 in CONSTATE=USEDBYHOCC is correct",2)
                self.add_success(NE1, "MVC4 CONSTATE CHECK","0.0", "MVC4 in CONSTATE=USEDBYHOCC is correct")
            else:
                dprint("KO\tMVC4 in CONSTATE=USEDBYHOCC exp: {} ".format(E_HO_CONN-1,2))
                dprint("\tMVC4 in CONSTATE=USEDBYHOCC act: {} ".format(zq_usedbyhocc_num,2))
                self.add_failure(NE1, "MVC4 CONSTATE CHECK","0.0", "MVC4 in CONSTATE=USEDBYHOCC is wrong","MVC4 in CONSTATE=USEDBYHOCC is wrong")
                
            '''
            Check number of UNUSED MVC4:
            expected value= E_LOA_MVC4-E_HO_CONN-1-math.ceil(((E_VCGVC3_MAXMBR*21+E_VCGVC12_MAXMBR) / 63)))
            '''
            if zq_unused_num == (E_LOA_MVC4-(E_HO_CONN-1)-math.ceil(((E_VCGVC3_MAXMBR*21+E_VCGVC12_MAXMBR) / 63))):
                dprint("OK\tMVC4 in CONSTATE=UNUSED is correct",2)
                self.add_success(NE1, "MVC4 CONSTATE=ALL CHECK","0.0", "MVC4 in CONSTATE=UNUSED is correct")
            else:
                dprint("KO\tMVC4 in CONSTATE=UNUSED exp: {} ".format(E_LOA_MVC4-(E_HO_CONN-1)-math.ceil(((E_VCGVC3_MAXMBR*21+E_VCGVC12_MAXMBR) / 63))),2)
                dprint("\tMVC4 in CONSTATE=USEDBYHOCC act: {} ".format(zq_unused_num),2)
                self.add_failure(NE1, "MVC4 CONSTATE=ALL CHECK","0.0", "MVC4 in CONSTATE=UNUSED is wrong","MVC4 in CONSTATE=UNUSED is wrong")
             
        


        '''
        Check only MVC4 UNUSED are retrieved when CONSTATE=UNUSED:
        '''
        zq_tl1_res=NE1.tl1.do("RTRV-LOPOOL::::::CONSTATE=UNUSED;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_unused_num = 0
            for zq_i in range(1,E_MAX_VC4):
                zq_mvc4_use=zq_msg.get_cmd_attr_value("MVC4-{}-{}".format(zq_mtxlo_slot,zq_i), "CONSTATE")
                if zq_mvc4_use == 'UNUSED':
                    zq_unused_num +=1

            if zq_unused_num == (E_LOA_MVC4-(E_HO_CONN-1)-math.ceil(((E_VCGVC3_MAXMBR*21+E_VCGVC12_MAXMBR) / 63))):
                dprint("OK\tMVC4 in CONSTATE=UNUSED is correct",2)
                self.add_success(NE1, "MVC4 CONSTATE=UNUSED CHECK","0.0", "MVC4 in CONSTATE=UNUSED is correct")
            else:
                dprint("KO\tMVC4 in CONSTATE=UNUSED exp: {} ".format(E_LOA_MVC4-(E_HO_CONN-1)-math.ceil(((E_VCGVC3_MAXMBR*21+E_VCGVC12_MAXMBR) / 63))),2)
                dprint("\tMVC4 in CONSTATE=USEDBYHOCC act: {} ".format(zq_unused_num),2)
                self.add_failure(NE1, "MVC4 CONSTATE=UNUSED CHECK","0.0", "MVC4 in CONSTATE=UNUSED is wrong","MVC4 in CONSTATE=UNUSED is wrong")



        '''
        Check only MVC4 USEBYHOCC are retrieved when CONSTATE=USEDBYHOCC:
        '''
        zq_tl1_res=NE1.tl1.do("RTRV-LOPOOL::::::CONSTATE=USEDBYHOCC;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_usedbyhocc_num = 0
            for zq_i in range(1,E_MAX_VC4):
                zq_mvc4_use=zq_msg.get_cmd_attr_value("MVC4-{}-{}".format(zq_mtxlo_slot,zq_i), "CONSTATE")
                if zq_mvc4_use == 'USEDBYHOCC':
                    zq_usedbyhocc_num +=1

            if zq_usedbyhocc_num == E_HO_CONN -1:
                dprint("OK\tMVC4 in CONSTATE=USEDBYHOCC is correct",2)
                self.add_success(NE1, "MVC4 CONSTATE=USEDBYHOCC CHECK","0.0", "MVC4 in CONSTATE=USEDBYHOCC is correct")
            else:
                dprint("KO\tMVC4 in CONSTATE=USEDBYHOCC exp: {} ".format(E_HO_CONN-1),2)
                dprint("\tMVC4 in CONSTATE=USEDBYHOCC act: {} ".format(zq_usedbyhocc_num),2)
                self.add_failure(NE1, "MVC4 CONSTATE=USEDBYHOCC CHECK","0.0", "MVC4 in CONSTATE=USEDBYHOCC is wrong","MVC4 in CONSTATE=USEDBYHOCC is wrong")


        
        '''
        Delete E_HO_CONN VC4 cross-connection  
        '''
        if len(zq_xc_list) == 1:
            zq_tl1_res=NE1.tl1.do("RTRV-CRS-VC4::ALL;")
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            if zq_msg.get_cmd_response_size() > 0:
                zq_xc_list=zq_msg.get_cmd_aid_list()
                zq_xc_list.insert(0,'EMPTY,EMPTY')
        
        for zq_i in range (1,len(zq_xc_list)):
            zq_tl1_res=NE1.tl1.do("DLT-CRS-VC4::{};".format(zq_xc_list[zq_i]))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                dprint("OK\tCross-connection deletion successfull {}".format(zq_xc_list[zq_i]),2)
                self.add_success(NE1, "Cross-connection deletion successfull {}".format(zq_xc_list[zq_i]),"0.0", "Cross-connection deletion successfull")
            else:    
                dprint("KO\tCross-connection deletion failed {}".format(zq_xc_list[zq_i]),2)
                self.add_failure(NE1, "TL1 COMMAND","0.0", "Cross-connection deletion failure","TL1 command fail")
        
        
        '''
        Delete VCGVC4 group
        '''
        zq_tl1_res=NE1.tl1.do("DLT-VCG::VCG-{}-{};".format(zq_pp10ms_slot,E_START_VC4))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tVCG-{}-{} group successfully deleted".format(zq_pp10ms_slot,E_START_VC4),2)
            self.add_success(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group successfully deleted".format(zq_pp10ms_slot,E_START_VC4))
        else:
            dprint("KO\tVCG-{}-{} group deletion failure".format(zq_pp10ms_slot,E_START_VC4),2)
            self.add_failure(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group deletion failure".format(zq_pp10ms_slot,E_START_VC4),"TL1 command failure")
            
        '''
        Delete VCGVC3 group
        '''
        zq_tl1_res=NE1.tl1.do("DLT-VCG::VCG-{}-{};".format(zq_pp10ms_slot,E_START_VC3))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tVCG-{}-{} group successfully deleted".format(zq_pp10ms_slot,E_START_VC3),2)
            self.add_success(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group successfully deleted".format(zq_pp10ms_slot,E_START_VC3))
        else:
            dprint("KO\tVCG-{}-{} group deletion failure".format(zq_pp10ms_slot,E_START_VC3),2)
            self.add_failure(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group deletion failure".format(zq_pp10ms_slot,E_START_VC3),"TL1 command failure")

        '''
        Delete VCGVC12 group
        '''
        zq_tl1_res=NE1.tl1.do("DLT-VCG::VCG-{}-{};".format(zq_pp10ms_slot,E_START_VC12))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            dprint("OK\tVCG-{}-{} group successfully deleted".format(zq_pp10ms_slot,E_START_VC12),2)
            self.add_success(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group successfully deleted".format(zq_pp10ms_slot,E_START_VC12))
        else:
            dprint("KO\tVCG-{}-{} group deletion failure".format(zq_pp10ms_slot,E_START_VC12),2)
            self.add_failure(NE1, "TL1 COMMAND","0.0", "VCG-{}-{} group deletion failure".format(zq_pp10ms_slot,E_START_VC12),"TL1 command failure")

        
        self.stop_tps_block(NE1.id,"FM", "5-2-7-1")


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
    CTEST.add_eqpt(NE1)
    
    # Run Test main flow
    # Please don't touch this code
    CTEST.run()

