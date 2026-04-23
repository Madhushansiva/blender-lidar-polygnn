import bpy
import math
import mathutils
from math import radians, ceil, sqrt

# -------------------------
# CONFIG
# -------------------------
REF_DISTANCE_M   = 10.0     # reference distance for density control


# changing parameters

TARGET_DENSITY   = 100.0    # points per m² at 10m
VERT_FOV_DEG     = 90  # vertical field of view (±30°)
HORIZ_FOV_DEG    = 90    # horizontal field of view
MAX_RANGE_M      = 100.0    # max ray length

# -------------------------
# DENSITY → DIVISIONS
# -------------------------
def divisions_from_density(D_pts_per_m2, r_m, v_fov_deg, h_fov_deg):
    """Compute vertical/horizontal divisions from target density at distance r."""
    if D_pts_per_m2 <= 0 or r_m <= 0:
        raise ValueError("Density and reference distance must be positive.")
    # angular step for square footprint
    delta_theta = sqrt(1.0 / (D_pts_per_m2 * r_m * r_m))
    v_divs = max(1, ceil(radians(v_fov_deg) / delta_theta))
    h_divs = max(1, ceil(radians(h_fov_deg) / delta_theta))
    return v_divs, h_divs, delta_theta

# -------------------------
# RAYCAST SCAN
# -------------------------
def generate_lidar_points(cam_obj, v_divs, h_divs, v_fov_deg, h_fov_deg, max_range=100.0):
    """Generate LiDAR-like points from a camera origin and orientation."""
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()

    points = []
    origin = cam_obj.matrix_world.translation

    # Camera basis vectors
    R = cam_obj.matrix_world.to_3x3()
    forward = R @ mathutils.Vector((0, 0, -1))  # Blender cameras look along -Z
    right   = R @ mathutils.Vector((1, 0, 0))   # local +X
    up      = R @ mathutils.Vector((0, 1, 0))   # local +Y

    # Vertical and horizontal sweeps (symmetric FOV)
    for vi in range(v_divs):
        t_v = (vi / (v_divs - 1)) if v_divs > 1 else 0.5
        v_angle = (t_v - 0.5) * radians(v_fov_deg)

        for hi in range(h_divs):
            t_h = (hi / (h_divs - 1)) if h_divs > 1 else 0.5
            h_angle = (t_h - 0.5) * radians(h_fov_deg)

            # Ray direction = forward + offsets
            dir_world = forward + math.tan(h_angle) * right + math.tan(v_angle) * up
            dir_world.normalize()

            hit, loc, normal, face_index, hit_obj, _ = scene.ray_cast(
                depsgraph, origin, dir_world, distance=max_range
            )
            if hit:
                points.append(loc)

    return points

# -------------------------
# POINT CLOUD OBJECT
# -------------------------
def create_point_cloud(name, points):
    mesh = bpy.data.meshes.new(name + "_mesh")
    coords = [(p.x, p.y, p.z) for p in points]
    mesh.from_pydata(coords, [], [])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

# -------------------------
# MAIN
# -------------------------
def main():
    # Collect ALL cameras
    sensors = [o for o in bpy.data.objects if o.type == 'CAMERA']
    if not sensors:
        raise RuntimeError("No cameras found in the scene.")

    # Compute divisions
    v_divs, h_divs, dtheta = divisions_from_density(
        TARGET_DENSITY, REF_DISTANCE_M, VERT_FOV_DEG, HORIZ_FOV_DEG
    )
    print(f"[DENSITY] {TARGET_DENSITY:.1f} pts/m² @ {REF_DISTANCE_M} m "
          f"→ Δθ={math.degrees(dtheta):.4f}° "
          f"→ v_divs={v_divs}, h_divs={h_divs}")

    # Process each camera
    for cam in sensors:
        print(f"[SIM] Scanning from: {cam.name}")
        pts = generate_lidar_points(
            cam_obj=cam,
            v_divs=v_divs,
            h_divs=h_divs,
            v_fov_deg=VERT_FOV_DEG,
            h_fov_deg=HORIZ_FOV_DEG,
            max_range=MAX_RANGE_M
        )
        pc_name = f"LiDAR_{cam.name}"
        create_point_cloud(pc_name, pts)
        print(f"[SIM] Created '{pc_name}' with {len(pts)} points.")

if __name__ == "__main__":
    main()
