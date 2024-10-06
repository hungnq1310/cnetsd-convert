python conv_sdcnet_to_onnx.py \
    --model_path "SG161222/Realistic_Vision_V5.1_noVAE" \
    --output_path "./model/sd-cvae-xformers-withslice" \
    --vae_path stabilityai/sd-vae-ft-mse \
    --vae-slicing \
    --xformers 

# python conv_sdcnet_to_onnx.py \
#     --model_path "SG161222/Realistic_Vision_V5.1_noVAE" \
#     --output_path "./model/sd-cvae-xformers" \
#     --vae_path stabilityai/sd-vae-ft-mse \
#     --xformers

# python conv_sdcnet_to_onnx.py \
#     --model_path "SG161222/Realistic_Vision_V5.1_noVAE" \
#     --output_path "./model/sd-cvae-xformers-withslice-fp16" \
#     --vae_path stabilityai/sd-vae-ft-mse \
#     --vae-slicing \
#     --xformers \
#     --fp16

# python convert_controlnet_to_onnx.py --model_path="lllyasviel/sd-controlnet-openpose" --output_path="model/openpose-fp16" --fp16