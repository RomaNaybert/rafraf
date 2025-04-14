import torch
import trimesh
import mediapy as media

from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config
from shap_e.util.notebooks import create_pan_cameras, decode_latent_images, gif_widget
from shap_e.util.notebooks import decode_latent_mesh


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

xm = load_model('transmitter', device=device)
model = load_model('text300M', device=device)
diffusion = diffusion_from_config(load_config('diffusion'))

def sample_wrapper(
    text = "a shark",
    image = None,
    guidance_scale = None,
    batch_size = 4,
  ):
  
  if image is None:
    model_kwargs=dict(texts=[text] * batch_size)
    if guidance_scale is None:
      guidance_scale = 15.0
  else:
    model_kwargs=dict(images=[image] * batch_size)
    if guidance_scale is None:
      guidance_scale = 3.0

  latents = sample_latents(
      batch_size=batch_size,
      model=model,
      diffusion=diffusion,
      guidance_scale=guidance_scale,
      model_kwargs=model_kwargs,
      progress=True,
      clip_denoised=True,
      use_fp16=True,
      use_karras=True,
      karras_steps=64,
      sigma_min=1e-3,
      sigma_max=160,
      s_churn=0,
  )

  return latents

def item_generate(image_path):
    image = media.read_image(image_path)

    media.show_image(image)

    latents = sample_wrapper(
        image = image,
        guidance_scale = 3.0,
    )

    for i, latent in enumerate(latents):
        with open(f'example_mesh_{i}.ply', 'wb') as f:
            decode_latent_mesh(xm, latent).tri_mesh().write_ply(f)

    mesh = trimesh.load('example_mesh_3.ply')

    mesh.export('item_model.obj')

    return 'item_model.obj'