import json

import openai

def validate_context(value):
    """
    Validate the context of a question.

    Args:
        value (str): The context to validate.

    Returns:
        bool: True if the context is valid, False otherwise.
    """
    words = value.split()
    return len(words) <= 40


def get_secret_key():
    """
    Get the OpenAI API key from secrets.json.

    Returns:
        str: The OpenAI API key.
    """
    with open('secrets.json') as f:
        secrets = json.load(f)
    return secrets.get('OPENAI_KEY')


api_key = get_secret_key()
if api_key:
    openai.api_key = api_key


def ask_open_ai(context, question, model="gpt-3.5-turbo-16k"):
    """
    Ask a question to the OpenAI model.

    Args:
        context (str): The context to use for the question.
        question (str): The question to ask.
        model (str, optional): The OpenAI model to use. Defaults to "gpt-3.5-turbo-16k".

    Returns:
        str: The model's response to the question.
    """
    prompt = f'''using the context: {context}
answer the next question: {question} in maximum 150 words. 
If the answer is not related to the context, 
give the following answer: "The question is not related to the course". 
Provide your answer using the language used in the question.'''

    chat_messages = [{"role": "user", "content": prompt}]
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=chat_messages,
            temperature=0,
            max_tokens=300,
            n=1
        )
        answer = response.choices[0].message if response and response.choices else None
    except Exception as e:
        print(e)
        answer = None
        # Handle exceptions, such as logging errors or returning an error response to the user
    return answer if answer else "No response"
