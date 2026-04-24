import os
import cv2

DATA_DIR = './data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

number_of_classes = 26

START_INDEX = 100
END_INDEX = 200

cap = cv2.VideoCapture(0)
start_class = 0

for j in range(start_class, start_class + number_of_classes):
    class_dir = os.path.join(DATA_DIR, str(j))
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)

    print('Collecting data for class {}'.format(j))

    # Tunggu user siap
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.putText(
            frame,
            'Press Q to start',
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        cv2.imshow('frame', frame)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    counter = START_INDEX

    while counter < END_INDEX:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow('frame', frame)
        cv2.waitKey(25)  

        save_path = os.path.join(class_dir, f'{counter}.jpg')
        cv2.imwrite(save_path, frame)

        counter += 1

cap.release()
cv2.destroyAllWindows()