# State machine

This file describes the vehicle state machine.
It uses [MermaidJS](https://mermaid.js.org/) to display the diagram.

For convenience, epsilon transitions are not included in the diagram.

```mermaid
---
title: Vehicle state machine
---
stateDiagram-v2
    [*] --> Idle

    Idle --> Driving: drive
    Arrived --> Driving: drive
    Healing --> Driving: drive

    Driving --> Arrived: arrive

    Driving --> Crashed: crash

    Crashed --> Healing: heal

    Driving --> Parked: park
    Arrived --> Parked: park

    Parked --> [*]
```
