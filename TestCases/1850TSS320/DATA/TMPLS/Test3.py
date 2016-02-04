#!/usr/bin/env python
"""
TestCase template for K@TE test developers

  :field Description: My test 'descritpion' 'row1
	:field Description:mytest descritpion row2
	:field Description:mytest decsr row3.
	
  :field Topology: 2
  
  :field Dependency: "None".
  
  :field Lab: SVT.
  
  :field TPS: EM__1-2-3
  :field TPS: TMPLS__5-3-13
  field TPS: TMPLS__5-3-22
  
  :field RunSections: 11111 
  
  :field Author: ippolf
"""
from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.instrumentONT     import InstrumentONT
#from katelibs.instrumentIXIA     import InstrumentIXIA
#from katelibs.instrumentSPIRENT  import InstrumentSPIRENT
from katelibs.swp1850tss320     import SWP1850TSS

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


    without input parameters all runSections will be ran
    '''

    def dut_setup(self):
        print('@Running DUT SetUp...')
        self.start_tps_block(NE1.id, "EM", "1-2-3")
        NE1.tl1.do("ACT-USER::admin:::Alcatel1;", policy="CMPLD")
        NE1.tl1.do("RTRV-COND-ALL;", policy="CMPLD")
        NE1.tl1.get_last_cmd_status()
        NE1.tl1.get_last_outcome()
        self.stop_tps_block(NE1.id, "EM", "1-2-3")

    def test_setup(self):
        print('@Running test Setup...')
        self.kenvironment.krepo.add_success(None, "test3 SetUp", '0', "Test3 SetUp Output")

    def test_body(self):
        print('@Running Main Test...')
        self.report.start_tps_block(NE1.id, 'TMPLS', '5-3-22')
        self.report.add_success(None, "comando1_test3", '1', "output comando1 Test3 V3")
        self.report.add_success(None, "comando2_test3", '1', "output comando2")
        self.kenvironment.krepo.stop_tps_block('TMPLS', '5-3-22')
        self.report.start_tps_block(NE1.id, 'TMPLS', '5-3-13')
        self.kenvironment.krepo.add_failure(None, "comando3_test3", '1', "output comando3 TPS V3", "mmm")
        self.report.stop_tps_block(NE1.id, 'TMPLS', '5-3-13')

    def test_cleanup(self):
        print('@Running Test cleanUp...')
        self.kenvironment.krepo.add_success(None, "test3 CleanUp", '0', "test3 CleanUp Output")

    def dut_cleanup(self):
        print('@Running DUT cleanUp...')
       


#Please don't change the code below

if __name__ == "__main__":
    #initializing the Test object instance, do not remove
    CTEST = Test(__file__)
    #initializing all local variable and constants used by Test object
    NE1 = Eqpt1850TSS320('NE1', CTEST.kenvironment)
    # Run Test main flow
    # Please don't touch this code
    CTEST.run()
    NE1.clean_up()