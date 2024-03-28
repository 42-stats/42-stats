from openai import OpenAI
import pandas as pd
import dotenv
import os

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))


def generate_text_labels(text):
    labels = []
    text_label_mapping = {}

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You rate feedback based on constructivity",
            },
            {
                "role": "user",
                "content": f"{text}; Rate this 42 Coding School evaluation feedback on a scale from 0 (completely out of place) to 9 (very constructive) - Only give me a number from 0 to 9, nothing else!",
            },
        ],
    )
    label = response.choices[0].message.content
    labels.append(label)
    text_label_mapping[text] = label

    return labels, text_label_mapping


print(
    generate_text_labels(
        "Unfortunately, when the input command/file opening fails, the program completely skips the output command table, which is not the way bash behaves.\r\nA few commands were also not protected, other than that, the code is very nice and readable, no leaks and we had an extensive talk about the subject."
    )
)
