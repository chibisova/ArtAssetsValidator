from dotenv import load_dotenv
import urllib.request
import json
import os

from groq import Groq
import pathlib

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def notify_slack(fbx_path: str, validation_report: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    filename = pathlib.Path(fbx_path).name

    message = {
        "text": f"*Asset validation failed:* `{filename}`\n{validation_report}"
    }

    data = json.dumps(message).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req)

def load_conventions() -> str:
    return pathlib.Path("CONVENTIONS.md").read_text()

def validate_asset(fbx_path: str, mesh_data: dict) -> str:
    conventions = load_conventions()
    filename = pathlib.Path(fbx_path).name

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"""You are a technical artist validator.

Studio conventions:
{conventions}

You will receive a filename and real mesh data extracted from the FBX.
Validate against the conventions and respond with PASS or FAIL, then bullet points."""},
            {"role": "user", "content": f"""Filename: {filename}
Vertices: {mesh_data['vertices']}
Triangles: {mesh_data['triangles']}
Has UVs: {mesh_data['has_uvs']}"""}
        ]
    )
    return response.choices[0].message.content

def rename_asset(fbx_path: str, validation_report: str) -> str:
    filename = pathlib.Path(fbx_path).name
    stem = pathlib.Path(fbx_path).stem

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": """You are a filename corrector.
Your ONLY job is to fix the prefix of the filename.
Do NOT change the rest of the name.
Do NOT invent a new name.
Do NOT summarize or describe the asset.

Rules:
- If filename does not start with Fbx_, add Fbx_ at the start
- Keep the original name exactly as is after the prefix
- Output ONLY the corrected filename with .fbx extension
- No explanation, no punctuation, no newlines

Example:
Input: spaceship_Very_Final.fbx
Output: Fbx_spaceship_Very_Final.fbx

Input: Fbx_SpaceshipFix.fbx
Output: Fbx_SpaceshipFix.fbx"""},
            {"role": "user", "content": f"Fix the prefix of this filename: {filename}"}
        ]
    )

    result = response.choices[0].message.content.strip().splitlines()[0]
    
    # safety net: force Fbx_ prefix if model still gets it wrong
    if not result.startswith("Fbx_"):
        result = f"Fbx_{stem}.fbx"
    
    return result

def rename_texture(tex_path: str) -> str:
    filename = pathlib.Path(tex_path).name
    extension = pathlib.Path(tex_path).suffix

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"""You are a filename corrector.
Output ONLY the corrected filename. Nothing else.
No explanation. No punctuation. No newlines. No reasoning.
Just a single filename like: Tex_RockProp_N.png

Rules:
- Start with Tex_
- Use PascalCase
- End with _D, _N, or _ORM before the extension
- Keep the original extension: {extension}"""},
            {"role": "user", "content": filename}
        ]
    )
    
    # Safety net: take only the first line in case model still rambles
    result = response.choices[0].message.content.strip().splitlines()[0]
    return result
