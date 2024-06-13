import pytoshop
from pytoshop import layers
from pytoshop.enums import BlendMode
import torch
import numpy as np
import os
import datetime

class PSDLayerCreator:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_image": ("IMAGE",),
                "masks": ("MASK",),
                "output_path": ("STRING", {}),
                "original_image": ("BOOLEAN", {"default": True}),
            }
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("layers",)
    FUNCTION = "main"

    CATEGORY = "LayersDivider"
    
    def main(self, input_image, masks, output_path, original_image):
        if input_image.shape[0] > 1:
            raise ValueError("Batch input is not supported.")
        # remove the batch
        input_image = input_image.squeeze(0)
        
        # check if alfa channel is present, if not add it to the original image
        if input_image.shape[2] != 4:  # Check if image already has 4 channels (RGBA)
            # Create an alpha channel with full opacity
            alpha_channel = torch.ones(input_image.shape[0], input_image.shape[1], 1)

            # Concatenate channels to create RGBA image
            input_image = torch.cat((input_image, alpha_channel), dim=2)
    
        # Validate mask and input image dimensions
        if masks.shape[1:] != input_image.shape[:2]:
            raise ValueError("Mask dimensions must match the input image dimensions.")
        
        # check if output_path contains the name of the file
        if not output_path.endswith(".psd"):
            # Generate random name using current time
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            random_name = f"layered_image_{timestamp}.psd"
            os.makedirs(output_path, exist_ok=True)
            output_path = os.path.join(output_path, random_name)  # Join path with random name

        # Create a new empty PSD document (consider using desired color mode if needed)
        psd = pytoshop.core.PsdFile(num_channels=4, height=input_image.shape[0], width=input_image.shape[1])
        
        if original_image:
            # Save the original image as the first layer (optional layer name)
            original_image_uint8 = (input_image.cpu().detach().numpy() * 255).astype(np.uint8)
        
            original_layer_data = [layers.ChannelImageData(image=original_image_uint8[:, :, channel], compression=1) for channel in range(input_image.shape[2])]
            original_layer_record = layers.LayerRecord(
                channels={-1: original_layer_data[3], 0: original_layer_data[0], 1: original_layer_data[1], 2: original_layer_data[2]},
                top=0, bottom=input_image.shape[0], left=0, right=input_image.shape[1],
                blend_mode=BlendMode.normal,
                name="Original Image",  # Optional layer name
                opacity=255,
            )
            psd.layer_and_mask_info.layer_info.layer_records.append(original_layer_record)


        all_masked_images = []
        # Create and add masked image layers
        for i in range(masks.shape[0]):  # Iterate based on number of channels
            print(f"Processing mask {i}")

            mask = masks[i]  # Select the i-th element (channel) as the mask

            # Ensure mask has a single leading dimension (batch dimension)
            if mask.ndim == 2:
                mask = mask.unsqueeze(2)

            masked_image = input_image * mask.float()
            
            all_masked_images.append(masked_image)

            # Convert masked image to numpy array (assuming CPU tensor)
            masked_image_numpy = masked_image.cpu().detach().numpy()
            
            # Convert masked image to a suitable unsigned integer format (e.g., uint8)
            masked_image_uint8 = (masked_image_numpy * 255).astype(np.uint8)

            # Create layer data objects from masked image channels (adjust based on mask count)
            layer_data = []
            for channel in range(input_image.shape[2]):
                layer_data.append(
                    layers.ChannelImageData(image=masked_image_uint8[:, :, channel], compression=1)
                )
                
            # Create a new layer record with the layer data
            new_layer_record = layers.LayerRecord(
                channels={-1: layer_data[3], 0: layer_data[0], 1: layer_data[1], 2: layer_data[2]},
                top=0, bottom=input_image.shape[0], left=0, right=input_image.shape[1],
                blend_mode=BlendMode.normal,
                name=f"Masked_{i+1}",
                opacity=255,
            )
            psd.layer_and_mask_info.layer_info.layer_records.append(new_layer_record)


            
        # Save the PSD file at the specified output path
        try:
            with open(f"{output_path}", 'wb') as fd2:
                psd.write(fd2)
            print(f"Masked images saved as PSD with separate layers: {output_path}")
        except Exception as e:
            print(f"Error saving PSD: {e}")
        return (all_masked_images,)
        
class PSDLayerCreatorFromImagesOnly:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_image": ("IMAGE",),
                "output_path": ("STRING", {}),
            }
        }
        
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("layers",)
    FUNCTION = "main"

    CATEGORY = "LayersDivider"
    
    def main(self, input_image, output_path):
        # Ensure the input is a batch
        print(input_image.shape)
        if input_image.ndim != 4 or input_image.shape[3] not in [1, 3, 4]:
            raise ValueError("Input image should have shape [batch_size, channels, height, width]")

        # Determine the number of images in the batch
        batch_size, height, width, channels = input_image.shape
        
        # Add alpha channel if not present
        if channels != 4:  # Check if image has 4 channels (RGBA)
            # Create an alpha channel with full opacity
            alpha_channel = torch.ones(batch_size, height, width, 1, device=input_image.device)
            # Concatenate channels to create RGBA image
            input_image = torch.cat((input_image, alpha_channel), dim=3)
        
        
        # check if output_path contains the name of the file
        if not output_path.endswith(".psd"):
            # Generate random name using current time
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            random_name = f"layered_image_{timestamp}.psd"
            os.makedirs(output_path, exist_ok=True)
            output_path = os.path.join(output_path, random_name)  # Join path with random name

        # Create a new empty PSD document (consider using desired color mode if needed)
        psd = pytoshop.core.PsdFile(num_channels=4, height=height, width=width)
        
        # Create and add image layers
        for i in range(batch_size):
            print(f"Processing image {i+1}/{batch_size}")
            
            image = input_image[i]  # Select the i-th image

            # Convert image to numpy array
            image_numpy = image.cpu().detach().numpy()
            
            # Convert image to uint8 format
            image_uint8 = (image_numpy * 255).astype(np.uint8)

            # Create layer data objects from image channels
            layer_data = [layers.ChannelImageData(image=image_uint8[:, :, channel], compression=1) for channel in range(image.shape[2])]
                    
            # Create a new layer record with the layer data
            new_layer_record = layers.LayerRecord(
                channels={-1: layer_data[3], 0: layer_data[0], 1: layer_data[1], 2: layer_data[2]},
                top=0, bottom=height, left=0, right=width,
                blend_mode=BlendMode.normal,
                name=f"Image_{i+1}",
                opacity=255,
            )
            psd.layer_and_mask_info.layer_info.layer_records.append(new_layer_record)
        
        
        # Save the PSD file at the specified output path
        try:
            with open(f"{output_path}", 'wb') as fd2:
                psd.write(fd2)
            print(f"Masked images saved as PSD with separate layers: {output_path}")
        except Exception as e:
            print(f"Error saving PSD: {e}")
        return (input_image,)

NODE_CLASS_MAPPINGS = {
    "LayersSaver - Save Layer": PSDLayerCreator,
    "LayersSaver - Save Layer From Images": PSDLayerCreatorFromImagesOnly
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LayerDividerDivideLayer": "LayersSaver - Save Layer",
    "PSDLayerCreatorFromImagesOnly": "LayersSaver - Save Layer From Images"
}