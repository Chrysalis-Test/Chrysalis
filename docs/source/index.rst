.. Chrysalis documentation master file, created by
   sphinx-quickstart on Thu Sep 11 18:06:32 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Chrysalis 🦋
============

A metamorphic testing framework that utilizes metamorphic relations to detect bugs.

What is Metamorphic Testing?
-----------------------------

Metamorphic testing is a software testing technique that examines relations
between multiple executions of a program. Instead of checking if a program
produces the "correct" output for a given input (which may be unknown) metamorphic
testing verifies that certain relationships hold between inputs and their
corresponding outputs.

A metamorphic relation consist of two key components: a transformation and an
invariant. The transformation defines how to modify the original input to create a
follow-up test case, such as shuffling the order of elements in a list, scaling
numerical values, or adding redundant data. The invariant specifies the expected
relationship between the outputs of the original and transformed inputs,
describing how the results should relate to each other even when the exact values
are unknown. For example, when testing a sorting algorithm, the transformation
might involve shuffling the input array, while the invariant would assert that
both the original and shuffled inputs should produce identically sorted outputs.

Key Features
------------

- **Easy Registration**: Simple API to register metamorphic relations
- **Chain Testing**: Execute multiple transformations in sequence
- **Tuneable Testing Engine**: Configure testing parameters
- **Logging and Replay**: Comprehensive test execution logs

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install chrysalis-test

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   import chrysalis as chry

   # Register a metamorphic relation
   chry.register(
       transformation=my_transformation,
       invariant=chry.invariants.equals
   )

   # Run tests
   results = chry.run(
       sut=my_function,
       input_data=test_data,
       chain_length=10,
       num_chains=20
   )

Publication
~~~~~~~~~~~

`Chrysalis: A Lightweight Logging and Replay Framework for Metamorphic Testing in Python <https://github.com/Chrysalis-Test/chrysalis-paper/blob/main/Chrysalis___Metamorphic_Testing__ASE25_Demo_.pdf>`_

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   getting-started
   concepts
   contributing

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api
