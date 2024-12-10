import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


habitaciones = ['1', '2', '3', '4', '+4']


precios = np.random.randint(400, 4288, size=len(habitaciones))


data = pd.DataFrame({
    'Habitación': habitaciones,
    'Precio': precios
})


print(data)


plt.figure(figsize=(8, 5))
plt.bar(data['Habitación'], data['Precio'], color='black', alpha=0.5)
plt.title('Precios de las habitaciones en la inmobiliaria')
plt.xlabel('Tipo de Habitación')
plt.ylabel('Precio (€)')
plt.xticks(rotation=15)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()


plt.show()
