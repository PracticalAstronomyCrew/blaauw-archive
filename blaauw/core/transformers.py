from typing import Optional
from blaauw.core import models

def imtyp_to_enum(imtyp: Optional[str] = None, filter: Optional[str] = None, obj: Optional[str] = None) -> Optional[models.ImageType]:
    if imtyp is not None:
        if imtyp.lower() in ("bias", "bias frame"):
            return models.ImageType.BIAS
        if imtyp.lower() in ("flat", "flat field"):
            return models.ImageType.FLAT
        if imtyp.lower() in ("dark", "dark frame"):
            return models.ImageType.DARK
        if imtyp.lower() in ("light", "light frame"):
            return models.ImageType.LIGHT

    if filter is not None:
        if filter.lower() == "dark":
            return models.ImageType.DARK

    if obj is not None:
        obj_cmp = obj.lower().strip()
        if obj_cmp.startswith("flat"):
            return models.ImageType.FLAT
        if obj_cmp.startswith("bias"):
            return models.ImageType.BIAS
        if obj_cmp.startswith("dark"):
            return models.ImageType.DARK
        elif obj_cmp != "":
            # When something is given as the object, assign it type light
            return models.ImageType.LIGHT

    return None
