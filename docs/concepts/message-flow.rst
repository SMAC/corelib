Message flow management title
=======================

The SMAC's message dispatching subsystem is built in a flexible and adaptable
way which allows powerful "module group" (broadcast, multicast) or "single
module" (unicast) targeting.

It is also possible to address a specific module instance as well as a random
one by targeting a module interface or a module implementation.

This section explains which targeting and distribution modes are available
and how they can be combined to gain complete control over the message
dispatching subsystem.

Message distribution
--------------------

The SMAC dispatching system allows to distribute a message among one or many
modules at the same time. It is thus possible to sen a message which will be
received from a defined set of hosts (module instances) in the system. There
are 3 levels of distribution which can be grouped into two logical groups:

* **Broadcast and Multicast**

  The message is simultaneously delivered to all modules registered to the
  system. Multicasting is achieved by sending a broadcast message with a well
  defined granularity (see below, Message targeting).

* **Unicast**

  Only one module of the system will receive the message. The unicast message 
  can be either uniquely addressed or sent to a pool of modules and then
  delivered to only one of these (the destination is chosen based on a
  round-robin algorithm).

Module targeting
-----------------

The SMAC message dispatching system allows to target each module or group with
4 levels of granularity:

* **Domain targeting**

  The message is sent to all registered modules on the system. E.g. to send a
  ping command to all currently active modules of the system.

* **Interface targeting**

  The message is sent to all modules instances of a specific interface. E.g.
  all Storage modules.

* **Implementation targeting**

  The message is sent to all modules of a specific implementation. E.g. all
  Analyze modules which are capable to analyze .ppt files.

* **Instance targeting**

  The message is sent to a well defined module on the system. This means that
  the module is uniquely addressable in the whole system. E.g. a Capturer
  module of a specific room.

Combinations of distribution and targeting
------------------------------------------

The two important properties of the message dispatching subsystem seen above
can be combined to either a whole interface of modules or to send a
command to only one module of a well-defined implementation.

The following table resumes the combination possibilities offered by the
subsystem:

+----------------+-----------------------+-----------------------------------+
| Targeting      | Distribution          | Notes                             |
+================+=======================+===================================+
| Domain         | Broadcast only        | Only ``oneway`` [#bd_lim]_ service|
|                |                       | declarations allowed              |
+----------------+-----------------------+-----------------------------------+
| Interface      | Multicast (broadcast) | Only ``oneway`` [#bd_lim]_ service|
|                | and Unicast           | declarations allowed for          |
|                |                       | multicast distribution            |
+----------------+-----------------------+-----------------------------------+
| Implementation | Multicast (broadcast) | Only ``oneway`` [#bd_lim]_ service|
|                | and Unicast           | declarations allowed for          |
|                |                       | multicast distribution            |
+----------------+-----------------------+-----------------------------------+
| Instance       | Unicast only          |                                   |
+----------------+-----------------------+-----------------------------------+

.. [#bd_lim] This limitation is due to the thrift architecture which expects only one response per request. If a message is relayed to more than one module and all modules provide a response the caller will receive only the first result. If a broadcast command needs a response, then the calling module MUST provide a callback which the called module can use to transmit the response. Note that the called method will be executed on each method, and not only on the first which provide the response. For more informations see :doc:`Thrift </technologies/thrift>`.

Services targeting
------------------

The last targeting mode supported by the system is not directly
module-dependent. A service is a message stream which a module sends to the
services exchange with a given routing key (defined by the service self).

Service consumers (i.e. normal modules with specific capabilities) can
subscribe to a service by binding their exclusive queue to the services
exchange with the service specific routing key.

The services exchange type is set to topic (to allow wild-cards in the
routing key) and the only available distribution mode is broadcast (this means
that all service exposed API methods have to be defined as ``oneway`` in
thrift).








