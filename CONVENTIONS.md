# Studio Asset Conventions

## Naming
- Meshes must start with Fbx_ (e.g. SM_RockProp_LOD0)
- Textures must start with Tex_ followed by the asset name and a suffix:
  - Tex_AssetName_D (diffuse)
  - Tex_AssetName_N (normal)
  - Tex_AssetName_ORM (occlusion/roughness/metallic)

## Poly limits
- Hero prop: 100k tris max
- Background prop: 3k tris max
- If prop type cannot be determined from filename, assume hero prop

## UV rules
- No overlapping UVs on channel 0
- Lightmap UVs must exist on channel 1

## Validation rules
- ONLY fail if a rule is definitively violated
- If prop type is ambiguous, assume hero prop and validate against hero limits
- UV channel data is not available — do not fail on UV rules unless has_uvs is False
