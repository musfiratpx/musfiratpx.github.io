// import the THREE.js library
import * as THREE from "https://cdn.skypack.dev/three@0.129.0/build/three.module.js";
// allow for the camera to move around the scene
import { OrbitControls } from "https://cdn.skypack.dev/three@0.129.0/examples/jsm/controls/OrbitControls.js";
// allow for importing the .gltf file
import { GLTFLoader } from "https://cdn.skypack.dev/three@0.129.0/examples/jsm/loaders/GLTFLoader.js";

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);

// canvas (planet container) setup
const renderer = new THREE.WebGLRenderer({ 
    canvas: document.querySelector('.planet-container'), 
    antialias: true,
    alpha: true //transparent background

});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setClearColor(0x000000, 0);

// lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
directionalLight.position.set(5, 10, 7);
scene.add(directionalLight);

// hold for animation & raycasting
const activePlanets = [];
const visualPlanets = []; 



// planet names 
const cleanPlanetNames = {
    "Mercury": "Mercury",
    "Venus": "Venus",
    "Earth": "Earth",
    "Mars": "Mars",
    "Jupiter": "Jupiter",
    "Saturn": "Saturn",
    "Uranus": "Uranus",
    "Neptune": "Neptune"
};

// this is the order the planets are in
const astronomicalOrder = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"];

const loader = new GLTFLoader();

loader.load('assets/Planets.glb', function(gltf) {
    const masterScene = gltf.scene;
    const foundPlanets = {};

    masterScene.traverse((child) => {
        if (child.isMesh && cleanPlanetNames[child.name]) {
            foundPlanets[child.name] = child;
        }
        if (child.isMesh) {
            console.log('Found mesh:', child.name); // see EVERY mesh name in the file
        }
    });

    const spacing = 4.2; 
    const startX = -((astronomicalOrder.length - 1) * spacing) / 2; // centers the planets perfectly

   astronomicalOrder.forEach((planetName, index) => {
    const planetMesh = foundPlanets[planetName];
    
    if (planetMesh) {
        planetMesh.position.set(0, 0, 0);
        planetMesh.position.x = startX + (index * spacing);
        planetMesh.userData = { isPlanet: true, displayName: cleanPlanetNames[planetName] };
        planetMesh.scale.set(2, 2, 2);

        scene.add(planetMesh);
        visualPlanets.push(planetMesh);

        //  hitbox sphere, same fixed size for every planet
        const hitSphere = new THREE.Mesh(
            new THREE.SphereGeometry(1.2*2, 8, 8), 
            new THREE.MeshBasicMaterial({ visible: false })
        );
        
        hitSphere.position.copy(planetMesh.position);
        hitSphere.userData = planetMesh.userData;
        scene.add(hitSphere);

        activePlanets.push(hitSphere); // raycast against the hitbox, not the mesh
    }
});

}, undefined, function(error) {
    console.error('Error opening Planets.glb:', error);
});

// position  camera to see all 8 items comfortably
camera.position.z = 20;

// raycasting = click detection
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

window.addEventListener('click', (event) => {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

   raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(activePlanets, true);
    console.log('activePlanets:', activePlanets.length, 'intersects:', intersects.length); 
  

    // loop through the hits until we find an actual solid planet body
    for (let i = 0; i < intersects.length; i++) {
    let hitObject = intersects[i].object;
    console.log('Hit:', hitObject.name); // NEW

    if (hitObject.name.toLowerCase().includes('ring') || hitObject.name.toLowerCase().includes('atmosphere')) {
        continue;
    }

    while (hitObject && !hitObject.userData.isPlanet) {
        hitObject = hitObject.parent;
    }

    console.log('Climbed to:', hitObject ? hitObject.name : 'null', hitObject ? hitObject.userData : 'n/a'); 

    if (hitObject && hitObject.userData.displayName) {
        alert('You clicked on ' + hitObject.userData.displayName + '!');
        break;
    } else {
        const rawName = intersects[i].object.name;
        if (rawName) {
            alert('You clicked on ' + rawName + '!');
            break;
        }
    }
}
});
const canvas = document.querySelector('.planet-container');

window.addEventListener('mousemove', (event) => {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(activePlanets, true);
    if (intersects.length > 0) {
         canvas.style.cursor = "url('assets/kirby.cur'), auto";
    } 
    else {
     canvas.style.cursor = 'default';
    }
     

   
});



// anim Loop
function animate() {
    requestAnimationFrame(animate);

    // Spin each loaded planet individually on its Y-axis
    visualPlanets.forEach((planet) => {
    planet.rotation.y += 0.01;
    });

    renderer.render(scene, camera);
}

// start the loop
animate();

// window resizing
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});




//puddles
function getScreenPosition(object3D) {
    const vector = object3D.position.clone();
    vector.project(camera);

    const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
    const y = (-vector.y * 0.5 + 0.5) * window.innerHeight;

    return { x, y };
}

function overlapsWithPlanets(x, y, size) {
    const planetPixelRadius = 100; 

    for (let planet of visualPlanets) {
        const screenPos = getScreenPosition(planet);

        const buffer = 45;
        const pLeft = screenPos.x - planetPixelRadius - buffer;
        const pRight = screenPos.x + planetPixelRadius + buffer;
        const pTop = screenPos.y - planetPixelRadius - buffer;
        const pBottom = screenPos.y + planetPixelRadius + buffer;

        if (x < pRight && x + size > pLeft && y < pBottom && y + size > pTop) {
            return true;
        }
    }
    return false;
}
function createPuddle() {
    const container = document.getElementById('puddle-container');
    if (!container) return;

    const puddle = document.createElement('div');
    puddle.classList.add('space-puddle');

    // set the size of the puddle
    const size = Math.floor(Math.random() * 50) + 50; // 50px to 100px
    puddle.style.width = `${size}px`;
    puddle.style.height = `${size}px`;

    // loop until we find coordinates that do not hit a planet
    let randomX = 0;
    let randomY = 0;
    let attempts = 0;
    let keepTrying = true;

    while (keepTrying && attempts < 100) {
        randomX = Math.floor(Math.random() * (window.innerWidth - size));
        randomY = Math.floor(Math.random() * (window.innerHeight - size));
        
        // no overlap= break the loop
        if (!overlapsWithPlanets(randomX, randomY, size)) {
            keepTrying = false;
        }
        attempts++;
    }

    puddle.style.left = `${randomX}px`;
    puddle.style.top = `${randomY}px`;

    // make puddle shape
    const r1 = Math.floor(Math.random() * 20) + 40; 
    const r2 = 100 - r1;
    const r3 = Math.floor(Math.random() * 20) + 40;
    const r4 = 100 - r3;
    puddle.style.borderRadius = `${r1}% ${r2}% ${r3}% ${r4}% / ${r3}% ${r1}% ${r2}% ${r4}%`;

    // random color
    const randomHue = Math.floor(Math.random() * 360);
    puddle.style.filter = `hue-rotate(${randomHue}deg)`;

    // interactiveness
    puddle.addEventListener('click', () => {
        alert("This is a space puddle"); 
        puddle.remove();
    });

    container.appendChild(puddle);

    // delete after 10s if left unclicked
    setTimeout(() => {
        if (puddle.parentNode) puddle.remove();
    }, 10000);
}

createPuddle();
setInterval(createPuddle, 10000);