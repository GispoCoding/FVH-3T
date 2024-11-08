<h1 align="center">Traffic Trajectory Toolkit</h2>
<p align="center">QGIS plugin for traffic trajectory analysis</p>

<!-- badges -->
<p align="center">
  <a href="https://github.com/GispoCoding/FVH-3T/actions/workflows/tests.yml">
    <img src="https://github.com/GispoCoding/fvh-3t/workflows/Tests/badge.svg"
  /></a>
  <a href="https://github.com/GispoCoding/FVH-3T/actions/workflows/code-style.yml">
    <img src="https://github.com/GispoCoding/fvh-3t/workflows/code-style/badge.svg"
  /></a>
  <a href="https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html">
    <img src="https://img.shields.io/badge/License-GPLv2-blue.svg"
  /></a>
</p>

<!-- links to sections / TOC -->
<p align="center">
  <a href="#introduction">Introduction</a>
  ·
  <a href="#getting-started">Getting started</a>
  ·
  <a href="#development">Development</a>
  ·
  <a href="#license">License</a>
</p>

## Introduction

FVH-3T (Forum Virium Helsinki - **T**raffic
**T**rajectory **T**oolkit) is a QGIS plugin which
allows users to analyze trajectory-based traffic data.
It is intended to be used with point data sets captured
by Lidar and processed to a format from which trajectories
can be created.

> [!IMPORTANT]
> FVH-3T is still in development!

## Getting started

You must have installed QGIS, version 3.34 or newer (earlier versions
might work but are not officially supported.
To install the plugin you can download the latest release through
[this](https://github.com/GispoCoding/FVH-3T/releases/latest)
link. Click to download the **fvh3t._\<version number\>_.zip** file.

You can install the plugin directly from the .zip file:
* Open QGIS
and from the top menu click **Plugins** >
**Manage and Install Plugins...**
* In the dialog click on the
**Install from ZIP** tab on the panel on the left
* Select the .zip
file you downloaded previously and click **Install Plugin**.

You can find the features of the plugin in:
*  the plugins **toolbar**
* the **Plugins** menu
* most importantly the
**Processing toolbox** (found in **Processing** > **Toolbox** > **Traffic trajectory toolkit**).

You can create a virtual **gate** or  an **area layer**
using the toolbar buttons, to which you digitize new features.
These layers can then in turn be used in the processing algorithms
with the Lidar point data to calculate information about the
trajectories passing through the gates or areas.

### Algorithms

Three algorithms are included.

#### Count trajectories (areas)
* Two inputs:
  1. Point layer from which trajectories can be created
  2. Gate layer
* Creates trajectories from the points
* Calculates their speed inside of the given areas
* Two outputs:
  1. Line layer for the trajectories
  2. Polygon layer for the areas with additional calculated data

#### Count trajectories (gates)
* Two inputs:
  1. Point layer from which trajectories can be created
  2. Area layer
* Creates trajectories from the points
* Calculates whether they pass the given gates
* Two outputs:
  1. Line layer for the trajectories
  2. Line layer for the gates with additional calculated data

#### Export to JSON
* Exports the data of "Count trajectories (gates)" output 2 to a JSON file
* Output adheres to [this](https://bitbucket.org/conveqs/conveqs_platform_interface/src/master/json_schemas/history-detectors.json)
JSON schema

## Development

Create a virtual environment activate it and install needed dependencies with the following commands:
```console
python create_qgis_venv.py
.venv\Scripts\activate # On Linux and macOS run `source .venv\bin\activate`
pip install -r requirements-dev.txt
```

For more detailed development instructions see [development](docs/development.md).

### Testing the plugin on QGIS

A symbolic link / directory junction should be made to the directory containing the installed plugins pointing to the dev plugin package.

On Windows Command promt
```console
mklink /J %AppData%\QGIS\QGIS3\profiles\default\python\plugins\fvh3t .\fvh3t
```

On Windows PowerShell
```console
New-Item -ItemType SymbolicLink -Path ${env:APPDATA}\QGIS\QGIS3\profiles\default\python\plugins\fvh3t -Value ${pwd}\fvh3t
```

On Linux
```console
ln -s fvh3t/ ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/fvh3t
```

After that you should be able to enable the plugin in the QGIS Plugin Manager.

### VsCode setup

On VS Code use the workspace [fvh3t.code-workspace](fvh3t.code-workspace).
The workspace contains all the settings and extensions needed for development.

Select the Python interpreter with Command Palette (Ctrl+Shift+P). Select `Python: Select Interpreter` and choose
the one with the path `.venv\Scripts\python.exe`.

## License
This plugin is distributed under the terms of the [GNU General Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) license.

See [LICENSE](LICENSE) for more information.
