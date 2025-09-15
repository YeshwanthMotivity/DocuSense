# utils/infer_model.py

# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch

# # Load a small language model for CPU (can be changed later to larger one if needed)
# model_name = "sshleifer/tiny-gpt2"  # ~82MB GPT-2 model
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)

# # Ensure we're on CPU
# device = torch.device("cpu")
# model.to(device)

# def generate_answer(query, top_chunks, max_new_tokens=100):
#     """
#     Generates an answer to the query using the model and top context chunks.
#     """
#     # Combine chunks and query into a single prompt
#     context = "\n".join(top_chunks)
#     prompt = f"{context}\n\nQuestion: {query}\nAnswer:"

#     # Tokenize
#     inputs = tokenizer(prompt, return_tensors="pt").to(device)

#     # Generate response
#     with torch.no_grad():
#         outputs = model.generate(
#             inputs["input_ids"],
#             max_new_tokens=max_new_tokens,
#             pad_token_id=tokenizer.eos_token_id
#         )

#     # Decode output
#     answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

#     # Remove the prompt part from the generated response
#     return answer[len(prompt):].strip()

# easycontext_cpu/infer_model.py

# # from transformers import GPT2Tokenizer, GPT2LMHeadModel
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
# import torch

# # # Load model & tokenizer once
# # tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
# # model = GPT2LMHeadModel.from_pretrained("gpt2")

# model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)
# model.eval()
# def generate_answer(query, chunks, max_input_tokens=1024, return_debug=False):
#     """
#     Generate a context-aware answer using TinyLlama-1.1B-Chat.
#     Ensures the input does not exceed model's token limit.
#     """
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model.to(device)

#     context = "\n".join(chunks)
    
#     # Use proper TinyLlama chat format
#     prompt = (
#         f"<|user|>\n"
#         f"You are a helpful assistant. Based solely on the following context, "
#         f"answer the question. If the answer cannot be found in the context, "
#         f"state that the information is not available.\n\n"
#         f"Context:\n{context}\n\n"
#         f"Question:\n{query}\n"
#         f"<|assistant|>\n"
#     )

#     inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_input_tokens)
#     inputs = {k: v.to(device) for k, v in inputs.items()}
    
#     # Store the number of input tokens
#     input_token_len = inputs['input_ids'].shape[1]

#     outputs = model.generate(
#         **inputs,
#         max_new_tokens=250, # Increased max_new_tokens for potentially longer answers
#         do_sample=True,
#         top_k=50,
#         top_p=0.95,
#         temperature=0.8,
#         pad_token_id=tokenizer.eos_token_id
#     )

#     response = tokenizer.decode(outputs[0], skip_special_tokens=False)
    
#     # generated_tokens = outputs[0][input_token_len:]
#     # answer_only_decoded = tokenizer.decode(generated_tokens, skip_special_tokens=True) # skip_special_tokens=True here


#     # Just return the raw model output for now
#     # return response.strip()
#     if return_debug:
#         # Return 3 things: answer (trimmed), prompt sent, raw model output (full)
#         return response.strip(), prompt, response
#     else:
#         return response.strip()
    
# def clean_answer(raw_model_output):
#     """
#     Cleans the raw model output to extract only the answer part,
#     specifically designed for TinyLlama's chat format.
#     """
#     # The expected start of the assistant's actual response
#     assistant_start_tag = "<|assistant|>"
    
#     # Find the index where the assistant's response should begin
#     start_index = raw_model_output.rfind(assistant_start_tag)

#     if start_index == -1:
#      # If the tag is not found, something is very wrong with the output format.
#      # Return the raw output or an error message.
#         return "Error: Assistant tag not found in model output."
    
#     # The actual answer starts immediately after the assistant_start_tag
#     # We add a newline to the index to account for the common pattern where the model
#     # generates a newline right after the assistant tag, before the actual answer.
#     # However, sometimes it generates immediately, so we need to be careful.
#     answer_potential_start = start_index + len(assistant_start_tag)
    
#     # Slice the string to get everything from the assistant tag onwards
#     answer_segment = raw_model_output[answer_potential_start:].strip()

#     # Look for common end-of-turn markers or special tokens
#     end_tags = ["<|endoftext|>", "<|user|>"]
    
#     for tag in end_tags:
#         if tag in answer_segment:
#             answer_segment = answer_segment.split(tag)[0].strip() # Take everything before the first occurrence of the tag

#     # Additional cleanup for any leading/trailing whitespace or repeated prompt parts
#     # (though the slicing should minimize this)
#     # answer_segment = answer_segment.replace(raw_model_output.split('<|assistant|>')[0], '').strip() # Attempt to remove leading prompt if it's there
#     pre_assistant_part = raw_model_output[:start_index].strip()
#     if answer_segment.startswith(pre_assistant_part) and len(pre_assistant_part) > 10: # Avoid removing tiny strings
#         answer_segment = answer_segment[len(pre_assistant_part):].strip()
#     # Post-processing: remove any potential leftover instruction phrases if the model repeats them
#     # For example, if the model starts with "Based on the context..."
#     common_start_phrases = [
#         "Based on the provided context, ",
#         "The context states that ",
#         "Based solely on the context, ",
#         "As per the context, ",
#         "According to the context, "
#     ]
#     for phrase in common_start_phrases:
#         if answer_segment.lower().startswith(phrase.lower()):
#             answer_segment = answer_segment[len(phrase):].strip()
#             break
#      # Remove the <s> token if it somehow appears at the very beginning
#     if answer_segment.startswith("<s>"):
#         answer_segment = answer_segment[3:].strip() # "<s>" is 3 characters

#     return answer_segment.strip()

#     # Also remove any trailing chat tags if the model includes them at the very end of its response
#     # if answer.endswith("<|endoftext|>"):
#     #     answer = answer[:-len("<|endoftext>")].strip()
#     # if answer.endswith("<|user|>"): # In case it starts a new turn
#     #     answer = answer[:-len("<|user|>")].strip()
#     # if answer.endswith("<|assistant|>"): # Should not happen, but for robustness
#     #     answer = answer[:-len("<|assistant|>")].strip()

#     trailing_tags = ["<|endoftext|>", "<|user|>", "<|assistant|>"]
#     for tag in trailing_tags:
#         if answer.endswith(tag):
#             answer = answer[:-len(tag)].strip()
#     return answer

# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch

# model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)
# model.eval()

# def generate_answer(query, chunks, max_input_tokens=1024, return_debug=False):
#     """
#     Generate a context-aware answer using TinyLlama-1.1B-Chat.
#     Ensures the input does not exceed model's token limit.
#     """
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model.to(device)

#     context = "\n".join(chunks)

#     # Use proper TinyLlama chat format
#     # It's crucial for the model to know where its turn starts.
#     # A newline after <|assistant|> often prompts the model to start generating.
#     prompt = (
#         f"<|user|>\n"
#         f"You are a helpful assistant. Based solely on the following context, "
#         f"answer the question. If the answer cannot be found in the context, "
#         f"state that the information is not available.\n\n"
#         f"Context:\n{context}\n\n"
#         f"Question:\n{query}\n"
#         f"<|assistant|>\n" # Keep the newline here as it's part of the standard chat format for starting a turn
#     )

#     inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_input_tokens)
#     inputs = {k: v.to(device) for k, v in inputs.items()}

#     # Store the number of input tokens
#     input_token_len = inputs['input_ids'].shape[1]

#     outputs = model.generate(
#         **inputs,
#         max_new_tokens=250,
#         do_sample=True,
#         top_k=50,
#         top_p=0.95,
#         temperature=0.8,
#         pad_token_id=tokenizer.eos_token_id
#     )

#     # Decode the *entire* output sequence (including prompt and generated tokens)
#     full_raw_output = tokenizer.decode(outputs[0], skip_special_tokens=False)

#     # Extract only the newly generated tokens (the answer part)
#     # This slices the tensor itself, then decodes *only* the new tokens, skipping special tokens.
#     generated_tokens_only = outputs[0][input_token_len:]
#     answer_only_decoded_content = tokenizer.decode(generated_tokens_only, skip_special_tokens=True)

#     if return_debug:
#         # When debugging, return the cleaned answer, the prompt, and the full raw output.
#         # clean_answer will now operate on the 'answer_only_decoded_content' directly for cleaning conversational filler.
#         return clean_answer(answer_only_decoded_content), prompt, full_raw_output
#     else:
#         # If not in debug mode, just return the cleaned answer directly.
#         return clean_answer(answer_only_decoded_content)


# def generate_answer(query, chunks, max_input_tokens=1024, return_debug=False):
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model.to(device)

#     context = "\n".join(chunks)

#     prompt_template = (
#         f"<|user|>\n"
#         f"You are a helpful assistant. Use the given context to answer the question clearly.\n\n"
#         f"Context:\n{context}\n\n"
#         f"Question:\n{query}\n"
#         f"<|assistant|>\n"
#     )

#     inputs = tokenizer(prompt_template, return_tensors="pt", truncation=True, max_length=max_input_tokens)
#     inputs = {k: v.to(device) for k, v in inputs.items()}
#     input_token_len = inputs['input_ids'].shape[1]

#     outputs = model.generate(
#         **inputs,
#         max_new_tokens=250,
#         do_sample=True,
#         top_k=50,
#         top_p=0.95,
#         temperature=0.8,
#         pad_token_id=tokenizer.eos_token_id
#     )

#     generated_tokens_only = outputs[0][input_token_len:]
#     answer = tokenizer.decode(generated_tokens_only, skip_special_tokens=True)
#     answer = clean_answer(answer)

#     if return_debug:
#         return answer, prompt_template, tokenizer.decode(outputs[0], skip_special_tokens=False)
#     else:
#         return answer

# def clean_answer(raw_generated_content):
#     """
#     Cleans the raw, newly generated content from the model.
#     This function expects to receive ONLY the model's generated text,
#     not the full prompt+response.
#     """
#     answer = raw_generated_content.strip()

#     # Remove any leading special tokens that might remain after skip_special_tokens=True
#     # (e.g., if the model started with a rogue <s>)
#     if answer.startswith("<s>"):
#         answer = answer[3:].strip() # "<s>" is 3 characters

#     # Remove any trailing special tokens or chat tags
#     trailing_tags = ["<|endoftext|>", "<|user|>", "<|assistant|>"]
#     for tag in trailing_tags:
#         if answer.endswith(tag):
#             answer = answer[:-len(tag)].strip()

#     # Post-processing: remove any potential leftover instruction phrases if the model repeats them
#     # For example, if the model starts with "Based on the context..."
#     common_start_phrases = [
#         "Based on the provided context, ",
#         "The context states that ",
#         "Based solely on the context, ",
#         "As per the context, ",
#         "According to the context, ",
        
#     ]
#     for phrase in common_start_phrases:
#         if answer.lower().startswith(phrase.lower()):
#             answer = answer[len(phrase):].strip()
#             # If a phrase is removed, re-check for other phrases that might now be at the start
#             # This handles cases like "Based on the context, The context states that..."
#             for sub_phrase in common_start_phrases:
#                 if answer.lower().startswith(sub_phrase.lower()):
#                     answer = answer[len(sub_phrase):].strip()
#             break # Break after finding and cleaning one main phrase

#     # TinyLlama sometimes generates extraneous newlines or spaces at the very start
#     answer = answer.lstrip('\n ').strip()

#     return answer.strip()

# # easycontext_cpu/infer_model.py
# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch, re, time

# MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
# model     = AutoModelForCausalLM.from_pretrained(MODEL_ID)
# model.eval()

# STOP_TOKENS = ["<|user|>", "<|assistant|>", "<|system|>", "</s>"]

# def build_prompt(context:str, query:str) -> str:
#     """Return a minimal, repetition-free prompt template."""
#     return (
#         "<|user|>\n"
#         "You are a helpful assistant.  Answer strictly from the context.\n\n"
#         f"Context:\n{context}\n\n"
#         f"Question:\n{query}\n"
#         "<|assistant|>\n"
#     )

# def clean_answer(txt:str) -> str:
#     """Remove trailing stop tokens, boiler-plate phrases, blank lines."""
#     # Strip stop tokens
#     for tok in STOP_TOKENS:
#         txt = txt.replace(tok, " ")
#     txt = re.sub(r"\s+", " ", txt).strip()

#     # Optional: cut generic sentence prefixes
#     boring = [
#         r"based (solely|entirely)? on the (provided )?context[, ]*",
#         r"according to the context[, ]*",
#         r"the context (states|says) that[, ]*",
#     ]
#     for pat in boring:
#         txt = re.sub("^" + pat, "", txt, flags=re.I).strip()

#     return txt

# def generate_answer(query, chunks, max_input_tokens=1536, return_debug=False):
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model.to(device)

#     context = "\n---\n".join(chunks)
#     prompt  = build_prompt(context, query)

#     inputs  = tokenizer(prompt, return_tensors="pt",
#                         truncation=True, max_length=max_input_tokens).to(device)
#     inp_len = inputs["input_ids"].shape[1]

#     t0 = time.time()
#     outputs = model.generate(
#         **inputs,
#         max_new_tokens=300,
#         repetition_penalty=1.2,
#         temperature=0.7,
#         top_p=0.9,
#         do_sample=True,             # greedy = fewer rambles
#         eos_token_id=tokenizer.eos_token_id,
#         pad_token_id=tokenizer.eos_token_id,
#         stopping_criteria=None,
#     )
#     elapsed = time.time() - t0

#     generated = tokenizer.decode(outputs[0][inp_len:], skip_special_tokens=True)
#     answer    = clean_answer(generated)

#     if return_debug:
#         full_raw = tokenizer.decode(outputs[0], skip_special_tokens=False)
#         return answer, prompt, full_raw, elapsed
#     return answer

# easycontext_cpu/infer_model.py
# from transformers import AutoTokenizer, AutoModelForCausalLM
import torch, re, time
import ollama

# MODEL_ID = "microsoft/phi-2"  # ✅ Updated model

# # Load tokenizer and model
# print("🔄 Loading Phi-2 model (this may take a while on CPU)...")
# tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
# model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
# model.eval()

STOP_TOKENS = ["<|user|>", "<|assistant|>", "<|system|>", "</s>"]

def build_prompt(context: str, query: str) -> str:
    return (
        "You are a helpful assistant. Answer strictly using the following context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{query}\n\nAnswer:"
    )

def clean_answer(txt: str) -> str:
    for tok in STOP_TOKENS:
        txt = txt.replace(tok, " ")
    txt = re.sub(r"\s+", " ", txt).strip()

    boring = [
        r"based (solely|entirely)? on the (provided )?context[, ]*",
        r"according to the context[, ]*",
        r"the context (states|says) that[, ]*",
    ]
    for pat in boring:
        txt = re.sub("^" + pat, "", txt, flags=re.I).strip()

    return txt
def generate_answer(query, chunks, return_debug=False):
    context = "\n---\n".join(chunks)
    prompt = build_prompt(context, query)

    t0 = time.time()

    try:
        print("Calling Ollama model...")
        response = ollama.chat(
            model='phi',  # ensure this matches your local Ollama model name exactly
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 350
            }
        )
        raw_output = response['message']['content']
        answer = clean_answer(raw_output)
        elapsed = time.time() - t0
        print(f"Ollama call done in {elapsed:.2f}s")

        if return_debug:
            return answer, prompt, raw_output, elapsed
        return answer

    except Exception as e:
        print("Error calling Ollama:", e)
        if return_debug:
            return "ERROR", prompt, str(e), 0.0
        return 'ERROR'
