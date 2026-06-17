from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
paths = [
    '/health',
    '/api/v1/fooddb/health',
    '/api/v1/fooddb/foods/search?q=angel&limit=2',
    '/api/v1/fooddb/foods/resolve?q=Angelica',
    '/api/v1/fooddb/foods/1',
    '/api/v1/fooddb/foods/1/compounds?limit=2',
    '/api/v1/fooddb/compounds/search?q=quercetin&limit=2',
    '/api/v1/fooddb/compounds/11907',
    '/api/v1/fooddb/compounds/11907/foods?limit=2',
    '/api/v1/fooddb/compounds/11907/bio-links?limit_per_kind=2',
    '/api/v1/fooddb/foods/1/vector?policy=zscore',
    '/api/v1/fooddb/foods/compare?food_a=Angelica&food_b=Ginger&policy=zscore',
    '/api/v1/fooddb/foods/similar?q=Angelica&policy=zscore&top_k=2',
]
for path in paths:
    response = client.get(path)
    assert response.status_code == 200, f'{path} failed: {response.status_code} {response.text}'
    print(f'OK {path}')
print('FoodDB smoke test passed.')
