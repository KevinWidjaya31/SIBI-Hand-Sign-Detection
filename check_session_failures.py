"""
check_session_failures.py - Check if failures are concentrated in session 1 (0-99)
"""
import os
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

DATA_DIR = './data'

session1_total = 0  # images 0-99
session1_fail = 0
session2_total = 0  # images 100-199
session2_fail = 0

for dir_ in sorted(os.listdir(DATA_DIR), key=lambda x: int(x)):
    class_dir = os.path.join(DATA_DIR, dir_)
    if not os.path.isdir(class_dir):
        continue

    for img_name in os.listdir(class_dir):
        img_path = os.path.join(class_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue

        # Get image index from filename (e.g., "45.jpg" -> 45)
        idx = int(os.path.splitext(img_name)[0])

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        detected = results.multi_hand_landmarks is not None

        if idx < 100:
            session1_total += 1
            if not detected:
                session1_fail += 1
        else:
            session2_total += 1
            if not detected:
                session2_fail += 1

print("Session 1 (images 0-99, OLD code with edge detection):")
print(f"  Total: {session1_total}, Failed: {session1_fail}, "
      f"Rate: {session1_fail/max(1,session1_total)*100:.1f}%")

print(f"\nSession 2 (images 100-199, NEW code, raw frames):")
print(f"  Total: {session2_total}, Failed: {session2_fail}, "
      f"Rate: {session2_fail/max(1,session2_total)*100:.1f}%")

print(f"\nConclusion:")
if session1_fail > session2_fail * 2:
    print("  -> Session 1 (edge-processed) has MUCH more failures!")
    print("  -> Solution: Re-collect images 0-99 with the new collect_imgs.py")
else:
    print("  -> Failures are spread across both sessions")
    print("  -> Solution: Lower min_detection_confidence or re-collect data")
