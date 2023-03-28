Developer documentation
=======================

Here we provide some guides for the development of *Argilla*.

.. _development-setup:

Development setup
-----------------

To set up your system for *Argilla* development, you first of all have to
`fork <https://guides.github.com/activities/forking/>`_ our `repository <https://github.com/argilla-io/argilla>`_
and clone the fork to your computer:

.. code-block:: bash

    git clone https://github.com/[your-github-username]/argilla.git
    cd argilla

To keep your fork's master branch up to date with our repo you should add it as an
`upstream remote branch <https://dev.to/louhayes3/git-add-an-upstream-to-a-forked-repo-1mik>`_:

.. code-block:: bash

    git remote add upstream https://github.com/argilla-io/argilla.git

Now go ahead and create a new conda environment in which the development will take place and activate it:

.. code-block:: bash

    conda env create -f environment_dev.yml
    conda activate argilla

In the new environment *Argilla* will already be installed in `editable mode <https://pip.pypa.io/en/stable/cli/pip_install/#install-editable>`_ with all its server dependencies.

To keep a consistent code format, we use `pre-commit <https://pre-commit.com/>`_ hooks.
You can install them by simply running:

.. code-block:: bash

    pre-commit install

Install the `commit-msg` hook if you want to check your commit messages in your contributions:

.. code-block:: bash

    pre-commit install --hook-type commit-msg

Build the static UI files in case you want to work on the UI:

.. code-block:: bash

    bash scripts/build_frontend.sh

Run database migrations executing the following task:

.. code-block:: bash

    python -m argilla.tasks.database.migrate

If you want to run the web app now, simply execute:

.. code-block:: bash

    python -m argilla

Congrats, you are ready to take *Argilla* to the next level 🚀

Building the documentation
--------------------------

To build the documentation, make sure you set up your system for *Argilla* development.
Then go to the `docs/_source` folder in your cloned repo and execute the ``make html`` command:

.. code-block:: bash

    cd docs/_source
    make html

This will create a ``_build/html`` folder in which you can find the ``index.html`` file of the documentation.

Alternatively, you can use install and `sphinx-autobuild` to continuously deploy the webpage using the following command:

.. code-block:: bash

    sphinx-autobuild docs/_source docs/_build/html
