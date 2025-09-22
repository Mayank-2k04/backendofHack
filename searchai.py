from geopy.distance import geodesic
from PIL import Image
import imagehash
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


def calculate_distance(coords1, coords2):
    """
    Calculates the distance in kilometers between two sets of coordinates.
    """
    if not all(coords1) or not all(coords2):
        return float('inf')  # Return a large distance if coordinates are invalid
    return geodesic(coords1, coords2).kilometers


import requests
from io import BytesIO



def calculate_image_similarity(img1_path, img2_path):
    """
    Calculates the similarity between two images based on perceptual hash.
    Can handle local paths or URLs.
    Returns a similarity score between 0 and 1.
    """
    def open_image(path):
        if path.startswith("http://") or path.startswith("https://"):
            response = requests.get(path)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        else:
            return Image.open(path)

    try:
        img1 = open_image(img1_path)
        img2 = open_image(img2_path)

        hash1 = imagehash.phash(img1)
        hash2 = imagehash.phash(img2)
        max_hash_diff = len(hash1.hash)
        return 1.0 - (hash1 - hash2) / max_hash_diff

    except Exception as e:
        print(f"Warning: Could not calculate image similarity. Error: {e}")
        return 0.0

def calculate_text_similarity_semantic(text1, text2):
    """
    Calculates semantic similarity between two texts using sentence-transformers.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    if not text1 or not text2:
        return 0.0
    embeddings = model.encode([text1, text2])
    return float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])


# --- Main Matching Logic ---

def find_matches_for_lost_items(
    lost_items,
    found_items,
    max_distance_km=10,
    min_combined_score=0.6,
    weight_distance=0.3,
    weight_image=0.4,
    weight_text=0.3
):
    """
    For each lost item, finds the best matches from found items.
    Returns a dictionary keyed by lost item ID.
    """
    all_matches = {}

    if not lost_items or not found_items:
        return {"status": "No items provided for matching."}

    for lost_item in lost_items:
        potential_matches = []

        for found_item in found_items:
            # 1. Distance check
            distance = calculate_distance(
                (lost_item['latitude'], lost_item['longitude']),
                (found_item['latitude'], found_item['longitude'])
            )

            if distance <= max_distance_km:
                # 2. Image similarity
                image_similarity = 0.0
                if lost_item.get('image_url') and found_item.get('image_url'):
                    image_similarity = calculate_image_similarity(lost_item['image_url'], found_item['image_url'])

                # 3. Text similarity
                text_similarity = calculate_text_similarity_semantic(
                    lost_item.get('description', ''),
                    found_item.get('description', '')
                )

                # 4. Combined score
                distance_score = 1 - (distance / max_distance_km)
                combined_score = (
                    distance_score * weight_distance +
                    image_similarity * weight_image +
                    text_similarity * weight_text
                )

                if combined_score >= min_combined_score:
                    potential_matches.append({
                        'found_item': found_item,
                        'combined_score': round(combined_score, 2),
                        'details': {
                            'distance_km': round(distance, 2),
                            'image_similarity': round(image_similarity, 2),
                            'text_similarity': round(text_similarity, 2)
                        }
                    })

        potential_matches.sort(key=lambda x: x['combined_score'], reverse=True)
        lost_item_key = lost_item.get('id', lost_item.get('_id', 'unknown'))

        if potential_matches:
            all_matches[lost_item_key] = potential_matches
        else:
            all_matches[lost_item_key] = "No accurate match found."

    return all_matches
