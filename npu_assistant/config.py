[config]
    name = "Assistant"
    system_prompt = ""
    thinking = False
    device = "NPU"
    model_path = "~/.cache/npu-assistant/models/Qwen2.5-3B-Instruct-int4-ov"
    do_sample = False
    max_new_tokens = 512
    repetition_penalty = 1.1
    