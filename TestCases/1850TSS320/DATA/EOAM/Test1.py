#!/usr/bin/env python
'''
TestCase template for K@TE test developers

[DESCRIPTION]
   Put your test decription here
[DESCRIPTION]
[TOPOLOGY] 1 [TOPOLOGY]
[DEPENDENCY]
   Insert Test dependencies
[DEPENDENCY]
[LAB] Insert the lab referneces i.e. SW,SVT [LAB]
[TPS]
   insert here the Test mapping
[TPS]
[RUNSECTIONS]
   Insert here the sections developed in this test i.e.
   DUTSet,testSet,testBody,testClean,DutClean,all
[RUNSECTIONS]
[AUTHOR] ippolf [AUTHOR]

'''

from katelibs.testcase          import TestCase
from katelibs.eqpt1850tss320    import Eqpt1850TSS320
from katelibs.instrumentONT     import InstrumentONT
#from katelibs.instrumentIXIA     import InstrumentIXIA
#from katelibs.instrumentSPIRENT  import InstrumentSPIRENT
from katelibs.swp1850tss320     import SWP1850TSS
from katelibs.database import TTest

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
        __a = TTest
        __b = ''
        print(__a.objects.all())
        for myobj in __a.objects.all():
            __b += str(myobj)+'\n'

        self.kenvironment.krepo.add_success(None, "Test1 DUT SetUp", '0', "Test1 DUT SetUp Output")
        self.kenvironment.krepo.add_success(None, "Getting DB Values", '0', __b)

    def test_setup(self):
        print('@Running test Setup...')
        self.kenvironment.krepo.add_success(None, "test1 SetUp", '0', "Test1 SetUp Output")

    def test_body(self):
        print('@Running Main Test...')
        self.start_tps_block(NE1.id, 'PROVIDER', '5-3-1')
        self.start_tps_block(NE1.id, 'DATAQOS', '5-3-2')
        self.kenvironment.krepo.add_success(None, "comando1_test1", '1', "output comando1 Test1 V3")
        self.kenvironment.krepo.add_success(None, "comando2_test1", '1', "output comando2")
        NE1.tl1.do("ACT-USER::admin:::Alcatel1;")
        self.stop_tps_block(NE1.id, 'DATAQOS', '5-3-2')
        self.start_tps_block(NE1.id, 'DATAQOS', '5-3-3')
        self.kenvironment.krepo.add_failure(None, "comando3_test1", '1', "output comando3 TPS V3", "mmm")
        self.stop_tps_block(NE1.id, 'DATAQOS', '5-3-3')

    def test_cleanup(self):
        print('@Running Test cleanUp...')
        self.kenvironment.krepo.add_success(None, "test1 CleanUp", '0', "test1 CleanUp Output")

    def dut_cleanup(self):

        print('@Running DUT cleanUp...')
        self.kenvironment.krepo.add_success(None, "test1 DUTCleanUp", '0', "test1 DUTCleanUp Output")
        self.stop_tps_block(NE1.id, 'PROVIDER', '5-3-1')

#Please don't change the code below

if __name__ == "__main__":
    #initializing the Test object instance and run the main flow
    CTEST = Test(__file__)
    
    NE1 = Eqpt1850TSS320('NE1', CTEST.kenvironment)
    
    CTEST.run()
    NE1.clean_up()
