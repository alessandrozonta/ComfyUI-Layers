import unittest
import torch
from layers_creation import PSDLayerCreator
import os
import glob


class LayerDividerTest(unittest.TestCase):

    def test_invalid_batch_input_dimensions(self):
        """Tests the function with mismatched mask dimensions."""
        input_image = torch.rand(4, 256, 256, 3)
        masks = torch.rand(3, 256, 256)   # Mismatched dimensions
        output_path = "test.psd"
        original_image = True
        
        layer_divide = PSDLayerCreator()
        with self.assertRaises(ValueError) as error:
            layer_divide.main(input_image, masks, output_path, original_image)

        self.assertEqual(str(error.exception), "Batch input is not supported.")

        
    def test_invalid_mask_dimensions(self):
        """Tests the function with mismatched mask dimensions."""
        input_image = torch.rand(1, 256, 256, 3)
        masks = torch.rand(3, 128, 128)   # Mismatched dimensions
        output_path = "test.psd"
        original_image = True

        layer_divide = PSDLayerCreator()
        with self.assertRaises(ValueError) as error:
            layer_divide.main(input_image, masks, output_path, original_image)

        self.assertEqual(str(error.exception), "Mask dimensions must match the input image dimensions.")


    def test_single_mask(self):
        """Tests the function with a single mask."""
        input_image = torch.rand(1, 256, 256, 3)
        masks = torch.rand(1, 256, 256) 
        output_path = "test.psd"  # Replace with a writable location for testing
        original_image = True

        layer_divide = PSDLayerCreator()
        # This test verifies basic layer creation logic without external libraries
        try:
            layer_divide.main(input_image, masks, output_path, original_image)
            # Since we're not saving the PSD, success means no exceptions
            print("Test successful: Layer creation logic seems functional for a single mask.")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        os.remove(output_path)


    def test_multiple_masks(self):
        """Tests the function with multiple masks."""
        input_image = torch.rand(1, 256, 256, 3)
        masks = torch.rand(10, 256, 256) 
        output_path = "test.psd"  # Replace with a writable location for testing
        original_image = True

        layer_divide = PSDLayerCreator()
        # This test verifies basic layer creation logic without external libraries
        try:
            layer_divide.main(input_image, masks, output_path, original_image)
            # Since we're not saving the PSD, success means no exceptions
            print("Test successful: Layer creation logic seems functional for multiple masks.")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        os.remove(output_path)
        
    def test_already_with_alpha_channel(self):
        """Tests the function with input image already with alpha channel."""
        input_image = torch.rand(1, 256, 256, 4)
        masks = torch.rand(10, 256, 256) 
        output_path = "test.psd"  # Replace with a writable location for testing
        original_image = True

        layer_divide = PSDLayerCreator()
        # This test verifies basic layer creation logic without external libraries
        try:
            layer_divide.main(input_image, masks, output_path, original_image)
            # Since we're not saving the PSD, success means no exceptions
            print("Test successful: Layer creation logic seems functional for multiple masks.")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        os.remove(output_path)
        
    def test_output_path_no_name(self):
        """Tests the function with without giving the name of the file as output"""
        input_image = torch.rand(1, 256, 256, 4)
        masks = torch.rand(10, 256, 256) 
        output_path = ""  # Replace with a writable location for testing
        original_image = True

        layer_divide = PSDLayerCreator()
        # This test verifies basic layer creation logic without external libraries
        try:
            layer_divide.main(input_image, masks, output_path, original_image)
            # Since we're not saving the PSD, success means no exceptions
            print("Test successful: Layer creation logic seems functional for multiple masks.")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
        psd_files = glob.glob(os.path.join(output_path, "*.psd"))
        # Be sure the file is saved
        self.assertEqual(len(psd_files), 1)
        os.remove(psd_files[0])
        
if __name__ == '__main__':
    unittest.main()
