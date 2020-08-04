After creating a copy of this template, change the name of the package in `setup.py`, `pytest.ini`, `MANIFEST.in`, `codebuild_formation.yaml` and the subfolder within the `src` directory.
Before CodeBuild can automatically publish to PyPI, the package must be registered using command `twine register`: https://twine.readthedocs.io/en/latest/#twine-register

Steps to create repo:
   - Log in as Curi-Bio-CI
   - Select python-github-template as template
   - Check box that says `include all branches`
   - Set repo to public
   - Publish repo
   - In Actions -> Dev: click Run workflow. Wait until workflow finishes
   - In Settings -> Security & analysis: enable Dependabot security updates
   - In Settings -> Branches:
      - Add Rule with master specified as Branch pattern name
         - check Require pull requests reviews before merging
         - check Dismiss stale pull requests
         - check Require Review from Code Owners
         - check Require status checks before merging
         - Under status checks, check all of the python checks
         - check Include administrators
         - check Restrict who can push to matching branches
      - Add Rule with development specified as Branch pattern name
         - repeat master branch steps

.. image:: https://github.com/CuriBio/python-github-template/workflows/Dev/badge.svg?branch=development
   :alt: Development Branch Build

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
