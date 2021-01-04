#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UNIT_TESTS: tests siswrapper
"""

__author__ = "Zenaro Stefano"
__version__ = "2020-11-14 1.0.0"

import os
import sys
import unittest

# import siswrapper from the ../siswrapper folder
curr_dir = os.path.realpath(os.path.dirname(__file__))
siswrapper_path = os.path.join(curr_dir, "..", "siswrapper")
sys.path.insert(1, os.path.realpath(siswrapper_path))
import siswrapper as sw

boold = True


class TestUtils(unittest.TestCase):

    def test_productionenv(self):
        """
        Makes sure we are running in production mode (when boold is False).
        """
        if not boold:
            self.assertFalse(sw.boold)

    def test_string_to_list(self):
        """
        Tests string_to_list() function.
        Converts a string to a list by using strip and split on a delimiter
        """
        tests = [
            {"i1": "", "i2": None, "o": [""]},
            {"i1": "   ", "i2": None, "o": [""]},
            {"i1": "       a      ", "i2": None, "o": ["a"]},
            {"i1": "      a b    ", "i2": None, "o": ["a", "b"]},
            {"i1": ",,a,b,c,d,,,,", "i2": ",", "o": ["a", "b", "c", "d"]}
        ]

        for test in tests:

            assert "i1" in test, ("Not well formatted input for testing ('i1' is missing in \"{}\")".format(test))
            assert "o" in test, ("Not well formatted input for testing ('o' is missing in \"{}\")".format(test))

            if test["i2"]:
                res = sw.string_to_list(test["i1"], test["i2"])
            else:
                res = sw.string_to_list(test["i1"])

            self.assertEqual(res, test["o"], "error during test: \"{}\"".format(test))

    def test_remove_empty_els(self):
        """
        Tests remove_empty_els() function.
        Removes empty strings inside a list.
        """
        tests = [
            {"i": [], "o": []},
            {"i": [""], "o": []},
            {"i": ["   "], "o": []},
            {"i": ["   ", "", " ", "     "], "o": []},
            {"i": ["   ", "a", "", " ", "     ", "c", "d", "test", "    "], "o": ["a", "c", "d", "test"]},
        ]

        for test in tests:
            assert "i" in test, ("Not well formatted input for testing ('i' is missing in \"{}\")".format(test))
            assert "o" in test, ("Not well formatted input for testing ('o' is missing in \"{}\")".format(test))

            res = sw.remove_empty_els(test["i"])
            self.assertEqual(res, test["o"], "error during test: \"{}\"".format(test))

    def test_str_to_numbers(self):
        """
        Tests str_to_numbers() function.
        Converts list of numeric strings into a list of integers.
        """
        tests = [
            {"i": [], "o": {"output": [], "errors": []}},
            {"i": [""], "o": {"output": [], "errors": ["Element(s) is/are not a number"]}},
            {"i": ["a"], "o": {"output": [], "errors": ["Element(s) is/are not a number"]}},
            {"i": ["1", "0", "a"], "o": {"output": [], "errors": ["Element(s) is/are not a number"]}},
            {"i": ["0", "1", "4"], "o": {"output": [0, 1, 4], "errors": []}},
            {"i": ["123456789"], "o": {"output": [123456789], "errors": []}},
        ]

        for test in tests:
            assert "i" in test, ("Not well formatted input for testing ('i' is missing in \"{}\")".format(test))
            assert "o" in test, ("Not well formatted input for testing ('o' is missing in \"{}\")".format(test))

            res = sw.str_to_numbers(test["i"])
            self.assertEqual(res, test["o"], "error during test: \"{}\"".format(test))
    
    @unittest.skip("TODO: write tests")
    def test_removeprefix(self):
        pass

    @unittest.skip("TODO: write tests")
    def test_removesuffix(self):
        pass


class TestSiswrapper(unittest.TestCase):

    def setUp(self):
        """
        Initializes a Siswrapper object.
        """
        self.sw_session = sw.Siswrapper()

        self.assertTrue(self.sw_session.started, "sis session should be running")
        self.assertFalse(self.sw_session.readsomething, "sis should be waiting to read an input")
        self.assertTrue(self.sw_session.res["success"], "sis session should be started successfully")
        self.assertEqual(self.sw_session.res["errors"], [], "there should be no errors when the session starts")

    def test_start(self):
        """
        Tests start() method, should fail because the session is already up and running.
        After the first fail the session is closed and then opened again.
        """
        # try to start the session manually while session is already running
        res = self.sw_session.start()
        self.assertFalse(res["success"], "action should fail, session is already running")
        self.assertIn("[ERROR][START] Couldn't start SIS: SIS's process is already running in this instance",
                      res["errors"], "error should be inside the errors list")
        self.assertTrue(self.sw_session.started, "sis session should still be running")

        # stop the session manually so that we can test start()
        res = self.sw_session.stop()
        self.assertTrue(res["success"], "action should be successfull, session can be stopped")
        self.assertEqual(res["errors"], [], "there should be no errors")
        self.assertFalse(self.sw_session.started, "sis sessions should be stopped")

        # start a session manually
        res = self.sw_session.start()
        self.assertTrue(res["success"], "action should be successfull, session can start")
        self.assertEqual(res["errors"], [], "there should be no errors")
        self.assertTrue(self.sw_session.started, "sis session should be running again")

    def test_stop(self):
        """
        Tests stop() method, should be successfull the first call.
        After that calling stop() a second time should fail.
        """
        # stop the session
        res = self.sw_session.stop()
        self.assertTrue(res["success"], "action should be successfull, session can be stopped")
        self.assertEqual(res["errors"], [], "there should be no errors")
        self.assertFalse(self.sw_session.started, "tmux and sis sessions should be stopped")

        # try to stop it again
        res = self.sw_session.stop()
        self.assertFalse(res["success"], "action should fail, session is not running")
        self.assertIn("[ERROR][STOP] Can't stop SIS: SIS's process is not running",
                      res["errors"], "error should be inside the errors list")
        self.assertFalse(self.sw_session.started, "tmux and sis sessions should still be stopped")

    def test_reset(self):
        """
        Tests reset() method, should be successfull while the session is running.
        When the session is stopped, reset() should fail.
        """
        # try to reset the session
        res = self.sw_session.reset()
        self.assertTrue(res["success"], "action should be successfull, session can be stopped")
        self.assertEqual(res["errors"], [], "there should be no errors")
        self.assertTrue(self.sw_session.started, "sis session should be up and running")

        # reset again
        res = self.sw_session.reset()
        self.assertTrue(res["success"], "action should be successfull, session can be stopped")
        self.assertEqual(res["errors"], [], "there should be no errors")
        self.assertTrue(self.sw_session.started, "sis session should be up and running")

        # stop the session
        res = self.sw_session.stop()
        self.assertTrue(res["success"], "action should be successfull, session can be stopped")
        self.assertEqual(res["errors"], [], "there should be no errors")
        self.assertFalse(self.sw_session.started, "sis session should be stopped")

        # try to reset while the session is stopped
        error = "[ERROR][RESET] Error while resetting (stop step): [ERROR][STOP] Can't stop SIS: SIS's process is not running"
        res = self.sw_session.reset()
        self.assertFalse(res["success"], "action should fail, session is not running")
        self.assertIn(error, res["errors"], "there should be an error")

    @unittest.skip("TODO: write tests")
    def test_wait_end_command(self):
        pass

    @unittest.skip("TODO: write tests")
    def test_exec(self):
        pass

    @unittest.skip("TODO: write tests")
    def test_parsed_exec(self):
        pass

    @unittest.skip("TODO: write tests")
    def test_interact(self):
        pass

    @unittest.skip("TODO: write tests")
    def test_manage_errors(self):
        pass

    # ====================================================================================================
    #
    #                                          READ METHODS
    #
    # ====================================================================================================

    def test_read_blif(self):
        """
        Tests read_blif() method, should be successfull when the session is running
        and when the input file exists.
        """
        # generate a random file name that points to a file that doesn't exist
        random_name = "file.that.does.not.exist"
        while os.path.isfile(random_name):
            random_name = os.urandom(10).hex()

        # try to open the file that doesn't exist
        file_path = os.path.join(curr_dir, random_name)
        res = self.sw_session.read_blif(file_path)
        self.assertFalse(res["success"], "action should fail, file doesn't exist")
        self.assertIn("[ERROR][READ_BLIF] '{}' file doesn't exist".format(file_path),
                      res["errors"], "there should be an error")

        # try to open a file that exists but not formatted correctly
        file_path = os.path.join(curr_dir, "err.blif")
        res = self.sw_session.read_blif(file_path)
        self.assertFalse(res["success"], "action should fail, file is not formatted correctly")
        self.assertIn('"{}", line 5: bad character in PLA table'.format(file_path), res["errors"], "there should be an error")

        # try to open a file that exists and is well formatted
        file_path = os.path.join(curr_dir, "and.blif")
        res = self.sw_session.read_blif(file_path)
        self.assertTrue(res["success"], "action should be successfull")
        self.assertEqual(res["errors"], [], "there should be no errors")

        # stop the session
        res = self.sw_session.stop()
        self.assertTrue(res["success"], "action should be successfull, session can be stopped")
        self.assertEqual(res["errors"], [], "there should be no errors")
        self.assertFalse(self.sw_session.started, "sis session should be stopped")

        # try to open the file that exists and is well formatted while the session is closed
        file_path = os.path.join(curr_dir, "and.blif")
        res = self.sw_session.read_blif(file_path)
        self.assertFalse(res["success"], "action should fail, session is closed")
        self.assertIn("[ERROR][READ_BLIF] Can't execute command: SIS's process is not running",
                      res["errors"], "there should be an error")

    @unittest.skip("TODO: write tests")
    def test_read_eqn(self):
        pass

    # ====================================================================================================
    #
    #                                          WRITE METHODS
    #
    # ====================================================================================================

    @unittest.skip("TODO: write tests")
    def test_write_blif(self):
        pass

    @unittest.skip("TODO: write tests")
    def test_write_eqn(self):
        pass

    # ====================================================================================================
    #
    #                                        SCRIPTS METHODS
    #
    # ====================================================================================================

    @unittest.skip("TODO: write tests")
    def test_script_rugged(self):
        pass

    # ====================================================================================================
    #
    #                                    PRINT/ECHO/SHOW METHODS
    #
    # ====================================================================================================

    @unittest.skip("TODO: write tests")
    def test_print_stats(self):
        pass

    # ====================================================================================================
    #
    #                                          OTHER METHODS
    #
    # ====================================================================================================

    @unittest.skip("TODO: write tests")
    def test_simulate(self):
        pass


if __name__ == "__main__":
    unittest.main()
