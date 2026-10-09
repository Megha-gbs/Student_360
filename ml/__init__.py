"""Student360 ML Package"""

# Canonical NumPy 2.x compatibility shim for SHAP
import numpy as np

if not hasattr(np, "obj2sctype"):
    def _obj2sctype(obj):
        try:
            return np.dtype(obj).type
        except TypeError:
            return obj if isinstance(obj, type) and issubclass(obj, np.generic) else None

    np.obj2sctype = _obj2sctype
