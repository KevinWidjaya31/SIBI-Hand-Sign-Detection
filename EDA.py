import os
import matplotlib.pyplot as plt

data_dir = "./data"

# Ambil daftar folder, lalu urutkan secara numerik
class_names = sorted(os.listdir(data_dir), key=lambda x: int(x))  # asumsikan nama folder adalah angka
class_counts = [len(os.listdir(os.path.join(data_dir, class_name))) for class_name in class_names]

plt.figure(figsize=(10,5))
plt.bar(class_names, class_counts)
plt.title("Distribusi Gambar per Kelas")
plt.xlabel("Kelas")
plt.ylabel("Jumlah Gambar")
plt.xticks(rotation=45)
plt.show()
