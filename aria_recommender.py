# aria_recommender.py — Terminal-Ready Collaborative Filter

from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split
from surprise import accuracy
import pandas as pd

# 1. Sample data — swap this with your real dataset later
data_dict = {
    'item': ['AI_Startup', 'Vision_Model', 'QuantumHack', 'Helo_Core', 'DreamNet'],
    'user': ['kiwon', 'ari', 'kiwon', 'ari', 'kiwon'],
    'rating': [5, 4, 4, 3, 5]
}

df = pd.DataFrame(data_dict)
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(df[['user', 'item', 'rating']], reader)

# 2. Train/test split
trainset, testset = train_test_split(data, test_size=0.2)

# 3. Model — User-based collaborative filter
algo = KNNBasic(sim_options={'user_based': True})
algo.fit(trainset)

# 4. Predictions + accuracy
predictions = algo.test(testset)
rmse = accuracy.rmse(predictions)

# 5. Recommend for ARIA
print("🧠 ARIA's Recommendations:")
items = ['AI_Startup', 'Vision_Model', 'QuantumHack', 'Helo_Core', 'DreamNet']
for item in items:
    pred = algo.predict('ari', item)
    print(f"→ {item}: predicted rating = {pred.est:.2f}")
