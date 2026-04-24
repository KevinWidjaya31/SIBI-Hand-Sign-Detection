# DATA DISIMPAN MENJADI KATA
import pickle
import cv2
import mediapipe as mp
import numpy as np
import time

# Load trained model
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

button_img = cv2.imread('./Kamus.jpg')
button_visible = False
kamus_window_open = False

def mouse_callback(event, x, y, flags, param):
    global button_visible
    if event == cv2.EVENT_LBUTTONDOWN:
        if 10 <= x <= 160 and frame.shape[0] - 60 <= y <= frame.shape[0] - 10:
            button_visible = not button_visible

cv2.namedWindow('Hand Gesture Recognition')
cv2.setMouseCallback('Hand Gesture Recognition', mouse_callback)


# Initialize camera
cap = cv2.VideoCapture(0)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.3)

# Define label dictionary
labels_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L',
               12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W',
               23: 'X', 24: 'Y', 25: 'Z'}

word = ""  # Menyimpan kata yang sedang dibentuk
last_character = None  # Menyimpan huruf terakhir untuk menghindari duplikasi
last_time = 0  # Menyimpan waktu terakhir huruf dimasukkan
delay = 1  # Delay dalam detik sebelum huruf baru bisa dimasukkan
add_character = False  # Flag untuk menambahkan karakter ke kata

while True:
    data_aux = []
    x_ = []
    y_ = []

    ret, frame = cap.read()
    if not ret:
        continue

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Tombol 'a' untuk memungkinkan penambahan karakter
    key = cv2.waitKey(1) & 0xFF
    if key == ord('a'):  # Tombol 'a' ditekan untuk mulai menambahkan karakter
        add_character = True
    elif key == ord('q'):  # Keluar
        break
    elif key == ord('r'):  # Reset kata
        word = ""
    elif key == ord(' '):  # Tambahkan spasi
        word += " "

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

        for hand_landmarks in results.multi_hand_landmarks:
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                x_.append(x)
                y_.append(y)

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

        x1 = int(min(x_) * W) - 10
        y1 = int(min(y_) * H) - 10
        x2 = int(max(x_) * W) - 10
        y2 = int(max(y_) * H) - 10

        # Perform prediction
        probabilities = model.predict_proba([np.asarray(data_aux)])
        max_index = np.argmax(probabilities)
        predicted_character = labels_dict[int(max_index)]

        current_time = time.time()
        if predicted_character != last_character and (current_time - last_time) > delay:
            last_character = predicted_character  # Update karakter terakhir
            last_time = current_time  # Update waktu terakhir

        confidence = probabilities[0][max_index] * 100  # Convert to percentage

        # Jika add_character aktif, tambahkan karakter ke kata
        if add_character:
            word += predicted_character
            add_character = False  # Reset flag setelah menambahkan karakter

        # Draw bounding box and label
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
        label_text = f'{predicted_character} ({confidence:.2f}%)'
        cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

    # Display the constructed word
    cv2.putText(frame, f'Word: {word}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3, cv2.LINE_AA)
    
    # Draw "Show Kamus" button - Improved
    button_color_top = (100, 100, 255)  # Biru kemerahan
    button_color_bottom = (50, 50, 150)

    for i in range(60):
        alpha = i / 60
        color = (
            int(button_color_top[0] * (1 - alpha) + button_color_bottom[0] * alpha),
            int(button_color_top[1] * (1 - alpha) + button_color_bottom[1] * alpha),
            int(button_color_top[2] * (1 - alpha) + button_color_bottom[2] * alpha)
        )
        cv2.line(frame, (10, frame.shape[0] - 80 + i), (200, frame.shape[0] - 80 + i), color, 1)

    cv2.rectangle(frame, (10, frame.shape[0] - 80), (200, frame.shape[0] - 20), (255, 255, 255), 2)
    cv2.putText(frame, 'Show Kamus', (25, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Tampilkan gambar kamus
    if button_visible and button_img is not None:
        if not kamus_window_open:
            cv2.imshow('Kamus', button_img)
            kamus_window_open = True

    # Deteksi jika window Kamus ditutup manual
    if kamus_window_open:
        try:
            # Coba resize window, kalau error berarti window sudah ditutup
            cv2.getWindowImageRect('Kamus')
        except:
            button_visible = False
            kamus_window_open = False

    cv2.imshow('Hand Gesture Recognition', frame)

cap.release()
cv2.destroyAllWindows()