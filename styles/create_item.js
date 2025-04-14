document.addEventListener('DOMContentLoaded', function() {
    // Получаем модальное окно для редактирования изображений
    var imageEditModal = document.getElementById("imageEditModal");

    // Получаем кнопку, которая открывает модальное окно для редактирования изображений
    var editImagesBtn = document.getElementById("edit-images");

    // Получаем элемент <span>, который закрывает модальное окно для редактирования изображений
    var imageEditModalClose = document.getElementsByClassName("close")[0];

    // Когда пользователь нажимает на кнопку, открываем модальное окно для редактирования изображений
    editImagesBtn.onclick = function() {
        imageEditModal.style.display = "block";
    }

    // Когда пользователь нажимает на <span> (x), закрываем модальное окно для редактирования изображений
    imageEditModalClose.onclick = function() {
        imageEditModal.style.display = "none";
    }

    // Когда пользователь нажимает вне модального окна для редактирования изображений, закрываем его
    window.onclick = function(event) {
        if (event.target == imageEditModal) {
            imageEditModal.style.display = "none";
        }
    }

    // Инициализируем Sortable для галереи изображений
    var imageGallery = document.getElementById('image-gallery');
    new Sortable(imageGallery, {
        animation: 150
    });

    // Обрабатываем загрузку файлов
    document.getElementById('upload-images').addEventListener('change', function(event) {
        var files = event.target.files;
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            var reader = new FileReader();
            reader.onload = function(e) {
                var img = document.createElement('img');
                img.src = e.target.result;
                var imageItem = document.createElement('div');
                imageItem.className = 'image-item';
                imageItem.appendChild(img);
                imageGallery.appendChild(imageItem);
            }
            reader.readAsDataURL(file);
        }
    });

    document.getElementById('change-item-button').addEventListener('click', function() {
        var form = document.getElementById('item-form');
        if (form) {
            var formData = new FormData(form);

            // Получаем товарный ID из элемента <div>
            var defaultValuesDiv = document.getElementById("default-values");
            var itemId = defaultValuesDiv.getAttribute("data-id");
            formData.append('item_id', itemId); // Добавляем товарный ID в FormData

            // Получаем все изображения из галереи
            var imageItems = document.querySelectorAll('#image-gallery .image-item img');
            var promises = [];

            imageItems.forEach(function(img, index) {
                // Проверяем, является ли изображение base64 или URL
                if (img.src.startsWith('data\:image')) {
                    // Если это base64, преобразуем его в Blob
                    promises.push(fetch(img.src)
                        .then(res => res.blob())
                        .then(blob => {
                            formData.append('images', blob, 'image' + index + '.jpg');
                        }));
                } else {
                    // Если это URL, загружаем его как Blob
                    promises.push(fetch(img.src)
                        .then(res => res.blob())
                        .then(blob => {
                            formData.append('images', blob, 'image' + index + '.jpg');
                        }));
                }
            });

            // Отправляем данные на сервер после завершения всех промисов
            Promise.all(promises).then(() => {
                fetch('/change_item', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        return response.text().then(text => { throw new Error(text) });
                    }
                })
                .then(data => {
                    console.log('Success:', data);
                    // Перенаправляем на страницу /items
                    window.location.href = '/items';
                })
                .catch((error) => {
                    console.error('Error:', error);
                    // Здесь можно добавить обработку ошибки
                });
            });
        } else {
            console.error('Form not found');
        }
    });

    // Получаем модальное окно для генерации модели
    var modelGenerateModal = document.getElementById("modelGenerateModal");

    // Получаем кнопку, которая открывает модальное окно для генерации модели
    var generateModelBtn = document.getElementById("generate-item-model");

    // Получаем элемент <span>, который закрывает модальное окно для генерации модели
    var modelGenerateModalClose = document.getElementsByClassName("close")[1];

    // Получаем модальное окно для создания модели
    var createModelModal = document.getElementById("createModelModal");

    // Получаем элемент <span>, который закрывает модальное окно для создания модели
    var createModelModalClose = document.getElementsByClassName("close")[2];

    // Когда пользователь нажимает на кнопку, открываем модальное окно для генерации модели и отправляем запрос
    generateModelBtn.onclick = function() {
        modelGenerateModal.style.display = "block";
        sendRequest(); // Отправляем запрос при нажатии на кнопку
    }

    // Когда пользователь нажимает на <span> (x), закрываем модальное окно для генерации модели
    modelGenerateModalClose.onclick = function() {
        modelGenerateModal.style.display = "none";
    }

    // Когда пользователь нажимает на <span> (x), закрываем модальное окно для создания модели
    createModelModalClose.onclick = function() {
        createModelModal.style.display = "none";
    }

    // Когда пользователь нажимает вне модального окна для генерации модели, закрываем его
    window.onclick = function(event) {
        if (event.target == modelGenerateModal) {
            modelGenerateModal.style.display = "none";
        }
        if (event.target == createModelModal) {
            createModelModal.style.display = "none";
        }
    }

    function handleResponse(response) {
        const canvas = document.getElementById('modelCanvas');

        if (response === null) {
            canvas.classList.add('hidden');
        } else {
            canvas.classList.remove('hidden');
        }
    }

    function sendRequest() {
        // Получаем значение id из элемента <div>
        var defaultValuesDiv = document.getElementById("default-values");
        var id = defaultValuesDiv.getAttribute("data-id");

        fetch('/check_model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: id }) // Отправляем id в теле запроса
        })
        .then(response => response.json())
        .then(data => {
            if (data.model === null) {
                // Если модель равна null, отображаем сообщение в модальном окне
                var modelGenerateModalContent = document.getElementById("mGM");
                modelGenerateModalContent.innerHTML = "У вас пока нет модели товара";

                // Обновляем текст кнопки
                var generateModelBtn = document.getElementById("mGM");
                generateModelBtn.innerHTML = "Создать модель";

                // Добавляем обработчик события для кнопки "Создать модель"
                generateModelBtn.onclick = function() {
                    modelGenerateModal.style.display = "none"; // Закрываем текущее модальное окно
                    createModelModal.style.display = "block"; // Открываем новое модальное окно
                }

                handleResponse(data.model);
            } else {
                // Если модель не равна null, отображаем её с помощью Three.js
                initThreeJS(data.model);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function initThreeJS(modelUrl) {
        var scene = new THREE.Scene();
        scene.background = new THREE.Color(0xcccccc); // Устанавливаем цвет фона

        var camera = new THREE.PerspectiveCamera(75, 400 / 300, 0.1, 1000); // Обновляем соотношение сторон
        var renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('modelCanvas'), antialias: true });
        renderer.setSize(400, 300); // Устанавливаем размеры рендерера
        renderer.setPixelRatio(window.devicePixelRatio); // Устанавливаем соотношение пикселей

        var light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(0, 1, 1).normalize();
        scene.add(light);

        // Динамическая загрузка OBJLoader
        var script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/OBJLoader.js';
        script.onload = function() {
            var loader = new THREE.OBJLoader();
            loader.load(modelUrl, function(object) {
                scene.add(object);

                // Приближаем камеру к модели
                var boundingBox = new THREE.Box3().setFromObject(object);
                var center = boundingBox.getCenter(new THREE.Vector3());
                var size = boundingBox.getSize(new THREE.Vector3());
                var maxDim = Math.max(size.x, size.y, size.z);
                var fov = camera.fov * (Math.PI / 180);
                var cameraZ = Math.abs(maxDim / Math.tan(fov / 2));
                camera.position.set(center.x, center.y, center.z + cameraZ);
                camera.lookAt(center);

                animate();
            }, undefined, function(error) {
                console.error('An error happened', error);
            });
        };
        document.head.appendChild(script);

        function animate() {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }
    }

    // Обработка выбора изображения
    var imageItems = document.querySelectorAll('.image-item');
    imageItems.forEach(function(item) {
        item.addEventListener('click', function() {
            // Проверяем, есть ли класс 'selected' у текущего элемента
            if (item.classList.contains('selected')) {
                // Если есть, удаляем его
                item.classList.remove('selected');
            } else {
                // Если нет, добавляем его
                item.classList.add('selected');
            }
        });
    });

    // Обработка нажатия кнопки "Создать модель"
    document.getElementById('createModelButton').addEventListener('click', function() {
        var selectedImage = document.querySelector('.image-item.selected img');
        if (selectedImage) {
            var formData = new FormData();
            var imageSrc = selectedImage.src;

            // Получаем товарный ID из элемента <div>
            var defaultValuesDiv = document.getElementById("default-values");
            var itemId = defaultValuesDiv.getAttribute("data-id");
            formData.append('item_id', itemId); // Добавляем товарный ID в FormData

            // Показать анимацию ожидания и скрыть кнопку
            document.getElementById('createModelButton').style.display = 'none';
            document.getElementById('loadingSpinner').classList.remove('hidden');

            // Проверяем, является ли изображение base64 или URL
            if (imageSrc.startsWith('data\:image')) {
                // Если это base64, преобразуем его в Blob
                fetch(imageSrc)
                    .then(res => res.blob())
                    .then(blob => {
                        formData.append('image', blob, 'selected_image.jpg');
                        sendCreateModelRequest(formData);
                    });
            } else {
                // Если это URL, загружаем его как Blob
                fetch(imageSrc)
                    .then(res => res.blob())
                    .then(blob => {
                        formData.append('image', blob, 'selected_image.jpg');
                        sendCreateModelRequest(formData);
                    });
            }
        } else {
            alert('Пожалуйста, выберите изображение.');
        }
    });

    function sendCreateModelRequest(formData) {
        fetch('/create_model', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.text().then(text => { throw new Error(text) });
            }
        })
        .then(data => {
            console.log('Success:', data);
            // Скрыть анимацию ожидания и показать кнопку
            document.getElementById('loadingSpinner').classList.add('hidden');
            document.getElementById('createModelButton').style.display = 'block';
            // Перенаправляем на страницу /items
            window.location.href = '/items';
        })
        .catch((error) => {
            console.error('Error:', error);
            // Скрыть анимацию ожидания и показать кнопку
            document.getElementById('loadingSpinner').classList.add('hidden');
            document.getElementById('createModelButton').style.display = 'block';
            // Здесь можно добавить обработку ошибки
        });
    }

    // Обработка нажатия кнопки "Удалить товар"
    document.getElementById('delete-item-button').addEventListener('click', function() {
        // Получаем товарный ID из элемента <div>
        var defaultValuesDiv = document.getElementById("default-values");
        var itemId = defaultValuesDiv.getAttribute("data-id");

        fetch('/delete_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ item_id: itemId }) // Отправляем item_id в теле запроса
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.text().then(text => { throw new Error(text) });
            }
        })
        .then(data => {
            console.log('Success:', data);
            // Перенаправляем на страницу /items
            window.location.href = '/items';
        })
        .catch((error) => {
            console.error('Error:', error);
            // Здесь можно добавить обработку ошибки
        });
    });
});