import pickle
import pandas as pd

with open('./augmented_split.pickle', 'rb') as f:
    data_dict = pickle.load(f)

data = data_dict['data']
labels = data_dict['labels']

contoh_per_label = {}

for d, l in zip(data, labels):
    l_int = int(l) 
    if l_int not in contoh_per_label:
        contoh_per_label[l_int] = d

rows = []

for label, coordinates in contoh_per_label.items():
    rows.append({
        "Label (Angka)": label,
        "Alfabet": chr(label + 65),  
        "Jumlah Titik": len(coordinates),
        "Contoh Koordinat (5 pertama)": coordinates[:5]
    })

df = pd.DataFrame(rows)

df = df.sort_values("Label (Angka)").reset_index(drop=True)

print(df)