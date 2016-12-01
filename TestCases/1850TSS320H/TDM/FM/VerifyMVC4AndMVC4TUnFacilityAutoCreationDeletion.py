#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: Verify that MVC4 and MVC4TUn are created/deleted when board is created/deleted
:field Topology: 7
:field Dependency:
:field Lab: SVT
:field TPS: FM__5-2-1-1
:field TPS: FM__5-2-1-2
:field TPS: FM__5-2-2-1
:field TPS: FM__5-2-2-2
:field RunSections: 11111 
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
from inspect import currentframe

E_LO_MTX = "MXH60GLO"

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


def Q010_Remove_Board(zq_slot):
    zq_tl1_res=NE1.tl1.do("RMV-EQPT::{}-{};".format(E_LO_MTX, zq_slot))
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    dprint(NE1.tl1.get_last_outcome(),1)
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        dprint('\tRemoving board {}-{} . . .'.format(E_LO_MTX, zq_slot),2)
        zq_pst=('',);
        while (zq_pst[0] != 'OOS-MA'):
            time.sleep(1)
            zq_tl1_res=NE1.tl1.do("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_slot))
            dprint(NE1.tl1.get_last_outcome(),1)
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_pst=zq_msg.get_cmd_pst("{}-{}".format(E_LO_MTX, zq_slot))
            dprint("\t. . . waiting for removing . . .{}".format(zq_pst),2)
        dprint("OK\tBoard {}-{} removed and {}".format(E_LO_MTX, zq_slot,zq_pst),2)
    return

def Q020_Delete_Board(zq_slot):
    zq_tl1_res=NE1.tl1.do("DLT-EQPT::{}-{};".format(E_LO_MTX, zq_slot))
    dprint(NE1.tl1.get_last_outcome(),1)
    zq_msg=TL1message(NE1.tl1.get_last_outcome())
    zq_cmd=zq_msg.get_cmd_status()
    if zq_cmd == (True,'COMPLD'):
        dprint('\tDeleting board {}-{} . . .'.format(E_LO_MTX, zq_slot),2)
        zq_flag=True;
        while zq_flag:
            #time.sleep(5)
            zq_tl1_res=NE1.tl1.do("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_slot))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_pst=zq_msg.get_cmd_pst("{}-{}".format(E_LO_MTX, zq_slot))
            zq_aid="MDL-"+zq_slot
            zq_prov=zq_msg.get_cmd_attr_value(zq_aid, "AUTOPROV")
            if zq_prov == 'OFF':
                zq_flag=False
                #print("\t. . . waiting for deleting . . .{}".format(zq_pst))
            dprint(NE1.tl1.get_last_outcome(),1)
        dprint("OK\tBoard {}-{} deleted and {}".format(E_LO_MTX, zq_slot,zq_pst),2)
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

        all runSections will be executed if run Test without input parameters
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
        print("\n******************** START ********************")
        E_MAX_VC4=385
 
        '''
        Check board is not configured
        '''            

        self.start_tps_block(NE1.id,"FM", "5-2-1-1")
        zq_mtxlo_slot=NE1.get_preset("M1")
        zq_tl1_res=NE1.tl1.do("RTRV-PTF::ALL::::PTFTYPE=MODVC4,PTFRATE=VC4;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_num_line=zq_msg.get_cmd_response_size()
        if zq_num_line == 0:
            '''
            #Create board
            '''            
            zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            dprint(NE1.tl1.get_last_outcome(),1)
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                print('\tProvisioning board {}-{} . . .'.format(E_LO_MTX, zq_mtxlo_slot))
                zq_pst=('',);
                while (zq_pst[0] != 'IS'):
                    time.sleep(5)
                    zq_tl1_res=NE1.tl1.do("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                    dprint(NE1.tl1.get_last_outcome(),1)
                    zq_msg=TL1message(NE1.tl1.get_last_outcome())
                    zq_pst=zq_msg.get_cmd_pst("{}-{}".format(E_LO_MTX, zq_mtxlo_slot))
                    print("\t. . . waiting for SWDL . . .{}".format(zq_pst))
                print("OK\tBoard {}-{} equipped and {}".format(E_LO_MTX, zq_mtxlo_slot,zq_pst))
                
        
        else:
            print('OK\tBoard {}-{} already provisioned.'.format(E_LO_MTX, zq_mtxlo_slot))
            
                    
        '''
        #Retrieve MVC4 and verify that 64xMVC4 are created
        '''            
        zq_tl1_res=NE1.tl1.do("RTRV-PTF::ALL::::PTFTYPE=MODVC4,PTFRATE=VC4;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            #print(NE1.tl1.get_last_outcome())
            zq_num_ptf_ok=0
            zq_num_ptf_ko=0
            for zq_i in range (1,E_MAX_VC4):
                zq_aid='MVC4-{}-{}'.format(zq_mtxlo_slot,zq_i)
                zq_ptf_type=zq_msg.get_cmd_attr_value("MVC4-{}-{}".format(zq_mtxlo_slot,zq_i), "PTFTYPE")
                zq_ptf_rate=zq_msg.get_cmd_attr_value("MVC4-{}-{}".format(zq_mtxlo_slot,zq_i), "PTFRATE")
                zq_ptf_lista=[]
                zq_ptf_lista.append(zq_aid)
                zq_ptf_lista.append(zq_ptf_type)
                zq_ptf_lista.append(zq_ptf_rate)
                if zq_ptf_lista != ['MVC4-{}-{}'.format(zq_mtxlo_slot,zq_i),'MODVC4','VC4']:
                    print("KO\tRetrieving PTF:\n")
                    print("\t\tAID    : {}".format(zq_aid))
                    print("\t\tPTFTYPE: {}".format(zq_ptf_type))
                    print("\t\tPTFRATE: {}".format(zq_ptf_rate))
                    zq_num_ptf_ko+=1
                    self.add_failure(NE1, "TL1 command","0.0", "Retrieving PTF: {}\n".format(zq_ptf_lista),"PTF not found! "+ QS_000_Print_Line_Function())
                    #break
                else:
                    print("OK\tRetrieving PTF: {}\n".format(zq_ptf_lista))
                    zq_num_ptf_ok+=1
                    self.add_success(NE1, "TL1 command","0.0", "Retrieving PTF: {}\n".format(zq_ptf_lista))
                    
                    
            print("\tNumber of correct MVC4: {}".format(zq_num_ptf_ok))    
            print("\tNumber of wrong   MVC4: {}\n".format(zq_num_ptf_ko))    

        '''
        #Retrieve MVC4TU3 and verify that 64x3=192 MVC4TU3 are created
        '''            
        zq_tl1_res=NE1.tl1.do("RTRV-TU3::ALL;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            #print(NE1.tl1.get_last_outcome())
            zq_num_ptf_ok=0
            zq_num_ptf_ko=0
            zq_aid_list=zq_msg.get_cmd_aid_list()
            for zq_i in range (1,E_MAX_VC4):
                for zq_j in range(1,4):
                    zq_aid='MVC4TU3-{}-{}-{}'.format(zq_mtxlo_slot,zq_i,zq_j)
                    if zq_aid in zq_aid_list:
                        print("OK\tRetrieving PTF: {}".format(zq_aid))
                        zq_num_ptf_ok+=1
                        self.add_success(NE1, "TL1 command","0.0", "Retrieving PTF: {}\n".format(zq_aid))
                        #break
                    else:
                        print("KO\tRetrieving PTF:")
                        print("\t\tAID missing   : {}\n".format(zq_aid))
                        self.add_failure(NE1, "TL1 command","0.0", "Retrieving PTF: {}\n".format(zq_aid),"PTF not found! "+ QS_000_Print_Line_Function())
                        zq_num_ptf_ko+=1
                            
            print("\tNumber of correct MVC4TU3: {}".format(zq_num_ptf_ok))    
            print("\tNumber of missing MVC4TU3: {}\n".format(zq_num_ptf_ko))    


        
        '''
        #Retrieve MVC4TU12 and verify that no MVC4TU12 exists
        '''            
        zq_tl1_res=NE1.tl1.do("RTRV-TU12::ALL;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_res=zq_msg.get_cmd_response_size()
        if zq_res == 0:
            dprint("OK\tMVC4TU12 correctly not created.\n",2)    
            
        self.stop_tps_block(NE1.id,"FM", "5-2-1-1")

        self.start_tps_block(NE1.id,"FM", "5-2-2-1")

        '''
        #Remove board
        '''            
        Q010_Remove_Board(zq_mtxlo_slot)
      
        '''
        #Delete board
        '''            
        Q020_Delete_Board(zq_mtxlo_slot)


        '''
        # DA TOGLIERE
        '''
        time.sleep(60)
        
        
        
        '''
        #Verify no MVC4TU3 exist after board removing & deleting 
        '''            
        zq_tl1_res=NE1.tl1.do("RTRV-TU3::ALL;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            if zq_msg.get_cmd_response_size() == 0:
                dprint('OK\tCorrectly no MVC4TU3 exist after board deletion',2)
                self.add_success(NE1, "TL1 command","0.0", "Correctly no MVC4TU3 exist after board deletion\n")
            else:
                dprint('KO\tWrongly some MVC4TU3 exist after board deletion',2)
                self.add_failure(NE1, "TL1 command","0.0", "RTRV-TU3::ALL","Wrongly some MVC4TU3 exist after board deletion "+ QS_000_Print_Line_Function())

        self.stop_tps_block(NE1.id,"FM", "5-2-2-1")


        self.start_tps_block(NE1.id,"FM", "5-2-1-2")



        '''
        Check board is not configured
        '''            
        zq_mtxlo_slot=NE1.get_preset("M1")
        zq_tl1_res=NE1.tl1.do("RTRV-PTF::ALL::::PTFTYPE=MODVC4,PTFRATE=VC4;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_num_line=zq_msg.get_cmd_response_size()
        if zq_num_line == 0:
            '''
            #Create board
            '''            
            zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            dprint(NE1.tl1.get_last_outcome(),1)
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                print('\tProvisioning board {}-{} . . .'.format(E_LO_MTX, zq_mtxlo_slot))
                zq_pst=('',);
                while (zq_pst[0] != 'IS'):
                    time.sleep(5)
                    zq_tl1_res=NE1.tl1.do("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                    dprint(NE1.tl1.get_last_outcome(),1)
                    zq_msg=TL1message(NE1.tl1.get_last_outcome())
                    zq_pst=zq_msg.get_cmd_pst("{}-{}".format(E_LO_MTX, zq_mtxlo_slot))
                    print("\t. . . waiting for SWDL . . .{}".format(zq_pst))
                print("OK\tBoard {}-{} equipped and {}".format(E_LO_MTX, zq_mtxlo_slot,zq_pst))
                
        
        else:
            print('OK\tBoard {}-{} already provisioned.'.format(E_LO_MTX, zq_mtxlo_slot))
            


        '''
        #Edit all 64xMVC4 changing from 3xTU3 to 63xTU12 
        '''            
        zq_tl1_res=NE1.tl1.do("RTRV-PTF::ALL::::PTFTYPE=MODVC4,PTFRATE=VC4;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_aid_list=zq_msg.get_cmd_aid_list()   #list of MVC4-1-1-36-x x in (1,65)
            for zq_i in range (1,E_MAX_VC4):
                zq_aid='MVC4-{}-{}'.format(zq_mtxlo_slot,zq_i)
                if zq_aid in zq_aid_list:
                    #time.sleep(10)
                    zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,zq_i))
                    zq_msg=TL1message(NE1.tl1.get_last_outcome())
                    dprint(NE1.tl1.get_last_outcome(),1)
                    zq_cmd=zq_msg.get_cmd_status()
                    if zq_cmd == (True,'COMPLD'):
                        dprint('OK\tMVC4-{}-{} structured to : 63xTU12'.format(zq_mtxlo_slot,zq_i),2)
                        self.add_success(NE1, "TL1 command","0.0", "Correctly no MVC4TU3 exist after board deletion\n")
                    else:
                        dprint('KO\tMVC4-{}-{} not structured to : 63xTU12'.format(zq_mtxlo_slot,zq_i),2)
                        self.add_failure(NE1, "TL1 command","0.0", "RTRV-TU3::ALL","Wrongly some MVC4TU3 exist after board deletion "+ QS_000_Print_Line_Function())

        
        '''
        #Retrieve MVC4TU12 and verify that 64x63=3582 MVC4TU12 are created
        '''            

        zq_tl1_res=NE1.tl1.do("RTRV-TU12::ALL;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            #print(NE1.tl1.get_last_outcome())
            zq_num_ptf_ok=0
            zq_num_ptf_ko=0
            zq_aid_list=zq_msg.get_cmd_aid_list()
            
            for zq_i in range (1,E_MAX_VC4):                                       #zq_i=VC4 index
                for zq_j in range(1,4):                                            #zq_j=TU3 index
                    for zq_k in range(1,8):                                       #zq_k=TU12 index
                        for zq_m in range(1,4):
                            zq_aid='MVC4TU12-{}-{}-{}-{}-{}'.format(zq_mtxlo_slot,zq_i,zq_j,zq_k,zq_m)
                            if zq_aid in zq_aid_list:
                                print("OK\tRetrieving PTF: {}".format(zq_aid))
                                self.add_success(NE1, "TL1 command","0.0", "Retrieving PTF: {}".format(zq_aid))
                                zq_num_ptf_ok+=1
                                #break
                            else:
                                print("KO\tRetrieving PTF:")
                                print("\t\tAID missing   : {}\n".format(zq_aid))
                                self.add_failure(NE1, "TL1 command","0.0", "Retrieving PTF: {}\n".format(zq_aid),"PTF not found! "+ QS_000_Print_Line_Function())
                                zq_num_ptf_ko+=1
                            
            print("\tNumber of correct MVC4TU12: {}".format(zq_num_ptf_ok))    
            print("\tNumber of missing MVC4TU12: {}\n".format(zq_num_ptf_ko))    
        
        self.stop_tps_block(NE1.id,"FM", "5-2-1-2")
        
        self.start_tps_block(NE1.id,"FM", "5-2-2-2")

        
        '''
        #Remove board
        '''            
        Q010_Remove_Board(zq_mtxlo_slot)
      
        '''
        #Delete board
        '''            
        Q020_Delete_Board(zq_mtxlo_slot)

        
        '''
        # DA TOGLIERE
        '''
        time.sleep(90)
        
        
        '''
        #Verify no MVC4TU12 exist after board removing & deleting 
        '''            
        zq_tl1_res=NE1.tl1.do("RTRV-TU12::ALL;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            if zq_msg.get_cmd_response_size() == 0:
                dprint('OK\tCorrectly no MVC4TU12 exist after board deletion',2)
            else:
                dprint('KO\tWrongly some MVC4TU12 exist after board deletion',2)


        self.stop_tps_block(NE1.id,"FM", "5-2-2-2")

        print("\n**************** STOP ****************")
        

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

