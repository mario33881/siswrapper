# SISWRAPPER

![Siswrapper](https://github.com/mario33881/siswrapper/workflows/Siswrapper/badge.svg)

Siswrapper is a **wrapper for [SIS](https://jackhack96.github.io/logic-synthesis/sis.html)**, the tool for synthesis and optimization of sequential circuits.

Siswrapper enables developers to code scripts that embeds SIS in any way.

> Read this README in: 
>
> |[English](https://github.com/mario33881/siswrapper/blob/main/README.md)|[Italiano](https://github.com/mario33881/siswrapper/blob/main/readmes/README.it.md)|
> |-|-|

<p align="center">
    <img height="150px" alt="logo" src="https://raw.githubusercontent.com/mario33881/siswrapper/main/images/logo.svg">
</p>

<br>

<br>


> **Disclaimer:**
>
> I'm not affiliated with the SIS developers in any way.
>
> The aim of this library is to enable the developers to use SIS via the Python programming language.

## Index
* [Description](#description)
* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)
* [Changelog](#changelog)
* [Author](#author)

## Description ![](https://i.imgur.com/wMdaLI0.png)
This library enables the developer
to **control SIS via Python** using an istance of the ```siswrapper.Siswrapper``` class.

This is possible thanks to **pexpect**,
a Python library that can easily be used
to control interactive shells by spawning and connecting to their process.

[Go to the index](#index)

## Requirements ![](https://i.imgur.com/H3oBumq.png)
* Unix-like OS
    > pexpect doesn't have all its features on Windows and SIS works best on linux OSes
* Python 3
* the pexpect library for Python: control interactive shells via Python
* SIS, set in the path environment variable (callable with the ```sis``` command): the tool for synthesis and optimization of sequential circuits
    > You can [download it here](https://jackhack96.github.io/logic-synthesis/sis.html)
    
[Go to the index](#index)

## Installation
You can install this library by:

* (Easiest) Running the following pip command:

    ```
    pip install siswrapper
    ```

* Build the python wheel file using the following command:

    ```
    python3 setup.py bdist_wheel
    ```

    And install the wheel by executing this command:

    ```
    pip install siswrapper-<version>-py3-none-any.whl
    ```
    > ```<version>``` is siswrapper's version

[Go to the index](#index)

## Usage
After siswrapper's installation you can import siswrapper
inside a script or inside the interpreter.

```python
import siswrapper
```

Now you can instance an object from the ```siswrapper.Siswrapper()``` class:

```python
sis = siswrapper.Siswrapper()
```

This instruction spawns a SIS process using pexpect.

From now on it is possible to execute sis commands using Python:

```python
sis.stop()  # stop SIS session

sis.start() # start SIS session
            # > Executed automatically after the siswrapper.Siswrapper() instance creation
            # > (might be useful if you have closed SIS before using sis.stop())

path = "file.blif"
sis.read_blif(path)  # reads a blif file

sis.simulate("010010") # executes a simulation
                       # > No need for spaces between each input !!

# optimize the circuit using the rugged script
sis.script_rugged()

# execute a command that is not 
# directly supported by this library:
sis.exec("help")

# try to execute a command and parse the output
# without calling directly the correct method (simulate() in this case)
# > In case parsed_exec() can't find the right method to call, exec() is called as a fallback
sis.parsed_exec("simulate 00 10 11")

# save the circuit to a new file
sis.write_blif("optimized.blif")

# if necessary it is possible to interact with SIS' shell
sis.interact()
```

All the methods return a dictionary with:
* a success exit status (which can be False or True)
* errors list (empty if there were no errors)
* warnings list (empty if there were no warnings, only on some commands that can return warnings)
* stdout of the command (None if the command returns nothing)
* parsed output of the SIS command (on some commands that return data)

[Go to the index](#index)

## Changelog ![](https://i.imgur.com/SDKHpak.png)
**2021-09-05 1.2.2:** <br>
### Fixes
* Commands that show paginated output don't timeout anymore
    > An example of command that shows paginated output is the ```help read_blif``` command.
* The ```exec()``` method didn't collect the ```wait_end_command()``` method's errors properly

**2021-03-16 1.2.1:** <br>
### Fixes
* the ```print_stats``` method failed the print_stats command output parsing when the circuit had 10000 literals/states or more

**2021-03-16 1.2.0:** <br>
### Features
* Added ```bsis_script``` command. Its accepted parameters are:
    * ```fsm_autoencoding_area```, useful for FSM circuits: minimizes states, automatically encodes states, optimizes area and maps the circuit by area (synch library)
        > Executed commands: ```state_minimize stamina```, ```state_assign jedi```, ```source script.rugged```, ```read_library synch.genlib```, ```map -m 0 -W -s```
    * ```fsm_autoencoding_delay```, useful for FSM circuits: minimizes states, automatically encodes states, optimizes delay and maps the circuit by delay (synch library)
        > Executed commands: ```state_minimize stamina```, ```state_assign jedi```, ```reduce_depth```, ```source script.rugged```, ```read_library synch.genlib```, ```map -n 1 -W -s```
    * ```fsm_area```, useful for FSM circuits: minimizes states, uses manual states encoding, optimizes area and maps the circuit by area (synch library)
        > Executed commands: ```state_minimize stamina```, ```stg_to_network```, ```source script.rugged```, ```read_library synch.genlib```, ```map -m 0 -W -s```
    * ```fsm_delay```, useful for FSM circuits: minimizes states, uses manual states encoding, optimizes delay and maps the circuit by delay (synch library)
        > Executed commands: ```state_minimize stamina```, ```stg_to_network```, ```reduce_depth```, ```source script.rugged```, ```read_library synch.genlib```, ```map -n 1 -W -s```
    * ```lgate_area_mcnc```, useful for combinational circuits: optimizes area and maps the circuit by area (mcnc library)
        > Executed commands: ```source script.rugged```, ```read_library mcnc.genlib```, ```map -m 0 -W -s```
    * ```lgate_delay_mcnc```, useful for combinational circuits: optimizes delay and maps the circuit by delay (mcnc library)
        > Executed commands: ```reduce_depth```, ```source script.rugged```, ```read_library mcnc.genlib```, ```map -n 1 -W -s```
    * ```lgate_area_synch```, useful for combinational circuits: optimizes area and maps the circuit by area (synch library)
        > Executed commands: ```source script.rugged```, ```read_library synch.genlib```, ```map -m 0 -W -s```
    * ```lgate_delay_synch```, useful for combinational circuits: optimizes delay and maps the circuit by delay (synch library)
        > Executed commands: ```reduce_depth```, ```source script.rugged```, ```read_library synch.genlib```, ```map -n 1 -W -s```
    * ```fsmd_area```, useful for FSMD circuits (circuits which include datapaths and an FSM): optimizes area and maps the circuit by area (synch library)
        > Executed commands: ```source script.rugged```, ```read_library synch.genlib```, ```map -m 0 -W -s```
    * ```fsmd_delay```, useful for FSMD circuits (circuits which include datapaths and an FSM): optimizes delay and maps the circuit by delay (synch library)
        > Executed commands: ```reduce_depth```, ```source script.rugged```, ```read_library synch.genlib```, ```map -n 1 -W -s```

    > This command also shows which command is executed and the statistics after some commands

    > Partial and full results are written to new BLIF files.

    > WARNING! These commands are executed in this order, thus does NOT guarantee the best result: multi-level minimization is not perfect!
    > to obtain better results you should try to execute these commands manually in a diffent order (try also to execute them more than once)
* Now this library verifies if the stg_to_network command is successful

### Fixes
* Now the ```write_eqn``` method is executed when ```write_eqn``` is passed to the ```parsed_output()``` method.
    > Before this fix the ```write_blif``` method was executed instead of the correct method
* If you call the ```write_eqn``` and ```write_blif``` method without parameters the output doesn't contain the command.
* When SIS is not installed the error message shows exactly what the problem is
* Can't execute the rugged script if no file as been read with a read command
* When you execute a read command, this library calls the ```reset``` method to close the SIS session and 
  open a new session inside the folder of the input file
    > This "fixes" the ".search x file not found" error when you try to read a file that is in another folder and contains the .search keyword.
    >
    > This error was normal but not intuitive (because the imported file was present inside the same folder as the input file but not inside the current folder).
    > It was the original SIS behaviour.

**2021-01-09 1.1.1:** <br>
### Fixes/features
* ```simulate()``` is executed by ```parsed_output()```
even with not correct input (non "0" and/or "1" chars)
and with the abbreviated command ```sim```
* ```simulate()``` and ```print_stats()``` can manage FSM outputs (fix:```TypeError: 'NoneType' object is not subscriptable```)

### Known bugs
* ```write_blif``` command/method is executed when ```write_eqn``` is passed to the ```parsed_output()``` method.
* When SIS is not installed the error message is incomplete (not easily understandable)

**2021-01-04 1.1.0:** <br>
### Added features
* Added the ```parsed_output()``` method:
  it reads a command and automatically calls the best method
  to parse the output of that command. 
  
  If the command is not recognized it falls back to the ```exec()``` method.

### Changes
* The ```simulate()``` method now returns a string with the outputs (not space between each output):
    > there was no reason to calculate sums, subtractions, ... from the output
    > so the string type makes more sense

### Fixes
* Now the ```exec()``` knows how to treat the ```quit``` 
  and ```exit``` commands without raising Exceptions.

**2020-11-14 1.0.0:** <br>
First commit

[Go to the index](#index)

## Author ![](https://i.imgur.com/ej4EVF6.png)
[Stefano Zenaro (mario33881)](https://github.com/mario33881)