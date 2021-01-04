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
    * started: boolean that is set to True if the SIS's process is started
    * readsomething: boolean that is set to True if a correct input has been read by SIS
    """

    def __init__(self):
        self.res = {"success": False, "errors": [], "stdout": None}
        self.sis = None
        self.started = False
        self.readsomething = False

        start_res = self.start()

        if start_res["success"]:
            self.started = True
            self.res["stdout"] = start_res["stdout"]
            self.res["success"] = True
        else:
            for error in start_res:
                self.res["errors"].append("[ERROR][INIT] Error while initializing (start step): " + error)

    def start(self):
        """
        Starts SIS's process.

        First the method tries to spawn the process.
        If the process responds with the sis> promt (after some waiting using the wait_end_command() method),
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
                        self.res["errors"].append("[ERROR][START] Error while waiting SIS's startup: " + error)

            except pexpect.exceptions.ExceptionPexpect:
                res["errors"].append("[ERROR][START] Couldn't start SIS: check if "
                                     "it is installed and callable from the terminal")
        else:
            res["errors"].append("[ERROR][START] Couldn't start SIS: "
                                 "SIS's process is already running in this instance")

        return res

    def reset(self):
        """
        Resets SIS's process.

        First the method tries to stop the process by calling stop() method
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

    def wait_end_command(self):
        """
        Waits the end of a command execution.

        It waits for the "sis>" promt to appear.

        :return dict res: results of the operation (success, errors, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        try:
            self.sis.expect("sis>")

            res["success"] = True
            res["stdout"] = self.sis.before.decode('utf-8')

        except pexpect.exceptions.TIMEOUT:
            res["errors"].append("[ERROR][WAIT_END_COMMAND] Timeout while waiting the end of command execution")

        except pexpect.exceptions.EOF:
            # entered "quit" or "exit" command
            res["success"] = True

        return res

    def exec(self, t_command):
        """
        Executes the <t_command> command using SIS.

        :param str t_command: command to execute using SIS
        :return dict res: results of the operation (success, errors, stdout)
        """
        res = {"success": False, "errors": [], "stdout": None}

        if self.started:
            self.sis.sendline(t_command.strip())

            wait_res = self.wait_end_command()
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
                for error in wait_res:
                    res["errors"].append("[ERROR][EXEC] Error while waiting for the end of the command: " + error)
        else:
            res["errors"].append("[ERROR][EXEC] Can't execute command: SIS's process is not running")

        return res

    def parsed_exec(self, t_command):  # noqa: C901
        """
        Parsed and executes the <t_command> command as best as it thinks it can.

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
        elif re.match(r"^write_blif[\s]*(\S*)$", strip_cmd):
            param = re.match(r"^write_blif[\s]*(\S*)$", strip_cmd).groups()[0]
            param = param.strip('"')
            cmd_res = self.write_blif(param)

        # write_eqn
        elif re.match(r"^write_eqn[\s]*(\S*)$", strip_cmd):
            param = re.match(r"^write_eqn[\s]*(\S*)$", strip_cmd).groups()[0]
            param = param.strip('"')
            cmd_res = self.write_blif(param)

        # source script.rugged
        elif strip_cmd == "source script.rugged":
            cmd_res = self.script_rugged()

        # print_stats
        elif strip_cmd == "print_stats":
            cmd_res = self.print_stats()

        # simulate
        elif re.match(r"^simulate [\s]*([ 01]*)$", strip_cmd):
            param = re.match(r"^simulate [\s]*([ 01]*)$", strip_cmd).groups()[0]
            cmd_res = self.simulate(param)

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
                    else:
                        res["success"] = True
                        self.readsomething = True
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
                    else:
                        res["success"] = True
                        self.readsomething = True
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
            exec_res = self.exec("source script.rugged")
            if exec_res["success"]:
                res["stdout"] = exec_res["stdout"]

                if res["stdout"] is None:
                    res["success"] = True
            else:
                for error in exec_res["errors"]:
                    res["errors"].append("[ERROR][SCRIPT_RUGGED] Error during execution: " + error)
        else:
            res["errors"].append("[ERROR][SCRIPT_RUGGED] Can't execute command: SIS's process is not running")

        return res

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
                        lits = v_stdout[1]
                        parsed_lits = lits.replace("lits(sop)=", "").strip()

                        minfos = re.match(pattern, infos)
                        if minfos:
                            try:
                                infosgroups = minfos.groups()
                                name = infosgroups[0]
                                pi = int(infosgroups[1])
                                po = int(infosgroups[2])
                                nodes = int(infosgroups[3])
                                latches = int(infosgroups[4])
                                int_lits = int(parsed_lits)

                                res["output"] = {
                                    "name": name,
                                    "pi": pi,
                                    "po": po,
                                    "nodes": nodes,
                                    "latches": latches,
                                    "lits": int_lits
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
    #                                          OTHER METHODS
    #
    # ====================================================================================================

    def simulate(self, inputs):
        """
        Executes SIS' simulate command to simulate a circuit.

        :param str inputs: string with inputs
        :return dict res: results of the operation (success, output, errors, stdout)
        """
        res = {"success": False, "output": None, "errors": [], "stdout": None}

        if self.started:
            if self.readsomething:
                inputs = "".join([char + " " for char in inputs if char in ["0", "1"]]).strip()

                exec_res = self.exec('simulate ' + inputs)

                res["stdout"] = exec_res["stdout"]

                if exec_res["success"]:
                    v_stdout = exec_res["stdout"].strip().split("\r\n")

                    if len(v_stdout) == 3:
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
                res["errors"].append("[ERROR][SIMULATE] Can't execute command: "
                                     "SIS has not read any files (use a read command first)")
        else:
            res["errors"].append("[ERROR][SIMULATE] Can't execute command: SIS's process is not running")

        return res


if __name__ == "__main__":

    sis = Siswrapper()
