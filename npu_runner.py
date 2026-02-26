from optimum.intel import OVModelForCausalLM
from transformers import AutoTokenizer
import torch
import time

model_path = "tiny-llama-eager"

print(f"--- 1. Loading {model_path} ---")
model = OVModelForCausalLM.from_pretrained(model_path, device="NPU", compile=False)
tokenizer = AutoTokenizer.from_pretrained(model_path)

print("--- 2. Reshaping in RAM to [1, 128] ---")
try:
    model.reshape(1, 128)
    print("   Reshape command sent.")
except Exception as e:
    print(f"   Warning: {e}")

print("--- 3. Compiling to NPU (Moment of Truth) ---")
model.compile()

print("--- 4. Running Inference ---")
prompt = "Explain what a neural network is."
inputs = tokenizer(prompt, return_tensors="pt")

# STATIC PADDING (Required)
pad_len = 128 - inputs.input_ids.shape[1]
if pad_len > 0:
    pad_ids = torch.full((1, pad_len), tokenizer.pad_token_id or 0, dtype=torch.long)
    pad_mask = torch.zeros((1, pad_len), dtype=torch.long)
    input_ids = torch.cat([inputs.input_ids, pad_ids], dim=1)
    attention_mask = torch.cat([inputs.attention_mask, pad_mask], dim=1)
else:
    input_ids = inputs.input_ids[:, :128]
    attention_mask = inputs.attention_mask[:, :128]

start = time.time()
output = model.generate(
    input_ids=input_ids,
    attention_mask=attention_mask,
    max_new_tokens=20,
    pad_token_id=tokenizer.eos_token_id
)
print(f"\nResponse: {tokenizer.decode(output[0], skip_special_tokens=True)}")
##e