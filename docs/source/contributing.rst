Contributing
============

We welcome contributions to Chrysalis!

Development Setup
-----------------

Prerequisites
~~~~~~~~~~~~~

- Python 3.12 or higher
- uv

Development Workflow
--------------------

Code Style and Formatting
~~~~~~~~~~~~~~~~~~~~~~~~~~

We use several tools to maintain code quality:

- **Ruff**: For linting and formatting
- **mypy**: For type checking
- **pytest**: For testing

Run all checks:

.. code-block:: bash

   ./scripts/format_and_check.sh

Running Tests
~~~~~~~~~~~~~

Run the full test suite:

.. code-block:: bash

   uv run pytest

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

Build the documentation:

.. code-block:: bash

   ./scripts/build_docs.sh

Types of Contributions
----------------------

Bug Reports
~~~~~~~~~~~

When reporting bugs, please include:

1. **Clear Description**: What happened vs. what you expected
2. **Reproduction Steps**: Minimal code to reproduce the issue
3. **Environment**: Python version, Chrysalis version, OS
4. **Error Messages**: Full stack traces if applicable

Feature Requests
~~~~~~~~~~~~~~~~

For new features, please:

1. **Check Existing Issues**: Avoid duplicates
2. **Describe the Use Case**: Why is this feature needed?
3. **Provide Examples**: Show how it would be used
4. **Consider Alternatives**: Are there existing ways to achieve this?

Code Review Guidelines
^^^^^^^^^^^^^^^^^^^^^^

- **Keep PRs Small**: Easier to review and merge
- **Write Tests**: All new code should have corresponding tests
- **Update Docs**: Include documentation updates when needed
- **Follow Patterns**: Match existing code style and patterns

Documentation Contributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Documentation improvements are always welcome:

- **Fix Typos**: Small fixes don't need issues
- **Improve Examples**: Add clearer or more realistic examples
- **Add Tutorials**: Help users understand complex concepts
- **API Documentation**: Keep function documentation up-to-date
