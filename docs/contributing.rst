.. _contributing:

Contributing
=============

🎉 **Welcome!**

Thank you for your interest in contributing to **Locust Telemetry**!
Whether it's fixing bugs, improving documentation, or adding new features, your contributions help make this project better for everyone.

Don't worry if this is your first time contributing—every small contribution counts, and we’re happy to guide you along the way!

**Project Repository**

You can find the source code and all issues on GitHub: `Locust Telemetry Repository <https://github.com/platform-crew/locust-telemetry>`_

**Getting Started**

Follow these simple steps to set up your local development environment:

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

4. **Install pre-commit hooks** to maintain code quality:

   .. code-block:: bash

       pre-commit install

   You can also run hooks manually on only changed files:

   .. code-block:: bash

       pre-commit run --files $(git diff --name-only)

**Coding Guidelines**

We want contributions to be **clean and consistent**. Please:

* Follow **PEP8** coding conventions.
* Write clear docstrings (**Google style** or **reStructuredText style**).
* Keep commits **small and focused** with descriptive messages.
* Include **unit tests** for all new functionality.
* Target your **PRs to the main branch**.

**Pre-commit Hooks**

We use `pre-commit` to enforce code style, linting, and other quality checks.
Make sure to run the hooks before submitting a pull request—it keeps the codebase clean and consistent for everyone.

**Pull Requests**

* Use the **PR template** provided.
* Give a **clear description** of the changes and why they are needed.
* Reference related **issues** if applicable.
* Ensure all tests **pass** and code coverage is maintained.

**Reporting Issues**

Encountered a bug or unexpected behavior?

1. Check the existing issues to avoid duplicates.
2. If none exist, create a new issue on GitHub: `Report an Issue <https://github.com/platform-crew/locust-telemetry/issues>`_

**Discussions**

For questions, ideas, or general discussions, join our community: `GitHub Discussions <https://github.com/platform-crew/locust-telemetry/discussions>`_

💡 **Tip:** Even small contributions like improving documentation, adding examples, or reporting issues are highly appreciated!

**License**

By contributing, you agree that your contributions will be licensed under the same license as the project.
