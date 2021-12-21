Developer documentation
=======================

Here we provide some guides for the development of *Rubrix*.

.. _development-setup:

Development setup
-----------------

To set up your system for *Rubrix* development, you first of all have to
`fork <https://guides.github.com/activities/forking/>`_ our `repository <https://github.com/recognai/rubrix>`_
and clone the fork to your computer:

.. code-block:: bash

    git clone https://github.com/[your-github-username]/rubrix.git
    cd rubrix

To keep your fork's master branch up to date with our repo you should add it as an
`upstream remote branch <https://dev.to/louhayes3/git-add-an-upstream-to-a-forked-repo-1mik>`_:

.. code-block:: bash

    git remote add upstream https://github.com/recognai/rubrix.git

Now go ahead and create a new conda environment in which the development will take place and activate it:

.. code-block:: bash

    conda env create -f environment_dev.yml
    conda activate rubrix


In the new environment *Rubrix* will already be installed in `editable mode <https://pip.pypa.io/en/stable/cli/pip_install/#install-editable>`_ with all its server dependencies.

To keep a consistent code format, we use `pre-commit <https://pre-commit.com/>`_ hooks.
You can install them by simply running:

.. code-block:: bash

    pre-commit install

The last step is to build the static UI files in case you want to work on the UI:

.. code-block:: bash

    bash scripts/build_frontend.sh

Now you are ready to take *Rubrix* to the next level 🚀


Building the documentation
--------------------------

To build the documentation, make sure you set up your system for *Rubrix* development.
Then go to the `docs` folder in your cloned repo and execute the ``make`` command:

.. code-block:: bash

    cd docs
    make html

This will create a ``_build/html`` folder in which you can find the ``index.html`` file of the documentation.
