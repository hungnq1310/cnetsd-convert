# Copyright 2022 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import shutil
from pathlib import Path

import torch
from torch.onnx import export

import onnx
from onnxruntime.transformers.float16 import convert_float_to_float16
from diffusers import OnnxStableDiffusionPipeline, StableDiffusionControlNetPipeline, ControlNetModel, OnnxRuntimeModel

from packaging import version
#from transformers import AutoFeatureExtractor, BertTokenizerFast, CLIPTextModel, CLIPTokenizer


is_torch_less_than_1_11 = version.parse(version.parse(torch.__version__).base_version) < version.parse("1.11")

def convert_to_fp16(
    model_path
):
    '''Converts an ONNX model on disk to FP16'''
    model_dir=os.path.dirname(model_path)
    # Breaking down in steps due to Windows bug in convert_float_to_float16_model_path
    onnx.shape_inference.infer_shapes_path(model_path)
    fp16_model = onnx.load(model_path)
    fp16_model = convert_float_to_float16(
        fp16_model, keep_io_types=True, disable_shape_infer=True
    )
    # clean up existing tensor files
    shutil.rmtree(model_dir)
    os.mkdir(model_dir)
    # save FP16 model
    onnx.save(fp16_model, model_path)

def onnx_export(
    model,
    model_args: tuple,
    output_path: Path,
    ordered_input_names,
    output_names,
    dynamic_axes,
    opset,
    use_external_data_format=False,
):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # PyTorch deprecated the `enable_onnx_checker` and `use_external_data_format` arguments in v1.11,
    # so we check the torch version for backwards compatibility
    if is_torch_less_than_1_11:
        export(
            model,
            model_args,
            f=output_path.as_posix(),
            input_names=ordered_input_names,
            output_names=output_names,
            dynamic_axes=dynamic_axes,
            do_constant_folding=True,
            use_external_data_format=use_external_data_format,
            enable_onnx_checker=True,
            opset_version=opset,
        )
    else:
        export(
            model,
            model_args,
            f=output_path.as_posix(),
            input_names=ordered_input_names,
            output_names=output_names,
            dynamic_axes=dynamic_axes,
            do_constant_folding=True,
            opset_version=opset,
        )


@torch.no_grad()
def convert_models(model_path: str, output_path: str, opset: int, fp16: bool, attention_slicing: str):
    controlnet = ControlNetModel.from_pretrained(model_path)
    output_path = Path(output_path)
    if attention_slicing is not None:
        print("Attention slicing: " + attention_slicing)
        controlnet.set_attention_slice(attention_slicing)

    dtype=torch.float32
    device = "cpu"
        
    cnet_path = output_path / "controlnet" / "model.onnx"

    #! This is a workaround for the current implementation of torch.onnx.dynamo_export
    # export_options = torch.onnx.ExportOptions(dynamic_shapes=True)
    # input_kwargs = 
    #     "sample": torch.randn(2, 4, 64, 64).to(device=device, dtype=dtype),
    #     "timestep": torch.randn(2).to(device=device, dtype=dtype),
    #     "encoder_hidden_states": torch.randn(2, 77, 768).to(device=device, dtype=dtype),
    #     "controlnet_cond": torch.randn(2, 3, 512,512).to(device=device, dtype=dtype),
    #     "return_dict": False,
    # }
    # onnx_program = torch.onnx.dynamo_export(

    onnx_export(
        controlnet,
        model_args=(
            torch.randn(2, 4, 64, 64).to(device=device, dtype=dtype),
            torch.randn(2).to(device=device, dtype=dtype),
            torch.randn(2, 77, 768).to(device=device, dtype=dtype),
            torch.randn(2, 3, 512,512).to(device=device, dtype=dtype),
            1.0,
            None, None, None, None, None,
            False, False
        ),
        output_path=cnet_path,
        ordered_input_names=["sample", "timestep", "encoder_hidden_states", "controlnet_cond"],

    
        output_names=[
            "down_block_0",
            "down_block_1",
            "down_block_2",
            "down_block_3",
            "down_block_4",
            "down_block_5",
            "down_block_6",
            "down_block_7",
            "down_block_8",
            "down_block_9",
            "down_block_10",
            "down_block_11",
            "mid_block_res_sample",
        ],  # has to be different from "sample" for correct tracing
        dynamic_axes={
            "sample": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "timestep": {0: "batch"},
            "encoder_hidden_states": {0: "batch", 1: "sequence"},
            "controlnet_cond": {0: "batch", 2: "height", 3: "width"},
            "down_block_0": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "down_block_1": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "down_block_2": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "down_block_3": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "down_block_4": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "down_block_5": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "down_block_6": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "down_block_7": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "down_block_8": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "down_block_9": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "down_block_10": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "down_block_11": {0: "batch", 1: "channels", 2: "height", 3: "width"},
            "mid_block_res_sample": {0: "batch", 1: "channels", 2: "height", 3: "width"},
        },
        opset=opset,
    )
    
    if fp16:
        cnet_path_model_path = str(cnet_path.absolute().as_posix())
        convert_to_fp16(cnet_path_model_path)
    
    # onnx_program.save(cnet_path.as_posix())
    print("ONNX controlnet saved to ", output_path)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Path to the `diffusers` checkpoint to convert (either a local directory or on the Hub).",
    )

    parser.add_argument("--output_path", type=str, required=True, help="Path to the output model.")

    parser.add_argument(
        "--opset",
        default=15,
        type=int,
        help="The version of the ONNX operator set to use.",
    )
    
    parser.add_argument(
        "--fp16",
        action="store_true",
        help="Export Controlnet in mixed `float16` mode"
    )
    
    parser.add_argument(
        "--attention-slicing",
        choices={"auto","max"},
        type=str,
        help="Attention slicing, off by default. Can be set to auto. Reduces amount of VRAM used."
    )

    args = parser.parse_args()

    convert_models(args.model_path, args.output_path, args.opset, args.fp16 ,args.attention_slicing)
