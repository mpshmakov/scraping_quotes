# Contributing Guide

I appreciate your interest in contributing to my Python project! This guide will help you get started with the contribution process.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone git@github.com:mpshmakov/scraping_books.git`
3. Create your feature branch: `git checkout -b super-new-feature`
4. Set up a virtual environment:

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   python3 -m pip install --upgrade pip
   ```

## Making Changes

1. Make your changes and ensure they follow the project's coding standards
2. Add or update tests as necessary
3. Run the tests locally to ensure they pass
4. Commit your changes: `git commit -s -m 'super-new-feature'`
5. Push to the branch: `git push origin super-new-feature`
6. Create a pull request

## Building and Testing

To run the tests:

```sh
coverage run -m unittest discover

## OR ##

pytest
```

## Submitting Changes

- Ensure your code passes all tests
- Update documentation if you're changing functionality

After your pull request is merged, you can safely delete your branch.

## Reporting Issues

If you find a bug or have a suggestion for improvement, please email the project's maintainer. Provide as much detail as possible, including:

- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (Python version, OS, etc.)

Thank you for contributing to my project!
