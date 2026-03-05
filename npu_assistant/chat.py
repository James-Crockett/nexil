import openvino_genai as ov_genai
from pathlib import Path

def cmd_chat(config):
    """Chat things """
    # NPU-specific options (MAX_PROMPT_LEN, MIN_RESPONSE_LEN only work on NPU)
    # 9s to load without cache, around 3s with
    cache_dir = str(Path.home() / ".cache" / "npu-assistant" / "compiled")
    if config.device == "NPU":
        pipe = ov_genai.LLMPipeline(
            config.model_path,
            config.device,
            MAX_PROMPT_LEN=1024,
            MIN_RESPONSE_LEN=512,
            CACHE_DIR=cache_dir,
        )
    else:
        pipe = ov_genai.LLMPipeline(
            config.model_path,
            config.device,
        )
    history = ov_genai.ChatHistory() 
    history.append({"role": "system", "content": config.system_prompt})

    while True:
        user_input = input("> ")

        #checks for slash
        if user_input.startswith("/"):
            if user_input == "/quit":
                print("Bye Bye!")
                break
            elif user_input == "/clear":
                history = ov_genai.ChatHistory()
                history.append({"role": "system", "content": config.system_prompt})
                print("History cleared.")
                continue
            else:                                                                                                                           
                  print("Unknown command:", user_input)
                  continue   
            
        history.append({"role": "user", "content": user_input})

        #generation config
        gen_config = ov_genai.GenerationConfig()
        gen_config.max_new_tokens = config.max_new_tokens
        gen_config.do_sample = config.do_sample
        gen_config.repetition_penalty = config.rep_penalty
        
        #stream it tolken by token
        response_tokens = []

        #stream response (does not wait for the whole response, prints response as it is generated)
        def streamer(token):
            response_tokens.append(token)
            print(token, end="",flush=True) #flush keeps it going
            return False #keeps generating until the whole response

        pipe.generate(history, generation_config= gen_config, streamer=streamer)

        #save full response to history
        full_response = "".join(response_tokens)
        history.append({"role": "assistant", "content": full_response})
        print() #newline




