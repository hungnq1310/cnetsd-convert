# onnx_stable_diffusion_controlnet
WIP: Get Stable DIffusion Controlnet running with DirectML via ONNX
<br>The original conversion script is from here: https://github.com/Amblyopius/Stable-Diffusion-ONNX-FP16
<br>For now, the conversion scripts only support diffusers format.
# How to use it:
First you have to convert the controlnet model to ONNX. I tested with Canny and Openpose. The example script testonnxcnet.py uses Canny.
<br>https://huggingface.co/lllyasviel/sd-controlnet-canny
<br>Do this:
```
convert_controlnet_to_onnx.py --model_path="lllyasviel/sd-controlnet-canny" --output_path="./model/canny_onnx" --fp16
```

1. Optimization

[!WARNING]
OPTIONAL ATTENTION SLICING BELOW FUNCTION NOT STABLE WHEN DEPLOYING:

Optionally enable attention slicing by adding this argument(you can use auto or max):
```
--attention-slicing max
```

[!NOTE]
Below option argument can used for more optimize, corresponding to [huggingface](https://huggingface.co/docs/diffusers/optimization/memory#reduce-memory-usage): 
```
--vae-slicing
--xformers
```

2. Stable Diffusion Convert

You now have the controlnet model converted. Next you need to convert a Stable Diffusion model to use it. Note that you can't use a model you've already converted with another script with controlnet, as it needs special inputs that standard ONNX conversions don't support, so you need to convert with this modified script. Again, you can optionally enable attention slicing by adding the same argument from before.
```
python conv_sdcnet_to_onnx.py --model_path "runwayml/stable-diffusion-v1-5" --output_path "./model/sd15_onnx" --fp16
```

3. Testing
Now you can run the test script. Cross your fingers!
```
python testonnxcnet.py
```
# Random notes
<br>I couldn't figure out how to pass a tuple of tensors as an input with Onnxruntime, so I just modified UNet2DConditionModel and renamed it UNet2DConditionModel_Cnet so that instead of a tuple of 12 tensors, it's 12 separate tensors passed as individual arguments.

