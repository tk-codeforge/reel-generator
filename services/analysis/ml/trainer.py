import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# ── Ensure folders exist ─────────────────────────────────────────
os.makedirs("models", exist_ok=True)

# ── Load dataset ────────────────────────────────────────────────
DATA_PATH = "data/training_data.csv"

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(
        "❌ training_data.csv not found. Run Pattern Finder first."
    )

df = pd.read_csv(DATA_PATH)

if df.empty:
    raise ValueError("❌ Dataset is empty.")

print(f"✅ Loaded dataset with {len(df)} rows")

# ── Feature Engineering ─────────────────────────────────────────
df["length"] = df["text"].astype(str).apply(len)

X = df[["position", "length", "engagement"]]
y = df["label"]

# ── Train/Test Split ────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Train Model ─────────────────────────────────────────────────
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ── Evaluate ────────────────────────────────────────────────────
accuracy = model.score(X_test, y_test)
print(f"🎯 Model Accuracy: {accuracy:.2f}")

# ── Save Model ──────────────────────────────────────────────────
MODEL_PATH = "models/viral_model.pkl"
joblib.dump(model, MODEL_PATH)

print(f"✅ Model saved at {MODEL_PATH}")