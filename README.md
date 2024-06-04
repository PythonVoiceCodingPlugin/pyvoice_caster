# Pyvoice Caster

These are the caster bindings for the [pyvoice project](ttps://github.com/PythonVoiceCodingPlugin/pyvoice)

<div>
<img src="https://github.com/PythonVoiceCodingPlugin/assets/blob/main/pyvoice_logo.png" align="right" height=320 width=320/>
</div>

<!-- MarkdownTOC  autolink="true" -->

- [Installation](#installation)
	- [Prerequisites](#prerequisites)
	- [Main steps](#main-steps)
- [Available commands](#available-commands)
- [Troubleshooting](#troubleshooting)
	- [Troubleshooting receiving data](#troubleshooting-receiving-data)
	- [Troubleshooting sending commands to sublime](#troubleshooting-sending-commands-to-sublime)
- [License](#license)
- [Acknowledgements](#acknowledgements)

<!-- /MarkdownTOC -->


# Installation

## Prerequisites

You need to make sure you have some version >= 1.0.0 of [Caster](https://github.com/dictation-toolbox/Caster) installed

## Main steps

- navigate to your [caster user directory](https://caster.readthedocs.io/en/latest/readthedocs/User_Dir/Caster_User_Dir/)and then to the corresponding rules section. 

> [!IMPORTANT]
> There is a discrepancy in the directory structure between older and newer versions of caster. After to https://github.com/dictation-toolbox/Caster/pull/905 rules are placed under `caster_user_content\rules` ,whereas prior it should be simply `rules` Both should be supported

- clone this repo with git

```bash
git clone https://github.com/PythonVoiceCodingPlugin/pyvoice_caster.git
```

- reboot caster
- enable the two pyvoice grammars with the following ***voice commands***

	- `enable pyvoice CCR` - enables the pyvoice CCR grammar, this is a responsible for making expressions (like symbol names,  attributes of variables etc) that can be inserted via keyboard for  usage in your CCR chains.
	- `enable pyvoice import` - enables the pyvoice import grammar, this is primarily responsible for allowing you to import symbols

# Available commands



# Troubleshooting

## Troubleshooting receiving data

In order to allow for receiving data from the editor, the client will set up an inter-process communication server that utilizes 

- named pipes on windows
- unix domain sockets on linux


When booting up, if successfull you should see something like the following in the messages window

```
INFO:pyvoice_caster.rpc:Server for service default started at \\.\pipe\voicerpc\blablablabla\default
```

When the editor makes a connection and sends data you should see something like 
- a message informing that the connection has been established 
- the list for which the data is being sent
- how many items are in the list
- as well as a sample of of the data 

```
INFO:pyvoice_caster.dict_lists:Enhanced list expression with 126 items over 0.115 seconds (completed 2024-03-03 17:20:22.303000)
INFO:pyvoice_caster.dict_lists:Enhanced list importable with 1919 items over 3.019 seconds (completed 2024-03-03 17:20:25.176000)

```

## Troubleshooting sending commands to sublime

Executing commands for sublime text is preformed via its commandline interface `subl` which may NOT always be in system path on all platforms by default.

The caster client will search through various directories based on your operating system in order to find its location. If this procedure fails, an error should appear in the logs. In that case please see the official sublime documentation for more information and submit an issue

https://www.sublimetext.com/docs/command_line.html

# License


# Acknowledgements


