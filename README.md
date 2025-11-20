[![Build Status](https://github.com/TomDakan/Copier_Python_Default/actions/workflows/main.yaml/badge.svg)](https://github.com/TomDakan/Copier_Python_Default/actions/workflows/main.yaml)
[![Documentation Status](https://github.com/TomDakan/Copier_Python_Default/actions/workflows/docs.yaml/badge.svg)](https://github.com/TomDakan/Copier_Python_Default/actions/workflows/docs.yaml)
[![Coverage Status](https://codecov.io/gh/TomDakan/Copier_Python_Default/branch/main/graph/badge.svg)](https://codecov.io/gh/TomDakan/Copier_Python_Default)

# Opinionated Python Project Template

> [!NOTE]
> Projects generated from this template will feature dynamic badges reflecting their specific repository and CI/CD status.

This is a project template that spins up a new python project in about a minute. You must have python and the copier package installed to use it.

It was inspired by my own desire for easily reproducible projects, and has a number of improvements borrowed from Tucker Beck's project <https://github.com/dusktreader/xerox-python> as well as 

> [!WARNING]
> This template is _extremely_ opinionated. It creates a Python project just the way I like. It might not be _immediately_ useful for anyone else unless they adapt it to their needs.

## Project Toolchain

The project created by this template is pre-configured to use a modern Python toolchain reflecting best practices as of late 2025. To develop within the new project, you (and any contributors) will need:

    * mise: For managing Python versions and project-specific virtual environments automatically. After cloning the project, you should run `mise install` to set up the environment.
    * just: A command runner for project-specific tasks. (Optional)
    * PDM: The primary project and dependency manager. Can also be used as a task runner if you don't want to use just.
    * uv: (Recommended) PDM uses uv as a high-speed backend for installing and locking, if available.


## Usage

I'm designing this project with the intention of being able to support subprojects that add additional dependencies, boilerplate files, etc. I'll link to subproject repos as I add them.

> [!WARNING]
> This project runs various copier tasks after the directory is setup. copier requires the '--trust' switch when running with 
> tasks due to the potential for unintended consequences when you run someone else's code. Make sure you review copier.yaml and  
> are happy with the tasks that it runs before you use this template.

## Dependencies

This template assumes that you have the following tools installed:

    * mise
    * pdm
    * copier
    * GitHub CLI (gh): (Optional)
    * just (Optional)

This template uses the github cli tool to commit and push to github at the end of the setup process. You will need to have ghcli installed and authenticated for that to work: <https://cli.github.com/manual/>

## One line project setup

You can use the following one-line commands to build a project from this repo without checking it out.

```bash
copier copy --trust gh:TomDakan/Copier_Python_Default .
```
