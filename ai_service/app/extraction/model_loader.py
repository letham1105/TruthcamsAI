import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

from ai_service.app.config import QWEN_MODEL_NAME
from ai_service.app.utils.logging_config import get_logger

logger = get_logger(__name__)

_model = None
_tokenizer = None

def load_qwen(model_name=QWEN_MODEL_NAME):
    """Load Qwen once. The notebook's 4-bit configuration requires CUDA."""
    global _model, _tokenizer

    if _model is not None and _tokenizer is not None:
        return _model, _tokenizer

    if not torch.cuda.is_available():
        raise RuntimeError(
            "Qwen3-8B 4-bit configuration expects a CUDA GPU. "
            "Use a GPU machine/remote inference environment or configure another model runtime."
        )

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    _tokenizer = AutoTokenizer.from_pretrained(model_name)
    _model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quantization_config,
        device_map="auto",
        torch_dtype=torch.float16,
        attn_implementation="sdpa",
    )
    _model.eval()
    logger.info("Loaded Qwen model: %s", model_name)
    return _model, _tokenizer

def get_qwen():
    if _model is None or _tokenizer is None:
        return load_qwen()
    return _model, _tokenizer
