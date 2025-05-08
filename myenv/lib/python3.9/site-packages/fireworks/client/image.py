from typing import List, Optional, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from .image_api import (
    AnimateAnyoneRequestBody,
    ImageToImageRequestBody,
    ImageToVideoRequestBody,
    TextToImageRequestBody,
    ControlNetRequestBody,
    QRCodeRequest,
)
from .api_client import FireworksClient

from PIL import Image
import httpx
import io
import os
from dataclasses import dataclass
import base64
import asyncio


@dataclass
class Answer:
    image: Optional[Image.Image]
    finish_reason: str


@dataclass
class AnswerVideo:
    video: bytes
    finish_reason: str


class ImageInference(FireworksClient):
    """
    Main client class for the Fireworks Image and Video Generation APIs.
    """

    def __init__(
        self,
        account: str = "fireworks",
        model: str = "stable-diffusion-xl-1024-v1-0",
        request_timeout=600,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(request_timeout, api_key=api_key, base_url=base_url, **kwargs)
        self.account = account
        self.model = model

    def _img_to_bytes(
        self, image: Union[Image.Image, str, os.PathLike, bytes]
    ) -> bytes:
        # Normalize all forms of `image` into a `bytes` object
        # to send over the wire
        if isinstance(image, Image.Image):
            img_bio = io.BytesIO()
            image.save(img_bio, format="PNG")
            image = img_bio.getvalue()
        elif isinstance(image, (str, os.PathLike)):
            with open(image, "rb") as f:
                image = f.read()

        return image

    def text_to_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        cfg_scale: Optional[int] = None,
        clip_guidance_preset: str = "NONE",
        height: Optional[int] = None,
        width: Optional[int] = None,
        sampler: Optional[str] = None,
        samples: int = 1,
        steps: Optional[int] = None,
        seed: int = 0,
        style_preset: Optional[str] = None,
        safety_check: bool = False,
        lora_adapter_name: Optional[str] = None,
        lora_weight_filename: Optional[str] = None,
        hf_access_key: Optional[str] = None,
        output_image_format: str = "PNG",
        model: Optional[str] = None,
    ):
        """
        Generate an image or images based on the given text prompt and optional negative prompt.
        See the OpenAPI spec (https://readme.fireworks.ai/reference/post_image-generation-stable-diffusion)
        for the most up-to-date description of the supported parameters

        Parameters:
        - prompt (str): The main text prompt based on which the image will be generated.
        - negative_prompt (str, optional): A secondary text prompt which can be used to guide the image generation in a negative way.
        - cfg_scale (int, optional): Context-free guidance scale for the image generation. If not specified, a model-specific default will be used
        - clip_guidance_preset (str, optional): CLIP guidance preset. Defaults to "NONE".
        - height (int, optional): Desired height of the generated image. If not specified, a model-specific default will be used.
        - width (int, optional): Desired width of the generated image. If not used, a model-specific default will be used.
        - sampler (str, optional): Sampler type. Optional.
        - samples (int, optional): Number of images to be generated. Defaults to 1.
        - steps (int, optional): Number of steps for the generation process. If not specified, a model-specific default will be used.
        - seed (int, optional): Seed for random number generation. Defaults to 0.
        - style_preset (str, optional): Style preset for the generated image. Optional.
        - lora_adapter_name (str, optional): LoRA adapter name. This can refer to a fully-qualified HuggingFace repo name, e.g. 'foo/bar'. Optional
        - lora_weight_filename (str, optional): The filename within the LoRA repo to load LoRA weights from. Should be a single filename like 'pytorch_lora_weights.safetensors'. Optional. Must be specified if lora_adapter_name is specified.
        - hf_access_key (str, optional): The access key to access HuggingFace to download a LoRA adapter. Specify if your adapter is in a private repo that requires permissions. Optional.
        - output_image_format (str): The format of the generated image. Defaults to "PNG". Options are "PNG" and "JPG". Use PNG for best quality and JPG for best speed. JPG currently only supported for samples=1.
        - model (str, optional): The model name to call. If not present, defaults to `self.model` on the ImageInference object.

        Returns:
        Image.Image or List[Image.Image]: Generated image or a list of generated images.

        Raises:
        RuntimeError: If there is an error in the image generation process.
        """
        return asyncio.run(
            self.text_to_image_async(
                prompt,
                negative_prompt,
                cfg_scale,
                clip_guidance_preset,
                height,
                width,
                sampler,
                samples,
                steps,
                seed,
                style_preset,
                safety_check,
                lora_adapter_name,
                lora_weight_filename,
                hf_access_key,
                output_image_format,
                model,
            )
        )

    async def text_to_image_async(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        cfg_scale: Optional[int] = None,
        clip_guidance_preset: str = "NONE",
        height: Optional[int] = None,
        width: Optional[int] = None,
        sampler: Optional[str] = None,
        samples: int = 1,
        steps: Optional[int] = None,
        seed: int = 0,
        style_preset: Optional[str] = None,
        safety_check: bool = False,
        lora_adapter_name: Optional[str] = None,
        lora_weight_filename: Optional[str] = None,
        hf_access_key: Optional[str] = None,
        output_image_format: str = "PNG",
        model: Optional[str] = None,
    ) -> Union[Image.Image, List[Image.Image]]:
        """
        Generate an image or images based on the given text prompt and optional negative prompt.
        See the OpenAPI spec (https://readme.fireworks.ai/reference/post_image-generation-stable-diffusion)
        for the most up-to-date description of the supported parameters

        Parameters:
        - prompt (str): The main text prompt based on which the image will be generated.
        - negative_prompt (str, optional): A secondary text prompt which can be used to guide the image generation in a negative way.
        - cfg_scale (int, optional): Context-free guidance scale for the image generation. If not specified, a model-specific default will be used
        - clip_guidance_preset (str, optional): CLIP guidance preset. Defaults to "NONE".
        - height (int, optional): Desired height of the generated image. If not specified, a model-specific default will be used.
        - width (int, optional): Desired width of the generated image. If not used, a model-specific default will be used.
        - sampler (str, optional): Sampler type. Optional.
        - samples (int, optional): Number of images to be generated. Defaults to 1.
        - steps (int, optional): Number of steps for the generation process. If not specified, a model-specific default will be used.
        - seed (int, optional): Seed for random number generation. Defaults to 0.
        - style_preset (str, optional): Style preset for the generated image. Optional.
        - lora_adapter_name (str, optional): LoRA adapter name. This can refer to a fully-qualified HuggingFace repo name, e.g. 'foo/bar'. Optional
        - lora_weight_filename (str, optional): The filename within the LoRA repo to load LoRA weights from. Should be a single filename like 'pytorch_lora_weights.safetensors'. Optional. Must be specified if lora_adapter_name is specified.
        - hf_access_key (str, optional): The access key to access HuggingFace to download a LoRA adapter. Specify if your adapter is in a private repo that requires permissions. Optional.
        - output_image_format (str): The format of the generated image. Defaults to "PNG". Options are "PNG" and "JPG". Use PNG for best quality and JPG for best speed. JPG currently only supported for samples=1.
        - model (str, optional): The model name to call. If not present, defaults to `self.model` on the ImageInference object.

        Returns:
        Image.Image or List[Image.Image]: Generated image or a list of generated images.

        Raises:
        RuntimeError: If there is an error in the image generation process.
        """
        request_body = TextToImageRequestBody(
            cfg_scale=cfg_scale,
            clip_guidance_preset=clip_guidance_preset,
            height=height,
            width=width,
            sampler=sampler,
            samples=samples,
            steps=steps,
            seed=seed,
            style_preset=style_preset,
            prompt=prompt,
            negative_prompt=negative_prompt,
            safety_check=safety_check,
            lora_adapter_name=lora_adapter_name,
            lora_weight_filename=lora_weight_filename,
        )
        payload_dict = request_body.dict()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if samples == 1:
            if output_image_format in {"JPG", "JPEG"}:
                headers["Accept"] = "image/jpeg"
            elif output_image_format == "PNG":
                headers["Accept"] = "image/png"
            else:
                raise ValueError(
                    f"Unsupported output_image_format: {output_image_format}"
                )
        else:
            if output_image_format == "PNG":
                headers["Accept"] = "application/json"
            else:
                raise ValueError(
                    f"Only PNG output image format is supported when samples != 1"
                )

        if hf_access_key is not None:
            headers["Huggingface-Access-Key"] = hf_access_key

        async with httpx.AsyncClient(
            headers=headers,
            timeout=self.request_timeout,
            **self.client_kwargs,
        ) as client:
            endpoint_base_uri = f"{self.base_url}/image_generation/accounts/{self.account}/models/{model or self.model}"
            response = await client.post(endpoint_base_uri, json=payload_dict)
            self._error_handling(response)
        if samples == 1:
            finish_reason = response.headers.get("finish-reason", "SUCCESS")
            return Answer(
                image=Image.open(io.BytesIO(response.content)),
                finish_reason=finish_reason,
            )
        else:
            return [
                Answer(
                    Image.open(io.BytesIO(base64.b64decode(artifact["base64"]))),
                    finish_reason=artifact["finishReason"],
                )
                for artifact in response.json()
            ]

    def image_to_image(
        self,
        init_image: Union[Image.Image, str, os.PathLike, bytes],
        prompt: str,
        height: Optional[int] = None,
        width: Optional[int] = None,
        crop_padding: bool = True,
        negative_prompt: Optional[str] = None,
        cfg_scale: Optional[int] = None,
        clip_guidance_preset: str = "NONE",
        sampler: Optional[str] = None,
        samples: int = 1,
        steps: Optional[int] = None,
        seed: int = 0,
        style_preset: Optional[str] = None,
        init_image_mode: str = "IMAGE_STRENGTH",
        image_strength: Optional[float] = None,
        step_schedule_start: Optional[float] = 0.65,
        step_schedule_end: Optional[float] = None,
        safety_check: bool = False,
        client_account_id_header: Optional[str] = None,
        lora_adapter_name: Optional[str] = None,
        lora_weight_filename: Optional[str] = None,
        hf_access_key: Optional[str] = None,
        output_image_format: str = "PNG",
        model: Optional[str] = None,
    ) -> Union[Image.Image, List[Image.Image]]:
        """
        Modify an existing image based on a given text prompt and optional negative prompt.
        See the OpenAPI spec (https://readme.fireworks.ai/reference/post_image-generation-stable-diffusion)
        for the most up-to-date description of the supported parameters

        Parameters:
        - init_image (Union[Image.Image, str, os.PathLike, bytes]): Initial image to be modified. It can be provided as a PIL Image object, path to an image, or raw bytes.
        - prompt (str): The main text prompt based on which the image will be modified.
        - height (int, optional): Desired height of the generated image. If not specified, a model-specific default will be used.
        - width (int, optional): Desired width of the generated image. If not used, a model-specific default will be used.
        - crop_padding (bool, optional): Whether to crop the padding from the generated image. Defaults to True.
        - negative_prompt (str, optional): A secondary text prompt which can be used to guide the image modification in a negative way.
        - cfg_scale (int, optional): Context-free guidance scale for the image modification. If not specified, a model-specific default will be used
        - clip_guidance_preset (str, optional): CLIP guidance preset. Defaults to "NONE".
        - sampler (str, optional): Sampler type. Optional.
        - samples (int, optional): Number of images to be generated. Defaults to 1.
        - steps (int, optional): Number of steps for the modification process. If not specified, a model-specific default will be used.
        - seed (int, optional): Seed for random number generation. Defaults to 0.
        - style_preset (str, optional): Style preset for the modified image. Optional.
        - init_image_mode (str, optional): Initialization mode for the image modification. Defaults to "IMAGE_STRENGTH".
        - image_strength (float, optional): Strength of the initial image. Required when init_image_mode is "IMAGE_STRENGTH".
        - step_schedule_start (float, optional): Start of the step schedule. Required when init_image_mode is "STEP_SCHEDULE". Defaults to 0.65.
        - step_schedule_end (float, optional): End of the step schedule. Required when init_image_mode is "STEP_SCHEDULE".
        - model (str, optional): which model to use. Defaults to "accounts/fireworks/models/stable-diffusion-xl-1024-v1-0".
        - client_account_id_header (str, optional): Client account ID header. Used for private deployments. Optional.
        - lora_adapter_name (str, optional): LoRA adapter name. This can refer to a fully-qualified HuggingFace repo name, e.g. 'foo/bar'. Optional
        - lora_weight_filename (str, optional): The filename within the LoRA repo to load LoRA weights from. Should be a single filename like 'pytorch_lora_weights.safetensors'. Optional. Must be specified if lora_adapter_name is specified.
        - hf_access_key (str, optional): The access key to access HuggingFace to download a LoRA adapter. Specify if your adapter is in a private repo that requires permissions. Optional.
        - output_image_format (str): The format of the generated image. Defaults to "PNG". Options are "PNG" and "JPG". Use PNG for best quality and JPG for best speed. JPG currently only supported for samples=1.
        - model (str, optional): The model name to call. If not present, defaults to `self.model` on the ImageInference object.

        Returns:
        Image.Image or List[Image.Image]: Modified image or a list of modified images.

        Raises:
        ValueError: If required parameters are missing based on the given init_image_mode.
        RuntimeError: If there is an error in the image modification process.
        """
        return asyncio.run(
            self.image_to_image_async(
                init_image,
                prompt,
                height,
                width,
                crop_padding,
                negative_prompt,
                cfg_scale,
                clip_guidance_preset,
                sampler,
                samples,
                steps,
                seed,
                style_preset,
                init_image_mode,
                image_strength,
                step_schedule_start,
                step_schedule_end,
                safety_check,
                client_account_id_header,
                lora_adapter_name,
                lora_weight_filename,
                hf_access_key,
                output_image_format,
                model=model,
            )
        )

    async def image_to_image_async(
        self,
        init_image: Union[Image.Image, str, os.PathLike, bytes],
        prompt: str,
        height: Optional[int] = None,
        width: Optional[int] = None,
        crop_padding: bool = True,
        negative_prompt: Optional[str] = None,
        cfg_scale: Optional[int] = None,
        clip_guidance_preset: str = "NONE",
        sampler: Optional[str] = None,
        samples: int = 1,
        steps: Optional[int] = None,
        seed: int = 0,
        style_preset: Optional[str] = None,
        init_image_mode: str = "IMAGE_STRENGTH",
        image_strength: Optional[float] = None,
        step_schedule_start: Optional[float] = 0.65,
        step_schedule_end: Optional[float] = None,
        safety_check: bool = False,
        client_account_id_header: Optional[str] = None,
        lora_adapter_name: Optional[str] = None,
        lora_weight_filename: Optional[str] = None,
        hf_access_key: Optional[str] = None,
        output_image_format: str = "PNG",
        model: Optional[str] = None,
    ) -> Union[Image.Image, List[Image.Image]]:
        """
        Modify an existing image based on a given text prompt and optional negative prompt.
        See the OpenAPI spec (https://readme.fireworks.ai/reference/post_image-generation-stable-diffusion)
        for the most up-to-date description of the supported parameters

        Parameters:
        - init_image (Union[Image.Image, str, os.PathLike, bytes]): Initial image to be modified. It can be provided as a PIL Image object, path to an image, or raw bytes.
        - prompt (str): The main text prompt based on which the image will be modified.
        - height (int, optional): Desired height of the generated image. If not specified, a model-specific default will be used.
        - width (int, optional): Desired width of the generated image. If not used, a model-specific default will be used.
        - crop_padding (bool, optional): Whether to crop the padding from the generated image. Defaults to True.
        - negative_prompt (str, optional): A secondary text prompt which can be used to guide the image modification in a negative way.
        - cfg_scale (int, optional): Context-free guidance scale for the image modification. If not specified, a model-specific default will be used
        - clip_guidance_preset (str, optional): CLIP guidance preset. Defaults to "NONE".
        - sampler (str, optional): Sampler type. Optional.
        - samples (int, optional): Number of images to be generated. Defaults to 1.
        - steps (int, optional): Number of steps for the modification process. If not specified, a model-specific default will be used.
        - seed (int, optional): Seed for random number generation. Defaults to 0.
        - style_preset (str, optional): Style preset for the modified image. Optional.
        - init_image_mode (str, optional): Initialization mode for the image modification. Defaults to "IMAGE_STRENGTH".
        - image_strength (float, optional): Strength of the initial image. Required when init_image_mode is "IMAGE_STRENGTH".
        - step_schedule_start (float, optional): Start of the step schedule. Required when init_image_mode is "STEP_SCHEDULE". Defaults to 0.65.
        - step_schedule_end (float, optional): End of the step schedule. Required when init_image_mode is "STEP_SCHEDULE".
        - model (str, optional): which model to use. Defaults to "accounts/fireworks/models/stable-diffusion-xl-1024-v1-0".
        - client_account_id_header (str, optional): Client account ID header. Used for private deployments. Optional.
        - lora_adapter_name (str, optional): LoRA adapter name. This can refer to a fully-qualified HuggingFace repo name, e.g. 'foo/bar'. Optional
        - lora_weight_filename (str, optional): The filename within the LoRA repo to load LoRA weights from. Should be a single filename like 'pytorch_lora_weights.safetensors'. Optional. Must be specified if lora_adapter_name is specified.
        - hf_access_key (str, optional): The access key to access HuggingFace to download a LoRA adapter. Specify if your adapter is in a private repo that requires permissions. Optional.
        - output_image_format (str): The format of the generated image. Defaults to "PNG". Options are "PNG" and "JPG". Use PNG for best quality and JPG for best speed. JPG currently only supported for samples=1.
        - model (str, optional): The model name to call. If not present, defaults to `self.model` on the ImageInference object.

        Returns:
        Image.Image or List[Image.Image]: Modified image or a list of modified images.

        Raises:
        ValueError: If required parameters are missing based on the given init_image_mode.
        RuntimeError: If there is an error in the image modification process.
        """
        # Argument Validation
        if init_image_mode == "IMAGE_STRENGTH" and image_strength is None:
            raise ValueError(
                "image_strength is required when init_image_mode is IMAGE_STRENGTH"
            )
        if init_image_mode == "STEP_SCHEDULE" and (
            step_schedule_start is None or step_schedule_end is None
        ):
            raise ValueError(
                "Both step_schedule_start and step_schedule_end are required when init_image_mode is STEP_SCHEDULE"
            )

        # Construct and validate request fields.
        # NB: prompt and init_image are not used here. Instead, we construct
        # them specially to be sent as multipart/form-data
        request_body = ImageToImageRequestBody(
            prompt=prompt,
            height=height,
            width=width,
            crop_padding=crop_padding,
            negative_prompt=negative_prompt,
            cfg_scale=cfg_scale,
            clip_guidance_preset=clip_guidance_preset,
            sampler=sampler,
            samples=samples,
            steps=steps,
            seed=seed,
            style_preset=style_preset,
            init_image_mode=init_image_mode,
            image_strength=image_strength,
            step_schedule_start=step_schedule_start,
            step_schedule_end=step_schedule_end,
            safety_check=safety_check,
            lora_adapter_name=lora_adapter_name,
            lora_weight_filename=lora_weight_filename,
        )
        payload_dict = request_body.dict()

        headers = {"Authorization": f"Bearer {self.api_key}"}
        if samples == 1:
            if output_image_format in {"JPG", "JPEG"}:
                headers["Accept"] = "image/jpeg"
            elif output_image_format == "PNG":
                headers["Accept"] = "image/png"
            else:
                raise ValueError(
                    f"Unsupported output_image_format: {output_image_format}"
                )
        else:
            if output_image_format == "PNG":
                headers["Accept"] = "application/json"
            else:
                raise ValueError(
                    f"Only PNG output image format is supported when samples != 1"
                )

        if client_account_id_header:
            headers["X-Fireworks-Routing-Account-ID"] = client_account_id_header

        if hf_access_key is not None:
            headers["Huggingface-Access-Key"] = hf_access_key

        init_image: bytes = self._img_to_bytes(init_image)

        files = {
            "init_image": init_image,
        }
        async with httpx.AsyncClient(
            headers=headers,
            timeout=self.request_timeout,
            **self.client_kwargs,
        ) as client:
            endpoint_base_uri = f"{self.base_url}/image_generation/accounts/{self.account}/models/{model or self.model}"
            response = await client.post(
                f"{endpoint_base_uri}/image_to_image",
                data=payload_dict,
                files=files,
            )
            self._error_handling(response)
        if samples == 1:
            finish_reason = response.headers.get("finish-reason", "SUCCESS")
            return Answer(
                image=Image.open(io.BytesIO(response.content)),
                finish_reason=finish_reason,
            )
        else:
            return [
                Answer(
                    Image.open(io.BytesIO(base64.b64decode(artifact["base64"]))),
                    finish_reason=artifact["finishReason"],
                )
                for artifact in response.json()
            ]

    def control_net(
        self,
        control_image: Union[Image.Image, str, os.PathLike, bytes],
        control_net_name: str,
        prompt: str,
        height: Optional[int] = None,
        width: Optional[int] = None,
        crop_padding: bool = True,
        negative_prompt: Optional[str] = None,
        cfg_scale: Optional[int] = None,
        clip_guidance_preset: str = "NONE",
        sampler: Optional[str] = None,
        samples: int = 1,
        steps: Optional[int] = None,
        seed: int = 0,
        style_preset: Optional[str] = None,
        step_schedule_start: Optional[float] = 0.0,
        step_schedule_end: Optional[float] = 1.0,
        conditioning_scale: Optional[float] = 0.5,
        safety_check: bool = False,
        client_account_id_header: Optional[str] = None,
        lora_adapter_name: Optional[str] = None,
        lora_weight_filename: Optional[str] = None,
        hf_access_key: Optional[str] = None,
        output_image_format: str = "PNG",
    ) -> Union[Image.Image, List[Image.Image]]:
        """
        Modify an existing image based on a given text prompt and optional negative prompt.
        See the OpenAPI spec (https://readme.fireworks.ai/reference/post_image-generation-stable-diffusion)
        for the most up-to-date description of the supported parameters

        Parameters:
        - control_image (Union[Image.Image, str, os.PathLike, bytes]): Initial image to be modified. It can be provided as a PIL Image object, path to an image, or raw bytes.
        - control_net_name (str): Name of HuggingFace repository with control net name or a simple reference like "canny".
        - prompt (str): The main text prompt based on which the image will be modified.
        - height (int, optional): Desired height of the generated image. If not specified, a model-specific default will be used.
        - width (int, optional): Desired width of the generated image. If not used, a model-specific default will be used.
        - crop_padding (bool, optional): Whether to crop the padding from the generated image. Defaults to True.
        - negative_prompt (str, optional): A secondary text prompt which can be used to guide the image modification in a negative way.
        - cfg_scale (int, optional): Context-free guidance scale for the image modification. If not specified, a model-specific default will be used
        - clip_guidance_preset (str, optional): CLIP guidance preset. Defaults to "NONE".
        - sampler (str, optional): Sampler type. Optional.
        - samples (int, optional): Number of images to be generated. Defaults to 1.
        - steps (int, optional): Number of steps for the modification process. If not specified, a model-specific default will be used.
        - seed (int, optional): Seed for random number generation. Defaults to 0.
        - style_preset (str, optional): Style preset for the modified image. Optional.
        - step_schedule_start (float, optional): The percentage of total steps at which the ControlNet starts applying.
        - step_schedule_end (float, optional): The percentage of total steps at which the ControlNet stops applying.
        - conditioning_scale (float, optional, defaults to 0.5): The outputs of the ControlNet are multiplied by this value before they are added to the residual.
        - model (str, optional): which model to use. Defaults to "accounts/fireworks/models/stable-diffusion-xl-1024-v1-0".
        - client_account_id_header (str, optional): Client account ID header. Used for private deployments. Optional.
        - lora_adapter_name (str, optional): LoRA adapter name. This can refer to a fully-qualified HuggingFace repo name, e.g. 'foo/bar'. Optional
        - lora_weight_filename (str, optional): The filename within the LoRA repo to load LoRA weights from. Should be a single filename like 'pytorch_lora_weights.safetensors'. Optional. Must be specified if lora_adapter_name is specified.
        - hf_access_key (str, optional): The access key to access HuggingFace to download a LoRA adapter. Specify if your adapter is in a private repo that requires permissions. Optional.
        - output_image_format (str): The format of the generated image. Defaults to "PNG". Options are "PNG" and "JPG". Use PNG for best quality and JPG for best speed. JPG currently only supported for samples=1.

        Returns:
        Image.Image or List[Image.Image]: Modified image or a list of modified images.

        Raises:
        RuntimeError: If there is an error in the image generation process.
        """
        return asyncio.run(
            self.control_net_async(
                control_image,
                control_net_name,
                prompt,
                height,
                width,
                crop_padding,
                negative_prompt,
                cfg_scale,
                clip_guidance_preset,
                sampler,
                samples,
                steps,
                seed,
                style_preset,
                step_schedule_start,
                step_schedule_end,
                conditioning_scale,
                safety_check,
                client_account_id_header,
                lora_adapter_name,
                lora_weight_filename,
                hf_access_key,
                output_image_format,
            )
        )

    async def control_net_async(
        self,
        control_image: Union[Image.Image, str, os.PathLike, bytes],
        control_net_name: str,
        prompt: str,
        height: Optional[int] = None,
        width: Optional[int] = None,
        crop_padding: bool = True,
        negative_prompt: Optional[str] = None,
        cfg_scale: Optional[int] = None,
        clip_guidance_preset: str = "NONE",
        sampler: Optional[str] = None,
        samples: int = 1,
        steps: Optional[int] = None,
        seed: int = 0,
        style_preset: Optional[str] = None,
        step_schedule_start: Optional[float] = 0.0,
        step_schedule_end: Optional[float] = 1.0,
        conditioning_scale: Optional[float] = 0.5,
        safety_check: bool = False,
        client_account_id_header: Optional[str] = None,
        lora_adapter_name: Optional[str] = None,
        lora_weight_filename: Optional[str] = None,
        hf_access_key: Optional[str] = None,
        output_image_format: str = "PNG",
    ) -> Union[Image.Image, List[Image.Image]]:
        """
        Modify an existing image based on a given text prompt and optional negative prompt.
        See the OpenAPI spec (https://readme.fireworks.ai/reference/post_image-generation-stable-diffusion)
        for the most up-to-date description of the supported parameters

        Parameters:
        - control_image (Union[Image.Image, str, os.PathLike, bytes]): Initial image to be modified. It can be provided as a PIL Image object, path to an image, or raw bytes.
        - control_net_name (str): Name of HuggingFace repository with control net name or a simple reference like "canny".
        - prompt (str): The main text prompt based on which the image will be modified.
        - height (int, optional): Desired height of the generated image. If not specified, a model-specific default will be used.
        - width (int, optional): Desired width of the generated image. If not used, a model-specific default will be used.
        - crop_padding (bool, optional): Whether to crop the padding from the generated image. Defaults to True.
        - negative_prompt (str, optional): A secondary text prompt which can be used to guide the image modification in a negative way.
        - cfg_scale (int, optional): Context-free guidance scale for the image modification. If not specified, a model-specific default will be used
        - clip_guidance_preset (str, optional): CLIP guidance preset. Defaults to "NONE".
        - sampler (str, optional): Sampler type. Optional.
        - samples (int, optional): Number of images to be generated. Defaults to 1.
        - steps (int, optional): Number of steps for the modification process. If not specified, a model-specific default will be used.
        - seed (int, optional): Seed for random number generation. Defaults to 0.
        - style_preset (str, optional): Style preset for the modified image. Optional.
        - step_schedule_start (float, optional): The percentage of total steps at which the ControlNet starts applying.
        - step_schedule_end (float, optional): The percentage of total steps at which the ControlNet stops applying.
        - conditioning_scale (float, optional, defaults to 0.5): The outputs of the ControlNet are multiplied by this value before they are added to the residual.
        - model (str, optional): which model to use. Defaults to "accounts/fireworks/models/stable-diffusion-xl-1024-v1-0".
        - client_account_id_header (str, optional): Client account ID header. Used for private deployments. Optional.
        - lora_adapter_name (str, optional): LoRA adapter name. This can refer to a fully-qualified HuggingFace repo name, e.g. 'foo/bar'. Optional
        - lora_weight_filename (str, optional): The filename within the LoRA repo to load LoRA weights from. Should be a single filename like 'pytorch_lora_weights.safetensors'. Optional. Must be specified if lora_adapter_name is specified.
        - hf_access_key (str, optional): The access key to access HuggingFace to download a LoRA adapter. Specify if your adapter is in a private repo that requires permissions. Optional.
        - output_image_format (str): The format of the generated image. Defaults to "PNG". Options are "PNG" and "JPG". Use PNG for best quality and JPG for best speed. JPG currently only supported for samples=1.

        Returns:
        Image.Image or List[Image.Image]: Modified image or a list of modified images.

        Raises:
        RuntimeError: If there is an error in the image generation process.
        """
        # Argument Validation
        # Construct and validate request fields.
        # NB: prompt and control_image are not used here. Instead, we construct
        # them specially to be sent as multipart/form-data
        request_body = ControlNetRequestBody(
            prompt=prompt,
            height=height,
            width=width,
            crop_padding=crop_padding,
            negative_prompt=negative_prompt,
            cfg_scale=cfg_scale,
            clip_guidance_preset=clip_guidance_preset,
            sampler=sampler,
            samples=samples,
            steps=steps,
            seed=seed,
            style_preset=style_preset,
            control_net_name=control_net_name,
            step_schedule_start=step_schedule_start,
            step_schedule_end=step_schedule_end,
            conditioning_scale=conditioning_scale,
            safety_check=safety_check,
            lora_adapter_name=lora_adapter_name,
            lora_weight_filename=lora_weight_filename,
        )
        payload_dict = request_body.dict()

        headers = {"Authorization": f"Bearer {self.api_key}"}
        if samples == 1:
            headers["Accept"] = "image/png"
        else:
            headers["Accept"] = "application/json"
        if samples == 1:
            if output_image_format in {"JPG", "JPEG"}:
                headers["Accept"] = "image/jpeg"
            elif output_image_format == "PNG":
                headers["Accept"] = "image/png"
            else:
                raise ValueError(
                    f"Unsupported output_image_format: {output_image_format}"
                )
        else:
            if output_image_format == "PNG":
                headers["Accept"] = "application/json"
            else:
                raise ValueError(
                    f"Only PNG output image format is supported when samples != 1"
                )

        if client_account_id_header:
            headers["X-Fireworks-Routing-Account-ID"] = client_account_id_header

        if hf_access_key is not None:
            headers["Huggingface-Access-Key"] = hf_access_key

        control_image: bytes = self._img_to_bytes(control_image)

        files = {
            "control_image": control_image,
        }
        async with httpx.AsyncClient(
            headers=headers,
            timeout=self.request_timeout,
            **self.client_kwargs,
        ) as client:
            endpoint_base_uri = f"{self.base_url}/image_generation/accounts/{self.account}/models/{self.model}"
            response = await client.post(
                f"{endpoint_base_uri}/control_net",
                data=payload_dict,
                files=files,
            )
            self._error_handling(response)
        if samples == 1:
            finish_reason = response.headers.get("finish-reason", "SUCCESS")
            return Answer(
                image=Image.open(io.BytesIO(response.content)),
                finish_reason=finish_reason,
            )
        else:
            return [
                Answer(
                    Image.open(io.BytesIO(base64.b64decode(artifact["base64"]))),
                    finish_reason=artifact["finishReason"],
                )
                for artifact in response.json()
            ]

    def canny_edge_detection(
        self,
        image: Union[Image.Image, str, os.PathLike, bytes],
        min_val: float = 100,
        max_val: float = 200,
    ) -> Image.Image:
        """
        Detect edges in an image using Canny edge detection.

        Parameters:
        - image (Union[Image.Image, str, os.PathLike, bytes]): Image to detect edges in. It can be provided as a PIL Image object, path to an image, or raw bytes.
        - min_val (float, optional): Minimum threshold value. Defaults to 100.
        - max_val (float, optional): Maximum threshold value. Defaults to 200.

        Returns:
        Image.Image: Image with detected edges.

        Raises:
        RuntimeError: If there is an error in the edge detection process.
        """
        return asyncio.run(
            self.canny_edge_detection_async(
                image,
                min_val,
                max_val,
            )
        )

    async def canny_edge_detection_async(
        self,
        image: Union[Image.Image, str, os.PathLike, bytes],
        min_val: float = 100,
        max_val: float = 200,
    ) -> Image.Image:
        """
        Detect edges in an image using Canny edge detection.

        Parameters:
        - image (Union[Image.Image, str, os.PathLike, bytes]): Image to detect edges in. It can be provided as a PIL Image object, path to an image, or raw bytes.
        - min_val (float, optional): Minimum threshold value. Defaults to 100.
        - max_val (float, optional): Maximum threshold value. Defaults to 200.

        Returns:
        Image.Image: Image with detected edges.

        Raises:
        RuntimeError: If there is an error in the edge detection process.
        """
        image: bytes = self._img_to_bytes(image)

        headers = {"Authorization": f"Bearer {self.api_key}"}

        files = {
            "image": image,
        }
        async with httpx.AsyncClient(
            headers=headers,
            timeout=self.request_timeout,
            **self.client_kwargs,
        ) as client:
            endpoint_base_uri = f"{self.base_url}/image_generation/accounts/{self.account}/models/{self.model}"
            response = await client.post(
                f"{endpoint_base_uri}/canny_edge_detection",
                files=files,
                data={"min_val": min_val, "max_val": max_val},
            )
            self._error_handling(response)

        return Image.open(io.BytesIO(response.content))

    def qr_code(
        self,
        prompt: str,
        height: int = 1024,
        width: int = 1024,
        output_image_format: str = "PNG",
    ) -> Image.Image:
        """
        Generate a QR code based on the given text prompt.

        Parameters:
        - prompt (str): The text prompt based on which the QR code will be generated.
        - height (int, optional): Desired height of the generated QR code. Defaults to 1024.
        - width (int, optional): Desired width of the generated QR code. Defaults to 1024.

        Returns:
        Image.Image: Generated QR code.

        Raises:
        RuntimeError: If there is an error in the QR code generation process.
        """
        return asyncio.run(
            self.qr_code_async(
                prompt,
                height,
                width,
                output_image_format,
            )
        )

    async def qr_code_async(
        self,
        prompt: str,
        height: int = 1024,
        width: int = 1024,
        output_image_format: str = "PNG",
    ) -> Image.Image:
        """
        Generate a QR code based on the given text prompt.

        Parameters:
        - prompt (str): The text prompt based on which the QR code will be generated.
        - height (int, optional): Desired height of the generated QR code. Defaults to 1024.
        - width (int, optional): Desired width of the generated QR code. Defaults to 1024.

        Returns:
        Image.Image: Generated QR code.

        Raises:
        RuntimeError: If there is an error in the QR code generation process.
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}

        if output_image_format in {"JPG", "JPEG"}:
            headers["Accept"] = "image/jpeg"
        elif output_image_format == "PNG":
            headers["Accept"] = "image/png"
        else:
            raise ValueError(f"Unsupported output_image_format: {output_image_format}")

        body = QRCodeRequest(
            prompt=prompt,
            height=height,
            width=width,
        )

        async with httpx.AsyncClient(
            headers=headers,
            timeout=self.request_timeout,
            **self.client_kwargs,
        ) as client:
            endpoint_base_uri = f"{self.base_url}/image_generation/accounts/{self.account}/models/{self.model}"
            response = await client.post(
                f"{endpoint_base_uri}/qr_code",
                json=body.dict(),
            )
            self._error_handling(response)

        return Image.open(io.BytesIO(response.content))

    async def image_to_video_async(
        self,
        input_image: Union[Image.Image, str, os.PathLike, bytes],
        height: int = 576,
        width: int = 1024,
        sampler: Optional[str] = None,
        frames: Optional[int] = None,
        steps: int = 25,
        min_guidance_scale: float = 1.0,
        max_guidance_scale: float = 3.0,
        fps: int = 7,
        motion_bucket_id: int = 127,
        noise_aug_strength: float = 0.02,
        decode_chunk_size: Optional[int] = None,
        seed: int = 0,
        safety_check: bool = False,
        frame_interpolation_factor: Optional[int] = None,
        output_video_bitrate: Optional[int] = 8_388_608,  # Default 8Mbps
        _infer_if_input_is_flagged_DEBUG_ONLY: bool = False,
    ) -> AnswerVideo:
        """
        Generate a video based on a given initial image.

        Parameters:
        - init_image (Union[Image.Image, str, os.PathLike, bytes]): Initial image to be modified. It can be provided as a PIL Image object, path to an image, or raw bytes.
        - height (int, optional): Desired height of the generated video. Defaults to 576.
        - width (int, optional): Desired width of the generated video. Defaults to 1024.
        - sampler (str, optional): Sampler type. Optional.
        - frames (int, optional): Number of frames to be generated. Defaults to None.
        - steps (int, optional): Number of steps for the modification process. Defaults to 25.
        - min_guidance_scale (float, optional): Minimum guidance scale. Defaults to 1.0.
        - max_guidance_scale (float, optional): Maximum guidance scale. Defaults to 3.0.
        - fps (int, optional): Frames per second. Defaults to 7.
        - motion_bucket_id (int, optional): Motion bucket ID. Defaults to 127.
        - noise_aug_strength (float, optional): Noise augmentation strength. Defaults to 0.02.
        - decode_chunk_size (int, optional): Decode chunk size. Defaults to None.
        - seed (int, optional): Seed for random number generation. Defaults to 0.
        - safety_check (bool, optional): Whether to perform a safety check on the input image and generated frames. Defaults to False.
        - frame_interpolation_factor(int, optional): Factor for frame interpolation. For example, a factor of 2 will produce 2x more frames, 3 3x more frames, and so on.
        - output_video_bitrate (int, optional): Bitrate of the generated video. Defaults to 8Mbps.

        Returns:
        bytes: Generated video.

        Raises:
        RuntimeError: If there is an error in the video generation process.
        """
        # Construct and validate request fields.
        # NB: init_image is not used here. Instead, we construct
        # it specially to be sent as multipart/form-data
        request_body = ImageToVideoRequestBody(
            height=height,
            width=width,
            sampler=sampler,
            frames=frames,
            steps=steps,
            min_guidance_scale=min_guidance_scale,
            max_guidance_scale=max_guidance_scale,
            fps=fps,
            motion_bucket_id=motion_bucket_id,
            noise_aug_strength=noise_aug_strength,
            decode_chunk_size=decode_chunk_size,
            seed=seed,
            safety_check=safety_check,
            frame_interpolation_factor=frame_interpolation_factor,
            output_video_bitrate=output_video_bitrate,
            infer_if_input_is_flagged_DEBUG_ONLY=_infer_if_input_is_flagged_DEBUG_ONLY,
        )
        payload_dict = request_body.dict()

        headers = {"Authorization": f"Bearer {self.api_key}"}
        headers["Accept"] = "video/mp4"

        input_image: bytes = self._img_to_bytes(input_image)

        files = {
            "input_image": input_image,
        }
        async with httpx.AsyncClient(
            headers=headers,
            timeout=self.request_timeout,
            **self.client_kwargs,
        ) as client:
            endpoint_base_uri = f"{self.base_url}/video_generation/accounts/{self.account}/models/{self.model}"
            response = await client.post(
                f"{endpoint_base_uri}/image_to_video",
                data=payload_dict,
                files=files,
            )
            self._error_handling(response)

        finish_reason = response.headers.get("finish-reason", "SUCCESS")
        return AnswerVideo(
            video=response.content,
            finish_reason=finish_reason,
        )

    def image_to_video(
        self,
        input_image: Union[Image.Image, str, os.PathLike, bytes],
        height: int = 576,
        width: int = 1024,
        sampler: Optional[str] = None,
        frames: Optional[int] = None,
        steps: int = 25,
        min_guidance_scale: float = 1.0,
        max_guidance_scale: float = 3.0,
        fps: int = 7,
        motion_bucket_id: int = 127,
        noise_aug_strength: float = 0.02,
        decode_chunk_size: Optional[int] = None,
        seed: int = 0,
        safety_check: bool = False,
        frame_interpolation_factor: Optional[int] = None,
        output_video_bitrate: Optional[int] = 8_388_608,  # Default 8Mbps
        _infer_if_input_is_flagged_DEBUG_ONLY: bool = False,
    ) -> AnswerVideo:
        """
        Generate a video based on a given initial image.

        Parameters:
        - input_image (Union[Image.Image, str, os.PathLike, bytes]): Initial image to be modified. It can be provided as a PIL Image object, path to an image, or raw bytes.
        - height (int, optional): Desired height of the generated video. Defaults to 576.
        - width (int, optional): Desired width of the generated video. Defaults to 1024.
        - sampler (str, optional): Sampler type. Optional.
        - frames (int, optional): Number of frames to be generated. Defaults to None.
        - steps (int, optional): Number of steps for the modification process. Defaults to 25.
        - min_guidance_scale (float, optional): Minimum guidance scale. Defaults to 1.0.
        - max_guidance_scale (float, optional): Maximum guidance scale. Defaults to 3.0.
        - fps (int, optional): Frames per second. Defaults to 7.
        - motion_bucket_id (int, optional): Motion bucket ID. Defaults to 127.
        - noise_aug_strength (float, optional): Noise augmentation strength. Defaults to 0.02.
        - decode_chunk_size (int, optional): Decode chunk size. Defaults to None.
        - seed (int, optional): Seed for random number generation. Defaults to 0.
        - safety_check (bool, optional): Whether to perform a safety check on the input image and generated frames. Defaults to False.
        - frame_interpolation_factor(int, optional): Factor for frame interpolation. For example, a factor of 2 will produce 2x more frames, 3 3x more frames, and so on.
        - output_video_bitrate (int, optional): Bitrate of the generated video. Defaults to 8Mbps.

        Returns:
        bytes: Generated video.

        Raises:
        RuntimeError: If there is an error in the video generation process.
        """
        return asyncio.run(
            self.image_to_video_async(
                input_image,
                height,
                width,
                sampler,
                frames,
                steps,
                min_guidance_scale,
                max_guidance_scale,
                fps,
                motion_bucket_id,
                noise_aug_strength,
                decode_chunk_size,
                seed,
                safety_check,
                frame_interpolation_factor,
                output_video_bitrate=output_video_bitrate,
                _infer_if_input_is_flagged_DEBUG_ONLY=_infer_if_input_is_flagged_DEBUG_ONLY,
            )
        )

    def _audio_to_bytes(self, input_audio: Union[bytes, os.PathLike]) -> bytes:
        # NB: assuming "bytes" is raw input data. If the user wants to
        # specify a file path, they should pass in a string
        if isinstance(input_audio, (str, os.PathLike)):
            with open(input_audio, "rb") as f:
                input_audio = f.read()

        return input_audio

    async def animate_async(
        self,
        ref_image: Union[Image.Image, str, os.PathLike, bytes],
        input_audio: Union[bytes, os.PathLike],
        width: int = 512,
        height: int = 512,
        steps: int = 10,
        audio_guidance_scale: float = 3.0,
        context_guidance_scale: float = 0.0,
        guidance_rescale: float = 0.7,
        seed: int = 0,
        output_video_bitrate: int = 8_388_608,
        _fake_request: bool = False,
    ):
        """
        Generate a video based on a given initial image and speech audio track.

        Parameters:
        - ref_image (Union[Image.Image, str, os.PathLike, bytes]): Initial image to be modified. It can be provided as a PIL Image object, path to an image, or raw bytes.
        - input_audio (Union[bytes, os.PathLike]): Input audio file to use for speech input. Can be raw audio file bytes or a file path.
        - width (int, optional): Desired width of the generated video. Defaults to 1024.
        - height (int, optional): Desired height of the generated video. Defaults to 576.
        - steps (int, optional): Number of steps for the modification process. Defaults to 25.
        - audio_guidance_scale (float, optional): Guidance scale to use for audio context. Defaults to 3.0.
        - context_guidance_scale (float, optional): Guidance scale to use for context. Defaults to 0.0.
        - guidance_rescale (float, optional): Rescaling factor for guidance. Defaults to 0.7.
        - seed (int, optional): Seed for random number generation. Defaults to 0.
        - output_video_bitrate (int, optional): Bitrate of the generated video. Defaults to 8Mbps.

        Returns:
        bytes: Generated video.

        Raises:
        RuntimeError: If there is an error in the video generation process.
        """
        # Construct and validate request fields.
        # NB: ref_image and input_audio are not used here. Instead, we send those
        # as separate form fields
        request_body = AnimateAnyoneRequestBody(
            width=width,
            height=height,
            steps=steps,
            audio_guidance_scale=audio_guidance_scale,
            context_guidance_scale=context_guidance_scale,
            guidance_rescale=guidance_rescale,
            seed=seed,
            output_video_bitrate=output_video_bitrate,
        )
        payload_dict = request_body.dict()

        headers = {"Authorization": f"Bearer {self.api_key}"}
        headers["Accept"] = "video/mp4"
        if _fake_request:
            headers["Fireworks-Test-Request"] = "true"

        ref_image: bytes = self._img_to_bytes(ref_image)
        input_audio: bytes = self._audio_to_bytes(input_audio)

        files = {
            "ref_image": ref_image,
            "input_audio": input_audio,
        }
        async with httpx.AsyncClient(
            headers=headers,
            timeout=self.request_timeout,
            **self.client_kwargs,
        ) as client:
            endpoint_base_uri = f"{self.base_url}/video_generation/accounts/{self.account}/models/{self.model}"
            response = await client.post(
                f"{endpoint_base_uri}/animate",
                data=payload_dict,
                files=files,
            )
            self._error_handling(response)

        finish_reason = response.headers.get("finish-reason", "SUCCESS")
        return AnswerVideo(
            video=response.content,
            finish_reason=finish_reason,
        )

    def animate(
        self,
        ref_image: Union[Image.Image, str, os.PathLike, bytes],
        input_audio: Union[bytes, os.PathLike],
        width: int = 512,
        height: int = 512,
        steps: int = 10,
        audio_guidance_scale: float = 3.0,
        context_guidance_scale: float = 0.0,
        guidance_rescale: float = 0.7,
        seed: int = 0,
        output_video_bitrate: int = 8_388_608,
        _fake_request: bool = False,
    ):
        """
        Generate a video based on a given initial image and speech audio track.

        Parameters:
        - ref_image (Union[Image.Image, str, os.PathLike, bytes]): Initial image to be modified. It can be provided as a PIL Image object, path to an image, or raw bytes.
        - input_audio (Union[bytes, os.PathLike]): Input audio file to use for speech input. Can be raw audio file bytes or a file path.
        - width (int, optional): Desired width of the generated video. Defaults to 1024.
        - height (int, optional): Desired height of the generated video. Defaults to 576.
        - steps (int, optional): Number of steps for the modification process. Defaults to 25.
        - audio_guidance_scale (float, optional): Guidance scale to use for audio context. Defaults to 3.0.
        - context_guidance_scale (float, optional): Guidance scale to use for context. Defaults to 0.0.
        - guidance_rescale (float, optional): Rescaling factor for guidance. Defaults to 0.7.
        - seed (int, optional): Seed for random number generation. Defaults to 0.
        - output_video_bitrate (int, optional): Bitrate of the generated video. Defaults to 8Mbps.

        Returns:
        bytes: Generated video.

        Raises:
        RuntimeError: If there is an error in the video generation process.
        """
        return asyncio.run(
            self.animate_async(
                ref_image=ref_image,
                input_audio=input_audio,
                width=width,
                height=height,
                steps=steps,
                audio_guidance_scale=audio_guidance_scale,
                context_guidance_scale=context_guidance_scale,
                guidance_rescale=guidance_rescale,
                seed=seed,
                output_video_bitrate=output_video_bitrate,
                _fake_request=_fake_request,
            )
        )
