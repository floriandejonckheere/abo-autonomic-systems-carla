# State machine

This file describes the vehicle state machine.
It uses [MermaidJS](https://mermaid.js.org/) to display the diagram.

For convenience, epsilon transitions are not included in the diagram.

```mermaid
---
title: Vehicle state machine
---
stateDiagram-v2
    [*] --> undefined
    
    undefined --> driving: drive
    arrived --> driving: drive
    healing --> driving: drive
    
    driving --> arrived: arrive
    arrived --> [*]
    
    driving --> crashed: crash
    
    crashed --> healing: heal
```
