#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: Verify the Linear MSP protection group creation and deletion on STM16 facility on MRSOE  
:field Topology: 10
:field Dependency:
:field Lab: SVT
:field TPS:  MSP__5-2-1-12
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


E_WAIT = 2

def dprint(str,level):
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
    
    if (E_DPRINT & level):
        print(str)
    return

def PrintLineFunction(gap=0):
    cf = currentframe()
    line = cf.f_back.f_lineno + gap
    code = str(cf.f_back.f_code)
    temp = code.split(",")
    function = temp[0].split(" ")
    res = "****** Line [{}] in function [{}]".format(line,function[2])
    
    return res

def CheckPrimaryState(run, NE, msg, type, aid, state,line):

    found=False
    
    #time.sleep(E_WAIT)
    #NE.tl1.do("RTRV-%s::%s;"%(type,aid))        
    
    #msg=TL1message(NE.tl1.get_last_outcome())
    
    cmd=msg.get_cmd_status()
    if cmd == (True,'COMPLD'):
           
        pstList=msg.get_cmd_pst(aid)
        
        if (pstList!=None):
           
            i=0
            
            while (i < len(pstList) and not found)  :
                if (pstList[i]==state):
                   found=True
                else:
                   i=i+1
                       
    if(not found):
        dprint("KO\t Primary state of %s is wrong\n"%aid,2)
        run.add_failure(NE, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","Primary state of %s is wrong  %s"%(aid,line))
        
    
        
    return found

def CheckSecondaryState(run, NE, msg, type, aid, state, line):

    found=False
    
    #time.sleep(E_WAIT)
    
    #NE.tl1.do("RTRV-%s::%s;"%(type,aid))        
    
    #msg=TL1message(NE.tl1.get_last_outcome())
    
    cmd=msg.get_cmd_status()
    
    if cmd == (True,'COMPLD'):
    
        sstList=msg.get_cmd_sst(aid)
        
        i=0
        
        if (sstList!=None):
        
            while (i < len(sstList) and not found)  :
                if (sstList[i]==state):
                   found=True
                else:
                   i=i+1
                       
    if(not found):
        dprint("KO\t Secondary state of %s is wrong\n"%aid,2)
        run.add_failure(NE, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","Secondary state of %s is wrong  %s"%(aid,line))
        
        
        
    return found

def CheckIfIsInUasAndDsbldState(run, NE, msg, type, aid, line):

    isInState=False
    
    if CheckPrimaryState(run, NE, msg, type, aid, "OOS-AUMA", line) and CheckSecondaryState(run, NE, msg, type, aid, "UAS", line) and CheckSecondaryState(run, NE, msg, type, aid, "DSBLD", line):  
       isInState=True
    
    else:
                 
       dprint("KO\t %s is not in UAS&DSBLD state \n"%aid,2)
       run.add_failure(NE, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL"," %s is not in UAS&DSBLD state  %s"%(aid,line))
                
    return isInState

def CheckIfIsNotConfigured(run, NE, msg, line):

    isNotConfigured=False
    
    #time.sleep(E_WAIT)
    
    #NE.tl1.do("RTRV-%s::%s;"%(type,aid))        
    
    #msg=TL1message(NE.tl1.get_last_outcome())
    
    cmd=msg.get_cmd_status()
    
    if cmd == (True,'COMPLD'):
    
        size=msg.get_cmd_response_size()
        
        if (size==0):
        
            isNotConfigured=True
                       
    if(not isNotConfigured):
        dprint("KO\t %s is unexpectedly configured\n"%aid,2)
        run.add_failure(NE, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","%s is unexpectedly configured %s"%(aid,line))
        
        
        
    return isNotConfigured
        
def Au4InStmN(rate,au4):

    
    conversion = {('STM1','AU4'): 1, ('STM4','AU4'): 4, ('STM4','AU44C'): 1,('STM16','AU4'): 16, ('STM16','AU44C'): 4, ('STM4','AU416C'): 1,('STM64','AU4'): 64, ('STM64','AU44C'): 16, ('STM64','AU416C'): 4,('STM64','AU464C'): 4}
       
    number=conversion.get((rate,au4),0)
                 
    return number

def CheckParameterValue(run, NE, msg,aid,parameter,expValue,line):

    
    #msg=TL1message(NE.tl1.get_last_outcome())
    
    cmd=msg.get_cmd_status()
    if cmd == (True,'COMPLD'):
                     
        if (msg.get_cmd_attr_value(aid, parameter) != expValue):
                dprint("KO\t Parameter %s of %s is wrong \n"%(parameter,aid),2)
                run.add_failure(NE, "TL1 COMMAND","0.0", "TL1 COMMAND FAIL","Parameter %s of %s is wrong  %s\n"%(parameter,aid,line))
      
            
    return


def CheckCondition (run, NE, msg, condition_exp, aid):

    '''
    Condition_exp same has to be equal [CONDTYPE] parameter of previous RTRV command
    
    If it is different from "" we expect a response having a body with 0 or 1 row
    
    If is void number of rows doesn't matter
     
    '''
    matched=False
    
    cmd=msg.get_cmd_status()
    
    if cmd == (True,'COMPLD'):
    
        responseSize=msg.get_cmd_response_size()
        
        if (responseSize==0): #NO ALARM FOUND
            if condition_exp == "":    #NO ALARM EXPECTED AND NO ALARM FOUND
                dprint("OK\tNO Condition/Alarm found on aid %s\n"%aid,2)
                run.add_success(NE, "TL1 Condition/Alarm check","0.0","NO Condition/Alarm found on aid %s\n"%aid )
                
            else:                   #ALARM EXPECTED BUT NO ALARM FOUND  
                dprint("KO\t NO Condition/Alarm found on aid %s\n"%aid,2)
                run.add_failure(NE, "TL1 Condition/Alarm check","0.0","NO Condition/Alarm found on aid %s\n"%aid,"NO Condition/Alarm found on aid %s\n"%aid)
                
        else:
            if condition_exp == "":    #NO ALARM EXPECTED BUT ALARM FOUND
                dprint("KO\t Condition/Alarm found on aid %s\n"%aid,2)
                run.add_failure(NE, "TL1 Condition/Alarm check","0.0","Condition/Alarm found on aid %s\n"%aid,"Condition/Alarm found on aid %s\n"%aid)
            else:                   #ALARM EXPECTED AND SAME ALARM FOUND  
                dprint("0K\t Condition/Alarm %s found on aid %s\n"%(condition_exp,aid),2)
                run.add_success(NE, "TL1 Condition/Alarm check","0.0","Condition/Alarm %s found on aid %s\n"%(condition_exp,aid))
                
    return


def CheckONTAlarm(run, ont, ont_port, alm_exp):

    ont.start_measurement(ont_port)
    time.sleep(E_WAIT)
    ont.halt_measurement(ont_port)
    alm = ont.retrieve_ho_lo_alarms(ont_port)
    if alm[0] == True:           #COMMAND IS OK
        if len(alm[1]) == 0:     #NO ALARM FOUND
            if alm_exp == "":    #NO ALARM EXPECTED AND NO ALARM FOUND
                dprint("OK\tNO Alarm found on ont {} port {}".format(ont,ont_port),2)
                run.add_success(NE1, "NO Alarm found on ont {} port {}".format(ont,ont_port),"0.0", "ont Alarm check")
                
                
            else:                   #NO ALARM EXPECTED BUT ALARM FOUND  
                dprint("KO\tAlarm found on ont {} port {}:".format(ont,ont_port),2)
                dprint("\t\tAlarm: Exp [{}]  - Rcv [{}]".format("no alarm",alm[1][0]),2)
                run.add_failure(NE1,  "ont Alarm check","0.0", "ont Alarms check", 
                                     "Alarm found on ont {} port {}: Exp [{}]  - Rcv [{}] {}".format(ont,ont_port, "no alarm", alm[1][0],Print_Line_Function()))
                
        else:                       #ALARM FOUND
            if alm[1][0] == alm_exp:      #ALARM FOUND AND ALARM WAS EXPECTED
                dprint("OK\t{} Alarm found on ont {} port {}".format(alm_exp,ont,ont_port),2)
                run.add_success(NE1, "{} Alarm found on ont {} port {}".format(alm_exp,ont,ont_port),"0.0", "ont Alarm check")
            else:                               #ALARM FOUND BUT ALARM WAS NOT EXPECTED
                dprint("KO\tAlarm mismatch on ont {} port {}:".format(ont,ont_port),2)
                dprint("\t\tAlarm: Exp [{}]  - Rcv [{}]".format(alm_exp,alm[1][0]),2)
                run.add_failure(NE1,  "Ont Alarm check","0.0", "Onont Alarms check", 
                                         "Alarm mismatch on Ont {} port {}: Exp [{}]  - Rcv [{}] {}".format(ont,ont_port, alm_exp, alm[1][0],Print_Line_Function()))

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
        
        NE1_WORK_FACILITY='%s-%s'%(MSP_RATE,NE1_WORK)
        NE1_PROT_FACILITY='%s-%s'%(MSP_RATE,NE1_PROT)
        NE1_S1_FACILITY='%s-%s'%(NE1_S1_RATE,NE1_S1) 
 
        NE2_WORK_FACILITY='%s-%s'%(MSP_RATE,NE2_WORK)
        NE2_PROT_FACILITY='%s-%s'%(MSP_RATE,NE2_PROT)
        NE2_S1_FACILITY='%s-%s'%(NE2_S1_RATE,NE2_S1) 
 
        self.start_tps_block(NE1.id,"MSP", "5-2-1-12")
        
        
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
        
        NE1.tl1.do("ED-%s::%s::::ALSENB=N;"%(MSP_RATE,NE1_WORK_FACILITY))        
        
        NE1.tl1.do("ED-%s::%s::::ALSENB=N,HOSTRUCT=%sxAU44C;"%(MSP_RATE,NE1_PROT_FACILITY,Au4InStmN(MSP_RATE,"AU44C")))        
        
        NE2.tl1.do("ED-%s::%s::::ALSENB=N;"%(NE2_S1_RATE,NE2_S1_FACILITY))        
        
        NE2.tl1.do("ED-%s::%s::::ALSENB=N;"%(MSP_RATE,NE2_WORK_FACILITY))        
        
        NE2.tl1.do("ED-%s::%s::::ALSENB=N;"%(MSP_RATE,NE2_PROT_FACILITY))        
        
        time.sleep(15)
        
        NE1.tl1.do("RTRV-%s::%s;"%(MSP_RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckParameterValue(self, NE1, msg ,NE1_PROT_FACILITY,"HOSTRUCT","%sxAU44C"%Au4InStmN(MSP_RATE,"AU44C"),PrintLineFunction())
        
        NE1.tl1.do("RTRV-AU4::%sAU4-%s-1;"%(MSP_RATE,NE1_WORK))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckPrimaryState(self, NE1, msg, "AU4", "%sAU4-%s-1"%(MSP_RATE,NE1_WORK),"IS-NR",PrintLineFunction())
        
        NE2.tl1.do("RTRV-AU4::%sAU4-%s-1;"%(MSP_RATE,NE2_WORK))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckPrimaryState(self, NE2, msg, "AU4", "%sAU4-%s-1"%(MSP_RATE,NE2_WORK),"IS-NR",PrintLineFunction())
    
        NE1.tl1.do("ENT-FFP-%s::FFP%s::::PTYPE=LINEAR,RVRTV=Y,WKG=%s,PROTN=%s,PSDIRN=UNI;"%(MSP_RATE,NE1_PROT_FACILITY,NE1_WORK_FACILITY,NE1_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP_RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PTYPE","LINEAR",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"RVRTV","Y",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"WKG",NE1_WORK_FACILITY,PrintLineFunction())
           
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PROTN",NE1_PROT_FACILITY,PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PSDIRN","UNI",PrintLineFunction())
        
        NE1.tl1.do("RTRV-AU4::%sAU4-%s-1&&-%s;"%(MSP_RATE,NE1_PROT,Au4InStmN(MSP_RATE,"AU4")))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        cmd=msg.get_cmd_status()
    
        if cmd == (True,'COMPLD'):
            
            aidList=msg.get_cmd_aid_list()
            for i in range (0, len(aidList)):
                CheckIfIsInUasAndDsbldState(self, NE1, msg, "AU4", aidList[i], PrintLineFunction())
            
            
        NE2.tl1.do("ENT-FFP-%s::FFP%s::::PTYPE=LINEAR,RVRTV=Y,WKG=%s,PROTN=%s,PSDIRN=UNI;"%(MSP_RATE,NE2_PROT_FACILITY,NE2_WORK_FACILITY,NE2_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP_RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PTYPE","LINEAR",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"RVRTV","Y",PrintLineFunction())
          
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"WKG",NE2_WORK_FACILITY,PrintLineFunction())
           
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PROTN",NE2_PROT_FACILITY,PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PSDIRN","UNI",PrintLineFunction())
                
        NE2.tl1.do("RTRV-AU4::%sAU4-%s-1&&-%s;"%(MSP_RATE,NE2_PROT,Au4InStmN(MSP_RATE,"AU4")))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        cmd=msg.get_cmd_status()
    
        if cmd == (True,'COMPLD'):
            
            aidList=msg.get_cmd_aid_list()
            for i in range (0, len(aidList)):
                CheckIfIsInUasAndDsbldState(self, NE2, msg, "AU4", aidList[i], PrintLineFunction())
            
        NE1.tl1.do("ENT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE1_S1_RATE,NE1_S1,MSP_RATE,NE1_WORK))        
            
        NE2.tl1.do("ENT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE2_S1_RATE,NE2_S1,MSP_RATE,NE2_WORK))        
        
        time.sleep(E_WAIT)
        
        CheckONTAlarm(self, ONT1, ONT1_P1, "")

        CheckONTAlarm(self, ONT2, ONT2_P1, "")

        NE1.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE1_PROT_FACILITY))        

        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckCondition (self, NE1, msg, "", "FFP%s"%(NE1_PROT_FACILITY))
        
        NE2.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckCondition (self, NE2, msg, "", "FFP%s"%(NE2_PROT_FACILITY))
        
        NE1.tl1.do("DLT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE1_S1_RATE,NE1_S1,MSP_RATE,NE1_WORK))        
            
        NE2.tl1.do("DLT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE2_S1_RATE,NE2_S1,MSP_RATE,NE2_WORK))        
        
        NE1.tl1.do("DLT-FFP-%s::FFP%s;"%(MSP_RATE,NE1_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP_RATE,NE1_PROT_FACILITY))        
    
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckIfIsNotConfigured(self, NE1, msg, PrintLineFunction())
        
        NE2.tl1.do("DLT-FFP-%s::FFP%s;"%(MSP_RATE,NE2_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP_RATE,NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckIfIsNotConfigured(self, NE2, msg, PrintLineFunction())
    

        NE1.tl1.do("ENT-FFP-%s::FFP%s::::PTYPE=LINEAR,RVRTV=N,WKG=%s,PROTN=%s,PSDIRN=UNI;"%(MSP_RATE,NE1_PROT_FACILITY,NE1_WORK_FACILITY,NE1_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP_RATE,NE1_PROT_FACILITY))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PTYPE","LINEAR",PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"RVRTV","N",PrintLineFunction())
          
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"WKG",NE1_WORK_FACILITY,PrintLineFunction())
           
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PROTN",NE1_PROT_FACILITY,PrintLineFunction())
        
        CheckParameterValue(self,NE1,msg,"FFP%s"%NE1_PROT_FACILITY,"PSDIRN","UNI",PrintLineFunction())
        
        NE1.tl1.do("RTRV-AU4::%sAU4-%s-1&&-%s;"%(MSP_RATE,NE1_PROT,Au4InStmN(MSP_RATE,"AU4")))        
        
        msg=TL1message(NE1.tl1.get_last_outcome())
        
        cmd=msg.get_cmd_status()
    
        if cmd == (True,'COMPLD'):
            
            aidList=msg.get_cmd_aid_list()
            for i in range (0, len(aidList)):
                CheckIfIsInUasAndDsbldState(self, NE1, msg, "AU4", aidList[i], PrintLineFunction())
            
            
        NE2.tl1.do("ENT-FFP-%s::FFP%s::::PTYPE=LINEAR,RVRTV=N,WKG=%s,PROTN=%s,PSDIRN=UNI;"%(MSP_RATE,NE2_PROT_FACILITY,NE2_WORK_FACILITY,NE2_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP_RATE,NE2_PROT_FACILITY))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PTYPE","LINEAR",PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"RVRTV","N",PrintLineFunction())
          
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"WKG",NE2_WORK_FACILITY,PrintLineFunction())
           
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PROTN",NE2_PROT_FACILITY,PrintLineFunction())
        
        CheckParameterValue(self,NE2,msg,"FFP%s"%NE2_PROT_FACILITY,"PSDIRN","UNI",PrintLineFunction())
                
        NE2.tl1.do("RTRV-AU4::%sAU4-%s-1&&-%s;"%(MSP_RATE,NE2_PROT,Au4InStmN(MSP_RATE,"AU4")))        
        
        msg=TL1message(NE2.tl1.get_last_outcome())
        
        cmd=msg.get_cmd_status()
    
        if cmd == (True,'COMPLD'):
            
            aidList=msg.get_cmd_aid_list()
            for i in range (0, len(aidList)):
                CheckIfIsInUasAndDsbldState(self, NE2, msg, "AU4", aidList[i], PrintLineFunction())
            
        NE1.tl1.do("ENT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE1_S1_RATE,NE1_S1,MSP_RATE,NE1_WORK))        
            
        NE2.tl1.do("ENT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE2_S1_RATE,NE2_S1,MSP_RATE,NE2_WORK))        
        
        time.sleep(E_WAIT)
        
        CheckONTAlarm(self, ONT1, ONT1_P1, "")

        CheckONTAlarm(self, ONT2, ONT2_P1, "")

        NE1.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE1_PROT_FACILITY))        

        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckCondition (self, NE1, msg, "", "FFP%s"%(NE1_PROT_FACILITY))
        
        NE2.tl1.do("RTRV-COND-FFP::FFP%s;"%(NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
    
        CheckCondition (self, NE2, msg, "", "FFP%s"%(NE2_PROT_FACILITY))
        
        NE1.tl1.do("DLT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE1_S1_RATE,NE1_S1,MSP_RATE,NE1_WORK))        
            
        NE2.tl1.do("DLT-CRS-VC4::%sAU4-%s-1,%sAU4-%s-1;"%(NE2_S1_RATE,NE2_S1,MSP_RATE,NE2_WORK))        
        
        NE1.tl1.do("DLT-FFP-%s::FFP%s;"%(MSP_RATE,NE1_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE1.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP_RATE,NE1_PROT_FACILITY))        
    
        msg=TL1message(NE1.tl1.get_last_outcome())
    
        CheckIfIsNotConfigured(self, NE1, msg, PrintLineFunction())
        
        NE2.tl1.do("DLT-FFP-%s::FFP%s;"%(MSP_RATE,NE2_PROT_FACILITY))        
        
        time.sleep(E_WAIT)
        
        NE2.tl1.do("RTRV-FFP-%s::FFP%s;"%(MSP_RATE,NE2_PROT_FACILITY))        

        msg=TL1message(NE2.tl1.get_last_outcome())
        
        CheckIfIsNotConfigured(self, NE2, msg, PrintLineFunction())
               
        NE1.tl1.do("CANC-USER;")
        
        NE2.tl1.do("CANC-USER;")
        
        self.stop_tps_block(NE1.id,"MSP", "5-2-1-12")
 

    def test_cleanup(self):
        '''
        test Cleanup Section implementation
        insert CleanUp code for your test below
        

        ONT1.deinit_instrument(ONT1_P1)
        ONT2.deinit_instrument(ONT2_P1)
        '''
        
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
    
    MSP_RATE=NE2.get_preset("MSP_RATE")
    
    CTEST.add_eqpt(NE1)
    CTEST.add_eqpt(NE2)

    # Run Test main flow
    # Please don't touch this code
    CTEST.run()
