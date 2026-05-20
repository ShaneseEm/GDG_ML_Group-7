import os


def get_dataset_stats(dataset_dir):
    stats = {}
    if not os.path.isdir(dataset_dir):
        return stats

    for label in sorted(os.listdir(dataset_dir)):
        label_dir = os.path.join(dataset_dir, label)
        if not os.path.isdir(label_dir):
            continue

        files = [
            f for f in os.listdir(label_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        stats[label] = len(files)

    return stats
