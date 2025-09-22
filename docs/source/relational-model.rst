Relational Model
================

Chrysalis uses a relational database model to track metamorphic testing execution and store the relationships between transformations and invariants.

Database Tables
---------------

The Chrysalis relational model consists of six core tables that capture all aspects of metamorphic testing execution:

Transformation Table
~~~~~~~~~~~~~~~~~~~~

The ``transformation`` table stores the registered transformation functions that can be applied to input data.

.. code-block:: sql

   CREATE TABLE transformation (
       id TEXT PRIMARY KEY,
       name TEXT UNIQUE NOT NULL
   );

- **id**: Unique identifier for the transformation
- **name**: Human-readable name of the transformation function

Invariant Table
~~~~~~~~~~~~~~~

The ``invariant`` table stores the registered invariant functions that verify expected relationships between outputs.

.. code-block:: sql

   CREATE TABLE invariant (
       id TEXT PRIMARY KEY,
       name TEXT NOT NULL
   );

- **id**: Unique identifier for the invariant
- **name**: Human-readable name of the invariant function

Relation Table
~~~~~~~~~~~~~~

The ``relation`` table defines which invariants are applicable to each transformation, establishing the metamorphic relations.

.. code-block:: sql

   CREATE TABLE relation (
       transformation TEXT NOT NULL,
       invariant TEXT NOT NULL,

       FOREIGN KEY (transformation) REFERENCES transformation(id),
       FOREIGN KEY (invariant) REFERENCES invariant(id)
   );

- **transformation**: Reference to a transformation ID
- **invariant**: Reference to an invariant ID that applies to this transformation

Input Data Table
~~~~~~~~~~~~~~~~

The ``input_data`` table stores serialized input data objects used during testing.

.. code-block:: sql

   CREATE TABLE input_data (
       id TEXT PRIMARY KEY,
       obj BLOB NOT NULL
   );

- **id**: Unique identifier for the input data
- **obj**: Serialized input data object stored as binary data

Applied Transformation Table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``applied_transformation`` table tracks the execution of transformations within relation chains, maintaining the order and context of each application.

.. code-block:: sql

   CREATE TABLE applied_transformation (
       id TEXT PRIMARY KEY,
       transformation TEXT NOT NULL,
       relation_chain_id TEXT,
       link_index INT NOT NULL,
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

       FOREIGN KEY (transformation) REFERENCES transformation(id)
   );

- **id**: Unique identifier for this application instance
- **transformation**: Reference to the transformation that was applied
- **relation_chain_id**: Identifier linking related transformations in a chain
- **link_index**: Position of this transformation within the chain
- **created_at**: Timestamp of when the transformation was applied

Failed Invariant Table
~~~~~~~~~~~~~~~~~~~~~~

The ``failed_invariant`` table records instances where invariants failed during testing, capturing the complete context of the failure.

.. code-block:: sql

   CREATE TABLE failed_invariant (
       id TEXT PRIMARY KEY,
       invariant TEXT NOT NULL,
       applied_transformation TEXT NOT NULL,
       input_data TEXT NOT NULL,

       FOREIGN KEY (invariant) REFERENCES invariant(id),
       FOREIGN KEY (applied_transformation) REFERENCES applied_transformation(id),
       FOREIGN KEY (input_data) REFERENCES input_data(id)
   );

- **id**: Unique identifier for this failure instance
- **invariant**: Reference to the invariant that failed
- **applied_transformation**: Reference to the transformation application that caused the failure
- **input_data**: Reference to the input data used when the failure occurred

Database Architecture
---------------------

SQLite During Testing
~~~~~~~~~~~~~~~~~~~~~

During metamorphic testing execution, Chrysalis uses SQLite as the primary database engine. This choice is driven by several factors:

- **Transactional Processing**: Testing follows a transactional pattern where transformations are applied sequentially and invariants are checked after each step
- **Lightweight**: SQLite requires no separate server process and provides immediate consistency
- **Temporary Storage**: The testing database is created in a temporary directory and exists only during test execution

The SQLite database is created through the ``TemporarySqlite3RelationConnection`` context manager, which:

1. Creates a temporary directory and SQLite database file
2. Initializes all table schemas with proper foreign key constraints
3. Populates the ``transformation``, ``invariant``, and ``relation`` tables with registered metamorphic relations
4. Provides a connection for recording test execution data
5. Automatically cleans up the temporary database when testing completes

DuckDB for User Analysis
~~~~~~~~~~~~~~~~~~~~~~~~

After testing completes, the SQLite database is converted to DuckDB format before being returned to users. This conversion provides several advantages:

- **Analytics Optimization**: DuckDB is optimized for analytical queries and data analysis workflows
- **Better Performance**: Column-oriented storage and vectorized execution provide faster query performance on test results
- **Rich SQL Support**: DuckDB supports advanced SQL features that are useful for analyzing test results
- **Python Integration**: Excellent integration with Python data analysis libraries like pandas

Data Storage Strategy
~~~~~~~~~~~~~~~~~~~~~

Chrysalis employs an efficient storage strategy that minimizes database size while maintaining complete reproducibility:

- **Transformation Results Not Stored**: The database does not store the actual results of applying transformations to input data
- **Replay-Based Approach**: Transformed data can be recreated by replaying the recorded transformations against the original input data
- **Space Efficiency**: This approach dramatically reduces storage requirements compared to storing all intermediate results
- **Complete Reproducibility**: The execution order and parameters are fully preserved, enabling exact reproduction of any test scenario if transformations are deterministic

This design enables comprehensive logging and replay capabilities while keeping the database size manageable, even for extensive testing campaigns with long relation chains.
