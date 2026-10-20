---
title: Balance · Prey and predators
summary: English version
---

An agent simulation in a closed meadow: rabbits eat vegetation, predators hunt and plants regrow. Each animal has its own energy and behaviour. This educational model illustrates emergent balances; it does not predict real ecosystems and uses no machine learning.

### Explore the meadow
The simulation starts automatically. **Pause** stops time, **Single step** advances one step and the speed selector changes playback speed. Tap an animal to inspect its age, energy and behaviour. Drag the meadow to move the camera; scroll to zoom and use **Reset view** to restore the original framing. Hiding the tab pauses the simulation.

### Build an experiment
Set initial populations, vegetation, burrow count and capacity, choose a seed, then select **Restart experiment**. Identical seeds and actions reproduce the same experiment. Speeds, regrowth and energy consumption change immediately. You can also add animals, show trails and display the selected animal’s perception. The population is limited to 650 animals.

### Understand shelters
Adjust individual burrow capacities without evicting occupants. Sheltered rabbits still count as prey and consume energy. They emerge when their energy reaches 45 points or danger moves away. Reproduction consumes energy; hunger, predation and ageing can lead to extinction.

### Read and export results
The chart shows prey, predators, available vegetation and sheltered rabbits. Hide series, follow recent minutes or choose a fixed period with the sliders. History retains the last 3,600 simulated seconds. **CSV** exports this history with stable English column names. Everything runs in your browser without server storage; reloading the page restarts the experiment.

### Implementation
TypeScript and Canvas simulation integrated into Flask, with a responsive interface and French/English text. Coded with Codex.
