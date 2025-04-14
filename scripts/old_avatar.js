document.getElementById('delete-avatar').addEventListener('click', function() {
    fetch('/del_avatar')
        .then(response => response.json())
        .then(data => {
            window.location.href = '/avatar'
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
});

document.getElementById('regenerate-avatar').addEventListener('click', function() {
    window.location.href = '/generate_avatar';
});

document.getElementById('modelForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const height = parseFloat(document.getElementById('height').value);
    const weight = parseFloat(document.getElementById('weight').value);
    const armSpan = parseFloat(document.getElementById('arm-span').value);
    const legLength = parseFloat(document.getElementById('leg-length').value);

    fetch('/generate_model', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            height: height,
            weight: weight,
            arm_span: armSpan,
            leg_length: legLength
        })
    })
    .then(response => response.json())
    .then(data => {
        loadModel(data.model_path);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById('saveButton').addEventListener('click', function(event) {
    event.preventDefault();  // Предотвращаем стандартное поведение ссылки
    fetch('/save_model')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/avatar';  // Перенаправляем на главную страницу после выхода
            } else {
                alert('Ошибка при выходе из системы.');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Ошибка при выходе из системы.');
        });
});

let scene, camera, renderer, model;

function init() {
    // Создание сцены
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x444444);

    // Создание камеры
    const aspect = document.getElementById('modelCanvas').clientWidth / document.getElementById('modelCanvas').clientHeight;
    camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
    camera.position.z = 5;

    // Создание рендерера
    renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('modelCanvas'), antialias: true });
    renderer.setSize(document.getElementById('modelCanvas').clientWidth, document.getElementById('modelCanvas').clientHeight);

    // Добавление освещения
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(5, 10, 7.5);
    scene.add(light);

    // Обработка событий мыши для вращения и масштабирования модели
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let zoom = 1;

    document.getElementById('modelCanvas').addEventListener('mousedown', (event) => {
        isDragging = true;
        previousMousePosition = { x: event.clientX, y: event.clientY };
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
    });

    document.addEventListener('mousemove', (event) => {
        if (isDragging) {
            const deltaMove = { x: event.clientX - previousMousePosition.x, y: event.clientY - previousMousePosition.y };
            const deltaRotationQuaternion = new THREE.Quaternion().setFromEuler(
                new THREE.Euler(toRadians(deltaMove.y * 1), toRadians(deltaMove.x * 1), 0, 'XYZ')
            );
            model.quaternion.multiplyQuaternions(deltaRotationQuaternion, model.quaternion);
            previousMousePosition = { x: event.clientX, y: event.clientY };
        }
    });

    document.getElementById('modelCanvas').addEventListener('wheel', (event) => {
        zoom += event.deltaY * -0.01;
        zoom = Math.max(0.125, Math.min(1.5, zoom));
        camera.position.z = zoom * 5;
    });

    // Функция для преобразования градусов в радианы
    function toRadians(degrees) {
        return degrees * (Math.PI / 180);
    }

    // Рендеринг сцены
    function animate() {
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
    }

    animate();
}

function loadModel(modelPath) {
    const loader = new THREE.OBJLoader();
    loader.load(modelPath, function(obj) {
        if (model) {
            scene.remove(model);
        }
        model = obj;
        model.position.set(0, 0, 0);
        scene.add(model);

        // Показать кнопку сохранения
        document.getElementById('saveButton').style.display = 'block';
    });
}

fetch('/get_model_name')
    .then(response => response.json())
    .then(data => {
        const modelPath = data.model_path;
        loadModel(modelPath);
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });

init();