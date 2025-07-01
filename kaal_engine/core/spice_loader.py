from skyfield.jpllib import SpiceKernel

def load_kernel(path: str) -> SpiceKernel:
    try:
        return SpiceKernel(path)
    except Exception as e:
        raise RuntimeError(f"Failed to load SPICE kernel: {str(e)}")

def interpolate_position(kernel: SpiceKernel, jd: float, body: str):
    return (0.0, 0.0, 0.0)
