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
                    "content": "You are evaluating feedback from a coding school. Constructive feedback typically identifies specific strengths and areas for improvement, offers concrete suggestions, and encourages positive development. Feedback that lacks detail, does not relate to specific actions, or fails to offer guidance for improvement is less constructive. One exception is when the student pushed an empty repository/empty folder - Please rate this with -1 so I can filter them out.Your task is to rate feedback based on its constructiveness.",
                },
                {
                    "role": "user",
                    "content": f"{text}; Considering the criteria for constructive feedback, rate this 42 Coding School evaluation feedback on a scale from 0 (completely out of place and not helpful) to 9 (very constructive, offering specific, actionable, and encouraging guidance). Only provide a number from 0 to 9. Be strict in your evaluation; the goal here is to identify feedback that genuinely contributes to improvement. Remember, a '9' should be reserved for feedback that is exemplary in specificity, helpfulness, and encouragement, while a '0' indicates feedback that is not applicable or useful for development.",
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
