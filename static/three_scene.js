/**
 * PhishGuard AI - Premium 3D Background
 * ========================================
 * Uses Three.js to render an interactive cyber-network particle system.
 */

document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("bgCanvas");
    if (!canvas || typeof THREE === "undefined") return;

    // Scene Setup
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x06080d, 0.0015);

    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 2000);
    camera.position.z = 800;

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Particles Configuration
    const particleCount = 600;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const colorA = new THREE.Color(0x38bdf8); // Cyan
    const colorB = new THREE.Color(0xa78bfa); // Purple

    for (let i = 0; i < particleCount; i++) {
        // Random spherical distribution
        const r = 800 * Math.cbrt(Math.random());
        const theta = Math.random() * 2 * Math.PI;
        const phi = Math.acos(2 * Math.random() - 1);

        positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
        positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
        positions[i * 3 + 2] = r * Math.cos(phi);

        const mixColor = colorA.clone().lerp(colorB, Math.random());
        colors[i * 3] = mixColor.r;
        colors[i * 3 + 1] = mixColor.g;
        colors[i * 3 + 2] = mixColor.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Material with additive blending for glow
    const material = new THREE.PointsMaterial({
        size: 3,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        sizeAttenuation: true,
        blending: THREE.AdditiveBlending,
        depthWrite: false
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);

    // Connecting Lines
    const lineMaterial = new THREE.LineBasicMaterial({
        color: 0x38bdf8,
        transparent: true,
        opacity: 0.08,
        blending: THREE.AdditiveBlending,
        depthWrite: false
    });

    // To keep it performant, we don't draw lines between all points,
    // we'll just add a subtle rotating wireframe globe in the center
    const globeGeometry = new THREE.IcosahedronGeometry(300, 2);
    const globeWireframe = new THREE.WireframeGeometry(globeGeometry);
    const globeLines = new THREE.LineSegments(globeWireframe, lineMaterial);
    scene.add(globeLines);

    // Mouse Interaction
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;

    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX - windowHalfX) * 0.5;
        mouseY = (event.clientY - windowHalfY) * 0.5;
    });

    // Animation Loop
    const clock = new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);
        const delta = clock.getDelta();
        const time = clock.getElapsedTime();

        // Smooth mouse follow
        targetX = mouseX * 0.05;
        targetY = mouseY * 0.05;
        
        camera.position.x += (mouseX - camera.position.x) * 0.02;
        camera.position.y += (-mouseY - camera.position.y) * 0.02;
        camera.lookAt(scene.position);

        // Rotate scene
        particles.rotation.y += 0.05 * delta;
        particles.rotation.x += 0.02 * delta;

        globeLines.rotation.y -= 0.1 * delta;
        globeLines.rotation.x += 0.05 * delta;

        // Subtle pulsing of globe
        const scale = 1 + Math.sin(time * 2) * 0.02;
        globeLines.scale.set(scale, scale, scale);

        renderer.render(scene, camera);
    }

    animate();

    // Resize Handler
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
});
