#!/usr/bin/env python3
"""
Generate Instagram Creator Network from MongoDB data
从MongoDB读取Instagram用户embedding和profile数据，生成创作者关系网络
"""
import os
import sys
import math
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Use the backend's database connection
from database.connection import get_database

# 相似度阈值
SIMILARITY_THRESHOLD = 0.7  # 余弦相似度阈值，高于此值才建立边


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """计算两个向量的余弦相似度"""
    if len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


class InstagramNetworkGenerator:
    """Instagram创作者网络生成器"""
    
    def __init__(self):
        """初始化MongoDB连接"""
        # Use the backend's database connection
        self.db = get_database()
        
        # Collections
        self.user_profiles = self.db['user_profiles']
        self.user_embeddings = self.db['user_embeddings']
        self.creator_networks = self.db['creator_networks']
        
        print("✅ MongoDB connection established")
    
    def load_instagram_data(self) -> tuple[List[Dict[str, Any]], Dict[str, List[float]]]:
        """
        从MongoDB加载Instagram用户数据和embeddings
        
        Returns:
            (profiles, embeddings) 元组
        """
        print("\n📊 Loading Instagram data from MongoDB...")
        
        # 加载所有Instagram用户档案
        profiles = list(self.user_profiles.find({'platform': 'instagram'}))
        print(f"   Found {len(profiles)} Instagram profiles")
        
        # 加载所有Instagram用户embeddings
        embeddings_docs = list(self.user_embeddings.find({'platform': 'instagram'}))
        print(f"   Found {len(embeddings_docs)} Instagram embeddings")
        
        # 构建embeddings字典 {user_id: embedding_vector}
        embeddings = {}
        for doc in embeddings_docs:
            user_id = doc.get('user_id')
            embedding = doc.get('embedding', [])
            if user_id and embedding:
                embeddings[user_id] = embedding
                print(f"   ✓ {user_id}: {len(embedding)} dimensions")
        
        return profiles, embeddings
    
    def build_creator_nodes(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        构建创作者节点数据
        
        Args:
            profiles: 用户档案列表
            
        Returns:
            创作者节点列表
        """
        print("\n🔨 Building creator nodes...")
        creators = []
        
        for profile in profiles:
            user_id = profile.get('user_id', '')
            nickname = profile.get('nickname') or user_id  # Instagram可能没有nickname
            profile_data = profile.get('profile_data', {})
            
            # 提取内容主题
            content_topics = []
            if isinstance(profile_data, dict):
                content_topics = profile_data.get('content_topics', [])
            
            # 提取用户风格
            user_style = profile_data.get('user_style', {}) if isinstance(profile_data, dict) else {}
            persona = user_style.get('persona', '') if isinstance(user_style, dict) else ''
            tone = user_style.get('tone', '') if isinstance(user_style, dict) else ''
            
            # 构建创作者节点
            creator_node = {
                'id': user_id,
                'name': nickname or user_id,
                'followers': 0,  # Instagram API不提供follower count
                'engagementIndex': 0,  # 可以后续从post_embeddings计算
                'primaryTrack': content_topics[0] if content_topics else 'Other',
                'contentForm': tone[:50] if tone else '',
                'recentKeywords': content_topics[:5],
                'position': {'x': 0, 'y': 0},  # 前端会重新计算布局
                'avatar': '',  # Instagram不提供avatar URL
                'ipLocation': '',
                'desc': persona[:100] if persona else '',
                'followersDelta': 0,
                'interactionDelta': 0,
                'indexSeriesRaw': [],
                'indexSeries': []
            }
            
            creators.append(creator_node)
            print(f"   ✓ {creator_node['name']}: {len(content_topics)} topics")
        
        print(f"✅ Built {len(creators)} creator nodes")
        return creators
    
    def build_network_edges(
        self,
        creators: List[Dict[str, Any]],
        embeddings: Dict[str, List[float]]
    ) -> List[Dict[str, Any]]:
        """
        基于embedding余弦相似度构建网络边
        
        Args:
            creators: 创作者节点列表
            embeddings: 用户embedding字典
            
        Returns:
            边列表
        """
        print(f"\n🔗 Computing creator similarities (threshold ≥ {SIMILARITY_THRESHOLD})...")
        edges = []
        
        for i, creator1 in enumerate(creators):
            for j, creator2 in enumerate(creators):
                if i >= j:  # 避免重复和自连接
                    continue
                
                id1 = creator1['id']
                id2 = creator2['id']
                
                # 如果两个创作者都有embedding，计算余弦相似度
                if id1 in embeddings and id2 in embeddings:
                    similarity = cosine_similarity(embeddings[id1], embeddings[id2])
                    
                    # 只保留相似度高于阈值的边
                    if similarity >= SIMILARITY_THRESHOLD:
                        edges.append({
                            'source': id1,
                            'target': id2,
                            'weight': round(similarity, 3),
                            'types': {
                                'style': round(similarity, 3)
                            }
                        })
                        print(f"   {creator1['name']} ↔ {creator2['name']}: {similarity:.3f}")
        
        print(f"✅ Generated {len(edges)} edges")
        return edges
    
    def build_track_clusters(self, creators: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        按主题聚类
        
        Args:
            creators: 创作者节点列表
            
        Returns:
            主题聚类字典
        """
        print("\n📦 Building topic clusters...")
        track_clusters = {}
        
        for creator in creators:
            track = creator.get('primaryTrack', 'Other')
            if track not in track_clusters:
                track_clusters[track] = []
            track_clusters[track].append(creator['id'])
        
        for track, creator_ids in track_clusters.items():
            print(f"   {track}: {len(creator_ids)} creators")
        
        print(f"✅ Built {len(track_clusters)} topic clusters")
        return track_clusters
    
    def save_to_mongodb(
        self,
        creators: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        track_clusters: Dict[str, List[str]]
    ):
        """
        保存网络数据到MongoDB
        
        Args:
            creators: 创作者节点列表
            edges: 边列表
            track_clusters: 主题聚类
        """
        print("\n💾 Saving network to MongoDB...")
        
        network_data = {
            'platform': 'instagram',
            'network_data': {
                'creators': creators,
                'edges': edges
            },
            'track_clusters': track_clusters,
            'metadata': {
                'creator_count': len(creators),
                'edge_count': len(edges),
                'cluster_count': len(track_clusters),
                'similarity_threshold': SIMILARITY_THRESHOLD
            },
            'created_at': datetime.now()
        }
        
        # 删除旧的Instagram网络数据
        deleted = self.creator_networks.delete_many({'platform': 'instagram'})
        if deleted.deleted_count > 0:
            print(f"   Deleted {deleted.deleted_count} old network(s)")
        
        # 插入新数据
        result = self.creator_networks.insert_one(network_data)
        print(f"✅ Saved network to MongoDB (ID: {result.inserted_id})")
        print(f"   - {len(creators)} creators")
        print(f"   - {len(edges)} edges")
        print(f"   - {len(track_clusters)} topic clusters")
    
    def generate(self):
        """生成Instagram创作者网络的主流程"""
        print("🚀 Starting Instagram Creator Network Generation")
        print("=" * 60)
        
        # 1. 加载数据
        profiles, embeddings = self.load_instagram_data()
        
        if not profiles:
            print("❌ No Instagram profiles found in database")
            return
        
        print(f"✅ Loaded {len(profiles)} profiles and {len(embeddings)} embeddings")
        
        # 2. 构建创作者节点
        creators = self.build_creator_nodes(profiles)
        
        # 3. 计算相似度并构建边（需要至少2个embeddings）
        edges = []
        if len(embeddings) >= 2:
            edges = self.build_network_edges(creators, embeddings)
        else:
            print(f"⚠️  Need at least 2 embeddings to build edges (found {len(embeddings)})")
            print("   Network will be saved without edges")
        
        # 4. 构建主题聚类
        track_clusters = self.build_track_clusters(creators)
        
        # 5. 保存到MongoDB
        self.save_to_mongodb(creators, edges, track_clusters)
        
        print("\n" + "=" * 60)
        print("✅ Instagram Creator Network Generation Complete!")
        print(f"   Network available at: GET /api/creators/network?platform=instagram")


def main():
    """主函数"""
    try:
        generator = InstagramNetworkGenerator()
        generator.generate()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
