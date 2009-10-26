System components
=================

As already partially seen in the :doc:`/concepts/stack` and
:doc:`/concepts/topology` documents, a complete SMAC system can be decoupled
in different pieces.

 * :ref:`message_broker`
 * :ref:`corelib`
 * :ref:`modules`
 * :ref:`frontend`

.. _message_broker:

Message broker
--------------

The message broker is the only component which all modules have to know in
order to interact with the rest of the system, it is the central component which allows the whole system to interact.

Its main task is to route each message sent from a module to one or more
recipients, using the AMQP 0.8 standard.

The actually implemented and tested broker is
`RabbitMQ <http://www.rabbitmq.com>`_, but theoretically all AMQP-compliant
brokers should work. This allows to exchange a broker implementation with
another based on individual system requirements without the need to
reconfigure the system.

.. _corelib:

SMAC Core Library
-----------------

..
  ``smac`` command line utility
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _modules:

Modules
-------

.. _frontend:

Web frontend
------------