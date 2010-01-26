Other batteries included
========================

This section contains simple guides about the development process covering 
different aspects of the built-in "mini frameworks" of the corelib.

Tasks
-----

The Tasks mini framework provides methods and means to manage long-running
processes of a module through the controller/web interface and to display his
results to the end-user.

A task must implement the ``ITask``[#]_ interface (or extend by an implementing
superclass). To start to manage the process through the controller, simply
use the task-related methods of the module instance[#]_.

Running a task by extending the ``TaskBase`` class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simplest way to run a task is to extend the ``TaskBase`` class and implement
its ``run`` method.

To start the observing and notifying process use the module's own ``add_task``
method. This methods adds the task to the internal register of the module,
registers the module as an observer of the task and sends the task out to the
controllers in broadcast mode.

Updates to the attributes (such as percent completed or remaining time) are
notified to the owner module (and all registered observers) and automatically
pushed to the controllers.

Running a task by implementing the ``ITask`` interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run a task by implementing the interface is slighter more complex than extending
the ``TaskBase`` class because all methods and functionalities have to be
implemented and changes to the attributed managed and notified to the observables.

For implementation specific details please refer to the API documentation which
describes the details about the requisites of each method.

.. [#] The documentation for the ``ITask`` interface could be found at @TODO
.. [#] See the API documentation for the implementation details @TODO


Management
----------

Observers and Observables
-------------------------

@TODO: Describe the IObservable interface and its usage