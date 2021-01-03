# SISWRAPPER

Siswrapper is a **wrapper for [SIS](https://jackhack96.github.io/logic-synthesis/sis.html)**, the tool for synthesis and optimization of sequential circuits.

Siswrapper enables developers to code scripts that embeds SIS in any way.

> Read this README in: 
>
> |[English](README.md)|[Italiano](readmes/README.it.md)|
> |-|-|

<p align="center">
    <img height="150px" alt="logo" src="images/logo.svg">
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
* SIS: the tool for synthesis and optimization of sequential circuits
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

**2020-11-14 1.0.0:** <br>
First commit

[Go to the index](#index)

## Author ![](https://i.imgur.com/ej4EVF6.png)
[Stefano Zenaro (mario33881)](https://github.com/mario33881)