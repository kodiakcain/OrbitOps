import base64
import json
import math
import webbrowser
from importlib.resources import files
from pathlib import Path
from tkinter import Tk, filedialog

import cartopy.feature as cfeature

#Constants
EARTH_RADIUS_KM = 6371.0
GEOGRAPHY_ALTITUDE_KM = 8.0
GRID_ALTITUDE_KM = 10.0
SATELLITE_MODEL_FILENAME = "goes_r.glb"


def geographic_to_xyz(
    latitude: float,
    longitude: float,
    altitude_km: float = 0.0,
) -> tuple[float, float, float]:
    """Change geographic coordinates to X,Y,Z Cartesian coordinates."""
    if type(latitude) not in (int, float):
        raise TypeError("Latitude must be a number.")
    if type(longitude) not in (int, float):
        raise TypeError("Longitude must be a number.")
    if type(altitude_km) not in (int, float):
        raise TypeError("Altitude must be a number.")

    latitude, longitude, altitude_km = float(latitude), float(longitude), float(altitude_km)

    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if altitude_km < 0:
        raise ValueError("Altitude cannot be negative.")

    longitude = (longitude + 180) % 360 - 180
    radius = EARTH_RADIUS_KM + altitude_km
    latitude_rad, longitude_rad = math.radians(latitude), math.radians(longitude)

    x = radius * math.cos(latitude_rad) * math.cos(longitude_rad)
    y = radius * math.cos(latitude_rad) * math.sin(longitude_rad)
    z = radius * math.sin(latitude_rad)
    return x, y, z


def _append_geometry_coordinates(
    geometry,
    coordinate_groups: list[list[list[float]]],
    altitude_km: float,
) -> None:
    """Use geographic geometry to convert lat/lon into X,Y,Z."""
    geometry_type = geometry.geom_type

    if geometry_type == "LineString":
        line_points = [
            [round(x, 3), round(y, 3), round(z, 3)]
            for longitude, latitude in geometry.coords
            for x, y, z in [geographic_to_xyz(latitude, longitude, altitude_km)]
        ]
        if len(line_points) >= 2:
            coordinate_groups.append(line_points)
        return

    if geometry_type == "MultiLineString":
        for line in geometry.geoms:
            _append_geometry_coordinates(line, coordinate_groups, altitude_km)
        return

    if geometry_type == "Polygon":
        polygon_points = [
            [round(x, 3), round(y, 3), round(z, 3)]
            for longitude, latitude in geometry.exterior.coords
            for x, y, z in [geographic_to_xyz(latitude, longitude, altitude_km)]
        ]
        if len(polygon_points) >= 2:
            coordinate_groups.append(polygon_points)
        return

    if geometry_type == "MultiPolygon":
        for polygon in geometry.geoms:
            _append_geometry_coordinates(polygon, coordinate_groups, altitude_km)


def _feature_to_coordinate_groups(
    feature: cfeature.NaturalEarthFeature,
    altitude_km: float,
) -> list[list[list[float]]]:
    """Send all Cartopy geometries through to X,Y,Z groups."""
    coordinate_groups: list[list[list[float]]] = []
    for geometry in feature.geometries():
        _append_geometry_coordinates(geometry, coordinate_groups, altitude_km)
    return coordinate_groups


def _get_coastline_coordinates() -> list[list[list[float]]]:
    """Retrieves coastline data from Cartopy and converts to X,Y,Z."""
    feature = cfeature.NaturalEarthFeature(
        category="physical",
        name="coastline",
        scale="110m",
        facecolor="none",
    )
    return _feature_to_coordinate_groups(feature, GEOGRAPHY_ALTITUDE_KM)


def _get_border_coordinates() -> list[list[list[float]]]:
    """Get ninbternational country borders from Cartopy and convert to X,Y,Z for the globe."""
    feature = cfeature.NaturalEarthFeature(
        category="cultural",
        name="admin_0_boundary_lines_land",
        scale="110m",
        facecolor="none",
    )
    return _feature_to_coordinate_groups(feature, GEOGRAPHY_ALTITUDE_KM)


def _ring_to_lon_lat(ring) -> list[list[float]]:
    """Take a ring from Earth and convert its coordinates to a python list."""
    return [[round(float(longitude), 4), round(float(latitude), 4)] for longitude, latitude in ring.coords]


def _append_land_polygon(polygon, polygon_data: list[dict]) -> None:
    """Take a land polygon and store outer boundary + holes."""
    polygon_data.append(
        {
            "exterior": _ring_to_lon_lat(polygon.exterior),
            "holes": [_ring_to_lon_lat(interior) for interior in polygon.interiors],
        }
    )


def _get_land_polygon_data() -> list[dict]:
    """Get worlds land polygons."""
    feature = cfeature.NaturalEarthFeature(
        category="physical",
        name="land",
        scale="110m",
        facecolor="none",
    )
    polygon_data: list[dict] = []

    for geometry in feature.geometries():
        if geometry.geom_type == "Polygon":
            _append_land_polygon(geometry, polygon_data)
        elif geometry.geom_type == "MultiPolygon":
            for polygon in geometry.geoms:
                _append_land_polygon(polygon, polygon_data)

    return polygon_data


def _get_grid_coordinates() -> list[list[list[float]]]:
    """Create the globe's lat/lon grid lines."""
    coordinate_groups: list[list[list[float]]] = []

    for latitude in range(-60, 61, 30):
        coordinate_groups.append(
            [
                [round(x, 3), round(y, 3), round(z, 3)]
                for longitude in range(-180, 181, 6)
                for x, y, z in [geographic_to_xyz(latitude, longitude, GRID_ALTITUDE_KM)]
            ]
        )

    for longitude in range(-180, 180, 30):
        coordinate_groups.append(
            [
                [round(x, 3), round(y, 3), round(z, 3)]
                for latitude in range(-90, 91, 6)
                for x, y, z in [geographic_to_xyz(latitude, longitude, GRID_ALTITUDE_KM)]
            ]
        )

    return coordinate_groups


def _ground_track_to_data(ground_track: list[tuple]) -> list[dict]:
    """Take raw ground track data and convert to a dictionary."""
    if type(ground_track) is not list:
        raise TypeError("Ground track must be a list.")
    if not ground_track:
        raise ValueError("Ground track cannot be empty.")

    track_data = []

    for point in ground_track:
        if len(point) != 4:
            raise ValueError(
                "Each ground-track point must contain timestamp, latitude, longitude, and altitude."
            )

        timestamp, latitude, longitude, altitude = point
        latitude, longitude, altitude = float(latitude), float(longitude), float(altitude)
        x, y, z = geographic_to_xyz(latitude, longitude, altitude)
        timestamp_text = (
            timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            if hasattr(timestamp, "strftime")
            else str(timestamp)
        )

        track_data.append(
            {
                "time": timestamp_text,
                "latitude": round(latitude, 4),
                "longitude": round(longitude, 4),
                "altitude": round(altitude, 2),
                "x": round(x, 3),
                "y": round(y, 3),
                "z": round(z, 3),
            }
        )

    return track_data


def _load_satellite_model_base64() -> str:
    """Embed the 3D satellite into the HTML."""
    model_resource = files("orbitops").joinpath("assets").joinpath(SATELLITE_MODEL_FILENAME)

    try:
        model_bytes = model_resource.read_bytes()
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"GOES-R model not found. Expected 'orbitops/assets/{SATELLITE_MODEL_FILENAME}'."
        ) from exc

    if not model_bytes:
        raise ValueError("GOES-R model file is empty.")

    return base64.b64encode(model_bytes).decode("ascii")


def generate_3d_globe(
    ground_track: list[tuple],
    satellite_name: str,
    catalog_number: int,
) -> str:
    """Create the visualization."""
    if type(ground_track) is not list:
        raise TypeError("Ground track must be a list.")
    if not ground_track:
        raise ValueError("Ground track cannot be empty.")
    if type(satellite_name) is not str:
        raise TypeError("Satellite name must be a string.")
    if not satellite_name:
        raise ValueError("Satellite name cannot be empty.")
    if type(catalog_number) is not int:
        raise TypeError("Catalog number must be an int.")

    track_data = _ground_track_to_data(ground_track)
    track_json = json.dumps(track_data, separators=(",", ":"))
    coastline_json = json.dumps(_get_coastline_coordinates(), separators=(",", ":"))
    border_json = json.dumps(_get_border_coordinates(), separators=(",", ":"))
    land_json = json.dumps(_get_land_polygon_data(), separators=(",", ":"))
    grid_json = json.dumps(_get_grid_coordinates(), separators=(",", ":"))
    safe_satellite_name = json.dumps(satellite_name)
    model_base64_json = json.dumps(_load_satellite_model_base64())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{satellite_name} Visualization</title>
<style>
html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #02040a; font-family: Arial, Helvetica, sans-serif; }}
#container {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
#title {{ position: absolute; top: 18px; left: 50%; transform: translateX(-50%); z-index: 10; color: white; font-size: 20px; font-weight: 600; pointer-events: none; white-space: nowrap; }}
#info {{ position: absolute; top: 18px; left: 18px; z-index: 10; padding: 12px 14px; background: rgba(4, 7, 15, 0.82); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; color: white; font-size: 14px; line-height: 1.6; pointer-events: none; }}
#controls {{ position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); z-index: 10; display: flex; gap: 10px; padding: 10px; background: rgba(4, 7, 15, 0.82); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 8px; }}
button {{ border: none; border-radius: 5px; padding: 8px 16px; background: #202938; color: white; cursor: pointer; font-size: 14px; }}
button:hover {{ background: #303b4e; }}
#progress {{ width: 280px; }}
#loading {{ position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); color: white; font-size: 15px; z-index: 20; pointer-events: none; }}
</style>
</head>
<body>
<div id="container"></div>
<div id="title"></div>
<div id="loading">Loading satellite model...</div>
<div id="info">
    <div id="satellite-name"></div>
    <div id="satellite-time"></div>
    <div id="satellite-latitude"></div>
    <div id="satellite-longitude"></div>
    <div id="satellite-altitude"></div>
</div>
<div id="controls">
    <button id="play-button">▶ Play</button>
    <button id="pause-button">⏸ Pause</button>
    <input id="progress" type="range" min="0" max="{len(track_data) - 1}" value="0" step="1">
</div>
<script type="importmap">
{{
    "imports": {{
        "three": "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"
    }}
}}
</script>
<script type="module">
import * as THREE from "three";
import {{ OrbitControls }} from "three/addons/controls/OrbitControls.js";
import {{ GLTFLoader }} from "three/addons/loaders/GLTFLoader.js";

const EARTH_RADIUS = {EARTH_RADIUS_KM};
const satelliteName = {safe_satellite_name};
const catalogNumber = {catalog_number};
const trackData = {track_json};
const coastlineData = {coastline_json};
const borderData = {border_json};
const landData = {land_json};
const gridData = {grid_json};
const modelBase64 = {model_base64_json};

const container = document.getElementById("container");
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x02040a);

const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 10, 100000);
camera.position.set(10500, 10500, 6500);

const renderer = new THREE.WebGLRenderer({{ antialias: true, powerPreference: "high-performance" }});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.25;
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.rotateSpeed = 0.55;
controls.zoomSpeed = 0.35;
controls.enablePan = false;
controls.minDistance = EARTH_RADIUS * 1.12;
controls.maxDistance = EARTH_RADIUS * 6.0;
controls.target.set(0, 0, 0);
controls.update();

function unwrapRing(ring) {{
    if (!ring.length) return [];

    const result = [];
    let previousLongitude = ring[0][0];
    result.push([previousLongitude, ring[0][1]]);

    for (let index = 1; index < ring.length; index++) {{
        let longitude = ring[index][0];
        const latitude = ring[index][1];

        while (longitude - previousLongitude > 180) longitude -= 360;
        while (longitude - previousLongitude < -180) longitude += 360;

        result.push([longitude, latitude]);
        previousLongitude = longitude;
    }}

    return result;
}}

function addRingToPath(path, ring, offsetX, width, height) {{
    const unwrapped = unwrapRing(ring);
    if (!unwrapped.length) return;

    for (let index = 0; index < unwrapped.length; index++) {{
        const [longitude, latitude] = unwrapped[index];
        const x = ((longitude + 180) / 360) * width + offsetX;
        const y = ((90 - latitude) / 180) * height;
        index === 0 ? path.moveTo(x, y) : path.lineTo(x, y);
    }}

    path.closePath();
}}

function createEarthTexture() {{
    const width = 2048;
    const height = 1024;
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;

    const context = canvas.getContext("2d");
    context.fillStyle = "#0c4f84";
    context.fillRect(0, 0, width, height);
    context.fillStyle = "#24552b";

    for (const polygon of landData) {{
        for (const offset of [-width, 0, width]) {{
            const path = new Path2D();
            addRingToPath(path, polygon.exterior, offset, width, height);
            for (const hole of polygon.holes) addRingToPath(path, hole, offset, width, height);
            context.fill(path, "evenodd");
        }}
    }}

    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    texture.needsUpdate = true;
    return texture;
}}

const earthTexture = createEarthTexture();
const earthGeometry = new THREE.SphereGeometry(EARTH_RADIUS, 96, 48);
earthGeometry.rotateX(Math.PI / 2);

const earthMaterial = new THREE.MeshPhongMaterial({{
    map: earthTexture,
    shininess: 10,
    specular: new THREE.Color(0x172b38)
}});
const earth = new THREE.Mesh(earthGeometry, earthMaterial);
scene.add(earth);

const atmosphereGeometry = new THREE.SphereGeometry(EARTH_RADIUS + 45, 64, 32);
const atmosphereMaterial = new THREE.MeshBasicMaterial({{
    color: 0x3e93ff,
    transparent: true,
    opacity: 0.045,
    side: THREE.BackSide
}});
scene.add(new THREE.Mesh(atmosphereGeometry, atmosphereMaterial));

const ambientLight = new THREE.AmbientLight(0xffffff, 1.25);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1.7);
directionalLight.position.set(15000, 8000, 12000);
scene.add(directionalLight);

function createLine(points, color, opacity) {{
    const positions = new Float32Array(points.length * 3);

    for (let index = 0; index < points.length; index++) {{
        positions[index * 3] = points[index][0];
        positions[index * 3 + 1] = points[index][1];
        positions[index * 3 + 2] = points[index][2];
    }}

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const material = new THREE.LineBasicMaterial({{ color, transparent: opacity < 1, opacity }});
    return new THREE.Line(geometry, material);
}}

const coastlineGroup = new THREE.Group();
for (const coastline of coastlineData) coastlineGroup.add(createLine(coastline, 0xffffff, 0.88));
scene.add(coastlineGroup);

const borderGroup = new THREE.Group();
for (const border of borderData) borderGroup.add(createLine(border, 0xffffff, 0.78));
scene.add(borderGroup);

const gridGroup = new THREE.Group();
for (const gridLine of gridData) gridGroup.add(createLine(gridLine, 0xffffff, 0.055));
scene.add(gridGroup);

const orbitPoints = trackData.map(point => new THREE.Vector3(point.x, point.y, point.z));
const orbitGeometry = new THREE.BufferGeometry().setFromPoints(orbitPoints);
const orbitMaterial = new THREE.LineBasicMaterial({{ color: 0xff2020 }});
scene.add(new THREE.Line(orbitGeometry, orbitMaterial));

const satelliteLight = new THREE.PointLight(0xffffff, 8.0, 3000);
scene.add(satelliteLight);

let satellite = null;

function base64ToArrayBuffer(base64) {{
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let index = 0; index < binaryString.length; index++) bytes[index] = binaryString.charCodeAt(index);
    return bytes.buffer;
}}

function centerSatelliteModel(model) {{
    const box = new THREE.Box3().setFromObject(model);
    const center = new THREE.Vector3();
    box.getCenter(center);
    model.position.sub(center);
}}

function normalizeSatelliteScale(model) {{
    const box = new THREE.Box3().setFromObject(model);
    const size = new THREE.Vector3();
    box.getSize(size);

    const largestDimension = Math.max(size.x, size.y, size.z);
    if (!Number.isFinite(largestDimension) || largestDimension <= 0) return;

    const targetVisualSize = 300;
    model.scale.setScalar(targetVisualSize / largestDimension);
}}

function brightenSatelliteModel(model) {{
    model.traverse(child => {{
        if (!child.isMesh || !child.material) return;

        const materials = Array.isArray(child.material) ? child.material : [child.material];
        for (const material of materials) {{
            if (material.color) material.color.multiplyScalar(1.65);

            if (material.emissive && material.color) {{
                material.emissive.copy(material.color);
                material.emissiveIntensity = 0.20;
            }}

            if ("roughness" in material) material.roughness = Math.min(material.roughness, 0.65);
            material.needsUpdate = true;
        }}
    }});
}}

const gltfLoader = new GLTFLoader();
const modelArrayBuffer = base64ToArrayBuffer(modelBase64);

gltfLoader.parse(
    modelArrayBuffer,
    "",
    gltf => {{
        const loadedModel = gltf.scene;
        brightenSatelliteModel(loadedModel);
        centerSatelliteModel(loadedModel);
        normalizeSatelliteScale(loadedModel);

        satellite = new THREE.Group();
        satellite.add(loadedModel);
        scene.add(satellite);
        setSatellitePosition(currentIndex);
        document.getElementById("loading").style.display = "none";
    }},
    error => {{
        console.error("Failed to load satellite model:", error);
        document.getElementById("loading").textContent = "Failed to load satellite model.";
    }}
);

const titleElement = document.getElementById("title");
const nameElement = document.getElementById("satellite-name");
const timeElement = document.getElementById("satellite-time");
const latitudeElement = document.getElementById("satellite-latitude");
const longitudeElement = document.getElementById("satellite-longitude");
const altitudeElement = document.getElementById("satellite-altitude");
const progressElement = document.getElementById("progress");

titleElement.textContent = `${{satelliteName}} (${{catalogNumber}})`;
nameElement.textContent = `${{satelliteName}} (${{catalogNumber}})`;

let currentIndex = 0;
let playing = false;
let lastFrameTime = 0;
const FRAME_INTERVAL = 100;

function orientSatellite(index) {{
    if (satellite === null) return;

    let nextIndex = index + 1;
    if (nextIndex >= trackData.length) nextIndex = Math.max(0, index - 1);

    const current = trackData[index];
    const next = trackData[nextIndex];
    const direction = new THREE.Vector3(
        next.x - current.x,
        next.y - current.y,
        next.z - current.z
    );

    if (direction.lengthSq() === 0) return;

    direction.normalize();
    const forward = new THREE.Vector3(0, 0, 1);
    const quaternion = new THREE.Quaternion();
    quaternion.setFromUnitVectors(forward, direction);
    satellite.quaternion.copy(quaternion);
}}

function setSatellitePosition(index) {{
    currentIndex = Math.max(0, Math.min(index, trackData.length - 1));
    const point = trackData[currentIndex];

    if (satellite !== null) {{
        satellite.position.set(point.x, point.y, point.z);
        orientSatellite(currentIndex);
    }}

    satelliteLight.position.set(point.x, point.y, point.z);
    progressElement.value = currentIndex;
    timeElement.textContent = `Time: ${{point.time}}`;
    latitudeElement.textContent = `Latitude: ${{point.latitude.toFixed(4)}}°`;
    longitudeElement.textContent = `Longitude: ${{point.longitude.toFixed(4)}}°`;
    altitudeElement.textContent = `Altitude: ${{point.altitude.toFixed(2)}} km`;
}}

document.getElementById("play-button").addEventListener("click", () => playing = true);
document.getElementById("pause-button").addEventListener("click", () => playing = false);
progressElement.addEventListener("input", () => {{
    playing = false;
    setSatellitePosition(Number(progressElement.value));
}});

window.addEventListener("resize", () => {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}});

function animate(timestamp) {{
    requestAnimationFrame(animate);

    if (playing && timestamp - lastFrameTime >= FRAME_INTERVAL) {{
        currentIndex++;
        if (currentIndex >= trackData.length) currentIndex = 0;
        setSatellitePosition(currentIndex);
        lastFrameTime = timestamp;
    }}

    controls.update();
    renderer.render(scene, camera);
}}

setSatellitePosition(0);
requestAnimationFrame(animate);
</script>
</body>
</html>
"""


def save_and_open_globe(html: str, filename: str) -> Path | None:
    """Save anbd open the visualization HTML file."""
    if type(html) is not str:
        raise TypeError("HTML must be a string.")
    if not html:
        raise ValueError("HTML cannot be empty.")
    if type(filename) is not str:
        raise TypeError("Filename must be a string.")
    if not filename:
        raise ValueError("Filename cannot be empty.")

    if not filename.lower().endswith(".html"):
        filename += ".html"

    root = Tk()
    root.withdraw()

    save_path = filedialog.asksaveasfilename(
        title="Save OrbitOps Visualization",
        initialfile=filename,
        defaultextension=".html",
        filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
    )

    root.destroy()

    if not save_path:
        return None

    html_path = Path(save_path)
    html_path.write_text(html, encoding="utf-8")
    webbrowser.open(html_path.as_uri())

    return html_path
