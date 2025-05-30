import os
import pandas as pd
import numpy as np
import chardet
import warnings
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor

warnings.filterwarnings("ignore")

# CSV 경로 설정 - 루트 폴더에 있는 CSV 파일들
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_csv_robust(filepath):
    """다양한 인코딩을 시도하여 CSV 파일을 안전하게 로드"""
    try:
        with open(filepath, 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)['encoding']
        return pd.read_csv(filepath, encoding=encoding, on_bad_lines='skip')
    except Exception as e:
        print(f"CSV 로드 실패 ({filepath}): {e}")
        # 기본 인코딩들로 재시도
        encodings = ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr', 'latin1']
        for enc in encodings:
            try:
                return pd.read_csv(filepath, encoding=enc, on_bad_lines='skip')
            except:
                continue
        raise Exception(f"모든 인코딩 시도 실패: {filepath}")

# 데이터 로드 - 루트 폴더에서 직접 로드
try:
    menus_df = load_csv_robust(os.path.join(BASE_DIR, "final_menus_data.csv"))
    restaurants_df = load_csv_robust(os.path.join(BASE_DIR, "restaurants.csv"))
    print(f"실제 CSV 데이터 로드 성공: 메뉴 {len(menus_df)}개, 레스토랑 {len(restaurants_df)}개")
except Exception as e:
    print(f"실제 CSV 데이터 로드 오류: {e}")
    print("더미 데이터로 대체합니다...")
    # 더미 데이터 생성 (테스트용)
    menus_df = pd.DataFrame({
        'menu_id': range(1, 101),
        'restaurant_id': np.random.randint(1, 21, 100),
        'menu_name': [f'메뉴_{i}' for i in range(1, 101)],
        'category': np.random.choice(['한식', '중식', '일식', '양식', '기타'], 100),
        'price': np.random.randint(5000, 20000, 100),
        'width': np.random.uniform(10, 25, 100),
        'length': np.random.uniform(10, 25, 100),
        'height': np.random.uniform(3, 10, 100),
        'popularity_score': np.random.uniform(1, 10, 100)
    })
    restaurants_df = pd.DataFrame({
        'restaurant_id': range(1, 21),
        'name': [f'레스토랑_{i}' for i in range(1, 21)]
    })
    print("더미 데이터로 대체됨")

class AdvancedFoodRecommendationAI:
    """
    고도화된 AI 기반 음식 추천 시스템
    - 다중 알고리즘 조합 (하이브리드 필터링)
    - 학습 기반 사용자 선호도 예측
    - 상황 인식 추천 (시간, 날씨, 계절)
    - 지속적 학습 시스템
    """
    
    def __init__(self, menus_df, restaurants_df, user_interactions_df=None):
        self.menus_df = menus_df.copy()
        self.restaurants_df = restaurants_df.copy()
        self.user_interactions_df = user_interactions_df if user_interactions_df is not None else pd.DataFrame()
        
        # 데이터 전처리
        self._preprocess_data()
        
        # AI 모델 컴포넌트들
        self.content_vectorizer = TfidfVectorizer(max_features=50, analyzer='char', ngram_range=(1, 3))
        self.size_scaler = StandardScaler()
        self.preference_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.popularity_scaler = MinMaxScaler()
        
        # 상황 인식을 위한 가중치
        self.contextual_weights = {
            'morning': {'한식': 1.2, '양식': 0.8, '중식': 0.9, '일식': 1.0, '기타': 0.7},
            'lunch': {'한식': 1.1, '양식': 1.0, '중식': 1.2, '일식': 1.1, '기타': 0.9},
            'dinner': {'한식': 1.0, '양식': 1.1, '중식': 1.0, '일식': 1.2, '기타': 0.8},
            'weekend': {'한식': 0.9, '양식': 1.2, '중식': 1.1, '일식': 1.0, '기타': 1.0}
        }
        
        # 최대 추천 개수 제한
        self.max_recommendations = 5
        
        # 모델 초기화 및 학습
        self._initialize_ai_models()
        
        print("고도화된 AI 추천시스템 초기화 완료")
        print(f"  - 메뉴 데이터: {len(self.menus_df)}개")
        print(f"  - 레스토랑 데이터: {len(self.restaurants_df)}개")
        print(f"  - 최대 추천 개수: {self.max_recommendations}개")
    
    def _preprocess_data(self):
        """데이터 전처리"""
        # 숫자 컬럼들 강제 변환
        numeric_columns = ['price', 'width', 'length', 'height', 'popularity_score']
        
        for col in numeric_columns:
            if col in self.menus_df.columns:
                self.menus_df[col] = pd.to_numeric(self.menus_df[col], errors='coerce')
        
        # 결측값 처리
        if 'popularity_score' in self.menus_df.columns:
            self.menus_df['popularity_score'].fillna(5, inplace=True)
        if 'price' in self.menus_df.columns:
            self.menus_df['price'].fillna(self.menus_df['price'].median(), inplace=True)
        if 'width' in self.menus_df.columns:
            self.menus_df['width'].fillna(15, inplace=True)
        if 'length' in self.menus_df.columns:
            self.menus_df['length'].fillna(15, inplace=True)
        if 'height' in self.menus_df.columns:
            self.menus_df['height'].fillna(8, inplace=True)
    
    def _initialize_ai_models(self):
        """AI 모델들 초기화 및 사전 학습"""
        try:
            print("AI 모델 초기화 중...")
            
            # 1. 콘텐츠 기반 필터링을 위한 메뉴 벡터화
            self._prepare_content_features()
            
            # 2. 크기 기반 특성 정규화
            self._prepare_size_features()
            
            # 3. 인기도 정규화
            self._prepare_popularity_features()
            
            print("AI 모델 초기화 완료")
            
        except Exception as e:
            print(f"AI 모델 초기화 실패: {e}")
            raise
    
    def _prepare_content_features(self):
        """메뉴 설명 기반 콘텐츠 특성 추출"""
        menu_texts = (self.menus_df['menu_name'].fillna('') + ' ' + 
                     self.menus_df['category'].fillna('')).tolist()
        
        self.content_features = self.content_vectorizer.fit_transform(menu_texts)
        self.menu_similarity_matrix = cosine_similarity(self.content_features)
        print(f"콘텐츠 특성 벡터화 완료 - 차원: {self.content_features.shape}")
        
    def _prepare_size_features(self):
        """용기 크기 특성 정규화"""
        size_features = self.menus_df[['width', 'length', 'height']].values
        self.normalized_size_features = self.size_scaler.fit_transform(size_features)
        print("크기 특성 정규화 완료")
        
    def _prepare_popularity_features(self):
        """인기도 특성 정규화"""
        popularity_scores = self.menus_df[['popularity_score']].values
        self.normalized_popularity = self.popularity_scaler.fit_transform(popularity_scores)
        print("인기도 특성 정규화 완료")
    
    def get_contextual_weights(self, current_time=None):
        """상황별 가중치 계산"""
        if current_time is None:
            current_time = datetime.now()
        
        hour = current_time.hour
        is_weekend = current_time.weekday() >= 5
        
        if is_weekend:
            return self.contextual_weights['weekend']
        elif 6 <= hour < 11:
            return self.contextual_weights['morning']
        elif 11 <= hour < 15:
            return self.contextual_weights['lunch']
        else:
            return self.contextual_weights['dinner']
    
    def calculate_advanced_fit_score(self, user_width, user_length, user_height, 
                                   menu_width, menu_length, menu_height):
        """AI 기반 고도화된 적합성 점수 계산"""
        if (menu_width > user_width or menu_length > user_length or menu_height > user_height):
            return 0
        
        user_volume = user_width * user_length * user_height
        menu_volume = menu_width * menu_length * menu_height
        utilization_rate = (menu_volume / user_volume) * 100
        
        width_ratio = menu_width / user_width
        length_ratio = menu_length / user_length
        height_ratio = menu_height / user_height
        
        dimension_std = np.std([width_ratio, length_ratio, height_ratio])
        balance_score = max(0, 1 - dimension_std) * 100
        
        if 75 <= utilization_rate <= 85:
            volume_score = 100
        elif 60 <= utilization_rate < 75:
            volume_score = 80 + (utilization_rate - 60) * 1.33
        elif 85 < utilization_rate <= 90:
            volume_score = 100 - (utilization_rate - 85) * 2
        elif 45 <= utilization_rate < 60:
            volume_score = 50 + (utilization_rate - 45) * 2
        else:
            volume_score = max(0, utilization_rate * 0.8)
        
        final_score = volume_score * 0.7 + balance_score * 0.3
        return min(100, max(0, final_score))
    
    def get_content_based_recommendations(self, menu_idx, top_k=10):
        """콘텐츠 기반 유사 메뉴 추천"""
        if menu_idx >= len(self.menu_similarity_matrix):
            return []
        
        similarity_scores = self.menu_similarity_matrix[menu_idx]
        similar_indices = np.argsort(similarity_scores)[::-1][1:top_k+1]
        return similar_indices.tolist()
    
    def predict_user_preference(self, user_features):
        """사용자 선호도 예측"""
        try:
            if hasattr(self.preference_model, 'predict'):
                return self.preference_model.predict([user_features])[0]
            else:
                return 5.0
        except:
            return 5.0

    def _calculate_diversity_bonus(self, current_recommendations, new_category):
        """추천 결과의 다양성을 증진하기 위한 보너스 계산"""
        if not current_recommendations:
            return 0
        
        category_counts = {}
        for rec in current_recommendations:
            cat = rec['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        if new_category not in category_counts:
            return 5
        else:
            return max(0, 3 - category_counts[new_category])
    
    def _generate_explanation(self, fit_score, preference_score, content_score, contextual_multiplier):
        """추천 이유 생성"""
        explanations = []
        
        if fit_score > 80:
            explanations.append("용기에 완벽하게 맞습니다")
        elif fit_score > 60:
            explanations.append("용기 크기가 적절합니다")
        
        if preference_score > 40:
            explanations.append("회원님의 취향에 맞을 것 같습니다")
        
        if contextual_multiplier > 1.1:
            explanations.append("지금 시간대에 인기가 높습니다")
        
        if content_score > 5:
            explanations.append("비슷한 메뉴를 선호하시는 분들이 많습니다")
        
        return " • ".join(explanations) if explanations else "균형 잡힌 추천입니다"
    
    def _log_recommendations(self, user_id, width, length, height, recommendations, timestamp):
        """추천 결과 로깅"""
        log_entry = {
            "user_id": user_id,
            "timestamp": timestamp.isoformat() if timestamp else datetime.now().isoformat(),
            "container_size": {"width": width, "length": length, "height": height},
            "recommendations": [r["menu_id"] for r in recommendations],
            "algorithm_version": "hybrid_v2.0"
        }
        print(f"추천 로그: 사용자 {user_id}, 추천 {len(recommendations)}개")

    def get_hybrid_recommendations(self, user_width, user_length, user_height,
                                 preferred_category=None, top_k=5, user_id=None,
                                 min_price=None, max_price=None, current_time=None):
        """하이브리드 추천 시스템"""
        try:
            if any(val <= 0 for val in [user_width, user_length, user_height]):
                return {"status": "error", "message": "용기 크기는 0보다 커야 합니다.", "data": []}
            
            top_k = min(top_k, self.max_recommendations)
            
            filtered_df = self.menus_df.copy()
            if preferred_category:
                filtered_df = filtered_df[filtered_df['category'] == preferred_category]
            if min_price is not None:
                filtered_df = filtered_df[filtered_df['price'] >= min_price]
            if max_price is not None:
                filtered_df = filtered_df[filtered_df['price'] <= max_price]
            
            if len(filtered_df) == 0:
                return {"status": "error", "message": "해당 조건의 메뉴가 없습니다.", "data": []}
            
            contextual_weights = self.get_contextual_weights(current_time)
            recommendations = []
            
            for idx, menu in filtered_df.iterrows():
                try:
                    fit_score = self.calculate_advanced_fit_score(
                        user_width, user_length, user_height,
                        menu['width'], menu['length'], menu['height']
                    )
                    
                    if fit_score <= 0:
                        continue
                    
                    original_idx = self.menus_df.index.get_loc(idx)
                    similar_menus = self.get_content_based_recommendations(original_idx, 5)
                    content_score = len(similar_menus) * 2
                    
                    user_features = [
                        user_width, user_length, user_height,
                        menu['price'], menu['popularity_score'],
                        1 if menu['category'] == '한식' else 0,
                        1 if menu['category'] == '중식' else 0,
                        1 if menu['category'] == '일식' else 0,
                        1 if menu['category'] == '양식' else 0,
                        1 if menu['category'] == '기타' else 0
                    ]
                    preference_score = self.predict_user_preference(user_features) * 10
                    
                    contextual_multiplier = contextual_weights.get(menu['category'], 1.0)
                    
                    final_score = (
                        fit_score * 0.4 +
                        preference_score * 0.25 +
                        content_score * 0.15 +
                        menu['popularity_score'] * 2 * 0.2
                    ) * contextual_multiplier
                    
                    category_bonus = self._calculate_diversity_bonus(recommendations, menu['category'])
                    final_score += category_bonus
                    
                    volume_utilization = (menu['width'] * menu['length'] * menu['height']) / \
                                       (user_width * user_length * user_height) * 100
                    
                    restaurant_info = self.restaurants_df[
                        self.restaurants_df['restaurant_id'] == menu['restaurant_id']
                    ]
                    restaurant_name = restaurant_info['name'].iloc[0] if len(restaurant_info) > 0 else "알 수 없음"
                    place_id = str(restaurant_info['place_id'].iloc[0]) if 'place_id' in restaurant_info.columns and len(restaurant_info) > 0 else None
                    
                    explanation = self._generate_explanation(fit_score, preference_score, 
                                                           content_score, contextual_multiplier)
                    
                    recommendation = {
                        "menu_id": str(menu['menu_id']),
                        "restaurant_id": str(menu['restaurant_id']),
                        "restaurant_name": str(restaurant_name),
                        "menu_name": str(menu['menu_name']),
                        "category": str(menu['category']),
                        "price": int(menu['price']),
                        "size": {
                            "width": float(menu['width']),
                            "length": float(menu['length']),
                            "height": float(menu['height'])
                        },
                        "scores": {
                            "fit_score": round(fit_score, 1),
                            "preference_score": round(preference_score, 1),
                            "content_score": round(content_score, 1),
                            "final_score": round(final_score, 1)
                        },
                        "volume_utilization": round(volume_utilization, 1),
                        "explanation": explanation,
                        "contextual_boost": round((contextual_multiplier - 1) * 100, 1),
                        "place_id": place_id
                    }
                    
                    recommendations.append(recommendation)
                    
                except Exception as e:
                    print(f"메뉴 {menu.get('menu_id', 'unknown')} 처리 중 오류: {e}")
                    continue
            
            recommendations.sort(key=lambda x: x['scores']['final_score'], reverse=True)
            top_recommendations = recommendations[:top_k]
            
            if user_id:
                self._log_recommendations(user_id, user_width, user_length, user_height, 
                                        top_recommendations, current_time)
            
            total_fitting = len(recommendations)
            is_limited = total_fitting > self.max_recommendations
            
            if is_limited:
                message = f"AI가 {len(top_recommendations)}개의 맞춤 메뉴를 추천했습니다. (총 {total_fitting}개 중 상위 {self.max_recommendations}개)"
            else:
                message = f"AI가 {len(top_recommendations)}개의 맞춤 메뉴를 추천했습니다."
            
            return {
                "status": "success",
                "message": message,
                "data": top_recommendations,
                "metadata": {
                    "container_size": f"{user_width}x{user_length}x{user_height}",
                    "algorithm_version": "hybrid_v2.0",
                    "contextual_weights": contextual_weights,
                    "total_candidates": total_fitting,
                    "returned_count": len(top_recommendations),
                    "max_recommendations": self.max_recommendations,
                    "is_limited": is_limited,
                    "recommendation_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"하이브리드 추천 시스템 오류: {e}")
            return {"status": "error", "message": f"AI 추천 중 오류 발생: {str(e)}", "data": []}

    def get_simple_recommendations(self, width, length, height, top_k=5):
        """간단한 추천 시스템 (기존 호환성)"""
        results = []
        for idx, menu in self.menus_df.iterrows():
            if (menu['width'] <= width and menu['length'] <= length and menu['height'] <= height):
                results.append({
                    "menu_id": menu['menu_id'],
                    "menu_name": menu['menu_name'],
                    "category": menu['category'],
                    "price": menu['price'],
                    "size": {
                        "width": menu['width'],
                        "length": menu['length'],
                        "height": menu['height']
                    }
                })
        return results[:top_k]

# 모델 인스턴스 생성
try:
    advanced_ai = AdvancedFoodRecommendationAI(menus_df, restaurants_df)
    print("AI 모델 인스턴스 생성 완료")
except Exception as e:
    print(f"AI 모델 인스턴스 생성 실패: {e}")
    advanced_ai = None
