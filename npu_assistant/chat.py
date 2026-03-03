import openvino_genai as ovg

def cmd_chat(config):
    pipe = ovg.LLMPipeline(config.model_path, config.device)
    history = ovg.ChatHistory() 
    history.append({"role": "system", "content": config.system_prompt})

    while True:
        user_input = input("> ")

        if user_input.startswith("/"):
            if user_input == "/quit":
                break
            elif user_input == "/clear":
                history = ovg.ChatHistory()
                history.append({"role": "system", "content": config.system_prompt})
                print("History cleared.")





