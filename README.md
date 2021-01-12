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

1. Running the following pip command:

    ```
    pip install siswrapper
    ```

2. Build the python wheel file using the following command:

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
sis.stop()  # stop SIS and tmux's session

sis.start() # start a tmux session and start SIS
            # > Executed automatically after the instance creation
            # > (useful after sis.stop() )

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
# without calling directly the correct method
# > fallback method in case the command is not recognized: exec()
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
**Work in progress 1.1.2:** <br>
### Fixes
* Now the ```write_eqn``` method is executed when ```write_eqn``` is passed to the ```parsed_output()``` method.
* When SIS is not installed the error message shows exactly what the problem is

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