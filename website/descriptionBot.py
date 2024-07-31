import requests
import json

api_token = "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"  # Replace this with your actual token

# Set up the headers for the API request
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

def generate_marketing_content(product_details):
    model_name = "mistralai/Mistral-7B-Instruct-v0.3"
    prompt = f"Generate product description like scentance no formatting is needed for this: {product_details} in the following format: Title, Product Description, Specification, USP.!!!!!"

    # Prepare the payload for the API request
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 1000,
            "min_length": 200,
            "repetition_penalty": 1.2,
            "no_repeat_ngram_size": 3,
            "num_return_sequences": 1,
            "early_stopping": True,
        }
    }

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{model_name}",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code == 200:
        response_data = response.json()
        return response_data[0]["generated_text"]
    else:
        raise Exception(f"Request failed with status code {response.status_code}, response: {response.text}")
    

