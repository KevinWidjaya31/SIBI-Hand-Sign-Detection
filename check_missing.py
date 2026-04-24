"""
check_missing.py - Find images where MediaPipe detected NO hand
"""
import os
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

DATA_DIR = './data'

total_images = 0
detected = 0
failed = 0
failed_per_class = {}

for dir_ in sorted(os.listdir(DATA_DIR), key=lambda x: int(x)):
    class_dir = os.path.join(DATA_DIR, dir_)
    if not os.path.isdir(class_dir):
        continue

    letter = chr(int(dir_) + 65)
    class_total = 0
    class_failed = 0
    failed_files = []

    for img_name in sorted(os.listdir(class_dir)):
        img_path = os.path.join(class_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue

        total_images += 1
        class_total += 1

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            detected += 1
        else:
            failed += 1
            class_failed += 1
            failed_files.append(img_name)

    failed_per_class[letter] = {
        "total": class_total,
        "failed": class_failed,
        "detected": class_total - class_failed,
        "files": failed_files
    }

    status = f"MISSING {class_failed}" if class_failed > 0 else "OK"
    print(f"  {letter}: {class_total} images, {class_total - class_failed} detected, "
          f"{class_failed} failed  [{status}]")

print(f"\n{'='*50}")
print(f"  Total images : {total_images}")
print(f"  Hand detected: {detected}")
print(f"  No hand found: {failed} ({failed/total_images*100:.1f}%)")
print(f"  In data.pickle: ~{detected} samples")

# Show worst classes
print(f"\nClasses with most failures:")
for letter, info in sorted(failed_per_class.items(), key=lambda x: -x[1]["failed"]):
    if info["failed"] > 0:
        print(f"  {letter}: {info['failed']}/{info['total']} failed "
              f"({info['failed']/info['total']*100:.0f}%)")
