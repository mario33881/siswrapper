#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SISWRAPPER: wraps SIS so that it can be controlled using python
> SIS is tool for synthesis and optimization of sequential circuits
> (https://jackhack96.github.io/logic-synthesis/sis.html#overview)

Requirements:
* pexpect: python library that can communicate with an interactive shell's process
* SIS: the tool for synthesis and optimization of sequential circuits
"""

__author__ = "Zenaro Stefano"

import os
import re

import pexpect

try:
    from ._version import __version__  # noqa: F401
except ImportError:
    from _version import __version__  # noqa: F401


def string_to_list(t_str, t_char=" "):
    """
    Returns a list of elements that are contains inside the string param.

    :param str t_str: string with elements and delimiters
    :param str t_char: delimiter of the elements
    :return list t_list: list of elements that were inside t_str
    """
    t_list = t_str.strip(t_char).split(t_char)
    return t_list


def remove_empty_els(t_v):
    """
    Returns a list that doesn't contain empty strings.
    :param list t_v: list of elements
    :return list t_parsed_v: list of elements (no empty strings)
    """
    t_parsed_v = []
    for el in t_v:
        if el.strip() != "":
            t_parsed_v.append(el.strip())

    return t_parsed_v


def str_to_numbers(t_v):
    """
    Returns a dictionary with a list of integers (converts strings into integers).

    :param list t_v: list of numbers (string type)
    :return dict out: dictionary with errors or the list of numbers converted to the integer type
    """
    out = {"output": [], "errors": []}

    try:
        for el in t_v:
            out["output"].append(int(el))
    except ValueError:
        out["output"] = []
        out["errors"].append("Element(s) is/are not a number")

    return out


def removeprefix(string, prefix):
    """
    Returns <string> without the <prefix> prefix.

    Copied from https://www.python.org/dev/peps/pep-0616/#specification
    to support python versions < 3.9

    :param str string: string from which to remove prefix
    :param str prefix: prefix to remove from string
    :return str: string without prefix
    """
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string[:]


def removesuffix(string, suffix):
    """
    Returns <string> without the <suffix> suffix.

    Copied from https://www.python.org/dev/peps/pep-0616/#specification
    to support python versions < 3.9

    :param str string: string from which to remove suffix
    :param str suffix: suffix to remove from string
    :return str: string without suffix
    """
    # suffix='' should not call self[:-0].
    if suffix and string.endswith(suffix):
        return string[:-len(suffix)]
    else:
        return string[:]


class Siswrapper:
    """
    Initializes a wrapper for a SIS process.

    After the creation of an instance
    a SIS process is ready to receive commands.

    Shared variables:
    * res: dictionary with results of the start operation (success, errors, stdout)
    * sis: connection to SIS's process
    * started: boolean that is set to True if SIS's process is started
    * readsomething: boolean that is set to True if a correct input has been read by SIS
    * read_path: string that contains the path of the read input file
    """

    def __init__(self):
        self.res = {"success": False, "errors": [], "stdout": None}
        self.sis = None
        self.started = False
        self.readsomething = False
        self.read_path = None

        start_res = self.start()

        if start_res["success"]:
            self.started = True
            self.res["stdout"] = start_res["stdout"]
            self.res["success"] = True
        else:
            for error in start_res["errors"]:
                self.res["errors"].append("[ERROR][INIT] Error while initializing (start step): " + error)

    def start(self):
        """
        Starts SIS's process.

        First the method tries to spawn the process.
        If the process responds with the sis> prompt (after some waiting using the wait_end_command() method),
        then the process started correctly.

        :return dict res: results of the operation (success, errors, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        if not self.started:
            try:
                self.sis = pexpect.spawn('sis')

                wait_res = self.wait_end_command()

                if wait_res["success"]:
                    self.started = True

                    res["success"] = True
                    res["stdout"] = wait_res["stdout"]
                else:
                    for error in wait_res["errors"]:
                        res["errors"].append("[ERROR][START] Error while waiting SIS's startup: " + error)

            except pexpect.exceptions.ExceptionPexpect:
                res["errors"].append("[ERROR][START] Couldn't start SIS: check if "
                                     "SIS is installed and callable from the terminal")
        else:
            res["errors"].append("[ERROR][START] Couldn't start SIS: "
                                 "SIS's process is already running in this instance")

        return res

    def reset(self):
        """
        Resets SIS's process.

        First the method tries to stop the process by calling the stop() method
        and then it calls the start() method to start the process.

        :return dict res: results of the operation (success, errors, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        stop_res = self.stop()
        if stop_res["success"]:
            start_res = self.start()
            if start_res["success"]:
                res["success"] = True
                res["stdout"] = start_res["stdout"]
            else:
                for error in start_res["errors"]:
                    res["errors"].append("[ERROR][RESET] Error while resetting (start step): " + error)
        else:
            for error in stop_res["errors"]:
                res["errors"].append("[ERROR][RESET] Error while resetting (stop step): " + error)

        return res

    def stop(self):
        """
        Stops SIS's process.

        First the method tries to exit normally by executing the quit command.
        If it doesn't work the method closes the connection to the process
        and terminates it.

        :return dict res: results of the operation (success, errors, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        if self.started:
            # try to exit SIS normally
            self.sis.sendline("quit")

            if not self.sis.isalive():
                res["success"] = True
                self.started = False
            else:
                # close connection and terminate process forcefully
                self.sis.close(force=True)

                if not self.sis.isalive():
                    res["success"] = True
                    self.started = False
                else:
                    res["errors"].append("[ERROR][STOP] Couldn't stop the process")
        else:
            res["errors"].append("[ERROR][STOP] Can't stop SIS: SIS's process is not running")

        return res

    def wait_end_command(self, t_command=""):
        """
        Waits the end of a command execution.

        It waits for the "sis>" prompt to appear.

        If the command is shown in pages where you need to press a key to show more,
        it sends spaces until the "sis>" prompt is shown.

        :param str t_command: command that was executed by exec (optional, not needed during the start() method)
        :return dict res: results of the operation (success, errors, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        try:
            output = ""
            paginated = False
            while True:
                # try to find the prompt or "--More--(xy%)" (paginated output)
                match = self.sis.expect(["sis>", r"--(.*)--\((.*)%\)"])
                page = self.sis.before.decode("utf-8")
                output += page
                if match == 0:
                    # the prompt was found: all the output is in the output variable
                    break
                elif match == 1:
                    # we are reading paginated output, use spaced to scroll through all the text
                    paginated = True
                    self.sis.send(" ")

            # If the command's output was divided in pages 
            # the first line is probably the command itself: if so then remove it
            if paginated:
                v_output = output.split("\r\n")
                if len(v_output) > 1:
                    if v_output[0].strip() == t_command:
                        v_output.pop(0)
                        output = "\r\n".join(v_output)

            res["success"] = True
            res["stdout"] = output

        except pexpect.exceptions.TIMEOUT:
            res["errors"].append("[ERROR][WAIT_END_COMMAND] Timeout while waiting the end of command execution")

        except pexpect.exceptions.EOF:
            # entered "quit" or "exit" command
            res["success"] = True

        return res

    def exec(self, t_command):
        """
        Executes the <t_command> command using SIS.

        TODO: this method should probably call the stop() method
        when someone executes the "quit" or "exit" command
        > the advantage of using that method is that the method
        > checks if SIS's process stopped running.
        > Currently passing "quit"/"exit" to this method
        > assumes that the command execution is successfull.

        :param str t_command: command to execute using SIS
        :return dict res: results of the operation (success, errors, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        if self.started:
            self.sis.sendline(t_command.strip())

            wait_res = self.wait_end_command(t_command)
            if wait_res["success"]:
                res["success"] = True

                # Remove the command from the output
                res["stdout"] = wait_res["stdout"]
                if wait_res["stdout"] is not None:
                    res["stdout"] = removeprefix(wait_res["stdout"].strip(), t_command).strip()
                else:
                    # if command was quit or exit, change self.started state
                    if t_command.strip() in ["quit", "exit"]:
                        self.started = False

                if res["stdout"] == "":
                    res["stdout"] = None
            else:
                for error in wait_res["errors"]:
                    res["errors"].append("[ERROR][EXEC] Error while waiting for the end of the command: " + error)
        else:
            res["errors"].append("[ERROR][EXEC] Can't execute command: SIS's process is not running")

        return res

    def parsed_exec(self, t_command):  # noqa: C901
        """
        Parses and executes the <t_command> command as best as it thinks it can.

        First it tries to find the correct method to call to execute the command.
        If this method doesn't find the best method for that command, it is
        executed by the self.exec() method.

        :param str t_command: command to execute using SIS
        :return dict cmd_res: results of the operation (success, errors, stdout)
        """
        cmd_res = {"success": False, "errors": [], "stdout": None}
        strip_cmd = t_command.strip()

        # read_blif
        if re.match(r"^read_blif [\s]*-a [\s]*(\S*)$", strip_cmd):
            param = re.match(r"^read_blif [\s]*-a [\s]*(\S*)$", strip_cmd).groups()[0]
            param = param.strip('"')
            cmd_res = self.read_blif(param, t_append=True)

        elif re.match(r"^read_blif [\s]*(\S*) [\s]*-a$", strip_cmd):
            param = re.match(r"^read_blif [\s]*(\S*) [\s]*-a$", strip_cmd).groups()[0]
            param = param.strip('"')
            cmd_res = self.read_blif(param, t_append=True)

        elif re.match(r"^read_blif [\s]*(\S*)$", strip_cmd):
            param = re.match(r"^read_blif [\s]*(\S*)$", strip_cmd).groups()[0]
            param = param.strip('"')
            cmd_res = self.read_blif(param)

        # read_eqn
        elif re.match(r"^read_eqn [\s]*-a [\s]*(\S*)$", strip_cmd):
            param = re.match(r"^read_eqn [\s]*-a [\s]*(\S*)$", strip_cmd).groups()[0]
            param = param.strip('"')
            cmd_res = self.read_eqn(param, t_append=True)

        elif re.match(r"^read_eqn [\s]*(\S*) [\s]*-a$", strip_cmd):
            param = re.match(r"^read_eqn [\s]*(\S*) [\s]*-a$", strip_cmd).groups()[0]
            param = param.strip('"')
            cmd_res = self.read_eqn(param, t_append=True)

        elif re.match(r"^read_eqn [\s]*(\S*)$", strip_cmd):
            param = re.match(r"^read_eqn [\s]*(\S*)$", strip_cmd).groups()[0]
            param = param.strip('"')
            cmd_res = self.read_eqn(param)

        # write_blif
        elif re.match(r"^write_blif [\s]*(\S*)$", strip_cmd):
            param = re.match(r"^write_blif [\s]*(\S*)$", strip_cmd).groups()[0]
            param = param.strip('"')
            cmd_res = self.write_blif(param)

        # write_eqn
        elif re.match(r"^write_eqn [\s]*(\S*)$", strip_cmd):
            param = re.match(r"^write_eqn [\s]*(\S*)$", strip_cmd).groups()[0]
            param = param.strip('"')
            cmd_res = self.write_eqn(param)

        # source script.rugged
        elif strip_cmd == "source script.rugged":
            cmd_res = self.script_rugged()

        # print_stats
        elif strip_cmd == "print_stats":
            cmd_res = self.print_stats()

        # simulate
        elif re.match(r"^simulate [\s]*(.*)$", strip_cmd):
            param = re.match(r"^simulate [\s]*(.*)$", strip_cmd).groups()[0]
            cmd_res = self.simulate(param)

        elif re.match(r"^sim [\s]*(.*)$", strip_cmd):
            param = re.match(r"^sim [\s]*(.*)$", strip_cmd).groups()[0]
            cmd_res = self.simulate(param)

        # bsis_script command
        elif strip_cmd.startswith("bsis_script"):
            param = strip_cmd.replace("bsis_script", "").strip()
            if param == "fsm_autoencoding_area":
                cmd_res = self.bsisscript_fsm(autoencoding=True, opt_area=True)
            elif param == "fsm_autoencoding_delay":
                cmd_res = self.bsisscript_fsm(autoencoding=True, opt_area=False)
            elif param == "fsm_area":
                cmd_res = self.bsisscript_fsm(autoencoding=False, opt_area=True)
            elif param == "fsm_delay":
                cmd_res = self.bsisscript_fsm(autoencoding=False, opt_area=False)
            elif param == "lgate_area_mcnc":
                cmd_res = self.bsisscript_lgate(opt_area=True, library="mcnc")
            elif param == "lgate_delay_mcnc":
                cmd_res = self.bsisscript_lgate(opt_area=False, library="mcnc")
            elif param == "lgate_area_synch":
                cmd_res = self.bsisscript_lgate(opt_area=True, library="synch")
            elif param == "lgate_delay_synch":
                cmd_res = self.bsisscript_lgate(opt_area=False, library="synch")
            elif param == "fsmd_area":
                cmd_res = self.bsisscript_fsmd(opt_area=True)
            elif param == "fsmd_delay":
                cmd_res = self.bsisscript_fsmd(opt_area=False)
            else:
                cmd_res = {"success": False,
                           "errors": ["[ERROR][BSIS_SCRIPT] Unexpected bsis_script parameter"],
                           "stdout": None}

        # stg_to_network
        elif strip_cmd == "stg_to_network":
            cmd_res = self.stg_to_network()

        # command not found... execute it
        else:
            cmd_res = self.exec(strip_cmd)

        return cmd_res

    def interact(self):
        """
        Gives SIS control to the user.
        """
        if self.started:
            self.sis.interact()
        else:
            raise Exception("SIS's process is not running")

    def manage_errors(self, t_output):
        """
        Manages not easily understandable errors.

        :param str t_output: string with error
        :return str detailed_output: detailed error.
        """
        detailed_output = t_output
        if "must give F or R, but not both" in t_output:
            detailed_output += " (use maxterms, zeros, or minterms, ones, to describe the function)"

        return detailed_output

    # ====================================================================================================
    #
    #                                          READ METHODS
    #
    # ====================================================================================================

    def read_blif(self, t_file, t_changedir=True, t_append=False):
        """
        Executes SIS' read_blif command which reads .blif files.

        :param str t_file: path to the .blif file
        :param bool t_changedir: True means change working directory to the blif directory
        :param bool t_append: True means append file to the current network
        :return dict res: results of the operation (success, errors, warnings, stdout)
        """
        res = {"success": False, "errors": [], "warnings": [], "stdout": None}

        if self.started:
            blif_fullpath = os.path.realpath(t_file)
            blif_path = os.path.dirname(blif_fullpath)

            if t_changedir:
                os.chdir(blif_path)
                self.reset()

            if os.path.isfile(blif_fullpath):
                if t_append:
                    exec_res = self.exec('read_blif -a "' + blif_fullpath + '"')
                else:
                    exec_res = self.exec('read_blif "' + blif_fullpath + '"')

                if exec_res["success"]:
                    res["stdout"] = exec_res["stdout"]

                    if exec_res["stdout"]:
                        found_errors = False

                        for message in res["stdout"].split("\r\n"):
                            if message.strip().startswith("Warning: "):
                                warning = self.manage_errors(message.strip())
                                res["warnings"].append(warning)
                            else:
                                error = self.manage_errors(message.strip())
                                res["errors"].append(error)
                                found_errors = True

                        if not found_errors:
                            res["success"] = True
                            self.readsomething = True
                            self.read_path = blif_fullpath
                    else:
                        res["success"] = True
                        self.readsomething = True
                        self.read_path = blif_fullpath
                else:
                    for error in exec_res["errors"]:
                        res["errors"].append("[ERROR][READ_BLIF] Error during execution: " + error)
            else:
                res["errors"].append("[ERROR][READ_BLIF] '{}' file doesn't exist".format(blif_fullpath))
        else:
            res["errors"].append("[ERROR][READ_BLIF] Can't execute command: SIS's process is not running")

        return res

    def read_eqn(self, t_file, t_changedir=True, t_append=False):
        """
        Executes SIS' read_eqn command which reads .eqn (equation) files.
        :param str t_file: path to the .eqn file
        :param bool t_changedir: True means change working directory to the eqn directory
        :param bool t_append: True means append file to the current network
        :return dict res: results of the operation (success, errors, warnings, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        if self.started:
            eqn_fullpath = os.path.realpath(t_file)
            eqn_path = os.path.dirname(eqn_fullpath)

            if t_changedir:
                os.chdir(eqn_path)
                self.reset()

            if os.path.isfile(eqn_fullpath):
                if t_append:
                    exec_res = self.exec('read_eqn -a "' + eqn_fullpath + '"')
                else:
                    exec_res = self.exec('read_eqn "' + eqn_fullpath + '"')

                if exec_res["success"]:
                    res["stdout"] = exec_res["stdout"]

                    if exec_res["stdout"]:
                        found_errors = False

                        for message in res["stdout"].split("\r\n"):
                            if message.strip().startswith("Warning: "):
                                warning = self.manage_errors(message.strip())
                                res["warnings"].append(warning)
                            else:
                                error = self.manage_errors(message.strip())
                                res["errors"].append(error)
                                found_errors = True

                        if not found_errors:
                            res["success"] = True
                            self.readsomething = True
                            self.read_path = eqn_fullpath
                    else:
                        res["success"] = True
                        self.readsomething = True
                        self.read_path = eqn_fullpath
                else:
                    for error in exec_res["errors"]:
                        res["errors"].append("[ERROR][READ_EQN] Error during execution: " + error)
            else:
                res["errors"].append("[ERROR][READ_EQN] '{}' file doesn't exist".format(eqn_fullpath))
        else:
            res["errors"].append("[ERROR][READ_EQN] Can't execute command: SIS's process is not running")

        return res

    # ====================================================================================================
    #
    #                                          WRITE METHODS
    #
    # ====================================================================================================

    def write_blif(self, t_file="", t_params=""):
        """
        Executes SIS' write_blif command which outputs the circuit to a .blif file.

        :param str t_file: file path of the output
        :param str t_params: extra parameters
        :return dict res: results of the operation (success, errors, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        if self.started:
            if self.readsomething:

                if t_file == "" and t_params == "":
                    exec_res = self.exec('write_blif')
                elif t_params == "" and t_file != "":
                    exec_res = self.exec('write_blif ' + t_file)
                elif t_params != "" and t_file == "":
                    exec_res = self.exec('write_blif ' + t_params)
                else:
                    exec_res = self.exec('write_blif ' + t_params + ' ' + t_file)

                res["stdout"] = exec_res["stdout"]

                if exec_res["success"]:
                    if t_file == "" and t_params == "":
                        res["success"] = True
                    else:
                        if res["stdout"] is None:
                            res["success"] = True
                        else:
                            res["errors"].append("[ERROR][WRITE_BLIF] Something went wrong during write_blif")
                else:
                    for error in exec_res["errors"]:
                        res["errors"].append("[ERROR][WRITE_BLIF] Error during execution: " + error)
            else:
                res["errors"].append("[ERROR][WRITE_BLIF] Nothing to write/show "
                                     "(missing an input, use read_blif or another read command)")
        else:
            res["errors"].append("[ERROR][WRITE_BLIF] Can't execute command: SIS's process is not running")

        return res

    def write_eqn(self, t_file="", t_params=""):
        """
        Executes SIS' write_eqn command which outputs the circuit to a .eqn (equation) file.

        :param str t_file: file path of the output (empty = print current network)
        :param str t_params: extra parameters (empty = no extra parameters)
        :return dict res: results of the operation (success, errors, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        if self.started:
            if self.readsomething:

                if t_file == "" and t_params == "":
                    exec_res = self.exec('write_eqn')
                elif t_params == "" and t_file != "":
                    exec_res = self.exec('write_eqn ' + t_file)
                elif t_params != "" and t_file == "":
                    exec_res = self.exec('write_eqn ' + t_params)
                else:
                    exec_res = self.exec('write_eqn ' + t_params + ' ' + t_file)

                res["stdout"] = exec_res["stdout"]

                if exec_res["success"]:
                    if t_file == "" and t_params == "":
                        res["success"] = True
                    else:
                        if exec_res["stdout"] is None:
                            res["success"] = True
                        else:
                            res["errors"].append("[ERROR][WRITE_EQN] Something went wrong during write_eqn")
                else:
                    for error in exec_res["errors"]:
                        res["errors"].append("[ERROR][WRITE_EQN] Error during execution: " + error)
            else:
                res["errors"].append("[ERROR][WRITE_EQN] Nothing to write/show "
                                     "(missing an input, use read_blif or another read command)")
        else:
            res["errors"].append("[ERROR][WRITE_EQN] Can't execute command: SIS's process is not running")

        return res

    # ====================================================================================================
    #
    #                                        SCRIPTS METHODS
    #
    # ====================================================================================================

    def script_rugged(self):
        """
        Executes rugged script with SIS.

        :return dict res: results of the operation (success, errors, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        if self.started:
            if self.readsomething:
                exec_res = self.exec("source script.rugged")
                if exec_res["success"]:
                    res["stdout"] = exec_res["stdout"]

                    if res["stdout"] is None:
                        res["success"] = True
                else:
                    for error in exec_res["errors"]:
                        res["errors"].append("[ERROR][SCRIPT_RUGGED] Error during execution: " + error)
            else:
                res["errors"].append("[ERROR][SCRIPT_RUGGED] Nothing to optimize "
                                     "(missing an input, use read_blif or another read command)")
        else:
            res["errors"].append("[ERROR][SCRIPT_RUGGED] Can't execute command: SIS's process is not running")

        return res

    def bsisscript_fsm(self, autoencoding, opt_area):  # noqa: C901
        """
        Executes many commands to optimize and map an FSM using SIS.

        * state_minimize stamina
        * state_assign jedi / stg_to_network (autoencoding True/False)
        * reduce_depth if opt_area is False
        * source script.rugged
        * read_library synch.genlib
        * map -m 0 -W -s / map -n 1 -W -s (opt_area True/False)

        :param bool autoencoding: True = automatically encodes states
        :param bool opt_area: True = optimize area, False = optimize delay
        :return dict res: results of the operation (success, output, errors, stdout)
        """
        res = {"success": True, "output": {}, "errors": [], "stdout": ""}

        newfile_path = os.path.dirname(self.read_path)

        newfile_name = os.path.basename(self.read_path)
        newfile_name = removesuffix(newfile_name, ".blif")
        newfile_name += ".{}.blif"

        newfile_fullpath = os.path.join(newfile_path, newfile_name)

        if self.started:
            if self.readsomething:

                # print_stats
                cmd_res = self.print_stats()
                res["stdout"] += "sis> print_stats\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["output"]:
                    res["output"]["1_initial_stats"] = cmd_res["output"]

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                # state_minimize stamina
                cmd_res = self.parsed_exec("state_minimize stamina")
                res["stdout"] += "sis> state_minimize stamina\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                # state_assign / stg_to_network
                if autoencoding:
                    cmd_res = self.parsed_exec("state_assign jedi")
                    res["stdout"] += "sis> state_assign jedi\n"
                else:
                    cmd_res = self.parsed_exec("stg_to_network")
                    res["stdout"] += "sis> stg_to_network\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                # print_stats
                cmd_res = self.print_stats()
                res["stdout"] += "sis> print_stats\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["output"]:
                    res["output"]["2_optimized_states"] = cmd_res["output"]

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                self.write_blif(newfile_fullpath.format("state_min_encoding"))

                # reduce_depth (if opt_area is False)
                if not opt_area:
                    cmd_res = self.parsed_exec("reduce_depth")

                    res["stdout"] += "sis> reduce_depth\n"

                    for error in cmd_res["errors"]:
                        res["errors"].append(error)

                    if cmd_res["stdout"]:
                        res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                    if not cmd_res["success"]:
                        res["success"] = False

                    # print_stats
                    cmd_res = self.print_stats()
                    res["stdout"] += "sis> print_stats\n"

                    for error in cmd_res["errors"]:
                        res["errors"].append(error)

                    if cmd_res["output"]:
                        res["output"]["3_reduce_depth_stats"] = cmd_res["output"]

                    if cmd_res["stdout"]:
                        res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                    if not cmd_res["success"]:
                        res["success"] = False

                # script.rugged
                cmd_res = self.parsed_exec("source script.rugged")
                res["stdout"] += "sis> source script.rugged\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                # print_stats
                cmd_res = self.print_stats()
                res["stdout"] += "sis> print_stats\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["output"]:
                    res["output"]["4_rugged_stats"] = cmd_res["output"]

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                self.write_blif(newfile_fullpath.format("optimized"))

                # read_library
                cmd_res = self.parsed_exec("read_library synch.genlib")
                res["stdout"] += "sis> read_library synch.genlib\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                # map
                if opt_area:
                    cmd_res = self.parsed_exec("map -m 0 -W -s")
                    res["stdout"] += "sis> map -m 0 -W -s\n"
                else:
                    cmd_res = self.parsed_exec("map -n 1 -W -s")
                    res["stdout"] += "sis> map -n 1 -W -s\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                # print_stats
                cmd_res = self.print_stats()
                res["stdout"] += "sis> print_stats\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["output"]:
                    res["output"]["5_map_stats"] = cmd_res["output"]

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                self.write_blif(newfile_fullpath.format("mapped"))

            else:
                res["success"] = False
                res["errors"].append("[ERROR][BSISSCRIPT_FSM] Nothing to optimize and map "
                                     "(missing an input, use read_blif or another read command)")
        else:
            # SIS is not running
            res["success"] = False
            res["errors"].append("[ERROR][BSISSCRIPT_FSM] Can't execute command: SIS's process is not running")

        return res

    def bsisscript_lgate(self, opt_area, library):  # noqa: C901
        """
        Executes many commands to optimize and map a combinational circuit using SIS.

        * reduce_depth if opt_area is False
        * source script.rugged
        * read_library synch.genlib / read_library mcnc.genlib (library synch/mcnc)
        * map -m 0 -W -s / map -n 1 -W -s (opt_area True/False)

        :param bool opt_area: True = optimize area, False = optimize delay
        :param str library: mcnc = mcnc.genlib, synch = synch.genlib
        :return dict res: results of the operation (success, output, errors, stdout)
        """
        res = {"success": True, "output": {}, "errors": [], "stdout": ""}

        newfile_path = os.path.dirname(self.read_path)

        newfile_name = os.path.basename(self.read_path)
        newfile_name = removesuffix(newfile_name, ".blif")
        newfile_name += ".{}.blif"

        newfile_fullpath = os.path.join(newfile_path, newfile_name)

        if self.started:
            if self.readsomething:
                # print_stats
                cmd_res = self.print_stats()
                res["stdout"] += "sis> print_stats\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["output"]:
                    res["output"]["1_initial_stats"] = cmd_res["output"]

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                # reduce_depth (if opt_area is False)
                if not opt_area:
                    cmd_res = self.parsed_exec("reduce_depth")

                    res["stdout"] += "sis> reduce_depth\n"

                    for error in cmd_res["errors"]:
                        res["errors"].append(error)

                    if cmd_res["stdout"]:
                        res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                    if not cmd_res["success"]:
                        res["success"] = False

                    # print_stats
                    cmd_res = self.print_stats()
                    res["stdout"] += "sis> print_stats\n"

                    for error in cmd_res["errors"]:
                        res["errors"].append(error)

                    if cmd_res["output"]:
                        res["output"]["2_reduce_depth_stats"] = cmd_res["output"]

                    if cmd_res["stdout"]:
                        res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                    if not cmd_res["success"]:
                        res["success"] = False

                # script.rugged
                cmd_res = self.parsed_exec("source script.rugged")
                res["stdout"] += "sis> source script.rugged\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                # print_stats
                cmd_res = self.print_stats()
                res["stdout"] += "sis> print_stats\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["output"]:
                    res["output"]["3_rugged_stats"] = cmd_res["output"]

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                self.write_blif(newfile_fullpath.format("optimized"))

                # read_library
                if library == "synch":
                    cmd_res = self.parsed_exec("read_library synch.genlib")
                    res["stdout"] += "sis> read_library synch.genlib\n"
                elif library == "mcnc":
                    cmd_res = self.parsed_exec("read_library mcnc.genlib")
                    res["stdout"] += "sis> read_library mcnc.genlib\n"
                else:
                    cmd_res = {"success": False,
                               "errors": ["[ERROR][BSISSCRIPT_LGATE] library '{}' doesn't exist".format(library)],
                               "stdout": None}
                    res["stdout"] += "sis> read_library {}\n".format(library)

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                # map
                if opt_area:
                    cmd_res = self.parsed_exec("map -m 0 -W -s")
                    res["stdout"] += "sis> map -m 0 -W -s\n"
                else:
                    cmd_res = self.parsed_exec("map -n 1 -W -s")
                    res["stdout"] += "sis> map -n 1 -W -s\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                # print_stats
                cmd_res = self.print_stats()
                res["stdout"] += "sis> print_stats\n"

                for error in cmd_res["errors"]:
                    res["errors"].append(error)

                if cmd_res["output"]:
                    res["output"]["4_map_stats"] = cmd_res["output"]

                if cmd_res["stdout"]:
                    res["stdout"] += "\n" + cmd_res["stdout"] + "\n"

                if not cmd_res["success"]:
                    res["success"] = False

                self.write_blif(newfile_fullpath.format("mapped"))
            else:
                res["success"] = False
                res["errors"].append("[ERROR][BSISSCRIPT_LGATE] Nothing to optimize and map "
                                     "(missing an input, use read_blif or another read command)")
        else:
            # SIS is not running
            res["success"] = False
            res["errors"].append("[ERROR][BSISSCRIPT_LGATE] Can't execute command: SIS's process is not running")

        return res

    def bsisscript_fsmd(self, opt_area):
        """
        Executes many commands to optimize a FSMD circuit using SIS by calling the bsisscript_lgate method.

        * reduce_depth if opt_area is False
        * source script.rugged
        * read_library synch.genlib
        * map -m 0 -W -s / map -n 1 -W -s (opt_area True/False)

        :param bool opt_area: True = optimize area, False = optimize delay
        :return dict res: results of the operation (success, output, errors, stdout)
        """
        cmd_res = self.bsisscript_lgate(opt_area, "synch")
        return cmd_res

    # ====================================================================================================
    #
    #                                    PRINT/ECHO/SHOW METHODS
    #
    # ====================================================================================================

    def print_stats(self):
        """
        Executes SIS' print_stats command which outputs statistics about the circuit.

        :return dict res: results of the operation (success, output, errors, stdout)
        """
        res = {"success": False, "output": None, "errors": [], "stdout": None}

        if self.started:
            if self.readsomething:
                exec_res = self.exec("print_stats")

                if exec_res["success"]:
                    res["stdout"] = exec_res["stdout"]
                    v_stdout = exec_res["stdout"].strip().split("\r\n")

                    if len(v_stdout) == 2:
                        pattern = r"^(\S*)[\s]*pi=[\s]*(\d*)[\s]*po=[\s]*(\d*)[\s]" \
                                  r"*nodes=[\s]*(\d*)[\s]*latches=[\s]*(\d*)[\s]*$"
                        infos = v_stdout[0]
                        lits_states = v_stdout[1]
                        mlits = re.match(r"lits\(sop\)=[\s]*(\d*).*", lits_states)
                        mstates = re.match(r".*#states\(STG\)=[\s]*(\d*)", lits_states)
                        minfos = re.match(pattern, infos)
                        if minfos and mlits:
                            try:
                                infosgroups = minfos.groups()
                                name = infosgroups[0]
                                pi = int(infosgroups[1])
                                po = int(infosgroups[2])
                                nodes = int(infosgroups[3])
                                latches = int(infosgroups[4])
                                int_lits = int(mlits.groups()[0].strip())
                                states = 0

                                if mstates:
                                    states = mstates.groups()[0].strip()
                                    states = int(states)

                                res["output"] = {
                                    "name": name,
                                    "pi": pi,
                                    "po": po,
                                    "nodes": nodes,
                                    "latches": latches,
                                    "lits": int_lits,
                                    "states": states
                                }

                                res["success"] = True
                            except ValueError:
                                res["errors"].append("[ERROR][PRINT_STATS] Command returned something that is not a number")
                        else:
                            res["errors"].append("[ERROR][PRINT_STATS] Something went wrong "
                                                 "during print_stats' output parsing")
                    else:
                        res["errors"].append("[ERROR][PRINT_STATS] Something went wrong during print_stats execution")
                else:
                    for error in exec_res["errors"]:
                        res["errors"].append("[ERROR][PRINT_STATS] Error during command execution: " + error)
            else:
                res["errors"].append("[ERROR][PRINT_STATS] Can't execute command: "
                                     "SIS has not read any files (use a read command first)")
        else:
            res["errors"].append("[ERROR][PRINT_STATS] Can't execute command: SIS's process is not running")

        return res

    # ====================================================================================================
    #
    #                                          FSM METHODS
    #
    # ====================================================================================================

    def stg_to_network(self):
        """
        Executes SIS' stg_to_network command which converts an FSM to a nodes network.

        :return dict res: results of the operation (success, errors, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        if self.started:
            if self.readsomething:
                exec_res = self.exec("stg_to_network")
                if exec_res["success"]:
                    res["stdout"] = exec_res["stdout"]

                    if res["stdout"] is None:
                        res["success"] = True
                else:
                    for error in exec_res["errors"]:
                        res["errors"].append("[ERROR][STG_TO_NETWORK] Error during execution: " + error)
            else:
                res["errors"].append("[ERROR][STG_TO_NETWORK] Nothing to convert into a network "
                                     "(missing an input, use read_blif or another read command)")
        else:
            res["errors"].append("[ERROR][STG_TO_NETWORK] Can't execute command: SIS's process is not running")

        return res

    # ====================================================================================================
    #
    #                                          OTHER METHODS
    #
    # ====================================================================================================

    def simulate(self, inputs):  # noqa: C901
        """
        Executes SIS' simulate command to simulate a circuit.

        :param str inputs: string with inputs
        :return dict res: results of the operation (success, output, errors, stdout)
        """
        res = {"success": False, "output": None, "errors": [], "stdout": None}

        if self.started:
            if self.readsomething:
                accepted_chars = True
                i = 0
                while accepted_chars and i < len(inputs):
                    if inputs[i] not in ["0", "1", " "]:
                        accepted_chars = False
                    i += 1

                if accepted_chars:
                    inputs = "".join([char + " " for char in inputs if char in ["0", "1"]]).strip()

                    exec_res = self.exec('simulate ' + inputs)

                    res["stdout"] = exec_res["stdout"]

                    if exec_res["success"]:
                        v_stdout = exec_res["stdout"].strip().split("\r\n")

                        if len(v_stdout) == 3:
                            # simulating a network with no STGs
                            if v_stdout[0] == "Network simulation:":
                                outputs = v_stdout[1].replace("Outputs:", "").replace(" ", "")
                                next_state = v_stdout[2].replace("Next state:", "")

                                res["success"] = True

                                res["output"] = {
                                    "outputs": outputs.strip(),
                                    "next_state": next_state.strip()
                                }
                            else:
                                stats = self.print_stats()
                                n_net_inputs = stats["output"]["pi"]

                                if "simulate network: network has {} inputs;".format(n_net_inputs) in v_stdout[0]:
                                    res["errors"].append(v_stdout[0])
                                else:
                                    res["errors"].append("[ERROR][SIMULATE] Something went wrong during simulation")
                        elif len(v_stdout) == 7:
                            # simulating a network with an STG (FSM)
                            if v_stdout[0] == "Network simulation:" and v_stdout[4] == "STG simulation:":
                                outputs = v_stdout[1].replace("Outputs:", "").replace(" ", "")
                                next_state = v_stdout[2].replace("Next state:", "")

                                stg_outputs = v_stdout[5].replace("Outputs:", "").replace(" ", "")
                                stg_next_state = v_stdout[6].replace("Next state:", "")

                                res["success"] = True

                                res["output"] = {
                                    "outputs": outputs.strip(),
                                    "next_state": next_state.strip(),
                                    "stg_outputs": stg_outputs.strip(),
                                    "stg_next_state": stg_next_state.strip()
                                }
                            else:
                                stats = self.print_stats()
                                n_net_inputs = stats["output"]["pi"]

                                if "simulate network: network has {} inputs;".format(n_net_inputs) in v_stdout[0]:
                                    res["errors"].append(v_stdout[0])
                                else:
                                    res["errors"].append("[ERROR][SIMULATE] Something went wrong during simulation")
                        else:
                            try:
                                stats = self.print_stats()
                                n_net_inputs = stats["output"]["pi"]

                                if "simulate network: network has {} inputs;".format(n_net_inputs) in v_stdout[0]:
                                    res["errors"].append(v_stdout[0])
                                else:
                                    res["errors"].append("[ERROR][SIMULATE] Something went wrong during simulation")
                            except KeyError:
                                res["errors"].append("[ERROR][SIMULATE] Something went wrong during simulation check")
                    else:
                        for error in exec_res["errors"]:
                            res["errors"].append("[ERROR][SIMULATE] Error during command execution: " + error)
                else:
                    res["errors"].append("[ERROR][SIMULATE] Invalid inputs (accepted inputs are made of 1s and 0s)")
            else:
                res["errors"].append("[ERROR][SIMULATE] Can't execute command: "
                                     "SIS has not read any files (use a read command first)")
        else:
            res["errors"].append("[ERROR][SIMULATE] Can't execute command: SIS's process is not running")

        return res


if __name__ == "__main__":

    sis = Siswrapper()
