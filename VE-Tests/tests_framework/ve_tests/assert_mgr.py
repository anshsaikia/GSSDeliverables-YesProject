import sys

__author__ = 'tchevall'


# The aim of this class is to setup some CheckPoint (ie. some assert) in a test function and to check the assert at the
# end of the function
class AssertMgr(object) :
    class CheckPoint(object):
        def __init__(self, name, index, condition, reason) :
            self.name = name
            self.index = index
            self.condition = condition
            self.reason = reason

        def __str__(self):
            if self.condition:
                return "[ "+str(self.name)+"] assert_"+str(self.index)+": True "
            else:
                try:
                    return "[ "+str(self.name)+"] assert_"+str(self.index)+": False because :" + str(self.reason)
                except UnicodeEncodeError:
                    return "[ "+str(self.name)+"] assert_"+str(self.index)+": False because :" + self.reason
                except:
                    return "[ "+str(self.name)+"] assert_"+str(self.index)+": False"

    class Failure(Exception):
        pass

    def __init__(self, vetest):
        self.asserts = []
        self.vetest = vetest
        self.current_test = ""
        self.current_index = 0

    def setup(self, test_name, start_index=0):
        self.current_index = start_index
        self.current_test = test_name

    # Add a checkPoint in a function
    def addCheckPoint(self, testName, index, condition, reason):
        self.asserts.append(self.CheckPoint(testName, index, condition, reason))

    def addCheckPointLight(self, condition, reason, do_exception=True):
        f_code = sys._getframe().f_back.f_code
        log_localisation = "{}:{:4} > {}()".format(f_code.co_filename.split("/")[-1], f_code.co_firstlineno, f_code.co_name)
        self.addCheckPoint("{:>30}: {:70}".format( self.current_test,log_localisation), self.current_index, condition,
                           "Internal check:"+reason)
        self.current_index += 1
        if do_exception and not condition:
            raise AssertMgr.Failure()

    # Check at the end of a test function all asserts (CheckPoint) that as been inserted
    def verifyAllCheckPoints(self):
        condition = True
        failed_msg = "\n"
        for cp in self.asserts:
            condition = condition and cp.condition
            if cp.condition is False:
                failed_msg += str(cp) + '\n'

        self.vetest.logger.log_assert(condition, "Failed asserts : "+ failed_msg)
