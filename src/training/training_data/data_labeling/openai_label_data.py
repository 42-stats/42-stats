import pandas as pd
import os
import dotenv
from openai import OpenAI

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

BATCH_SIZE = 20


def generate_text_labels_batch(texts):
    labels = []
    text_label_mapping = {}

    for text in texts:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You rate feedback based on constructivity",
                },
                {
                    "role": "user",
                    "content": f"{text}; Rate this 42 Coding School evaluation feedback on a scale from 0 (completely out of place) to 9 (very constructive) - Only give me a number from 0 to 9, nothing else! Remember to be strict, the goal here is to improve the feedbacks",
                },
            ],
        )
        label = response.choices[0].message.content
        labels.append(label)
        text_label_mapping[text] = label

    return labels, text_label_mapping


def generate_labels_for_dataframe(df, text_column_name):
    new_data = []
    batch_texts = []

    for index, row in df.iterrows():
        batch_texts.append(row[text_column_name])

        if len(batch_texts) == BATCH_SIZE:
            labels, _ = generate_text_labels_batch(batch_texts)
            new_data.extend(zip(batch_texts, labels))
            batch_texts = []

    if batch_texts:
        labels, _ = generate_text_labels_batch(batch_texts)
        new_data.extend(zip(batch_texts, labels))

    labels_df = pd.DataFrame(new_data, columns=["text", "label"])
    labels_df.to_csv("labeled_data.csv", index=False)


# df = pd.read_csv("src/training/training_data/data_labeling/vienna_all_eval_comments.csv")
df = pd.read_csv("src/training/training_data/data_labeling/test.csv")
generate_labels_for_dataframe(df, "comment")
