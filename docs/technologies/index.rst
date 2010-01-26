Technologies
============


Infra-module communication
--------------------------

The first version of SMAC used RPC to communicate between the various modules of the system. AMQP wad mainly adopted to provide a lower entry point for new modules and allow for a better distribution of the workload.

With an AMQP message broker, the system central point was moved from the controller module to the message broker itself. Considering that an AMQP message broker is built from ground-up to be scalable, reliable and distributable, there are theoretically no more bottlenecks and the complete system is horizontally scalable.

Another advantage brought from the inherent architecture of a distributed AMQP system is represented by a easier management of the connected modules and the routing of the message between them.
The Message flow management page offers more insight on this topic.

RabbitMQ was chosen as message broker for the development and initial deployment of SMAC v2, but theoretically it's possible to switch to a standards compliant broker of choice (such as Qpid, which is implemented in either C++ or Java). Please note that none of this brokers were tested.


Module API specification
------------------------

The possibility offered by a complete rewriting of the SMAC architecture made possible the adoption of a further abstraction layer which allows the exchange of messages in native data types between different programming languages of choice.

The first considered possibility was Thrift, a code generation framework to build cross-languages services initially developed at Facebook and then open sourced on the Apache Incubator.

Later a second implementation was considered: bert-rpc, an Erlang based binary serialization format which offers the advantage of being completely dynamic (no code generation necessary) but does not support static/compiled languages.

Due to this main disadvantage and the existence of Thrift-Twisted-AMQP python libraries, Thrift was preferred over bert-rpc.


Concurrency
-----------

The highly distributed nature of the system and the concurrency of the tasks to execute seems a reasonable fit for a single-thread, event driven programming style based on asynchronous I/O.

In the Python world, this support is given by the Twisted networking engine. A framework for writing network based python applications with implementations of different network protocols and a good application development framework.

While other modules does not have to necessarily use this library, the corelib and the default modules are all based upon it.


Documentation
-------------

Two needed documentation types were identified: an API documentation, needed to develop further SMAC modules and a formal prose documentation to serve as a User/Administrator/Installation guide for the whole system.

For the first one, Epydoc was chosen. Epydoc generates documentation based on the source code and python docstrings. It supports a wide range of syntax constructs and can generate HTML or PDF output. It's main drawback is the python based output formatting which is tightly coupled with the application code forcing a non customizable output template.

For the second one, the best fit seemed Spinhx. This tool, created to translate the whole Python documentation, is reStructuredText based and can generate HTML, Windows HTML Help, LaTeX and PDF.
Research in underway to find/develop a wiki-like web interface to easily edit the documentation without having to struggle with text editors and consoles.


Distribution & Packaging
------------------------

The biggest issues of the actual (v1) SMAC version are the distribution, installation and configuration tasks which are all to be done manually and involve a big dependency list.

While the dependencies are difficult to avoid, a better an well configured distribution and packaging system offers an automatic way to check the requirements of the software. In the Python world there are multiple tools to achieve this goal, but all are based upon the distutils architecture.

By using the distutils architecture, each SMAC module can easily be installed in a standard fashion, and with an easy (later) switch to other solutions (such as easy_install or PIP), automatic installs without downloads and with dependency resolving are also possible.
