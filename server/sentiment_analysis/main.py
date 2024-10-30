from transformers import pipeline
import torch
import re
from statistics import harmonic_mean

model = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
task = "sentiment-analysis"


def filter_garbage_batch(chat_batch):
    # add type checker for list n string
    messages = chat_batch.split('\n')
    preprocessed_messages = []

    for chat_message in messages:
        preprocessed_messages.append(filter_garbage(chat_message))

    return '\n'.join(preprocessed_messages)


def filter_garbage(chat_message):
    if len(chat_message.split("\n")) > 1:
        return filter_garbage_batch

    chat_message = re.sub(r'http\S+', '', chat_message)  # Remove URLs
    chat_message = re.sub(r'@\w+', '', chat_message) # Remove mentions
    chat_message = re.sub(r'[^\w\s]', '', chat_message) # removes any non character characters
    chat_message = re.sub(r'(.)\1{2,}', r'\1\1', chat_message) # makes things like noooooooo noo
    chat_message = chat_message.strip()
    return chat_message


def single_message_classification(chat_message):
    results = classifier(chat_message)[0]
    score_dict = {item['label']: item['score'] for item in results}
    return score_dict


def get_cum_score(chat_messages):
    cumulative_scores = {}
    for message in chat_messages:
        scores = single_message_classification(message)
        for label, score in scores.items():
            if label not in cumulative_scores:
                cumulative_scores[label] = []
            cumulative_scores[label].append(score)

    return cumulative_scores


def normalize(scores):
    total_score = sum(scores.values())
    normalized_scores = {label: score / total_score for label, score in scores.items()}
    return normalized_scores


def multiple_message_classification_avg(chat_messages):
    cumulative_scores = get_cum_score(chat_messages)
    avg_scores = {label: sum(scores) / len(scores) for label, scores in cumulative_scores.items()}
    return normalize(avg_scores)


def multiple_message_classification_harmonic_mean(chat_messages):
    cumulative_scores = get_cum_score(chat_messages)
    harmonic_mean_scores = {label: harmonic_mean(scores) for label, scores in cumulative_scores.items()}
    return normalize(harmonic_mean_scores)


if __name__ == '__main__':
    print(device)
    classifier = pipeline(task=task, model=model, top_k=None, device=device, use_fast=False)

    messages = [
        "nikogo jebany lewus nie interesuje",
        "wyłącz tego śmiecia lewusa",
        "mutuj lewusa",
        "aha co to za gówno",
        "nienawidze LEWUSA boze on jest taki cringe",
        "skip kurwa worlds'y sa",
        "wyłącz ten syf",
        "wyłącz"
    ]

    print(multiple_message_classification_harmonic_mean(messages))
