import open3d as o3d

mesh = o3d.io.read_triangle_mesh("./watch_folder/Debris_prop.fbx")
print(f"Vertices: {len(mesh.vertices)}")
print(f"Triangles: {len(mesh.triangles)}")
