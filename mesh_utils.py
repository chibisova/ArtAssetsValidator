import open3d as o3d

o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error)

def get_mesh_data(fbx_path: str) -> dict:
    mesh = o3d.io.read_triangle_mesh(fbx_path)
    return {
        "vertices": len(mesh.vertices),
        "triangles": len(mesh.triangles),
        "has_uvs": mesh.has_triangle_uvs(),
    }
