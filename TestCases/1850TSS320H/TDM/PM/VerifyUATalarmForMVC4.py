#!/usr/bin/env python
"""
TestCase template for K@TE test developers

:field Description: This test provides a method to verify the TCA alarms is not present  
:field Description: when the MVC4 facility is OOS-MA and during error insertion. 
:field Description: As soon as the MVC4 is restored in IS-NR, the TCA alarms arise.
:field Topology: 1
:field Dependency: NA
:field Lab: SVT
:field TPS: PM__5-5-32-1
:field TPS: PM__5-5-32-2
:field TPS: PM__5-5-32-3
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
        VERIFY UAS COUNTER AND UAT ALARM FOR MVC4 FACILITIES
        '''
        print("\n*******************************************************************")
        print("\n   CONFIGURATION OF MVC4 AND LOVC3 CROSS-CONNECTION                ")
        print("\n*******************************************************************")
        
        self.start_tps_block(NE1.id,"PM","5-5-32-1")
        self.start_tps_block(NE1.id,"PM","5-5-32-2")
        self.start_tps_block(NE1.id,"PM","5-5-32-3")

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
        ### BEGIN ### Board equipment if not yet!
        '''
        zq_tl1_res=NE1.tl1.do("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
        zq_msg=TL1message(NE1.tl1.get_last_outcome())
        zq_cmd=zq_msg.get_cmd_status()
        if zq_cmd == (True,'COMPLD'):
            zq_attr_list1=zq_msg.get_cmd_attr_values("{}-{}".format(E_LO_MTX, zq_mtxlo_slot))
            zq_attr_list2=zq_msg.get_cmd_attr_values("{}-{}".format("MDL", zq_mtxlo_slot))

            if zq_attr_list1[0] is not None:
                if zq_attr_list1[0]['PROVISIONEDTYPE']==E_LO_MTX and zq_attr_list1[0]['ACTUALTYPE']==E_LO_MTX:  #Board equipped 
                    print("Board already equipped")
                else:
                    zq_filter=TL1check()
                    zq_filter.add_pst("IS")
                    zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                    NE1.tl1.do_until("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),zq_filter)
            else:
                if zq_attr_list2[0] is not None:
                    if zq_attr_list2[0]['ACTUALTYPE']==E_LO_MTX:  #Equip Board 
                        zq_filter=TL1check()
                        zq_filter.add_pst("IS")
                        zq_tl1_res=NE1.tl1.do("ENT-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot))
                        NE1.tl1.do_until("RTRV-EQPT::{}-{};".format(E_LO_MTX, zq_mtxlo_slot),zq_filter)
        '''
        ### END ### Board equipment if not yet!
        '''

        '''
        ### BEGIN ### Find 4 free slots and equip 4 x 1P10GSOE
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
        '''
        ### END ### Find 4 free slots and equip 4 x 1P10GSOE
        '''
        
        '''
        ### BEGIN ### Configure both ONT ports to VC3 mapping
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
        '''
        ### END ### Configure both ONT ports to VC3 mapping
        '''
        
        
        print("\n******************************************************************************")
        print("\n   CHECK 2xMVC4 in FIRST BLOCK                                                ")
        print("\n******************************************************************************")
        #Delete ALL PM data for 15min/24hour
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/15m/*")
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/24h/*")

        '''
        CHECK FIRST 128 BLOCK of MVC4 
        '''
        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_040_Modify_AU4_HO_Trace_Block(self, NE1, NE1_stm64p1, (E_VC4_1_1 % E_BLOCK_SIZE), 1, E_HO_TI)
        QS_040_Modify_AU4_HO_Trace_Block(self, NE1, NE1_stm64p2, (E_VC4_1_2 % E_BLOCK_SIZE), 1, E_HO_TI)
        
        QS_050_Modify_MVC4_HO_Trace_Block(self, NE1, zq_mtxlo_slot, E_VC4_1_1, 1, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, NE1, zq_mtxlo_slot, E_VC4_1_2, 1, E_HO_TI)
        
        QS_030_Create_LO_XC_Block(self, NE1, E_VC4_1_1, E_VC4_1_2, zq_xc_list)

        time.sleep(E_WAIT)
        
        QS_900_Set_Date(self, NE1,"16-05-02", "01-01-00")

        zq_vc4_ch1="{}.1.1.1".format(str(E_VC4_1_1 % E_BLOCK_SIZE))
        zq_vc4_ch2="{}.1.1.1".format(str(E_VC4_1_2 % E_BLOCK_SIZE))
         
        zq_vc4_idx1 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_1_1))
        zq_vc4_idx2 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_1_2)) 


        if QS_070_Check_No_Alarm(self, NE1, ONT, ONT_P1, ONT_P2, zq_vc4_ch1, zq_vc4_ch2):

            print("\n******************************************************************************")
            print("\n       ENABLE PM - WAIT FIRST PERIOD - VERIFY COUNTERS = 0                    ")
            print("\n******************************************************************************")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "NEND", "ON", "BOTH")

            if QS_120_Verify_PM_Counter_Zero(self, NE1, zq_vc4_idx1) == 0:
                dprint("OK\tAll PM counters are = 0",2)
                self.add_success(NE1, "PM counter reading","0.0", "All PM counters are = 0")
            else:
                dprint("KO\tSome PM counters are NOT = 0",2)
                self.add_failure(NE1, "PM counter reading","0.0", "PM counter reading", "Some PM counters are NOT = 0 " + QS_000_Print_Line_Function())

            print("\n******************************************************************************")
            print("\n       VERIFY UAT NEAR END                                                    ")
            print("\n******************************************************************************")

            QS_115_Check_UAT(self, NE1, ONT, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","15-MIN","RCV","AUAIS")
            
            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "NEND", "DISABLED", "BOTH")

            print("\n******************************************************************************")
            print("\n       VERIFY UAT FAR END                                                     ")
            print("\n******************************************************************************")
            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "FEND", "ON", "BOTH")
    
            QS_115_Check_UAT(self, NE1, ONT, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","15-MIN","RCV","HPRDI")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "FEND", "DISABLED", "BOTH")

            print("\n******************************************************************************")
            print("\n       VERIFY UAT BIDIR                                                       ")
            print("\n******************************************************************************")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "BIDIR", "ON", "1-DAY")

            QS_115_Check_UAT(self, NE1, ONT, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "BIDIR","1-DAY","RCV","HPRDI")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "BIDIR", "DISABLED", "1-DAY")


        QS_060_Delete_LO_XC_Block(self, NE1, E_VC4_1_1, E_VC4_1_2, zq_xc_list)
        
        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p2, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        print("\n******************************************************************************")
        print("\n   CHECK 2xMVC4 in SECOND BLOCK                                               ")
        print("\n******************************************************************************")
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/15m/*")
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/24h/*")

        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")

        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p4, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_050_Modify_MVC4_HO_Trace_Block(self, NE1, zq_mtxlo_slot, E_VC4_2_1, 1, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, NE1, zq_mtxlo_slot, E_VC4_2_2, 1, E_HO_TI)
        
        QS_030_Create_LO_XC_Block(self, NE1, E_VC4_2_1, E_VC4_2_2, zq_xc_list)
        
        time.sleep(E_WAIT)

        QS_900_Set_Date(self, NE1,"16-05-01", "02-00-00")
        
        print("\n******************************************************************************")
        print("\n       VERIFY BBE-ES-SES-UAS COUNTER NEAR END 15-MIN/1-DAY                    ")
        print("\n******************************************************************************")

        zq_vc4_ch1="{}.1.1.1".format(str(E_VC4_2_1 % E_BLOCK_SIZE))
        zq_vc4_ch2="{}.1.1.1".format(str(E_VC4_2_2 % E_BLOCK_SIZE))
         
        zq_vc4_idx1 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_2_1))
        zq_vc4_idx2 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_2_2)) 
    
        if QS_070_Check_No_Alarm(self, NE1, ONT, ONT_P1, ONT_P2, zq_vc4_ch1, zq_vc4_ch2):

            print("\n******************************************************************************")
            print("\n       ENABLE PM - WAIT FIRST PERIOD - VERIFY COUNTERS = 0                    ")
            print("\n******************************************************************************")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "NEND", "ON", "BOTH")

            if QS_120_Verify_PM_Counter_Zero(self, NE1, zq_vc4_idx1) == 0:
                dprint("OK\tAll PM counters are = 0",2)
                self.add_success(NE1, "PM counter reading","0.0", "All PM counters are = 0")
            else:
                dprint("KO\tSome PM counters are NOT = 0",2)
                self.add_failure(NE1, "PM counter reading","0.0", "PM counter reading", "Some PM counters are NOT = 0 " + QS_000_Print_Line_Function())

            print("\n******************************************************************************")
            print("\n       VERIFY UAT NEAR END                                                    ")
            print("\n******************************************************************************")

            QS_115_Check_UAT(self, NE1, ONT, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","15-MIN","RCV","AUAIS")
            
            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "NEND", "DISABLED", "BOTH")

            print("\n******************************************************************************")
            print("\n       VERIFY UAT FAR END                                                     ")
            print("\n******************************************************************************")
            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "FEND", "ON", "BOTH")
    
            QS_115_Check_UAT(self, NE1, ONT, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","15-MIN","RCV","HPRDI")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "FEND", "DISABLED", "BOTH")

            print("\n******************************************************************************")
            print("\n       VERIFY UAT BIDIR                                                       ")
            print("\n******************************************************************************")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "BIDIR", "ON", "1-DAY")

            QS_115_Check_UAT(self, NE1, ONT, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "BIDIR","1-DAY","RCV","HPRDI")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "BIDIR", "DISABLED", "1-DAY")

 
        QS_060_Delete_LO_XC_Block(self, NE1, E_VC4_2_1, E_VC4_2_2, zq_xc_list)
        
        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p4, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p1, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p2, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)

        
        print("\n******************************************************************************")
        print("\n   CHECK 2xMVC4 in THIRD BLOCK                                                ")
        print("\n******************************************************************************")
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/15m/*")
        NE1.flc_send_cmd("rm /pureNeApp/FLC/DB/PM/rack-01/subrack-01/tdm/24h/*")

        zq_xc_list=list()
        zq_xc_list.append("EMPTY,EMPTY")

        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p5, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p6, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p3, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p4, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p1, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_010_Create_HO_XC_Block(self, NE1, NE1_stm64p2, 1, E_BLOCK_SIZE, zq_xc_list)

        QS_050_Modify_MVC4_HO_Trace_Block(self, NE1, zq_mtxlo_slot, E_VC4_3_1, 1, E_HO_TI)
        QS_050_Modify_MVC4_HO_Trace_Block(self, NE1, zq_mtxlo_slot, E_VC4_3_2, 1, E_HO_TI)
        
        QS_030_Create_LO_XC_Block(self, NE1, E_VC4_3_1, E_VC4_3_2, zq_xc_list)
        
        time.sleep(E_WAIT)

        QS_900_Set_Date(self, NE1,"16-05-01", "03-00-00")
        
        zq_vc4_ch1="{}.1.1.1".format(str(E_VC4_3_1 % E_BLOCK_SIZE))
        zq_vc4_ch2="{}.1.1.1".format(str(E_VC4_3_2 % E_BLOCK_SIZE))
         
        zq_vc4_idx1 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_3_1))
        zq_vc4_idx2 = "MVC4-{}-{}".format(zq_mtxlo_slot,str(E_VC4_3_2)) 
    
        if QS_070_Check_No_Alarm(self, NE1, ONT, ONT_P1, ONT_P2, zq_vc4_ch1, zq_vc4_ch2):

            print("\n******************************************************************************")
            print("\n       ENABLE PM - WAIT FIRST PERIOD - VERIFY COUNTERS = 0                    ")
            print("\n******************************************************************************")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "NEND", "ON", "BOTH")

            if QS_120_Verify_PM_Counter_Zero(self, NE1, zq_vc4_idx1) == 0:
                dprint("OK\tAll PM counters are = 0",2)
                self.add_success(NE1, "PM counter reading","0.0", "All PM counters are = 0")
            else:
                dprint("KO\tSome PM counters are NOT = 0",2)
                self.add_failure(NE1, "PM counter reading","0.0", "PM counter reading", "Some PM counters are NOT = 0 " + QS_000_Print_Line_Function())

            print("\n******************************************************************************")
            print("\n       VERIFY UAT NEAR END                                                    ")
            print("\n******************************************************************************")

            QS_115_Check_UAT(self, NE1, ONT, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "NEND","15-MIN","RCV","AUAIS")
            
            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "NEND", "DISABLED", "BOTH")

            print("\n******************************************************************************")
            print("\n       VERIFY UAT FAR END                                                     ")
            print("\n******************************************************************************")
            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "FEND", "ON", "BOTH")
    
            QS_115_Check_UAT(self, NE1, ONT, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "FEND","15-MIN","RCV","HPRDI")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "FEND", "DISABLED", "BOTH")

            print("\n******************************************************************************")
            print("\n       VERIFY UAT BIDIR                                                       ")
            print("\n******************************************************************************")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "BIDIR", "ON", "1-DAY")

            QS_115_Check_UAT(self, NE1, ONT, ONT_P1, ONT_P2, zq_mtxlo_slot, zq_vc4_idx1, zq_vc4_idx2, "BIDIR","1-DAY","RCV","HPRDI")

            QS_090_Set_PM_Mode(self, NE1, zq_vc4_idx1, "BIDIR", "DISABLED", "1-DAY")

        QS_060_Delete_LO_XC_Block(self, NE1, E_VC4_3_1, E_VC4_3_2, zq_xc_list)
        
        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p5, 1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p6, E_BLOCK_SIZE+1, E_BLOCK_SIZE, zq_xc_list)

        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p3, E_BLOCK_SIZE*2+1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p4, E_BLOCK_SIZE*3+1, E_BLOCK_SIZE, zq_xc_list)
        
        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p1, E_BLOCK_SIZE*4+1, E_BLOCK_SIZE, zq_xc_list)
        QS_020_Delete_HO_XC_Block(self, NE1, NE1_stm64p2, E_BLOCK_SIZE*5+1, E_BLOCK_SIZE, zq_xc_list)


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

        
        self.stop_tps_block(NE1.id,"PM","5-5-32-1")
        self.stop_tps_block(NE1.id,"PM","5-5-32-2")
        self.stop_tps_block(NE1.id,"PM","5-5-32-3")


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
    