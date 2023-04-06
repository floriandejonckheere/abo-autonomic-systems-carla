# Autonomic Systems and Software (IT00CE05)

This repository contains the CARLA simulation project for the Autonomic Systems and Software course (IT00CE05).

## Setup

Download the CARLA simulator v0.9.4 from [Github](https://github.com/carla-simulator/carla/releases/tag/0.9.4) and extract the files into the repository directory.
Install Anaconda/Miniconda 3, and create a new Python 3.7 environment.

```sh
conda create -n carla python=3.7
conda activate carla
```

Install the Python requirements.

```sh
pip install -r requirements
```

Run the `CarlaUE4.exe` binary to start the simulation server, and run the Python scripts in the repository.

```sh
python manual_control.py
```

## Troubleshooting

When running any Python script:

```
ImportError: DLL load failed: The named module can't be found
```

[Add Anaconda/Miniconda to your PATH](https://github.com/pypa/virtualenv/issues/1139#issuecomment-453865723) (System Properties > Environment variables).

```
%ANACONDA_HOME%
%ANACONDA_HOME%\Library\mingw-w64\bin
%ANACONDA_HOME%\Library\usr\bin
%ANACONDA_HOME%\Library\bin
%ANACONDA_HOME%\Scripts
%ANACONDA_HOME%\bin
```

When running `manual_control.py`:

```
...
    mono = default_font if default_font in fonts else fonts[0]
IndexError: list index out of range
```

Modify the file and replace line 374:

```
# Replace
mono = default_font if default_font in fonts else fonts[0]

# With
mono = 'consolas'
```

## License

This repository is released under the [MIT License](LICENSE.md).
