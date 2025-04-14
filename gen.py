import requests

url = 'http://localhost:8000/'
files = {'image': open('styles/items2generate/selected_image.jpg', 'rb')}

response = requests.post(url, files=files)

# Проверяем, что ответ содержит файл
if response.status_code == 200:
    with open('received_file.jpg', 'wb') as f:
        f.write(response.content)
    print("File received and saved as received_file.txt")
else:
    print("Error:", response.json())