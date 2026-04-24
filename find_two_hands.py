"""
find_two_hands.py - Find images where MediaPipe detects 2 hands
"""
import os
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

DATA_DIR = './data'
two_hand_images = []

for dir_ in sorted(os.listdir(DATA_DIR), key=lambda x: int(x)):
    class_dir = os.path.join(DATA_DIR, dir_)
    if not os.path.isdir(class_dir):
        continue
    for img_name in sorted(os.listdir(class_dir)):
        img_path = os.path.join(class_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        if results.multi_hand_landmarks:
            n_hands = len(results.multi_hand_landmarks)
            if n_hands > 1:
                letter = chr(int(dir_) + 65)
                two_hand_images.append((img_path, letter, n_hands))
                print(f"  [!] {n_hands} hands -> class {dir_} ({letter}) / {img_name}")

print(f"\nTotal images with 2+ hands: {len(two_hand_images)}")
if two_hand_images:
    print("\nFull paths:")
    for path, letter, n in two_hand_images:
        print(f"  {path}  (letter {letter}, {n} hands)")
else:
    print("All images have exactly 1 hand detected.")
