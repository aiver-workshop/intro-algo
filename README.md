# intro-algo
Introduction to algorithmic trading


### Anaconda - Setting up a Python environment

Install Anaconda, then open a `Anaconda Prompt` to create a Python 3.7 environment by:
```
conda create -n py37-smu python=3.7
activate py37-smu
```
To see a list of Anaconda environments and the installation directory:
```
conda env list
```
The installation directory contains the `python.exe`, and we will need this path for configuring PyCharm later.

### Github - Download the code
Install Git, then open a `Git Shell` to download this repository to your local computer by:
```
git clone https://github.com/aiver-workshop/intro-algo.git
```
This command will download the codes under a subfolder called `intro-algo`, which we call `working directory`.

### PyCharm - Development IDE
1. Open the project by `File` -> `Open...` -> select `working directory`
2. Configure the Python interpreter by `File` -> `Settings...` -> `Project: intro-algo` -> `Python Interpreter` -> `Add` -> `Conda Environment` -> `Existing environment` -> select Anaconda environment directory of py37-smu
