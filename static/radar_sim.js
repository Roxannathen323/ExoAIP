document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('radar-container');
    const threeContainer = document.getElementById('radar-3d-container');
    const heightmap = JSON.parse(container.dataset.heightmap);
    const blackoutSec = parseFloat(container.dataset.blackoutSec) || 120;
    const stallSpeed = parseFloat(container.dataset.stallSpeed) || 120;
    const bioHazard = container.dataset.bioHazard || "";
    const isHighRisk = bioHazard.includes("LEVEL 4") || bioHazard.includes("LEVEL 5");
    
    const spaceWeatherBox = document.getElementById('space-weather-box');
    const isDegraded = spaceWeatherBox && spaceWeatherBox.dataset.status === 'DEGRADED';

    // --- Three.js Setup ---
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, threeContainer.clientWidth / threeContainer.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(threeContainer.clientWidth, threeContainer.clientHeight);
    threeContainer.appendChild(renderer.domElement);

    // Terrain Geometry
    const size = heightmap.length;
    const geometry = new THREE.PlaneBufferGeometry(100, 100, size - 1, size - 1);
    const vertices = geometry.attributes.position.array;
    
    for (let i = 0; i < size; i++) {
        for (let j = 0; j < size; j++) {
            const index = (i * size + j) * 3 + 2;
            vertices[index] = heightmap[i][j];
        }
    }
    geometry.computeVertexNormals();

    const material = new THREE.MeshBasicMaterial({ 
        color: 0x00f2ff, 
        wireframe: true, 
        transparent: true, 
        opacity: 0.3 
    });
    const terrain = new THREE.Mesh(geometry, material);
    terrain.rotation.x = -Math.PI / 2;
    scene.add(terrain);

    camera.position.set(0, 60, 100);
    camera.lookAt(0, 0, 0);

    // --- Radar Targets ---
    const targets = [];
    const numTargets = 3 + Math.floor(Math.random() * 3);
    const targetMaterial = new THREE.PointsMaterial({ color: 0x00f2ff, size: 2 });
    
    for (let i = 0; i < numTargets; i++) {
        const sprite = new THREE.Group();
        const dot = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshBasicMaterial({ color: 0x00f2ff }));
        sprite.add(dot);
        
        const t = {
            mesh: sprite,
            x: (Math.random() - 0.5) * 80,
            z: (Math.random() - 0.5) * 80,
            y: 20 + Math.random() * 30,
            vx: (Math.random() - 0.5) * 0.1,
            vz: (Math.random() - 0.5) * 0.1,
            status: "ACT",
            callsign: ["EXO-1", "PROBE-7", "SCOUT-4"][i % 3],
            blackoutStart: 5000 + Math.random() * 5000,
            isBlackedOut: false
        };
        scene.add(sprite);
        targets.push(t);
    }

    // --- Animation Loop ---
    let frame = 0;
    function animate() {
        requestAnimationFrame(animate);
        frame++;

        // Rotate terrain slowly
        terrain.rotation.z += 0.001;

        targets.forEach(t => {
            if (!t.isBlackedOut) {
                t.x += t.vx;
                t.z += t.vz;
                if (Math.abs(t.x) > 50) t.vx *= -1;
                if (Math.abs(t.z) > 50) t.vz *= -1;
            }

            // Blackout Simulation
            if (frame > t.blackoutStart / 16 && frame < (t.blackoutStart + blackoutSec * 1000) / 16) {
                if (!t.isBlackedOut) {
                    t.isBlackedOut = true;
                    t.mesh.children[0].material.color.setHex(0xff5555);
                    document.getElementById('radar-status').textContent = "SIGNAL BLACKout / IONIZATION";
                    document.getElementById('radar-status').style.color = "#ff5555";
                }
                // Random drift and noise
                t.mesh.position.set(t.x + (Math.random()-0.5), t.y, t.z + (Math.random()-0.5));
            } else {
                if (t.isBlackedOut) {
                    t.isBlackedOut = false;
                    t.mesh.children[0].material.color.setHex(0x00f2ff);
                    document.getElementById('radar-status').textContent = "SCANNING... [LINK_RESTORED]";
                    document.getElementById('radar-status').style.color = "#00ff00";
                }
                t.mesh.position.set(t.x, t.y, t.z);
            }
        });

        // Global Interference (Space Weather)
        if (isDegraded && Math.random() > 0.98) {
            renderer.domElement.style.opacity = "0.5";
            setTimeout(() => renderer.domElement.style.opacity = "1", 50);
        }

        renderer.render(scene, camera);
    }
    animate();

    // --- Transcript & FPL Ajax (kept from previous version) ---
    const transcriptBody = document.getElementById('transcript-body');
    const rawTranscript = document.querySelectorAll('#raw-transcript p');
    let lineIndex = 0;

    function typeLine(text, container, callback) {
        const line = document.createElement('div');
        line.className = 'transcript-line';
        container.appendChild(line);
        container.scrollTop = container.scrollHeight;
        let charIndex = 0;
        const interval = setInterval(() => {
            if (charIndex < text.length) {
                line.textContent += text[charIndex];
                charIndex++;
                container.scrollTop = container.scrollHeight;
            } else {
                clearInterval(interval);
                if (callback) callback();
            }
        }, 30);
    }

    function processNextTranscriptLine() {
        if (lineIndex < rawTranscript.length) {
            typeLine(rawTranscript[lineIndex].textContent, transcriptBody, () => {
                lineIndex++;
                setTimeout(processNextTranscriptLine, 1500);
            });
        }
    }
    setTimeout(processNextTranscriptLine, 2000);

    const fplForm = document.getElementById('fpl-form');
    if (fplForm) {
        fplForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const mass = document.getElementById('fpl-mass').value;
            const dv = document.getElementById('fpl-dv').value;
            const relay = document.getElementById('fpl-relay').checked;
            const planetName = document.querySelector('h1').textContent;
            
            const fplResponse = document.getElementById('fpl-response');
            fplResponse.style.display = 'block';
            fplResponse.className = 'fpl-response-box';
            document.getElementById('fpl-status-label').textContent = 'STATUS: UPLOADING...';

            fetch('/api/fpl/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mass, dv, planet: planetName, relay: relay })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('fpl-status-label').textContent = `STATUS: ${data.status}`;
                document.getElementById('fpl-reason').textContent = data.reason;
                fplResponse.className = `fpl-response-box ${data.status.toLowerCase()}`;
            });
        });
    }

    // Sterile Checks logic
    const sterileChecks = document.querySelectorAll('.sterile-check');
    const sterileStatus = document.getElementById('sterile-status');
    sterileChecks.forEach(c => {
        c.addEventListener('change', () => {
            const allChecked = Array.from(sterileChecks).every(sc => sc.checked);
            if (allChecked) {
                sterileStatus.textContent = "READY FOR DEPARTURE: STERILIZATION COMPLETE";
                sterileStatus.style.color = "#00ff00";
            } else {
                sterileStatus.textContent = "DEPARTURE BLOCKED: STERILIZATION INCOMPLETE";
                sterileStatus.style.color = "#ff5555";
            }
        });
    });

    window.addEventListener('resize', () => {
        camera.aspect = threeContainer.clientWidth / threeContainer.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(threeContainer.clientWidth, threeContainer.clientHeight);
    });
});
