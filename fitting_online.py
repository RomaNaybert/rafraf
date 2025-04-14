from gradio_client import Client, handle_file
from PIL import Image

import random

def fitting(person, item):
    client = Client("levihsu/OOTDiffusion")
    result = client.predict(
            vton_img=handle_file(person),
            garm_img=handle_file(item),
            n_samples=1,
            n_steps=20,
            image_scale=2,
            seed=-1,
            api_name="/process_hd"
    )

    image_path = result[0]['image']
    image = Image.open(image_path)

    strr = 'qwertyuiopasdfghjklzxcvbnm1234567890'
    filename = ''.join([strr[random.randint(0, len(strr) - 1)] for _ in range(20)])

    image.save(f'styles/online_fitting/{filename}.png', 'PNG')

    return f'/styles/online_fitting/{filename}.png'