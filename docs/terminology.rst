Terminology
====================

System
  The whole set of modules instances connected to the AMQP message broker 
  which interact to provide the functionalities offered by SMAC.

Module interface
  A logical group of modules performing similar tasks but with different
  implementations and features. The following are examples of module
  interfaces:
  ``Capturer``, ``Controller``, ``Publisher``.

Module implementation
  A specific implementation of the basic features and functionalities defined
  by a module interface in a chosen programming language. For example, some
  module implementations for the module interface ``Capturer`` are:
  
  * ``WebcamCapturer``: A Capturer module specialized in capturing webcam
    videos.
  * ``ExternalSVideoInputCapturer``: A Capturer module which records video
    from an external S-Video stream.
  * ``DiskCapturer``: A Capturer which allows to import media files from disk.

Module instance
  A current running module implementation. A system can have multiple instance
  of a single module implementation active at the same time. For example we
  have three ``WebcamCapturer`` running on different laptops which capture the
  video of three speakers sitting around a conference table.
  
  Each module instance has an own system unique module ID.

Module ID
  A module ID is a string which identifies a module instance across the whole
  SMAC system.
  
  A module ID is composed of different chunks as follows::
  
    smac.<interface>.<implementation>.<instance_id>
  
  The first chunk is the SMAC namespace, the second one the interface of the
  module, the third the implementation and the last one is an ID which must be
  unique only at the instance level (there cannot be multiple module instances
  of the same implementation with the same ID).

Message
  A single command sent from a module to another one or to a set of modules in
  order to produce an action on the remote peer/s.

