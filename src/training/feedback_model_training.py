from transformers import BertModel
from transformers import BertTokenizer
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import pandas as pd


class FeedbackDataset(Dataset):
    def __init__(self, filepath: str, max_len=512):
        self.df = pd.read_csv(filepath)
        self.df = self.df.dropna(subset=["label"])
        self.df["label"] = self.df["label"].astype(int)
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.max_len = max_len

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        text = self.df.iloc[index, 0]
        label = self.df.iloc[index, 1]
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding="max_length",
            return_attention_mask=True,
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(label, dtype=torch.long),
        }


class BertClassifier(nn.Module):
    def __init__(self, bert_model, num_labels):
        super(BertClassifier, self).__init__()
        self.bert = bert_model
        self.classifier = nn.Linear(768, num_labels)

    def forward(self, input_ids, attention_mask=None):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)

        pooled_output = outputs.pooler_output

        logits = self.classifier(pooled_output)

        return logits


class Trainer:
    def __init__(self, pre_trained_model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.init_model(pre_trained_model_path)
        pass

    def init_model(self, pre_trained_model_path=None):
        bert_model = BertModel.from_pretrained("bert-base-uncased")
        self.model = BertClassifier(bert_model, num_labels=5).to(self.device)

        if pre_trained_model_path is not None:
            self.model.load_state_dict(
                torch.load(pre_trained_model_path, map_location=self.device)
            )
            print(f"loaded model weights from {pre_trained_model_path}")

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(self.model.parameters(), lr=2e-5)

        train_dataset = FeedbackDataset(
            "src/training/training_data/feedback_training.csv"
        )
        test_dataset = FeedbackDataset("src/training/training_data/feedback_test.csv")

        train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=16)

        for epoch in range(3):
            self.train(train_loader, optimizer, criterion)
            self.evaluate(test_loader, criterion)
        self.save_model()

    def train(self, train_loader, optimizer, criterion):
        self.model.train()
        total_loss = 0
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["labels"].to(self.device)
            outputs = self.model(input_ids, attention_mask=attention_mask)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Training loss: {total_loss / len(train_loader)}")

    def evaluate(self, test_loader, criterion):
        self.model.eval()
        total_loss = 0
        total_acc = 0
        for batch in test_loader:
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["labels"].to(self.device)
            outputs = self.model(input_ids, attention_mask=attention_mask)
            loss = criterion(outputs, labels)
            total_loss += loss.item()
            predictions = torch.argmax(outputs, dim=1)
            total_acc += (predictions == labels).sum().item()
        print(
            f"Test loss: {total_loss / len(test_loader)}, Test acc: {total_acc / len(test_loader.dataset) * 100}%"
        )

    def save_model(
        self, save_path="src/training/models/feedback_analysis_finetuned_BERT"
    ):
        torch.save(self.model.state_dict(), save_path)
        print(f"Model saved to {save_path}")


Trainer("src/training/models/feedback_analysis_finetuned_BERT")
