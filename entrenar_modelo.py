import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

ARCHIVO_CSV = "dataset_keypoints.csv"
ARCHIVO_MODELO = "modelo_senas.pkl"

if not os.path.exists(ARCHIVO_CSV):
    print(f"Error: no encontré '{ARCHIVO_CSV}' en esta carpeta.")
    print("Asegúrate de ejecutar este script en la misma carpeta donde corriste 'recolectar_datos.py'.")
    exit()

# 1. Cargar los datos recolectados
datos = pd.read_csv(ARCHIVO_CSV)
print(f"Total de muestras cargadas: {len(datos)}")
print(f"Letras encontradas: {sorted(datos['letra'].unique())}\n")

# 2. Separar características (las coordenadas) de la etiqueta (la letra)
X = datos.drop("letra", axis=1)
y = datos["letra"]

# 3. Dividir en datos de entrenamiento (80%) y de prueba (20%)
#    Los de prueba NO se usan para enseñar, solo para examinar al final
X_entrenamiento, X_prueba, y_entrenamiento, y_prueba = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 4. Crear y entrenar el modelo
print("Entrenando modelo, esto puede tardar unos segundos...")
modelo = RandomForestClassifier(n_estimators=200, random_state=42)
modelo.fit(X_entrenamiento, y_entrenamiento)

# 5. Evaluar qué tan bien aprendió usando los datos de prueba
predicciones = modelo.predict(X_prueba)
precision = accuracy_score(y_prueba, predicciones)

print(f"\n=== RESULTADOS ===")
print(f"Precisión del modelo: {precision * 100:.2f}%")
print("\nDetalle por letra:")
print(classification_report(y_prueba, predicciones))

# 6. Guardar el modelo entrenado para usarlo después
joblib.dump(modelo, ARCHIVO_MODELO)
print(f"Modelo guardado en: {os.path.abspath(ARCHIVO_MODELO)}")
