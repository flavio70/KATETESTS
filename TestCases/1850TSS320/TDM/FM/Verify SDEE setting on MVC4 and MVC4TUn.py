#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: To verify that, for each MVC4-TUn path facility, SDEE is set when used in cross-connection.
:field Topology: 6
:field Dependency: Needs at least 5 half slot free to equip 10GSO extra board
:field Lab: SVT
:field TPS: FM__5-2-4-1
:field TPS: FM__5-2-5-1
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

E_LO_MTX = "MXH60GLO"

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
        E_SLOT = ['2','3','4','5','6','7','8','12','13','14','15','16','17','18','19']
        E_MAX_VC4=385
        E_AU4 = 64
 
        '''
        Check board equipment
        '''            

        self.start_tps_block(NE1.id,"FM", "5-2-4-1")
        zq_stm64p1=NE1.get_preset("S1")
        zq_mtxlo_slot=NE1.get_preset("M1")

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
        Find 5 free slots and equip 5 x 1P10GSO
        '''
        zq_board_to_remove=list()
        zq_filter=TL1check()
        zq_filter.add_pst("OOS-AU")
        zq_tl1_res=NE1.tl1.do("RTRV-EQPT::ALL;")
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_num=0
            zq_i = 0
            zq_aid_list=zq_msg.get_cmd_aid_list()
            while ((zq_i in range(0,len(zq_aid_list))) and (zq_num < 5)):
                if (('MDL' in zq_aid_list[zq_i]) and (''.join(zq_aid_list[zq_i]).count('-') == 3)):
                    zq_slot=''.join(zq_aid_list[zq_i])
                    zq_slot=zq_slot.split('-')
                    if (zq_slot[3] in E_SLOT):
                        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}::::PROVISIONEDTYPE=1P10GSO;".format(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO')))
                        NE1.tl1.do_until("RTRV-EQPT::{};".format(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO')),zq_filter)
                        print('Board Equipped: {}'.format(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO')))
                        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-1::::PROVISIONEDTYPE=XI-641;".format(''.join(zq_aid_list[zq_i]).replace('MDL','XFP')))
                        NE1.tl1.do_until("RTRV-EQPT::{}-1;".format(''.join(zq_aid_list[zq_i]).replace('MDL','XFP')),zq_filter)
                        zq_board_to_remove.append(''.join(zq_aid_list[zq_i]).replace('MDL','10GSO'))
                        print('\tXFP equipped: {}-1'.format(''.join(zq_aid_list[zq_i]).replace('MDL','XFP')))
                        zq_num += 1
                zq_i += 1

            
        zq_stm64p2 = (''.join(zq_board_to_remove[0]).replace('10GSO-',''))+'-1'
        zq_stm64p3 = (''.join(zq_board_to_remove[1]).replace('10GSO-',''))+'-1'
        zq_stm64p4 = (''.join(zq_board_to_remove[2]).replace('10GSO-',''))+'-1'
        zq_stm64p5 = (''.join(zq_board_to_remove[3]).replace('10GSO-',''))+'-1'
        zq_stm64p6 = (''.join(zq_board_to_remove[4]).replace('10GSO-',''))+'-1'
        
        '''
        Check MVC4/MVC4TU3 secondary state doesn't contain SDEE
        '''            
        for zq_i in range (1,E_MAX_VC4):
            zq_tl1_res=NE1.tl1.do("RTRV-PTF::MVC4-{}-{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mtxlo_slot,zq_i))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_sst=zq_msg.get_cmd_sst("MVC4-{}-{}".format(zq_mtxlo_slot,zq_i))
            if "SDEE" in zq_sst:
               dprint('KO\tMVC4-{}-{} sst wrongly contains SDEE'.format(zq_mtxlo_slot,zq_i),2) 
            else: 
               dprint('OK\tMVC4-{}-{} sst correctly not contains SDEE'.format(zq_mtxlo_slot,zq_i),2) 
            
            for zq_j in range(1,4):
                zq_tl1_res=NE1.tl1.do("RTRV-TU3::MVC4TU3-{}-{}-{};".format(zq_mtxlo_slot,zq_i,zq_j))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_sst=zq_msg.get_cmd_sst("MVC4TU3-{}-{}-{}".format(zq_mtxlo_slot,zq_i,zq_j))
                if "SDEE" in zq_sst:
                   dprint('KO\t\tMVC4TU3-{}-{}-{} SST wrongly contains SDEE'.format(zq_mtxlo_slot,zq_i,zq_j),2) 
                   self.add_failure(NE1, "TL1 command","0.0", "Retrieving MVC4TU3-{}-{}-{}: {}\n".format(zq_mtxlo_slot,zq_i,zq_j),"SST wrong")
                else: 
                   dprint('OK\t\tMVC4TU3-{}-{}-{} SST correctly not contains SDEE'.format(zq_mtxlo_slot,zq_i,zq_j),2) 
                   self.add_success(NE1, "TL1 command","0.0", "Retrieving MVC4TU3-{}-{}-{}: SST correct\n".format(zq_mtxlo_slot,zq_i,zq_j))
                    
        '''
        Create 64xHI order cross-connection from STM64AU4-1-1-x-y-n to LOPOOL
        and verify MVC4 SST contains SDEE while MVC4TU3 SST doesn't contains SDEE
        '''            
        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")
        for zq_i in range (1,E_MAX_VC4):
            if zq_i in range (1,65):
                zq_tl1_res=NE1.tl1.do("ENT-CRS-VC4::STM64AU4-{}-{},LOPOOL-1-1-1;".format(zq_stm64p1,zq_i))
            if zq_i in range (65,129):
                zq_tl1_res=NE1.tl1.do("ENT-CRS-VC4::STM64AU4-{}-{},LOPOOL-1-1-1;".format(zq_stm64p2,zq_i-64))
            if zq_i in range (129,193):
                zq_tl1_res=NE1.tl1.do("ENT-CRS-VC4::STM64AU4-{}-{},LOPOOL-1-1-1;".format(zq_stm64p3,zq_i-128))
            if zq_i in range (193,257):
                zq_tl1_res=NE1.tl1.do("ENT-CRS-VC4::STM64AU4-{}-{},LOPOOL-1-1-1;".format(zq_stm64p4,zq_i-192))
            if zq_i in range (257,321):
                zq_tl1_res=NE1.tl1.do("ENT-CRS-VC4::STM64AU4-{}-{},LOPOOL-1-1-1;".format(zq_stm64p5,zq_i-256))
            if zq_i in range (321,385):
                zq_tl1_res=NE1.tl1.do("ENT-CRS-VC4::STM64AU4-{}-{},LOPOOL-1-1-1;".format(zq_stm64p6,zq_i-320))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                zq_xc_list.append(''.join(zq_msg.get_cmd_aid_list()))
                dprint("\nOK\tCross-connection creation successfull {}".format(zq_xc_list[zq_i]),2)

                '''
                Check MVC4 SST contains SDEE
                '''            
                zq_mvc4_temp=''.join(zq_xc_list[-1]).split(',')
                zq_mvc4_str=zq_mvc4_temp[1]
                zq_tl1_res=NE1.tl1.do("RTRV-PTF::{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mvc4_str))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_sst=zq_msg.get_cmd_sst("{}".format(zq_mvc4_str))
                if "SDEE" in zq_sst:
                   dprint('OK\t\t{} SST correctly contains SDEE'.format(zq_mvc4_str),2) 
                else: 
                   dprint('KO\t\t{} SST wrongly does not contains SDEE'.format(zq_mvc4_str),2) 
                
                '''
                Check MVC4TU3 SST doesn't contain SDEE
                '''            
                for zq_k in range (1,4):
                    zq_tu3_temp=''.join(zq_xc_list[-1]).replace('MVC4','MVC4TU3').split(',')
                    zq_tu3_str=zq_tu3_temp[1]
                    zq_tl1_res=NE1.tl1.do("RTRV-TU3::{}-{};".format(zq_tu3_str,zq_k))
                    zq_msg=TL1message(NE1.tl1.get_last_outcome())
                    zq_sst=zq_msg.get_cmd_sst("{}-{}".format(zq_tu3_str,zq_k))
                    if "SDEE" in zq_sst:
                       dprint('KO\t\t\t{}-{} SST wrongly contains SDEE'.format(zq_tu3_str,zq_k),2) 
                    else: 
                       dprint('OK\t\t\t{}-{} SST correctly does not contains SDEE'.format(zq_tu3_str,zq_k),2) 
                    

            else:
                if zq_cmd[1]== 'COMPLD':    
                    dprint("\nKO\tCross-connection creation failed {}\n".format(zq_xc_list[zq_i]),2)
                else:
                    dprint("\nKO\tTL1 Cross-connection command DENY\n",2)
                    
        
        '''
        Verify board cannot be deleted if AU4 to VC4 cross-connections exist
        '''
        
        zq_tl1_res=NE1.tl1.do("RMV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),policy='DENY')
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        dprint(NE1.tl1.get_last_outcome(),1)
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'DENY'):
            dprint("\nOK\tEquipment in SDEE status correctly not be removed",2)
        else:
            dprint("\nKO\tEquipment in SDEE status wrongly removed",2)

        
        
        if len(zq_xc_list) > 1:
            '''
            Create/Delete 64x3LOVC3 cross-connections and verify MVC4TU3 SST contains/not contains SDEE
            '''            
            for zq_i in range (1,len(zq_xc_list)):
                zq_tu3_list=zq_xc_list[zq_i].split(',')
                zq_tu3_idx=zq_tu3_list[1].replace('MVC4','MVC4TU3')
                for zq_j in range (1,4):
                    zq_tl1_res=NE1.tl1.do("ENT-CRS-LOVC3::{}-{},{}-{}:::1WAY;".format(zq_tu3_idx,zq_j,zq_tu3_idx,zq_j))
                    zq_msg=TL1message(NE1.tl1.get_last_outcome())
                    dprint(NE1.tl1.get_last_outcome(),1)
                    zq_cmd=zq_msg.get_cmd_status()
                    if zq_cmd == (True,'COMPLD'):
                        dprint("\nOK\tCross-connection successfully created {}-{}".format(zq_tu3_idx,zq_j),2)
                        zq_tl1_res=NE1.tl1.do("RTRV-TU3::{}-{};".format(zq_tu3_idx,zq_j))
                        zq_msg=TL1message(NE1.tl1.get_last_outcome())
                        dprint(NE1.tl1.get_last_outcome(),1)
                        zq_sst=zq_msg.get_cmd_sst("{}-{}".format(zq_tu3_idx,zq_j))
                        if 'SDEE' in zq_sst:
                            dprint("OK\t\t{}-{} SST correctly contains SDEE".format(zq_tu3_idx,zq_j),2)
    
                            
                            '''
                            Verify TUn cannot be modified if LOVC3 cross-connections exist
                            '''
                    
                            zq_tl1_res=NE1.tl1.do("ED-PTF::MVC4-{}-{}::::CMDMDE=NORM,LOSTRUCT=63xTU12;".format(zq_mtxlo_slot,zq_i), policy='DENY')
                            zq_msg=TL1message(NE1.tl1.get_last_outcome())
                            dprint(NE1.tl1.get_last_outcome(),1)
                            zq_cmd=zq_msg.get_cmd_status()
                            if zq_cmd == (True,'DENY'):
                                dprint("\nOK\tEquipment SST in SDEE status correctly TUn structure cannot be modified",2)
                            else:
                                dprint("\nKO\tEquipment SST in SDEE status wrongly TUn structure can be modified",2)
                    
                        else:
                            dprint("KO\t\t{}-{} SST wrongly does not contain SDEE".format(zq_tu3_idx,zq_j),2)
                            
                        '''
                        Delete LOVC3 cross-connection
                        '''
                        zq_tl1_res=NE1.tl1.do("DLT-CRS-LOVC3::{}-{},{}-{}:::1WAY;".format(zq_tu3_idx,zq_j,zq_tu3_idx,zq_j))
                        zq_msg=TL1message(NE1.tl1.get_last_outcome())
                        dprint(NE1.tl1.get_last_outcome(),1)
                        zq_cmd=zq_msg.get_cmd_status()
                        if zq_cmd == (True,'COMPLD'):
                            dprint("\nOK\tCross-connection successfully deleted {}-{}".format(zq_tu3_idx,zq_j),2)
                            zq_tl1_res=NE1.tl1.do("RTRV-TU3::{}-{};".format(zq_tu3_idx,zq_j))
                            zq_msg=TL1message(NE1.tl1.get_last_outcome())
                            dprint(NE1.tl1.get_last_outcome(),1)
                            zq_sst=zq_msg.get_cmd_sst("{}-{}".format(zq_tu3_idx,zq_j))
                            if 'SDEE' in zq_sst:
                                dprint("KO\t\t{}-{} SST wrongly contains SDEE".format(zq_tu3_idx,zq_j),2)
                            else:
                                dprint("OK\t\t{}-{} SST correctly does not contain SDEE".format(zq_tu3_idx,zq_j),2)
                            
    
                    else:
                        dprint("\nKO\tCross-connection creation failed {}-{}\n".format(zq_tu3_idx,zq_j),2)
                    
                    
        self.stop_tps_block(NE1.id,"FM", "5-2-4-1")
        
        self.start_tps_block(NE1.id,"FM", "5-2-5-1")
        
                
        if len(zq_xc_list) == 1:
            zq_tl1_res=NE1.tl1.do("RTRV-CRS-VC4::ALL;")
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            if zq_msg.get_cmd_response_size() > 0:
                zq_xc_list=zq_msg.get_cmd_aid_list()
                zq_xc_list.insert(0,'EMPTY,EMPTY')

        '''
        Structure MVC4 to 63xTU12
        '''            
        for zq_i in range (1,len(zq_xc_list)):
            zq_mvc4_temp=zq_xc_list[zq_i].split(',')
            zq_mvc4_str=''.join(zq_mvc4_temp[1])
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::CMDMDE=FRCD,LOSTRUCT=63xTU12;".format(zq_mvc4_str))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            dprint(NE1.tl1.get_last_outcome(),1)
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                '''
                Verify MVC4 were correctly structured to 63xTU12
                '''            
                zq_tl1_res=NE1.tl1.do("RTRV-PTF::{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mvc4_str))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                zq_struct=zq_msg.get_cmd_attr_value("{}".format(zq_mvc4_str),'LOSTRUCT' )
                if (zq_cmd[1]=='COMPLD' and zq_struct=='63xTU12'):
                    dprint("\nOK\t{} structure changed to 63xTU12".format(zq_mvc4_str),2)
                    '''
                    Create/Delete 64x63LOVC12 cross-connections and verify MVC4TU12 SST contains/not contains SDEE
                    '''            
                    zq_tu12_tmp=zq_mvc4_str.replace('MVC4','MVC4TU12')
                    for zq_j in range(1,4):                                            #zq_j=TU3 index
                        for zq_k in range(1,8):                                        #zq_k=TU12 index
                            for zq_m in range(1,4):
                                zq_tu12_str=zq_tu12_tmp+'-'+str(zq_j)+'-'+str(zq_k)+'-'+str(zq_m)
                                zq_tl1_res=NE1.tl1.do("ENT-CRS-LOVC12::{},{}:::1WAY;".format(zq_tu12_str,zq_tu12_str))
                                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                                dprint(NE1.tl1.get_last_outcome(),1)
                                zq_cmd=zq_msg.get_cmd_status()
                                if zq_cmd == (True,'COMPLD'):
                                    dprint("\nOK\tCross-connection successfully created {}".format(zq_tu12_str),2)

                                    zq_tl1_res=NE1.tl1.do("RTRV-TU12::{};".format(zq_tu12_str))
                                    zq_msg=TL1message(NE1.tl1.get_last_outcome())
                                    dprint(NE1.tl1.get_last_outcome(),1)
                                    zq_sst=zq_msg.get_cmd_sst("{}".format(zq_tu12_str))
                                    if 'SDEE' in zq_sst:
                                        dprint("OK\t\t{} SST correctly contains SDEE".format(zq_tu12_str),2)
                
                                        
                                        '''
                                        Verify TUn cannot be modified if LOVC12 cross-connections exist
                                        '''
                                
                                        zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::CMDMDE=NORM,LOSTRUCT=3xTU3;".format(zq_mvc4_str), policy='DENY')
                                        zq_msg=TL1message(NE1.tl1.get_last_outcome())
                                        dprint(NE1.tl1.get_last_outcome(),1)
                                        zq_cmd=zq_msg.get_cmd_status()
                                        if zq_cmd == (True,'DENY'):
                                            dprint("\nOK\tEquipment SST in SDEE status correctly TUn structure cannot be modified",2)
                                        else:
                                            dprint("\nKO\tEquipment SST in SDEE status wrongly TUn structure can be modified",2)
                                
                                    else:
                                        dprint("KO\t\t{} SST wrongly does not contain SDEE".format(zq_tu12_str),2)
                            

                                    '''
                                    Delete LOVC12 cross-connection
                                    '''
                                    zq_tl1_res=NE1.tl1.do("DLT-CRS-LOVC12::{},{}:::1WAY;".format(zq_tu12_str,zq_tu12_str))
                                    zq_msg=TL1message(NE1.tl1.get_last_outcome())
                                    dprint(NE1.tl1.get_last_outcome(),1)
                                    zq_cmd=zq_msg.get_cmd_status()
                                    if zq_cmd == (True,'COMPLD'):
                                        dprint("\nOK\tCross-connection successfully deleted {}".format(zq_tu12_str),2)
                                        zq_tl1_res=NE1.tl1.do("RTRV-TU12::{};".format(zq_tu12_str))
                                        zq_msg=TL1message(NE1.tl1.get_last_outcome())
                                        dprint(NE1.tl1.get_last_outcome(),1)
                                        zq_sst=zq_msg.get_cmd_sst("{}".format(zq_tu12_str))
                                        if 'SDEE' in zq_sst:
                                            dprint("KO\t\t{} SST wrongly contains SDEE".format(zq_tu12_str),2)
                                        else:
                                            dprint("OK\t\t{} SST correctly does not contain SDEE".format(zq_tu12_str),2)
            

                                else:
                                    dprint("\nKO\tCross-connection creation failed {}".format(zq_tu12_str),2)

                                
                    
                else: 
                    dprint("\nOK\t{} structure NOT changed to 63xTU12",2)
                
                
            
            else:
                dprint("\nKO\t{} structure NOT changed to 63xTU12",2)
    
        '''
        Restore MVC4 structure to 3xTU3
        '''            
        for zq_i in range (1,len(zq_xc_list)):
            zq_mvc4_temp=zq_xc_list[zq_i].split(',')
            zq_mvc4_str=''.join(zq_mvc4_temp[1])
            zq_tl1_res=NE1.tl1.do("ED-PTF::{}::::CMDMDE=FRCD,LOSTRUCT=3xTU3;".format(zq_mvc4_str))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            dprint(NE1.tl1.get_last_outcome(),1)
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                '''
                Verify MVC4 were correctly structured to 3xTU3
                '''            
                zq_tl1_res=NE1.tl1.do("RTRV-PTF::{}::::PTFTYPE=MODVC4,PTFRATE=VC4;".format(zq_mvc4_str))
                zq_msg=TL1message(NE1.tl1.get_last_outcome())
                zq_cmd=zq_msg.get_cmd_status()
                zq_struct=zq_msg.get_cmd_attr_value("{}".format(zq_mvc4_str),'LOSTRUCT' )
                if (zq_cmd[1]=='COMPLD' and zq_struct=='3xTU3'):
                    dprint("\nOK\t{} structure changed to 3xTU3".format(zq_mvc4_str),2)
                else: 
                    dprint("\nKO\t{} structure NOT changed to 3xTU3",2)
            else:
                dprint("\nKO\t{} structure NOT changed to 3xTU3",2)
    
        '''
        Delete MVC4 cross-connection
        '''            
        for zq_i in range (1,len(zq_xc_list)):
            zq_tl1_res=NE1.tl1.do("DLT-CRS-VC4::{};".format(zq_xc_list[zq_i]))
            zq_msg=TL1message(NE1.tl1.get_last_outcome())
            zq_cmd=zq_msg.get_cmd_status()
            if zq_cmd == (True,'COMPLD'):
                dprint("\nOK\tCross-connection deletion successfull {}".format(zq_xc_list[zq_i]),2)
            else:    
                dprint("\nKO\tCross-connection deletion failed {}".format(zq_xc_list[zq_i]),2)
        


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
            print('Board Deleted: {}'.format(''.join(zq_board_to_remove[zq_i]).replace('10GSO','MDL')))



        
        '''
        #Remove board
        '''            
        Q010_Remove_Board(zq_mtxlo_slot)
      
        '''
        #Delete board
        '''            
        Q020_Delete_Board(zq_mtxlo_slot)



        self.stop_tps_block(NE1.id,"FM", "5-2-5-1")

        
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

