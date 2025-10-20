# Opinionated Python Project Template

This is a project template that spins up a new python project in about a minute. You must have python and the copier package installed to use it.

It was inspired by my own desire for easily reproducible projects, and has a number of improvements borrowed from Tucker Beck's project <https://github.com/dusktreader/xerox-python> as well as 

> [!WARNING]
> This template is _extremely_ opinionated. It creates a Python project just the way I like. It might not be _immediately_ useful for anyone else unless they adapt it to their needs.

## Usage

I'm designing this project with the intention of being able to support subprojects that add additional dependencies, boilerplate files, etc. I'll link to subproject repos as I add them.

> [!WARNING]
> This project runs various copier tasks after the directory is setup. copier requires the '--trust' switch when running with 
> tasks due to the potential for unintended consequences when you run someone else's code. Make sure you review copier.yaml and  
> are happy with the tasks that it runs before you use this template.

## Dependencies

This template assumes that you have the following python packages installed:

    * mise (auto virtual environment switching)
    * pdm (project management)
    * uv (dependency management)

This template uses the github cli tool to commit and push to github at the end of the setup process. You will need to have ghcli installed and authenticated for that to work: <https://cli.github.com/manual/>

## One line project setup

You can use the following one-line commands to build a project from this repo without checking it out.

```bash
copier copy --trust gh:tomdakan/main_python_template .
```
