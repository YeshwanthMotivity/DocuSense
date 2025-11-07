import re
import time
import ollama
import logging
from abc import ABC, abstractmethod

# Configure logging for enhanced error handling
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

# Configuration for Ollama Model ID (global constant)
OLLAMA_MODEL_ID = "phi" # Default Ollama model ID, can be overridden during instantiation

# Configurable Prompt Template (global constant)
DEFAULT_PROMPT_TEMPLATE = (
    "You are a helpful assistant. Answer strictly using the following context.\n\n"
    "Context:\n{context}\n\n"
    "Question:\n{query}\n\nAnswer:"
)

# Stop tokens used for cleaning model output, typically specific to chat models
# These are internal to the cleaning logic, not passed directly to Ollama.
_STOP_TOKENS = ["<|user|>", "<|assistant|>", "<|system|>", "</s>"]

class LLMInferenceEngine(ABC):
    """
    Abstract Base Class for various Large Language Model (LLM) inference engines.
    Defines a common interface for generating answers and handling prompt/output logic.
    """

    def __init__(self, prompt_template: str = DEFAULT_PROMPT_TEMPLATE):
        """
        Initializes the LLMInferenceEngine with a configurable prompt template.
        """
        self.prompt_template = prompt_template

    @abstractmethod
    def generate_answer(self, query: str, chunks: list[str], return_debug: bool = False) -> tuple | str:
        """
        Generates an answer to a query based on provided context chunks.

        :param query: The user's question.
        :param chunks: A list of relevant text chunks to use as context.
        :param return_debug: If True, returns additional debug information (answer, prompt, raw_output, elapsed_time).
        :return: The generated answer string, or a tuple if return_debug is True.
                 Returns 'ERROR' or logs exceptions on failure.
        """
        pass

    def _build_prompt(self, context: str, query: str) -> str:
        """
        Builds the prompt string using the configured template.
        This method formats the template with the given context and query.
        """
        try:
            return self.prompt_template.format(context=context, query=query)
        except KeyError as e:
            logging.error(f"Prompt template missing expected key: {e}", exc_info=True)
            raise ValueError(f"Prompt template must contain {{context}} and {{query}} placeholders.") from e

    def _clean_answer(self, txt: str) -> str:
        """
        Removes trailing stop tokens, boilerplate phrases, and cleans whitespace
        from the raw LLM output.
        """
        # Strip stop tokens that might be generated
        for tok in _STOP_TOKENS:
            txt = txt.replace(tok, " ")
        txt = re.sub(r"\s+", " ", txt).strip()

        # Optional: cut generic sentence prefixes that models sometimes generate
        boring_patterns = [
            r"based (solely|entirely)? on the (provided )?context[, ]*",
            r"according to the context[, ]*",
            r"the context (states|says) that[, ]*",
            r"based on the context information, ",
            r"based on the context, "
        ]
        for pat in boring_patterns:
            txt = re.sub("^" + pat, "", txt, flags=re.IGNORECASE).strip()

        return txt

class OllamaInferenceEngine(LLMInferenceEngine):
    """
    Concrete implementation of LLMInferenceEngine for interacting with Ollama models.
    """
    def __init__(self, model_id: str = OLLAMA_MODEL_ID, prompt_template: str = DEFAULT_PROMPT_TEMPLATE):
        """
        Initializes the OllamaInferenceEngine.

        :param model_id: The ID of the Ollama model to use (e.g., "phi", "llama2").
        :param prompt_template: The string template for building the prompt.
        """
        super().__init__(prompt_template=prompt_template)
        self.model_id = model_id
        logging.info(f"OllamaInferenceEngine initialized for model: '{self.model_id}'")

    def generate_answer(self, query: str, chunks: list[str], return_debug: bool = False) -> tuple | str:
        """
        Generates an answer using the configured Ollama model.
        """
        context = "\n---\n".join(chunks)
        prompt = self._build_prompt(context, query)

        t0 = time.time()

        try:
            logging.debug(f"Calling Ollama model '{self.model_id}' with prompt: \n{prompt}")
            response = ollama.chat(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 350 # Max tokens to generate
                }
            )
            raw_output = response['message']['content']
            answer = self._clean_answer(raw_output)
            elapsed = time.time() - t0
            logging.debug(f"Ollama call done in {elapsed:.2f}s for model '{self.model_id}'")

            if return_debug:
                return answer, prompt, raw_output, elapsed
            return answer

        except ollama.ResponseError as e:
            # Specific error from Ollama API (e.g., model not found, server down)
            logging.error(f"Ollama API error with model '{self.model_id}': {e}", exc_info=True)
            if return_debug:
                return "ERROR: Ollama API", prompt, str(e), 0.0
            return 'ERROR'
        except Exception as e:
            # Catch any other unexpected errors during inference
            logging.error(f"An unexpected error occurred during Ollama inference for model '{self.model_id}': {e}", exc_info=True)
            if return_debug:
                return "ERROR: General Inference", prompt, str(e), 0.0
            return 'ERROR'

# Example usage (can be put in a separate main/test file)
# if __name__ == "__main__":
#     # Initialize the inference engine
#     ollama_engine = OllamaInferenceEngine(model_id="phi") # Using the default 'phi' model
#
#     # Example data
#     test_query = "What is the capital of France?"
#     test_chunks = [
#         "France is a country in Western Europe. Its capital city is Paris.",
#         "Paris is known for its Eiffel Tower and Louvre Museum."
#     ]
#
#     # Generate answer without debug info
#     answer = ollama_engine.generate_answer(test_query, test_chunks)
#     print("\n--- Answer (non-debug) ---")
#     print(answer)
#
#     # Generate answer with debug info
#     answer_debug, prompt_sent, raw_output, time_taken = ollama_engine.generate_answer(test_query, test_chunks, return_debug=True)
#     print("\n--- Answer (debug) ---")
#     print(f"Cleaned Answer: {answer_debug}")
#     print(f"Prompt Sent:\n{prompt_sent}")
#     print(f"Raw Model Output:\n{raw_output}")
#     print(f"Time Taken: {time_taken:.2f} seconds")
#
#     # Test with custom prompt template
#     custom_template = (
#         "Please provide a concise answer to the following question, "
#         "drawing only from the provided information:\n\n"
#         "Information:\n{context}\n\n"
#         "Question: {query}\n\nResponse:"
#     )
#     custom_ollama_engine = OllamaInferenceEngine(model_id="llama2", prompt_template=custom_template)
#     custom_answer = custom_ollama_engine.generate_answer("What is a LLM?", ["A Large Language Model (LLM) is a type of AI program that can recognize and generate text."])
#     print("\n--- Custom Prompt Answer ---")
#     print(custom_answer)
#
#     # Test error handling (e.g., with a non-existent model)
#     error_engine = OllamaInferenceEngine(model_id="nonexistent-model-123")
#     error_result = error_engine.generate_answer("What?", ["Context."], return_debug=True)
#     print("\n--- Error Handling Test ---")
#     print(f"Error Result: {error_result}")
#
#     # Test with an empty context/query to see how it handles it (might be model-dependent behavior)
#     empty_context_answer = ollama_engine.generate_answer("What is the main topic?", [], return_debug=True)
#     print("\n--- Empty Context Test ---")
#     print(empty_context_answer)