<p align="center">
  <img width="300" src="./docs/images/logo.png?raw=true" alt="icon"/>
</p>
<h1 align="center">FCP7XML to Unreal</h1>
<br></br>

 [![Build Status](https://github.com/viacomcbs/fcp7xml-to-unreal/actions/workflows/python-package.yml/badge.svg)](https://github.com/viacomcbs/fcp7xml-to-unreal/actions/workflows/python-package.yml)
[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://viacomcbs.github.io/fcp7xml-to-unreal/)
[![GitHub License](https://img.shields.io/github/license/viacomcbs/fcp7xml-to-unreal)](https://github.com/viacomcbs/fcp7xml-to-unreal/blob/main/LICENSE)
<!-- Pytest Coverage Comment:Begin -->
<!-- Pytest Coverage Comment:End -->

`fcp7xml-to-unreal` is a utility for filtering FCP XML (FCP 7 XML v5) editorial output for import into Unreal Engine.

Edit shots rendered from Unreal Engine in your preferred editing software and import the edits back into Unreal Engine, without crashing. **Only FCP 7 XML v5 is supported.**

**This is the readme for developers.** The documentation for users is available here: [https://viacomcbs.github.io/fcp7xml-to-unreal/](https://viacomcbs.github.io/fcp7xml-to-unreal/)

## Prerequisites

You will need [Python](https://www.python.org/) installed. Tested with Python 3.9, expected to work with Python 3.9+.

## Quickstart

Install using [pip](https://pypi.org/project/pip/) or [pipx](https://pipx.pypa.io/stable/).

```bash
$ pip install fcp7xml-to-unreal
```

or

```bash
$ pipx install fcp7xml-to-unreal
```

This will provide the command-line utilities:

- `fcp7xml-to-unreal` - an XML filtering utility, fixing XML (**FCP 7 XML v5 format only**) exports for import into Unreal Engine.

See the [user documentation](https://viacomcbs.github.io/fcp7xml-to-unreal/) for examples.

## Developer Setup

Clone this repository (or fork on GitHub).

In the local repository directory, set up for Python development. The steps below show [Astral's uv](https://docs.astral.sh/uv/) in use - but using Python [venv](https://docs.python.org/3/library/venv.html) is also fine.

```bash
# Create and activate Python virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies with the project set as editable
uv pip install -e ".[dev]"

or (not using uv)

python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate

# update pip in venv
python -m pip install -U pip

# install
python -m pip install .
python -m pip install ".[dev]" # install with optional development packages

# Install Git pre-commit hooks
pre-commit install
```

## Contributing

Contributions to improve this utility are welcome! Please submit [issues](https://github.com/viacomcbs/fcp7xml-to-unreal/issues) and [pull requests](https://github.com/viacomcbs/fcp7xml-to-unreal/pulls) on GitHub.

### Tests

See [TESTS.md](./TESTS.md) for details on running this product's tests.

## License

This code is MIT licensed. See the [LICENSE](LICENSE) file for details.

## References

- [FCP7 XML Reference](<https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/FinalCutPro_XML/VersionsoftheInterchangeFormat/VersionsoftheInterchangeFormat.html>)
