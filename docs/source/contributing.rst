Contributing Guide
================================

First of all, **thank you** for your interest in contributing!
Whether it's fixing bugs, improving documentation, or adding new features, your contributions help make Locust Telemetry better for everyone.

Project Repository
------------------
:link: `GitHub Repository <https://github.com/platform-crew/locust-telemetry>`_

Getting Started
---------------
Follow these steps to set up your local development environment:

1. **Fork** the repository and clone it locally:

   .. code-block:: bash

       git clone https://github.com/your-username/locust-telemetry.git
       cd locust-telemetry

2. **Create a new branch** for your work:

   .. code-block:: bash

       git checkout -b my-feature-branch

3. **Install dependencies**:

   .. code-block:: bash

       pip install -r requirements.txt

4. **Install pre-commit hooks** to ensure code quality:

   .. code-block:: bash

       pre-commit install

   You can also run hooks manually on only changed files:

   .. code-block:: bash

       pre-commit run --files $(git diff --name-only)

Coding Guidelines
-----------------
* Follow **PEP8** coding conventions.
* Ensure your code is **well-documented** with clear docstrings (Google style or reStructuredText style).
* Keep commits **small and focused**, with descriptive messages.
* Include **unit tests** for all new functionality.
* Target your **PRs to the main branch**.

Pre-commit Hooks
----------------
We use `pre-commit` to enforce code style, linting, and other quality checks.
Make sure to run the hooks before submitting a pull request. This keeps the codebase clean and consistent.

Pull Requests
-------------
* Use the **PR template** provided.
* Provide a **clear description** of the changes and why they are needed.
* Reference related **issues** if applicable.
* Ensure all tests **pass** and code coverage is maintained.

Reporting Issues
----------------
Encountered a bug or unexpected behavior?

1. Check the existing issues to avoid duplicates.
2. If none exist, create a new issue on GitHub:

   :link: `Report an Issue <https://github.com/platform-crew/locust-telemetry/issues>`_

Discussions
-----------
For questions, ideas, or general discussions:

:link: `GitHub Discussions <https://github.com/platform-crew/locust-telemetry/discussions>`_

License
-------
By contributing, you agree that your contributions will be licensed under the same license as the project.
