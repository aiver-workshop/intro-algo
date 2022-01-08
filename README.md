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
Next install the following packages:
```
conda install numpy
conda install matplotlib
conda install -c conda-forge python-dotenv
conda install -c anaconda requests
conda install -c conda-forge websockets
pip install python-gnupg
```

### Github - Download the code
Install Git, then open a `Git Shell` to download this repository to your local computer by:
```
git clone https://github.com/aiver-workshop/intro-algo.git
```
This command will download the codes in a folder called `intro-algo`, where you will find a `.\intro-algo\python` subfolder we call the `python working directory`.

### PyCharm - Development IDE
1. Open the project by `File` -> `Open...` -> select `python working directory`
2. Configure the Python interpreter by `File` -> `Settings...` -> `Project: intro-algo` -> `Python Interpreter` -> `Add` -> `Conda Environment` -> `Existing environment` -> select Anaconda environment directory of py37-smu

### Environment variable - Secret info management
:warning: **This folder contains sensitive information! Never share or check-in the files**
| The simplest way and the wrong way to handle credentials is to hardcode it in our code. |
| --- |
 

A safe way to handle your secret keys/password is saving them in envirnoment variables. 
We create a folder `c:\vault` to store secret files with sensitive information like api credentials. The key/value pairs in the file will be read as `environment variable` when Python program runs. All the secret filename will start with a dot such as `.keys`. In script, we can read the values as follow:
```
import os
from dotenv import load_dotenv

dotenv_path = 'c:/vault/.keys'
load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
```



