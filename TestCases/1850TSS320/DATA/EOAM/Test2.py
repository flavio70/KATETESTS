#!/usr/bin/env python
"""
TestCase template for K@TE test developers

  :field Description: EOAM Test2 description
	:field Description:mytest descritpion row2

	
  :field Topology: 1
  
  :field Dependency: "None".
  
  :field Lab: SVT.
  
  :field TPS: DATAQOS__5-4-2
  :field TPS: DATAQOS__5-4-3
  
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
        self.kenvironment.krepo.add_success(None, "Test2 DUT SetUp", '0', "Test2 DUT SetUp Output")

    def test_setup(self):
        print('@Running test Setup...')
        self.kenvironment.krepo.add_success(None, "test2 SetUp", '0', "Test2 SetUp Output")

    def test_body(self):
        print('@Running Main Test...')
        self.start_tps_block(NE1.id, 'DATAQOS', '5-4-2')
        self.kenvironment.krepo.add_success(None, "comando1_test2", '1', "output comando1 Test2 V3")
        self.kenvironment.krepo.add_success(None, "comando2_test2", '1', "output comando2")
        self.stop_tps_block(NE1.id, 'DATAQOS', '5-4-2')
        self.start_tps_block(NE1.id,'DATAQOS', '5-4-3')
        self.add_failure(None, "comando3_test2", '1', "output comando3 TPS V3", "mmm")
        self.stop_tps_block(NE1.id, 'DATAQOS', '5-4-3')

    def test_cleanup(self):
        print('@Running Test cleanUp...')
        self.kenvironment.krepo.add_success(None, "test2 CleanUp", '0', "test2 CleanUp Output")

    def dut_cleanup(self):

        print('@Running DUT cleanUp...')
        self.kenvironment.krepo.add_success(None, "test2 DUTCleanUp", '0', "test2 DUTCleanUp Output")



#Please don't change the code below

if __name__ == "__main__":
    #initializing the Test object instance and run the main flow
    CTEST = Test(__file__)
    NE1 = Eqpt1850TSS320('NE1', CTEST.kenvironment)
    CTEST.run()