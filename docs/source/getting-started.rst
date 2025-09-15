Getting Started
===============

This guide will help you get up and running with Chrysalis for metamorphic testing.

Your First Test
---------------

Let's create a simple, contrived metamorphic test for a sorting function:

.. code-block:: python

   import random

   import chrysalis as chry

   def sort_function(arr):
       """The system under test - a sorting function"""
       return sorted(arr)

   def add_element_transformation(data):
       """Add a random element to the array"""
       new_data = data.copy()
       new_data.append(random.randint(1, 100))
       return new_data

   def length_invariant(original_output, transformed_output):
       """The transformed output should be one element longer"""
       return len(transformed_output) == len(original_output) + 1

   # Register the metamorphic relation
   chry.register(
       transformation=add_element_transformation,
       invariant=length_invariant
   )

   test_data = [
       [1, 3, 2],
       [5, 1, 9, 3],
       [10, 20, 15]
   ]

   # Run metamorphic testing
   results = chry.run(
       sut=sort_function,
       input_data=test_data,
       chain_length=5,
       num_chains=10
   )

   # `results` now contains a duckdb connection that can be used replay testing
   # logs.

Next Steps
----------

- Learn about :doc:`concepts` to better understand metamorphic testing
