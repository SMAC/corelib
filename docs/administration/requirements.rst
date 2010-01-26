System requirements
===================

General requirements
--------------------

* **AMQP Message broker**

  Only RabbitMQ was used for the development process. Theoretically each standard-compliant AMQP
  message broker should do the trick, but none were tested.
  
  The currently adopted protocol version is version 0-8 as provided by RabbitMQ; upgrades to never
  versions will be considered if they supports a wider range of services defined by the protocol
  itself (at the moment, the implementation of RabbitMQ does not support the ``file`` or ``stream``
  transfer types).
  
  The `Interoperability <http://www.rabbitmq.com/interoperability.html>`_ page of the RabbitMQ
  documentation provides more details about the differences between Qpid and RabbitMQ.
  
  


Default included modules
--------------------

* Python >=2.6, <3.0
* Twisted
* Thrift python libraries


Core generation
---------------

* Thrift binaries


Documentation generation
------------------------

* Sphinx
* Epydoc
