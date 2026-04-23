# Blender LiDAR Simulator for PolyGNN Research

## Overview
This repository contains a custom LiDAR simulation script built in **Blender Python (`bpy`)** for generating synthetic 3D point clouds from one or more camera objects in a Blender scene. The simulator was developed as part of a research workflow for training a **PolyGNN** model on LiDAR-like spatial data.

Instead of using a physical LiDAR sensor, this script performs **ray casting** from Blender camera positions and orientations, sampling the scene over a configurable vertical and horizontal field of view. The hit locations are collected and converted into a point-cloud-style mesh object inside Blender.

The main goal of this project is to create controllable synthetic sensor data that can later be exported, processed, and transformed into graph-based representations suitable for PolyGNN training.

## What the Script Does
The script:

1. Defines LiDAR-like scan settings such as:
   - target point density
   - reference distance
   - vertical field of view
   - horizontal field of view
   - maximum sensing range
2. Computes the angular sampling resolution required to approximate a desired point density at a chosen reference distance.
3. Collects **all camera objects** in the Blender scene.
4. Emits rays from each camera across the configured scanning grid.
5. Uses Blender's `scene.ray_cast(...)` to detect intersections with scene geometry.
6. Stores all hit locations as 3D points.
7. Creates a new point-cloud-style mesh object for each camera scan.

This means the script acts as a basic LiDAR simulator using Blender's geometry and camera transforms as the sensing setup. 

---

## Current Script Configuration
The uploaded script currently uses the following parameters:

- **Reference distance:** `10.0 m`
- **Target density:** `100.0 points/m²`
- **Vertical FOV:** `90°`
- **Horizontal FOV:** `90°`
- **Maximum range:** `100.0 m`

The script converts the density target into angular divisions using a square-footprint approximation. It then scans the scene from every camera found in the Blender file. 

---

## Core Functions

### `divisions_from_density(D_pts_per_m2, r_m, v_fov_deg, h_fov_deg)`
This function computes the vertical and horizontal sampling divisions needed to achieve an approximate target point density at a specified distance.

It:
- checks that density and distance are positive,
- estimates the angular spacing,
- converts that spacing into vertical and horizontal scan divisions.

This is useful because it gives your simulator a density-based interpretation rather than hardcoding only the number of rays. fileciteturn0file0

### `generate_lidar_points(cam_obj, v_divs, h_divs, v_fov_deg, h_fov_deg, max_range=100.0)`
This is the main scanning function.

It:
- gets the camera world position,
- derives the camera basis vectors (`forward`, `right`, `up`),
- sweeps through vertical and horizontal angles,
- constructs a world-space ray direction for each beam,
- ray casts into the scene,
- stores hit points when intersections occur.

This produces the synthetic LiDAR returns from a given camera. fileciteturn0file0

### `create_point_cloud(name, points)`
This function converts the collected hit points into a Blender mesh object by creating vertices without edges or faces.

This is a simple and effective way to visualize the resulting point cloud directly in Blender. fileciteturn0file0

### `main()`
The entry point:
- finds all cameras in the Blender scene,
- computes scan divisions from the configured density,
- scans from each camera,
- creates a point cloud object named `LiDAR_<camera_name>`.

If no cameras exist, the script raises an error.

## Objectives
- Simulate LiDAR scanning in Blender
- Generate point cloud datasets
- Support PolyGNN training workflows

## Features
- Density-based sampling
- Adjustable field of view (vertical & horizontal)
- Multi-camera support
- Ray-casting based point detection
- Automatic point cloud generation

## Project Structure
```
lidar-project/
├── blender/
│   └── lidar_simulator.py
├── data/
├── outputs/
├── README.md
└── .gitignore
```

## Requirements
- Blender
- Python (Blender environment)
- bpy module
- mathutils

## How to Run
1. Open Blender
2. Load a scene with camera objects
3. Open scripting workspace
4. Run lidar_simulator.py

## Parameters
- TARGET_DENSITY: points per square meter
- VERT_FOV_DEG: vertical field of view
- HORIZ_FOV_DEG: horizontal field of view
- MAX_RANGE_M: max scanning distance

## Output
Creates point cloud objects in Blender:
- Named as LiDAR_<CameraName>

## Research Context
Used for generating synthetic LiDAR data for training PolyGNN models.

## Future Work
- Export point clouds (.ply, .csv)
- Dataset automation
- Integration with ML pipeline

## Author
Sivakumar Madhushan

## License
For research and educational use
