from optimum.intel import OVModelForCausalLM
from transformers import AutoTokenizer

model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
save_dir = "tiny-llama-eager"  # New folder name

print("--- 1. Exporting with 'Eager' Attention (Driver Compatibility Mode) ---")
model = OVModelForCausalLM.from_pretrained(
    model_id,
    export=True,
    stateful=False,       # Keep it stateless
    load_in_8bit=False,   # Keep it FP16
    attn_implementation="eager",  # <--- FORCE SIMPLE MATH
    device="cpu",
    compile=False
)

print("--- 2. Saving Clean Model ---")
model.half()
model.save_pretrained(save_dir)
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.save_pretrained(save_dir)
print("--- Success. Model saved. ---")