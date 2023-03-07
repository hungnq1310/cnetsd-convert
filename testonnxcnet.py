from diffusers.utils import load_image
import cv2
from PIL import Image
import numpy as np
from diffusers import UniPCMultistepScheduler
from diffusers.pipelines.onnx_utils import OnnxRuntimeModel
from pipeline_onnx_stable_diffusion_controlnet import OnnxStableDiffusionControlNetPipeline
import onnxruntime as ort



image = load_image(
    "./input_image_vermeer.png"
)

image = np.array(image)

low_threshold = 100
high_threshold = 200

image = cv2.Canny(image, low_threshold, high_threshold)
image = image[:, :, None]
image = np.concatenate([image, image, image], axis=2)
canny_image = Image.fromarray(image)

opts = ort.SessionOptions()
opts.enable_cpu_mem_arena = False
opts.enable_mem_pattern = False

controlnet = OnnxRuntimeModel.from_pretrained("./model/cnet/canny_onnx", sess_options=opts, provider="DmlExecutionProvider")
pipe = OnnxStableDiffusionControlNetPipeline.from_pretrained(
    "./model/sd15_onnx", controlnet=controlnet,
    sess_options=opts, 
    provider="DmlExecutionProvider",
)


pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
prompt = "jpop singer on stage, best quality, extremely detailed"
seed=42
generator = np.random.RandomState(seed)

images = pipe(
    prompt,
    canny_image,
    negative_prompt="monochrome, lowres, bad anatomy, worst quality, low quality",
    num_inference_steps=20,
    generator=generator,
).images[0]
images.save("test.png")
