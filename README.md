# Autonomic Systems and Software (IT00CE05)

This repository contains the CARLA simulation project for the Autonomic Systems and Software course (IT00CE05).

## Demonstration

The presentation can be found in [presentation.](presentation.pdf).

Several short demonstration video's of various scenario's were recorded:

- [Milestone One](demo/milestone_one.mp4): drive to the roundabout, stop, then enter and go around
- [Milestone Two](demo/milestone_two.mp4): full simulation of pathfinding towards a destination
- [Milestone Three](demo/milestone_three.mp4): collision avoidance
- [Crash](demo/crash.mp4): crash detection and recovery
- [Learner driver](demo/learner_driver.mp4): traffic observation
- [Stop and go](demo/stop_and_go.mp4): stop and go in dense traffic
- [Traffic lights](demo/traffic_lights.mp4): traffic light detection

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

## Usage

Run the `manual_control.py` script to control the vehicle in the simulation.
Append `--help` to see the available options.

```sh
python manual_control.py
```

Run the `spawn_custom_npc.py` script to spawn a number of autonomic vehicles in the simulation.
Append `--help` to see the available options.

```sh
python spawn_custom_npc.py
```

Run the `ai_test.py` script to test the AI controller.
Append `--help` to see the available options.

```sh
python ai_test.py

# Test a specific scenario (see game/scenarios for available scenarios)
python ai_test.py --scenario MilestoneOne

# Enable debug window
python ai_test.py --debug

# Let spectator camera follow the vehicle
python ai_test.py --follow
```

Run the `extract_graph.py` script to extract the navigation graph from the map.

```sh
python extract_graph.py
```

Extracting the planned paths requires modifying the `Navigator` class.
See the note at the end of the `extract_graph.py` file for more information.

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
