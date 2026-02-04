<p align="center">
  <img width="300" src="images/logo.png?raw=true" alt="icon"/>
</p>
<h1 align="center">FCP7XML to Unreal</h1>
<br></br>

 [![Build Status](https://github.com/viacomcbs/fcp7xml-to-unreal/actions/workflows/python-package.yml/badge.svg)](https://github.com/viacomcbs/fcp7xml-to-unreal/actions/workflows/python-package.yml)
[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://viacomcbs.github.io/fcp7xml-to-unreal/)
[![GitHub License](https://img.shields.io/github/license/viacomcbs/fcp7xml-to-unreal)](https://github.com/viacomcbs/fcp7xml-to-unreal/blob/main/LICENSE)

`fcp7xml-to-unreal` is a utility for processing XML editorial output for import into Unreal Engine.

Edit shots rendered from Unreal Engine in your preferred editing software, export as XML, then import the edits into Unreal Engine.

![workflow steps](./images/workflow.png)

## Prerequisites

You will need [Python](https://www.python.org/) installed - all [supported versions of Python](https://devguide.python.org/versions/) should work.

## Quickstart

Install using [pip](https://pypi.org/project/pip/) or [pipx](https://pipx.pypa.io/stable/).

```bash
$ pip install fcp7xml-to-unreal
```

or

```bash
$ pipx install fcp7xml-to-unreal
```

This will provide the `fcp7xml-to-unreal` utility. Launch it by typing `fcp7xml-to-unreal` in a shell or terminal.

## Workflow

- Set up your narrative project using some shot naming and structure conventions. Episode, Scene, and Shot are the defaults - see [film_language](./film_language.md) for details.
  - If configuring differently from the defaults, copy and edit a [config.yaml](../src/premiere_to_ue/config.yaml) file as needed. See [configuration.md](./configuration.md) for details.
- Render a movie for each shot from Unreal Engine, following the naming established in `config.yaml`.
  - The defaults provided assume an Episode, Scene, Shot naming convention, where the movie rendered for Episode 101, Scene 02, Shot 003 would be named `101_02_shot_003.mov`.
- Import the movies into an editing application (Final Cut Pro, Adobe Premiere, Resolve...) and edit them.
  - In the editing application, make cuts, labeling Unreal Scenes and Shots with burnin images to mark them for syncing back to Unreal. (this contemplates Dissolve and Fade transitions, as well as non-shot items like leaders and breaks). See [marking shots](./marking_shots.md) for details.
- Export an XML representation of the cut from the editing application in the **FCP7 XML** format.
- **Process the XML with `fxp7xml-to-unreal`**.
- Import the filtered XML into Unreal Engine (in the Level Sequence) to apply the edits to Unreal shots!

### Audio Report

The "Audio report" function produces a csv file listing all audio files used in the edit.

## Applications Tested

- Adobe Premiere Pro 26.0.0
- Unreal Engine 5.1.1

Note: Other editing applications (for example, Resolve) that can export Final Cut Pro 7 XML should be usable.

## Changes

See the product [Change Log](https://github.com/viacomcbs/fcp7xml-to-unreal/blob/main/CHANGELOG.md) on GitHub for a history of changes.

## Problems?

Please submit [issues](https://github.com/viacomcbs/fcp7xml-to-unreal/issues) on GitHub.

## Want to contribute?

Details on the GitHub page: [https://github.com/viacomcbs/fcp7xml-to-unreal](https://github.com/viacomcbs/fcp7xml-to-unreal).
