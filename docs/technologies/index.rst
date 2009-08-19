Technologies
============

.. toctree::
   :hidden:
   
   thrift

Technologies and solutions used by SMAC:

==========================  ==========================  ==============
Issue                       Solution                    Implementation
==========================  ==========================  ==============
Infra-module communication  AMQP                        RabbitMQ
Module API specification    Abstracted code generation  Thrift
Network asynchronicity      Event driven programming    Twisted
Documentation               Auto generated + rst        Sphinx
Distribution + packaging    @TODO                       @TODO
==========================  ==========================  ==============