import torch
import torch.nn.functional as F
import numpy as np
from scipy.ndimage import gaussian_filter1d


# from baseline:
def gauss_smooth(inputs, device, smooth_kernel_std=2, smooth_kernel_size=100,  padding='same'):
    """
    Applies a 1D Gaussian smoothing operation with PyTorch to smooth the data along the time axis.
    Args:
        inputs (tensor : B x T x N): A 3D tensor with batch size B, time steps T, and number of features N.
                                     Assumed to already be on the correct device (e.g., GPU).
        kernelSD (float): Standard deviation of the Gaussian smoothing kernel.
        padding (str): Padding mode, either 'same' or 'valid'.
        device (str): Device to use for computation (e.g., 'cuda' or 'cpu').
    Returns:
        smoothed (tensor : B x T x N): A smoothed 3D tensor with batch size B, time steps T, and number of features N.
    """
    # Get Gaussian kernel
    inp = np.zeros(smooth_kernel_size, dtype=np.float32)
    inp[smooth_kernel_size // 2] = 1
    gaussKernel = gaussian_filter1d(inp, smooth_kernel_std)
    validIdx = np.argwhere(gaussKernel > 0.01)
    gaussKernel = gaussKernel[validIdx]
    gaussKernel = np.squeeze(gaussKernel / np.sum(gaussKernel))

    # Convert to tensor
    gaussKernel = torch.tensor(gaussKernel, dtype=torch.float32, device=device)
    gaussKernel = gaussKernel.view(1, 1, -1)  # [1, 1, kernel_size]

    # Prepare convolution
    B, T, C = inputs.shape
    inputs = inputs.permute(0, 2, 1)  # [B, C, T]
    gaussKernel = gaussKernel.repeat(C, 1, 1)  # [C, 1, kernel_size]

    # Perform convolution
    smoothed = F.conv1d(inputs, gaussKernel, padding=padding, groups=C)
    return smoothed.permute(0, 2, 1)  # [B, T, C]


def temporal_masking_batched(inputs, lengths, num_masks=(1, 2), T=40, fill=0.0):
    """
    inputs: (B, T, C) tensor
    lengths: (B,) int tensor of valid lengths (<=T)
    T: maximum mask width
    num_masks: number of independent time masks
    """
    B, Tmax, C = inputs.shape
    device = inputs.device

    # ensure integer lengths are on device
    lengths = lengths.to(device)

    # loop over batch
    for b in range(B):
        L = int(lengths[b].item())
        if L <= 0:
            continue

        # width cannot exceed the valid length
        max_w = min(T, L)
        if max_w <= 0:
            continue

        # randomly select number of masks to create
        k = int(torch.randint(num_masks[0], num_masks[1] + 1, (1,), device=device).item())
        for _ in range(k):
            # randomly create width of max
            w = int(torch.randint(1, max_w + 1, (1,), device=device).item())
            
            # randomly find start index of mask
            start = int(torch.randint(0, L - w + 1, (1,), device=device).itme())

            # update selected indices of input to masked
            inputs[b, start:start+w, :] = fill

        return inputs
