This is the caster bindings for the pyvoice project

https://github.com/PythonVoiceCodingPlugin/pyvoice

<!-- MarkdownTOC  autolink="true" -->

- [Installation](#installation)
- [Troubleshooting](#troubleshooting)
	- [Troubleshooting sending commands to sublime](#troubleshooting-sending-commands-to-sublime)
	- [Troubleshooting receiving data from sublime](#troubleshooting-receiving-data-from-sublime)

<!-- /MarkdownTOC -->


# Installation

- clone this repo into your caster user directory

```bash
git clone https://github.com/PythonVoiceCodingPlugin/pyvoice_caster.git
```

- reboot caster
- enable the two pyvoice grammars with the following ***voice commands***

	- `enable pyvoice CCR` - enables the pyvoice CCR grammar, this is a responsible for making expressions (like symbol names,  attributes of variables etc) that can be inserted via keyboard for  usage in your CCR chains.
	- `enable pyvoice import` - enables the pyvoice import grammar, this is primarily responsible for allowing you to import symbols


# Troubleshooting


## Troubleshooting sending commands to sublime

Executing commands for sublime text is preformed via its commandline interface `subl` which may NOT always be in system path on all platforms by default.

The caster client will search through various directories based on your operating system in order to find its location. If this procedure fails, an error should appear in the logs. In that case please see the official sublime documentation for more information and submit an issue

https://www.sublimetext.com/docs/command_line.html


## Troubleshooting receiving data from sublime

In order to allow for receiving data from the editor, the client will set up an inter-process communication server that utilizes 

- named pipes on windows
- unix domain sockets on linux


When booting up, if successfull you should see something like the following in the messages window

```
('Server started at', '\\\\.\\pipe\\voicerpc\\mplamla\\default', 'default')
```

When the editor makes a connection and sends data you should see something like 
- a message informing that the connection has been established 
- the list for which the data is being sent
- how many items are in the list
- as well as a sample of of the data 

```
('client connected', <read-write PipeConnection, handle 4792>)
('Enhancing: ', u'importable', 649, {u'spoken': u'docs conf', u'name': u'conf', u'module': u'docs'})
('client disconnected ', <read-write PipeConnection, handle 4792>)
```



