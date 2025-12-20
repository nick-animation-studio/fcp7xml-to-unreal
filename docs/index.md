<p align="center">
  <img width="300" src="images/logo.png?raw=true" alt="icon"/>
</p>
<h1 align="center">Premiere to UE</h1>
<br></br>

 [![Build Status](https://github.com/viacomcbs/premiere-to-ue/actions/workflows/python-package.yml/badge.svg)](https://github.com/viacomcbs/premiere-to-ue/actions/workflows/python-package.yml)
[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://viacomcbs.github.io/premiere-to-ue/)
[![GitHub License](https://img.shields.io/github/license/viacomcbs/premiere-to-ue)](https://github.com/viacomcbs/premiere-to-ue/blob/main/LICENSE)

`premiere-to-ue` is a utility for processing XML editorial output from Adobe Premiere, for import into Unreal Engine.

Edit a sequence from Unreal Engine in Adobe Premiere and send the edits back to Unreal Engine.

## Prerequisites

You will need [Python](https://www.python.org/) installed - all [supported versions of Python](https://devguide.python.org/versions/) should work.

## Quickstart

Install using [pip](https://pypi.org/project/pip/) or [pipx](https://pipx.pypa.io/stable/).

```bash
$ pip install premiere-to-ue
```

or

```bash
$ pipx install premiere-to-ue
```

This will provide the `premiere-to-ue` utility. Launch it by typing `premiere-to-ue` in a shell or terminal.

## Workflow

- Render a sequence of images from Unreal Engine.
- Import those images into Adobe Premiere and edit them.
- Export an XML edit decision list from Adobe Premiere.
- **Process the XML with `premiere-to-ue`**
- Import the filtered XML into Unreal Engine to bring in the edits!

## Changes

See the product [Change Log](https://github.com/viacomcbs/premiere-to-ue/blob/main/CHANGELOG.md) on GitHub for a history of changes.

## Problems?

Please submit [issues](https://github.com/viacomcbs/premiere-to-ue/issues) on GitHub.

## Want to contribute?

Details on the GitHub page: [https://github.com/viacomcbs/premiere-to-ue](https://github.com/viacomcbs/premiere-to-ue).
