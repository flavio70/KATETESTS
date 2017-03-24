#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description:  Verify the denial of facility protection group creation with loopback on STM16 on MRSOE 
:field Topology: 7
:field Dependency:
:field Lab: SVT
:field TPS:  MSP__5-2-8-12
:field TPS: 
:field RunSections: 11111
:field Author: selvaa

"""

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.instrumentONT     import InstrumentONT
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.facility_tl1      import *
import time
from inspect import currentframe
from kateUsrLibs.selvaa.SelvaggiMspLib import *

E_WAIT = 2

E_WTR_TIME = 300

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


    def test_setup(self):
        '''
        test Setup Section implementation
        insert general SetUp code for your test below
        '''
                
        #ONT1.init_instrument(ONT1_P1)
        #ONT2.init_instrument(ONT2_P1)
        
        
    def test_body(self):
        '''
        test Body Section implementation
        insert Main body code for your test below
        '''
        MSP__RATE=ExtractRate(MSP_RATE)  
               
        NE1_WORK_FACILITY='%s-%s'%(MSP__RATE,NE1_WORK)
        NE1_PROT_FACILITY='%s-%s'%(MSP__RATE,NE1_PROT)
        NE1_S1_FACILITY='%s-%s'%(NE1_S1_RATE,NE1_S1) 
 
        NE2_WORK_FACILITY='%s-%s'%(MSP__RATE,NE2_WORK)
        NE2_PROT_FACILITY='%s-%s'%(MSP__RATE,NE2_PROT)
        NE2_S1_FACILITY='%s-%s'%(NE2_S1_RATE,NE2_S1) 
 
        self.start_tps_block(NE1.id,"MSP", "5-2-8-12")
        
        
        #ONT configuration
        '''
        ONT1.get_set_tx_bit_rate(ONT1_P1, NE1_S1_RATE)
        ONT2.get_set_tx_bit_rate(ONT2_P1, NE2_S1_RATE)
        
        ONT1.get_set_rx_bit_rate(ONT1_P1, NE1_S1_RATE)
        ONT2.get_set_rx_bit_rate(ONT2_P1, NE2_S1_RATE)
        
        ONT1.get_set_rx_channel_mapping_size(ONT1_P1, "VC4")
        ONT2.get_set_rx_channel_mapping_size(ONT2_P1, "VC4")
        
        ONT1.get_set_tx_channel_mapping_size(ONT1_P1, "VC4")
        ONT2.get_set_tx_channel_mapping_size(ONT2_P1, "VC4")

        ONT1.get_set_laser_status(ONT1_P1, "ON")
        ONT2.get_set_laser_status(ONT2_P1, "ON")

        ONT1.get_set_clock_reference_source(ONT1_P1, "RX")
        ONT2.get_set_clock_reference_source(ONT2_P1, "RX")
        
        ONT1.get_set_background_channels_fill_mode(ONT1_P1, "FIX")
        ONT2.get_set_background_channels_fill_mode(ONT2_P1, "FIX")
        
        time.sleep(E_WAIT)
        
        #ONT configuration end
        '''
        
        NE1.tl1.do("ACT-USER::admin:::Alcatel1;")
    
        NE1.tl1.do("ED-%s::%s:::::OOS;"%(MSP__RATE,NE1_WORK_FACILITY))
        
        NE1.tl1.do("OPR-LPBK-%s::%s:::,,,FACILITY;"%(MSP__RATE,NE1_WORK_FACILITY))

        commandResult = NE1.tl1.do("ENT-FFP-%s::FFP%s::::PTYPE=LINEAR,RVRTV=Y,WKG=%s,PROTN=%s,PSDIRN=BI;"%(MSP__RATE,NE1_PROT_FACILITY,NE1_WORK_FACILITY,NE1_PROT_FACILITY),policy="DENY")        
        
        if commandResult:
           
           msg=TL1message(NE1.tl1.get_last_outcome())
    
           CheckErrorCode(self, NE1, msg, "SNVS", PrintLineFunction())

        commandResult = NE1.tl1.do("ENT-FFP-%s::FFP%s::::PTYPE=LINEAR,RVRTV=Y,WKG=%s,PROTN=%s,PSDIRN=BI;"%(MSP__RATE,NE1_WORK_FACILITY,NE1_PROT_FACILITY,NE1_WORK_FACILITY),policy="DENY")        
        
        if commandResult:
           
           msg=TL1message(NE1.tl1.get_last_outcome())
           
           CheckErrorCode(self, NE1, msg, "SNVS", PrintLineFunction())
        
        NE1.tl1.do("RLS-LPBK-%s::%s:::,,,FACILITY;"%(MSP__RATE,NE1_WORK_FACILITY))
        
        NE1.tl1.do("OPR-LPBK-%s::%s:::,,,TERMINAL;"%(MSP__RATE,NE1_WORK_FACILITY))

        commandResult = NE1.tl1.do("ENT-FFP-%s::FFP%s::::PTYPE=LINEAR,RVRTV=Y,WKG=%s,PROTN=%s,PSDIRN=BI;"%(MSP__RATE,NE1_PROT_FACILITY,NE1_WORK_FACILITY,NE1_PROT_FACILITY),policy="DENY")        
        
        if commandResult:
           
           msg=TL1message(NE1.tl1.get_last_outcome())
           
           CheckErrorCode(self, NE1, msg, "SNVS", PrintLineFunction())

        commandResult = NE1.tl1.do("ENT-FFP-%s::FFP%s::::PTYPE=LINEAR,RVRTV=Y,WKG=%s,PROTN=%s,PSDIRN=BI;"%(MSP__RATE,NE1_WORK_FACILITY,NE1_PROT_FACILITY,NE1_WORK_FACILITY),policy="DENY")        
        
        if commandResult:

           msg=TL1message(NE1.tl1.get_last_outcome())

           CheckErrorCode(self, NE1, msg, "SNVS", PrintLineFunction())
        
        NE1.tl1.do("RLS-LPBK-%s::%s:::,,,TERMINAL;"%(MSP__RATE,NE1_WORK_FACILITY))
        
        NE1.tl1.do("ED-%s::%s:::::IS;"%(MSP__RATE,NE1_WORK_FACILITY))
        
        NE1.tl1.do("ENT-FFP-%s::FFP%s::::PTYPE=LINEAR,RVRTV=Y,WKG=%s,PROTN=%s,PSDIRN=BI;"%(MSP__RATE,NE1_PROT_FACILITY,NE1_WORK_FACILITY,NE1_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
         
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PTYPE","LINEAR",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"RVRTV","Y",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"WKG",NE1_WORK_FACILITY,PrintLineFunction())
           
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PROTN",NE1_PROT_FACILITY,PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PSDIRN","BI",PrintLineFunction())
        
        #Deprovisioning    
        
        NE1.tl1.do("DLT-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
    
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckIfIsNotConfigured(self, NE1, msg, "FFP%s"%NE1_PROT_FACILITY, PrintLineFunction())
        
        NE1.tl1.do("RTRV-AU4::%sAU4-%s-1&&-%s;"%(MSP__RATE,NE1_WORK,Au4InStmN(MSP__RATE,"AU4")))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        cmd=msg.get_cmd_status()
    
        if cmd == (True,'COMPLD'):
            
            aidList=msg.get_cmd_aid_list()
            
            if aidList!=None:
            
                for i in range (0, len(aidList)):
                                    
                   CheckPrimaryState(self, NE1, msg, aidList[i], "IS-NR",PrintLineFunction())
               
        NE1.tl1.do("RTRV-AU4::%sAU4-%s-1&&-%s;"%(MSP__RATE,NE1_PROT,Au4InStmN(MSP__RATE,"AU4")))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        cmd=msg.get_cmd_status()
    
        if cmd == (True,'COMPLD'):
            
            aidList=msg.get_cmd_aid_list()
            
            if aidList!=None:
            
                for i in range (0, len(aidList)):
                                    
                   CheckPrimaryState(self, NE1, msg, aidList[i], "IS-NR",PrintLineFunction())
               
        NE1.tl1.do("CANC-USER;")
        
        self.stop_tps_block(NE1.id,"MSP", "5-2-8-12")
        

    def test_cleanup(self):
        '''
        
        test Cleanup Section implementation
        insert CleanUp code for your test below
        '''

        #ONT1.deinit_instrument(ONT1_P1)
        #ONT2.deinit_instrument(ONT2_P1)
        
        
    def dut_cleanup(self):
        '''
        DUT CleanUp Section implementation
        insert DUT CleanUp code for your test below
        '''


#Please don't change the code below#
if __name__ == "__main__":
    #initializing the Test object instance, do not remove
    CTEST = Test(__file__)

    #initializing all local variable and constants used by Test object
    NE1 = Eqpt1850TSS320('NE1', CTEST.kenvironment)
    NE1_S1=NE1.get_preset("S1")
    NE1_WORK=NE1.get_preset("WORK")
    NE1_PROT=NE1.get_preset("PROT")
    NE1_S1_RATE=NE1.get_preset("S1_RATE")
    
    NE2 = Eqpt1850TSS320('NE2', CTEST.kenvironment)
    NE2_S1=NE2.get_preset("S1")
    NE2_WORK=NE2.get_preset("WORK")
    NE2_PROT=NE2.get_preset("PROT")
    NE2_S1_RATE=NE2.get_preset("S1_RATE")
    
    ONT1=InstrumentONT('ONT1', CTEST.kenvironment)
    ONT1_P1="P1"
    
    ONT2=InstrumentONT('ONT2', CTEST.kenvironment)
    ONT2_P1="P1"
    
    MSP_RATE="STM16_MRSOE"
    
    CTEST.add_eqpt(NE1)
    CTEST.add_eqpt(NE2)

    # Run Test main flow
    # Please don't touch this code
    CTEST.run()
