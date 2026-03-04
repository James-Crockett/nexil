MODELS_DIR = Path.home() / ".cache" / "npu-assistant" / "models"

def find_model():
    """Auto-detect installed model. Returns path string or None."""
    if not MODELS_DIR.exists():
        return None
    
    models = []
    for folder in MODELS_DIR.iterdir():
        if folder.is_dir() and any(folder.glob("*.xml")): #just checking for.xml is fine because openvino is taking care of the installation
            models.append(folder)                           
    
    if len(models) == 1:
        return str(models[0])
    if len(models) > 1:
        return str(models[0])  # use first found else user can override with --model
    return None