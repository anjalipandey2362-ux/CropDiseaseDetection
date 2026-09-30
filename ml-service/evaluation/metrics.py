from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

def calculate_metrics(y_true, y_pred, target_names=None):
    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average='weighted', zero_division=0
    )
    
    report_text = classification_report(
        y_true, y_pred, target_names=target_names, zero_division=0
    )

    metrics_dict = {
        "accuracy": float(acc),
        "precision_weighted": float(precision),
        "recall_weighted": float(recall),
        "f1_score_weighted": float(f1)
    }

    return metrics_dict, report_text
