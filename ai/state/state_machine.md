# State machine

This file describes the vehicle state machine.
It uses [MermaidJS](https://mermaid.js.org/) to display the diagram.

```mermaid
---
title: Vehicle state machine
---
stateDiagram-v2
    [*] --> Idle

    Arrived --> Driving: drive
    Idle --> Driving: drive
    Healing --> Driving: drive
    Recovering --> Driving: drive
    Waiting --> Driving: drive

    Driving --> Arrived: arrive
    Idle --> Arrived: arrive

    Arrived --> Crashed: crash
    Driving --> Crashed: crash
    Idle --> Crashed: crash
    Healing --> Crashed: crash

    Driving --> Healing: heal

    Driving --> Parked: park
    Arrived --> Parked: park

    Crashed --> Recovering: recover

    Driving --> Waiting: wait

    Parked --> [*]
```
