import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import string
import warnings
warnings.filterwarnings("ignore")

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)
from sklearn.pipeline import Pipeline


nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)



def load_data(filepath: str = "spam.csv") -> pd.DataFrame:
    """
    Load the UCI SMS Spam Collection dataset.
    Expected columns: 'v1' (label: ham/spam), 'v2' (message text).
    Download from: https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset
    """
    df = pd.read_csv(filepath, encoding="latin-1")[["v1", "v2"]]
    df.columns = ["label", "message"]
    df["label_enc"] = df["label"].map({"ham": 0, "spam": 1})
    print(f"Dataset loaded: {df.shape[0]} rows")
    print(df["label"].value_counts(), "\n")
    return df



stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))


def preprocess_text(text: str) -> str:
    """Lowercase → remove punctuation/numbers → tokenize → remove stopwords → stem."""
    text = text.lower()
    text = re.sub(r"\d+", "", text)                         
    text = text.translate(str.maketrans("", "", string.punctuation))  
    tokens = text.split()
    tokens = [stemmer.stem(t) for t in tokens if t not in stop_words and len(t) > 1]
    return " ".join(tokens)


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["clean_message"] = df["message"].apply(preprocess_text)
    return df



def split_data(df: pd.DataFrame):
    X = df["clean_message"]
    y = df["label_enc"]
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)



def build_pipelines() -> dict:
    tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))

    pipelines = {
        "Naive Bayes": Pipeline([
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ("clf",   MultinomialNB()),
        ]),
        "Logistic Regression": Pipeline([
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ("clf",   LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs")),
        ]),
        "SVM": Pipeline([
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ("clf",   LinearSVC(C=1.0, max_iter=2000)),
        ]),
    }
    return pipelines


def evaluate(name: str, pipeline, X_train, X_test, y_train, y_test) -> dict:
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    metrics = {
        "Model":     name,
        "Accuracy":  round(accuracy_score(y_test, y_pred)  * 100, 2),
        "Precision": round(precision_score(y_test, y_pred) * 100, 2),
        "Recall":    round(recall_score(y_test, y_pred)    * 100, 2),
        "F1 Score":  round(f1_score(y_test, y_pred)        * 100, 2),
    }

    print(f"\n{'='*45}")
    print(f"  {name}")
    print(f"{'='*45}")
    print(classification_report(y_test, y_pred, target_names=["Ham", "Spam"]))

    return metrics, pipeline, y_pred



def plot_label_distribution(df: pd.DataFrame):
    counts = df["label"].value_counts()
    plt.figure(figsize=(5, 4))
    sns.barplot(x=counts.index, y=counts.values, palette=["steelblue", "tomato"])
    plt.title("Label Distribution (Ham vs Spam)")
    plt.ylabel("Count")
    plt.xlabel("Label")
    plt.tight_layout()
    plt.savefig("label_distribution.png", dpi=150)
    plt.show()
    print("Saved: label_distribution.png")


def plot_confusion_matrix(y_test, y_pred, title: str):
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Ham", "Spam"],
                yticklabels=["Ham", "Spam"])
    plt.title(f"Confusion Matrix – {title}")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    plt.tight_layout()
    fname = f"cm_{title.lower().replace(' ', '_')}.png"
    plt.savefig(fname, dpi=150)
    plt.show()
    print(f"Saved: {fname}")


def plot_model_comparison(results: list[dict]):
    df_res = pd.DataFrame(results).set_index("Model")
    df_res.plot(kind="bar", figsize=(9, 5), colormap="Set2", edgecolor="black")
    plt.title("Model Comparison")
    plt.ylabel("Score (%)")
    plt.ylim(85, 102)
    plt.xticks(rotation=15)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig("model_comparison.png", dpi=150)
    plt.show()
    print("Saved: model_comparison.png")


def plot_top_spam_keywords(pipeline, n: int = 20):
    """Visualize top TF-IDF features for the spam class (works with Logistic Regression)."""
    try:
        vectorizer = pipeline.named_steps["tfidf"]
        clf        = pipeline.named_steps["clf"]
        feature_names = np.array(vectorizer.get_feature_names_out())

       
        coef = clf.coef_[0] if hasattr(clf, "coef_") else None
        if coef is None:
            print("Keyword visualization only supported for Logistic Regression / SVM.")
            return

        top_idx   = np.argsort(coef)[-n:]
        top_words = feature_names[top_idx]
        top_vals  = coef[top_idx]

        plt.figure(figsize=(9, 6))
        sns.barplot(x=top_vals, y=top_words, palette="Reds_r")
        plt.title(f"Top {n} Spam-Indicating Keywords (Logistic Regression)")
        plt.xlabel("TF-IDF Weight")
        plt.tight_layout()
        plt.savefig("spam_keywords.png", dpi=150)
        plt.show()
        print("Saved: spam_keywords.png")
    except Exception as e:
        print(f"Could not plot keywords: {e}")



def classify_email(text: str, pipeline) -> str:
    """Classify a single email/SMS as Spam or Ham."""
    clean = preprocess_text(text)
    pred  = pipeline.predict([clean])[0]
    label = "🚨 SPAM" if pred == 1 else "✅ HAM (Legitimate)"
    print(f"\nInput : {text}")
    print(f"Result: {label}")
    return label



def main():
    
    df = load_data("spam.csv")          
    df = preprocess_dataframe(df)
    plot_label_distribution(df)


    X_train, X_test, y_train, y_test = split_data(df)

  
    pipelines = build_pipelines()
    results   = []
    trained   = {}

    for name, pipe in pipelines.items():
        metrics, trained_pipe, y_pred = evaluate(name, pipe, X_train, X_test, y_train, y_test)
        results.append(metrics)
        trained[name] = (trained_pipe, y_pred)


    summary = pd.DataFrame(results)
    print("\n" + "="*55)
    print("  SUMMARY")
    print("="*55)
    print(summary.to_string(index=False))

    
    plot_model_comparison(results)

    for name, (pipe, y_pred) in trained.items():
        plot_confusion_matrix(y_test, y_pred, name)

   
    plot_top_spam_keywords(trained["Logistic Regression"][0])

    
    best_name = max(results, key=lambda r: r["F1 Score"])["Model"]
    best_pipe  = trained[best_name][0]
    print(f"\nBest model by F1: {best_name}")


    sample_emails = [
        "Congratulations! You've won a FREE iPhone. Click here to claim NOW!!!",
        "Hey, are we still on for lunch tomorrow?",
        "URGENT: Your bank account has been compromised. Verify immediately.",
        "Just checking in to see how the project is going.",
        "Win £1000 cash! Text WIN to 80800 now. T&Cs apply.",
    ]

    print("\n--- Real-time Classification Demo ---")
    for email in sample_emails:
        classify_email(email, best_pipe)


if __name__ == "__main__":
    main()