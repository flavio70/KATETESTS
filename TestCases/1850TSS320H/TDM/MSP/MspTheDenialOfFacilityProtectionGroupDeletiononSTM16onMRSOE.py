#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description:  Verify the denial of facility protection group on STM16 facility on MRSOE 
:field Topology: 7
:field Dependency:
:field Lab: SVT
:field TPS:  MSP__5-2-2-12
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

E_WTR_TIME = 5


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
                
        ONT1.init_instrument(ONT1_P1)
        ONT2.init_instrument(ONT2_P1)
        
        
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
 
        self.start_tps_block(NE1.id,"MSP", "5-2-2-12")
        
        
        #ONT configuration
       
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
        
        NE1.tl1.do("ACT-USER::admin:::Alcatel1;")
    
        NE2.tl1.do("ACT-USER::admin:::Alcatel1;")
                    
        NE1.tl1.do("ED-%s::%s::::ALSENB=N;"%(NE1_S1_RATE,NE1_S1_FACILITY))        
        
        NE1.tl1.do("ED-%s::%s::::ALSENB=N;"%(MSP__RATE,NE1_WORK_FACILITY))        
        
        NE1.tl1.do("ED-%s::%s::::ALSENB=N;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        NE2.tl1.do("ED-%s::%s::::ALSENB=N;"%(NE2_S1_RATE,NE2_S1_FACILITY))        
        
        NE2.tl1.do("ED-%s::%s::::ALSENB=N;"%(MSP__RATE,NE2_WORK_FACILITY))        
        
        NE2.tl1.do("ED-%s::%s::::ALSENB=N;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        time.sleep(15)
        
        NE1.tl1.do("ENT-FFP-%s::FFP%s::::PTYPE=LINEAR,RVRTV=Y,WKG=%s,PROTN=%s,PSDIRN=BI;"%(MSP__RATE,NE1_PROT_FACILITY,NE1_WORK_FACILITY,NE1_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
         
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PTYPE","LINEAR",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"RVRTV","Y",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"WKG",NE1_WORK_FACILITY,PrintLineFunction())
           
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PROTN",NE1_PROT_FACILITY,PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PSDIRN","BI",PrintLineFunction())
        
        NE2.tl1.do("ENT-FFP-%s::FFP%s::::PTYPE=LINEAR,RVRTV=Y,WKG=%s,PROTN=%s,PSDIRN=BI;"%(MSP__RATE,NE2_PROT_FACILITY,NE2_WORK_FACILITY,NE2_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PTYPE","LINEAR",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"RVRTV","Y",PrintLineFunction())
          
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"WKG",NE2_WORK_FACILITY,PrintLineFunction())
           
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PROTN",NE2_PROT_FACILITY,PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PSDIRN","BI",PrintLineFunction())
                
        NE1.tl1.do("ENT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE1_S1_RATE,NE1_S1,MSP__RATE,NE1_WORK))        
            
        NE2.tl1.do("ENT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE2_S1_RATE,NE2_S1,MSP__RATE,NE2_WORK))        
        
        time.sleep(E_WAIT)
        
        CheckONTAlarm(self, NE1, ONT1, ONT1_P1, "",PrintLineFunction())

        CheckONTAlarm(self, NE2, ONT2, ONT2_P1, "",PrintLineFunction())
        
        NE1.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE1_PROT_FACILITY))        

        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckCondition (self, NE1, msg, "", "FFP%s"%(NE1_PROT_FACILITY),PrintLineFunction())
        
        NE2.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckCondition (self, NE2, msg, "", "FFP%s"%(NE2_PROT_FACILITY),PrintLineFunction())
        
        #Switch caused by failure 
        
        NE1.tl1.event_collection_start()
        
        NE2.tl1.event_collection_start()
        
        NE1.tl1.do("ED-%s::%s::::ALSENB=N_OFF;"%(MSP__RATE,NE1_WORK_FACILITY))        
      
        time.sleep(10)
        
        NE1.tl1.event_collection_stop()
        
        NE2.tl1.event_collection_stop()
        
        CheckEvent (self, NE1, "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), "WKSWPR-FE,SC")
    
        CheckEvent (self, NE2, "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), "WKSWPR,SC")
    
        CheckONTAlarm(self, NE1, ONT1, ONT1_P1, "",PrintLineFunction())

        CheckONTAlarm(self, NE2, ONT2, ONT2_P1, "",PrintLineFunction())

        NE1.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE1_PROT_FACILITY))        

        msg=TL1message(NE1.tl1.get_last_outcome())
      
        CheckCondition (self, NE1, msg, "WKSWPR-FE", "FFP%s"%(NE1_PROT_FACILITY),PrintLineFunction())
          
        NE2.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
      
        CheckCondition (self, NE2, msg, "WKSWPR", "FFP%s"%(NE2_PROT_FACILITY),PrintLineFunction())
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"ACTIVE","PROTN",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"CURRREQ","SF-FE",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"ACTIVE","PROTN",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"CURRREQ","SF",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PENDREQ","AUTOSWITCH",PrintLineFunction())
        
        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_WORK_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_WORK_FACILITY, "STBYS", PrintLineFunction())

        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_PROT_FACILITY, "WRK", PrintLineFunction())

        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_WORK_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_WORK_FACILITY, "STBYS", PrintLineFunction())

        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE2_PROT_FACILITY, "WRK", PrintLineFunction())

        tl1Res=NE1.tl1.do("DLT-FFP-%s::FFP%s::::CMDMDE=NORM;"%(MSP__RATE,NE1_PROT_FACILITY),policy="DENY")
        
        if (tl1Res==False):
           
           dprint("KO\t FFP%s is unexpectedly deleted %s"%(NE1_PROT_FACILITY,PrintLineFunction()),2)
           self.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","FFP%s is unexpectedly deleted %s"%(NE1_PROT_FACILITY,PrintLineFunction()))
                   
        tl1Res=NE2.tl1.do("DLT-FFP-%s::FFP%s::::CMDMDE=NORM;"%(MSP__RATE,NE2_PROT_FACILITY),policy="DENY")
        
        if (tl1Res==False):
           
           dprint("KO\t FFP%s is unexpectedly deleted %s"%(NE1_PROT_FACILITY,PrintLineFunction()),2)
           self.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","FFP%s is unexpectedly deleted %s"%(NE2_PROT_FACILITY,PrintLineFunction()))
          
        NE1.tl1.event_collection_start()
        
        NE2.tl1.event_collection_start()
        
        NE1.tl1.do("ED-%s::%s::::ALSENB=N;"%(MSP__RATE,NE1_WORK_FACILITY))        
      
        time.sleep(10)
        
        NE1.tl1.event_collection_stop()
        
        NE2.tl1.event_collection_stop()
        
        CheckEvent (self, NE1, "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), "WKSWPR-FE,CL")
    
        CheckEvent (self, NE2, "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), "WKSWPR,CL")
        
        CheckEvent (self, NE1, "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), "WTR-FE,SC")
    
        CheckEvent (self, NE2, "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), "WTR,SC")
    
        CheckONTAlarm(self, NE1, ONT1, ONT1_P1, "",PrintLineFunction())

        CheckONTAlarm(self, NE2, ONT2, ONT2_P1, "",PrintLineFunction())

        NE1.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE1_PROT_FACILITY))        

        msg=TL1message(NE1.tl1.get_last_outcome())
      
        CheckCondition (self, NE1, msg, "WTR-FE", "FFP%s"%(NE1_PROT_FACILITY),PrintLineFunction())
          
        NE2.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
      
        CheckCondition (self, NE2, msg, "WTR", "FFP%s"%(NE2_PROT_FACILITY),PrintLineFunction())
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"ACTIVE","PROTN",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"CURRREQ","WTR-FE",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"ACTIVE","PROTN",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"CURRREQ","WTR",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_WORK_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_WORK_FACILITY, "STBYH", PrintLineFunction())

        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_PROT_FACILITY, "WRK", PrintLineFunction())
        
        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_WORK_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_WORK_FACILITY, "STBYH", PrintLineFunction())

        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_PROT_FACILITY, "WRK", PrintLineFunction())
        
        NE1.tl1.event_collection_start()
        
        NE2.tl1.event_collection_start()
        
        if E_WTR_TIME > 1:

            for minute in range  (1, E_WTR_TIME):
                
                time.sleep(60)
        
                CheckEvent (self, NE1,  "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), None, False)
        
                CheckEvent (self, NE2,  "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), None, False)
                
                dprint("Minuto numero %s"%minute,4)
        
        time.sleep(60)
        
        NE1.tl1.event_collection_stop()
        
        NE2.tl1.event_collection_stop()
        
        CheckEvent (self, NE1,  "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), "WTR-FE,CL")
    
        CheckEvent (self, NE2,  "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), "WTR,CL")
        
        CheckONTAlarm(self, NE1, ONT1, ONT1_P1, "",PrintLineFunction())

        CheckONTAlarm(self, NE2, ONT2, ONT2_P1, "",PrintLineFunction())

        NE1.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE1_PROT_FACILITY))        

        msg=TL1message(NE1.tl1.get_last_outcome())
      
        CheckCondition (self, NE1, msg, "", "FFP%s"%(NE1_PROT_FACILITY),PrintLineFunction())
          
        NE2.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
      
        CheckCondition (self, NE2, msg, "", "FFP%s"%(NE2_PROT_FACILITY),PrintLineFunction())
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"ACTIVE","WKG",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"CURRREQ","NR",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"ACTIVE","WKG",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"CURRREQ","NR",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_WORK_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_WORK_FACILITY, "WRK", PrintLineFunction())

        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_PROT_FACILITY, "STBYH", PrintLineFunction())
        
        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_WORK_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_WORK_FACILITY, "WRK", PrintLineFunction())

        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_PROT_FACILITY, "STBYH", PrintLineFunction())
        
        #Switch caused by failure end
        
        #Manual switch  
        
        ONT1.start_measurement(ONT1_P1)

        ONT2.start_measurement(ONT2_P1)

        NE1.tl1.event_collection_start()
        
        NE2.tl1.event_collection_start()
        
        NE1.tl1.do("OPR-PROTNSW-%s::FFP%s:::MAN::DESTINATION=PROTN;"%(MSP__RATE,NE1_PROT_FACILITY))
        
        time.sleep(2)
        
        ONT1.halt_measurement(ONT1_P1)
        
        ONT2.halt_measurement(ONT2_P1)
        
        NE1.tl1.event_collection_stop()
        
        NE2.tl1.event_collection_stop()
        
        CheckEvent (self, NE1,  "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), "MANWKSWPR,SC")
    
        CheckEvent (self, NE2,  "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), "MANWKSWPR-FE,SC")
    
        CheckONTAlarm(self, NE1, ONT1, ONT1_P1, "",PrintLineFunction(),False,False)

        CheckONTAlarm(self, NE2, ONT2, ONT2_P1, "",PrintLineFunction(),False,False)

        NE1.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE1_PROT_FACILITY))        

        msg=TL1message(NE1.tl1.get_last_outcome())
      
        CheckCondition (self, NE1, msg, "MANWKSWPR", "FFP%s"%(NE1_PROT_FACILITY),PrintLineFunction())
          
        NE2.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
      
        CheckCondition (self, NE2, msg, "MANWKSWPR-FE", "FFP%s"%(NE2_PROT_FACILITY),PrintLineFunction())
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"ACTIVE","PROTN",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"CURRREQ","MAN",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"ACTIVE","PROTN",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"CURRREQ","MAN-FE",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_WORK_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_WORK_FACILITY, "STBYS", PrintLineFunction())

        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_PROT_FACILITY, "WRK", PrintLineFunction())

        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_WORK_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_WORK_FACILITY, "STBYS", PrintLineFunction())

        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE2_PROT_FACILITY, "WRK", PrintLineFunction())

        tl1Res=NE1.tl1.do("DLT-FFP-%s::FFP%s::::CMDMDE=NORM;"%(MSP__RATE,NE1_PROT_FACILITY),policy="DENY")
        
        if (tl1Res==False):
           
           dprint("KO\t FFP%s is unexpectedly deleted %s"%(NE1_PROT_FACILITY,PrintLineFunction()),2)
           self.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","FFP%s is unexpectedly deleted %s"%(NE1_PROT_FACILITY,PrintLineFunction()))
                   
        tl1Res=NE2.tl1.do("DLT-FFP-%s::FFP%s::::CMDMDE=NORM;"%(MSP__RATE,NE2_PROT_FACILITY),policy="DENY")
        
        if (tl1Res==False):
           
           dprint("KO\t FFP%s is unexpectedly deleted %s"%(NE1_PROT_FACILITY,PrintLineFunction()),2)
           self.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","FFP%s is unexpectedly deleted %s"%(NE2_PROT_FACILITY,PrintLineFunction()))
          
        ONT1.start_measurement(ONT1_P1)

        ONT2.start_measurement(ONT2_P1)

        NE1.tl1.event_collection_start()
        
        NE2.tl1.event_collection_start()
        
        NE1.tl1.do("RLS-PROTNSW-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))
        
        time.sleep(2)
        
        ONT1.halt_measurement(ONT1_P1)
        
        ONT2.halt_measurement(ONT2_P1)
        
        NE1.tl1.event_collection_stop()
        
        NE2.tl1.event_collection_stop()
  
        CheckEvent (self, NE1,  "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), "MANWKSWPR,CL")
    
        CheckEvent (self, NE2,  "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), "MANWKSWPR-FE,CL")
        
        CheckONTAlarm(self, NE1, ONT1, ONT1_P1, "",PrintLineFunction(),False,False)

        CheckONTAlarm(self, NE2, ONT2, ONT2_P1, "",PrintLineFunction(),False,False)

        NE1.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE1_PROT_FACILITY))        

        msg=TL1message(NE1.tl1.get_last_outcome())
      
        CheckCondition (self, NE1, msg, "", "FFP%s"%(NE1_PROT_FACILITY),PrintLineFunction())
          
        NE2.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
      
        CheckCondition (self, NE2, msg, "", "FFP%s"%(NE2_PROT_FACILITY),PrintLineFunction())
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"ACTIVE","WKG",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"CURRREQ","NR",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"ACTIVE","WKG",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"CURRREQ","NR",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_WORK_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_WORK_FACILITY, "WRK", PrintLineFunction())

        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_PROT_FACILITY, "STBYH", PrintLineFunction())
        
        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_WORK_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_WORK_FACILITY, "WRK", PrintLineFunction())

        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_PROT_FACILITY, "STBYH", PrintLineFunction())
                
        #Manual switch end
           
        #Switch caused by failure second run
        
        NE1.tl1.event_collection_start()
        
        NE2.tl1.event_collection_start()
        
        NE1.tl1.do("ED-%s::%s::::ALSENB=N_OFF;"%(MSP__RATE,NE1_WORK_FACILITY))        
      
        time.sleep(10)
        
        NE1.tl1.event_collection_stop()
        
        NE2.tl1.event_collection_stop()
        
        CheckEvent (self, NE1,  "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), "WKSWPR-FE,SC")
    
        CheckEvent (self, NE2,  "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), "WKSWPR,SC")
    
        CheckONTAlarm(self, NE1, ONT1, ONT1_P1, "",PrintLineFunction())

        CheckONTAlarm(self, NE2, ONT2, ONT2_P1, "",PrintLineFunction())

        NE1.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE1_PROT_FACILITY))        

        msg=TL1message(NE1.tl1.get_last_outcome())
      
        CheckCondition (self, NE1, msg, "WKSWPR-FE", "FFP%s"%(NE1_PROT_FACILITY),PrintLineFunction())
          
        NE2.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
      
        CheckCondition (self, NE2, msg, "WKSWPR", "FFP%s"%(NE2_PROT_FACILITY),PrintLineFunction())
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"ACTIVE","PROTN",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"CURRREQ","SF-FE",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"ACTIVE","PROTN",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"CURRREQ","SF",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PENDREQ","AUTOSWITCH",PrintLineFunction())
        
        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_WORK_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_WORK_FACILITY, "STBYS", PrintLineFunction())

        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_PROT_FACILITY, "WRK", PrintLineFunction())

        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_WORK_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_WORK_FACILITY, "STBYS", PrintLineFunction())

        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE2_PROT_FACILITY, "WRK", PrintLineFunction())

        tl1Res=NE1.tl1.do("DLT-FFP-%s::FFP%s::::CMDMDE=NORM;"%(MSP__RATE,NE1_PROT_FACILITY),policy="DENY")
        
        if (tl1Res==False):
           
           dprint("KO\t %s Protection group was unexpectedly deleted\n"%aid,2)
           run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","FFP%s is unexpectedly deleted %s"%(NE1_PROT_FACILITY,PrintLineFunction()))
                   
        tl1Res=NE2.tl1.do("DLT-FFP-%s::FFP%s::::CMDMDE=NORM;"%(MSP__RATE,NE2_PROT_FACILITY),policy="DENY")
        
        if (tl1Res==False):
           
           dprint("KO\t %s Protection group was unexpectedly deleted\n"%aid,2)
           run.add_failure(NE1, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","FFP%s is unexpectedly deleted %s"%(NE2_PROT_FACILITY,PrintLineFunction()))
          
        time.sleep(180)
        
        NE1.tl1.event_collection_start()
        
        NE2.tl1.event_collection_start()
        
        NE1.tl1.do("ED-%s::%s::::ALSENB=N;"%(MSP__RATE,NE1_WORK_FACILITY))        
      
        time.sleep(10)
        
        NE1.tl1.event_collection_stop()
        
        NE2.tl1.event_collection_stop()
        
        CheckEvent (self, NE1, "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), "WKSWPR-FE,CL")
    
        CheckEvent (self, NE2, "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), "WKSWPR,CL")
        
        CheckEvent (self, NE1, "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), "WTR-FE,SC")
    
        CheckEvent (self, NE2, "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), "WTR,SC")
    
        CheckONTAlarm(self, NE1, ONT1, ONT1_P1, "",PrintLineFunction())

        CheckONTAlarm(self, NE2, ONT2, ONT2_P1, "",PrintLineFunction())

        NE1.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE1_PROT_FACILITY))        

        msg=TL1message(NE1.tl1.get_last_outcome())
      
        CheckCondition (self, NE1, msg, "WTR-FE", "FFP%s"%(NE1_PROT_FACILITY),PrintLineFunction())
          
        NE2.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
      
        CheckCondition (self, NE2, msg, "WTR", "FFP%s"%(NE2_PROT_FACILITY),PrintLineFunction())
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"ACTIVE","PROTN",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"CURRREQ","WTR-FE",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"ACTIVE","PROTN",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"CURRREQ","WTR",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_WORK_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_WORK_FACILITY, "STBYH", PrintLineFunction())

        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_PROT_FACILITY, "WRK", PrintLineFunction())
        
        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_WORK_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_WORK_FACILITY, "STBYH", PrintLineFunction())

        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_PROT_FACILITY, "WRK", PrintLineFunction())
        
        NE1.tl1.event_collection_start()
        
        NE2.tl1.event_collection_start()
        
        if E_WTR_TIME > 1:

            for minute in range  (1, E_WTR_TIME):
                
                sleepTime= 60         
                
                time.sleep(sleepTime)
        
                CheckEvent (self, NE1, "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), None, False)
        
                CheckEvent (self, NE2, "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), None, False)
                
                dprint("Minuto numero %s"%minute,4)
        
        time.sleep(60)
                
        NE1.tl1.event_collection_stop()
        
        NE2.tl1.event_collection_stop()
        
        CheckEvent (self, NE1, "A", PrintLineFunction(), "FFP%s"%(NE1_PROT_FACILITY), "WTR-FE,CL")
    
        CheckEvent (self, NE2, "A", PrintLineFunction(), "FFP%s"%(NE2_PROT_FACILITY), "WTR,CL")
        
        CheckONTAlarm(self, NE1, ONT1, ONT1_P1, "",PrintLineFunction())

        CheckONTAlarm(self, NE2, ONT2, ONT2_P1, "",PrintLineFunction())

        NE1.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE1_PROT_FACILITY))        

        msg=TL1message(NE1.tl1.get_last_outcome())
      
        CheckCondition (self, NE1, msg, "", "FFP%s"%(NE1_PROT_FACILITY),PrintLineFunction())
          
        NE2.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
      
        CheckCondition (self, NE2, msg, "", "FFP%s"%(NE2_PROT_FACILITY),PrintLineFunction())
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"ACTIVE","WKG",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"CURRREQ","NR",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"ACTIVE","WKG",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"CURRREQ","NR",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PENDREQ","NR",PrintLineFunction())
        
        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_WORK_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_WORK_FACILITY, "WRK", PrintLineFunction())

        NE1.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE1, msg, "%s"%NE1_PROT_FACILITY, "STBYH", PrintLineFunction())
        
        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_WORK_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_WORK_FACILITY, "WRK", PrintLineFunction())

        NE2.tl1.do("RTRV-%s::%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckSecondaryState(self, NE2, msg, "%s"%NE2_PROT_FACILITY, "STBYH", PrintLineFunction())
        
        #Switch caused by failure end

        NE1.tl1.do("DLT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE1_S1_RATE,NE1_S1,MSP__RATE,NE1_WORK))        
            
        NE2.tl1.do("DLT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE2_S1_RATE,NE2_S1,MSP__RATE,NE2_WORK))        
        
        NE1.tl1.do("DLT-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE1_PROT_FACILITY))        
    
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckIfIsNotConfigured(self, NE1, msg, "FFP%s"%NE1_PROT_FACILITY, PrintLineFunction())
        
        NE2.tl1.do("DLT-FFP-%s::FFP%s;"%(MSP__RATE,NE2_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP__RATE,NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckIfIsNotConfigured(self, NE2, msg, "FFP%s"%NE2_PROT_FACILITY, PrintLineFunction())
        
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
               
        NE2.tl1.do("RTRV-AU4::%sAU4-%s-1&&-%s;"%(MSP__RATE,NE2_WORK,Au4InStmN(MSP__RATE,"AU4")))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        cmd=msg.get_cmd_status()
    
        if cmd == (True,'COMPLD'):
            
            aidList=msg.get_cmd_aid_list()
            
            if aidList!=None:
            
                for i in range (0, len(aidList)):
                                    
                   CheckPrimaryState(self, NE2, msg, aidList[i], "IS-NR",PrintLineFunction())
               
        NE2.tl1.do("RTRV-AU4::%sAU4-%s-1&&-%s;"%(MSP__RATE,NE2_PROT,Au4InStmN(MSP__RATE,"AU4")))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        cmd=msg.get_cmd_status()
    
        if cmd == (True,'COMPLD'):
            
            aidList=msg.get_cmd_aid_list()
            
            if aidList!=None:
            
                for i in range (0, len(aidList)):
                                    
                   CheckPrimaryState(self, NE2, msg, aidList[i], "IS-NR",PrintLineFunction())
               
        NE1.tl1.do("CANC-USER;")
        
        NE2.tl1.do("CANC-USER;")
        
        self.stop_tps_block(NE1.id,"MSP", "5-2-2-12")
        

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

