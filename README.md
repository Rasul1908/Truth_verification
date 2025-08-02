
---

## 🔍 Objective

To develop a voice-based binary classifier that distinguishes **deceptive** speech from **truthful** speech using audio features and machine learning models.

---

##  Pipeline Overview

###  Step 1: Audio Segmentation
Original recordings are sliced into **30-second segments** and saved to `/segmented`. Metadata is recorded in `segment_metadata_enriched.csv`.

###  Step 2: Feature Extraction
Each audio segment is processed to extract features such as:
- MFCCs
- Chroma
- Spectral centroid/rolloff
- Zero crossing rate

Optional **data augmentation** (pitch/time) is applied during training.

###  Step 3: Feature Selection
CatBoost’s built-in feature importance helps rank extracted features. The **top 35** are retained for training the final model.

###  Step 4: Preprocessing
- Features are standardized using `StandardScaler`.
- Separate train/test splits are handled via metadata.

###  Step 5: Model Training
An ensemble classifier is trained with **soft voting** using the following models:
- `CatBoostClassifier`
- `KNeighborsClassifier (k=2)`
- `MLPClassifier (1 layer, 64 units)`

Final weights:  
`CatBoost: 2.0`, `KNN: 1.0`, `MLP: 1.2`

###  Step 6: Evaluation

On a test set of 67 samples:
- **Accuracy:** `0.6418`
- **F1 Score:** `0.6667`

| Class       | Precision | Recall | F1 Score |
|-------------|-----------|--------|----------|
| Deceptive   | 0.61      | 0.61   | 0.61     |
| Truthful    | 0.67      | 0.67   | 0.67     |

---

##  Inference on New Audio

You can use the trained model (`best_voting_model.pkl`) for predicting a new audio file:

```python
features = extract_features("test_unit.wav", augment=False)[0]
feature_names = [f"f{i+1}" for i in range(len(features))]
df = pd.DataFrame([features], columns=feature_names)
X_input = df[top_features].values

model = joblib.load("best_voting_model.pkl")
prediction = model.predict(X_input)[0]
print("Prediction:", prediction)
"# Truth_verification" 
