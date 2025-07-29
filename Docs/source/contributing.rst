Contribute
==========

Thank you for considering contributing to **PyPLUTO**!

We welcome contributions of all kinds, including bug reports, feature requests, 
documentation improvements, and code contributions.

Getting Started
---------------

To contribute:

1. Fork the repository: https://github.com/GiMattia/PyPLUTO
2. Create a feature branch:

.. code-block:: console

   $ git checkout -b feature/your-feature-name

3. Make your changes and write tests.
4. Ensure your code adheres to the project's coding standards.
5. Commit with a descriptive message.
6. Push and open a pull request.

Installation guidelines
-----------------------

In order to install the project, you can use the following command:

.. code-block:: console

    $ pip install -r requirements_dev.txt

In order to ensure that the pre-commit hooks are installed, run:

.. code-block:: console

    $ pre-commit install

You should see this (or similar) output:

.. code-block:: console

    pre-commit installed at .git/hooks/pre-commit

Testing
-------

The core functionalty of PyPLUTO is tested through a set of pytes benchmarks 
present in the `Tests` folder. To run the tests, you can use:

.. code-block:: console

   $ pytest --cov=pyPLUTO --cov-report=term-missing

This will run all tests and provide a coverage report in the terminal.
Please ensure that all tests pass before submitting a pull request.

Pre-commit Hooks
----------------

PyPLUTO uses pre-commit hooks to ensure code quality and consistency.
These hooks will automatically format your code and check for common issues 
before committing.
In order to use them, make sure you have `pre-commit` installed and run:

.. code-block:: console

   $ pre-commit run --all-files

The following pre-commit hooks are active and run automatically before every 
commit:

1. **official pre-commit hooks** checks for common issues like trailing 
   whitespace, end-of-file newlines, case conflict and more.

2. **docformatter** automatically reformats Python docstrings in-place using 
   Black-style formatting with enforced blank lines.

3. **blacken-docs** formats code blocks inside docstrings using Black with a 
   line length of 80 characters.

4. **ruff** lints and fixes Python code, catching both stylistic and logical 
   issues. Runs with --fix enabled to apply auto-fixes.

5. **black** automatically formats all Python files according to Black's style 
   guide for consistent code formatting.

The code undergoes a strict series of checks during every pull request.
In order to avoid rejections, is convenient to run the full set of checks
through the command

.. code-block:: console

   $ pre-commit run --all-files --hook-stage manual

In addition to all the previous pre-commit checks, the code also runs the 
following tools:

6. **pytest** runs automatically all the tests (see Testing section above)  
   ensuring a minimum coverage of 45% (will be increased in the near future).

7. **interrogate** ensures a docstring coverage above 70%  
   (will also be increased in the near future).

We aim at also adding checking tools such as mypy and pylint, although they have
not been included yet.

Code style
----------

During every pre-commit the code is automatically formatted to adhere with the
**black** codestyle.
In order to format automatically the code at every saving in VsCode, you can 
do the following:

1. Search the VS Code Marketplace for the formatter extension "Black formatter"

2. Go to File -> Preferences -> Settings

3. Search "format"

4. In the "Editor: Default formatter" panel select "Black formatter"

5. Check the "Format on save" box

Code Structure
--------------

WIP...


Questions or Suggestions?
-------------------------

For any question, suggestion or comment please send an e-mail to G. Mattia 
(mail: `mattia@mpia.de <mailto:mattia@mpia.de>`_).

Feel also free to open an issue or discuss in the GitHub repo.

Happy coding!

|

----

.. This is a comment to prevent the document from ending with a transition.