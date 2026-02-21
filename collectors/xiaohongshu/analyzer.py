#!/usr/bin/env python3
"""分析快照：使用 GPT-4o 生成用户画像并计算 embeddings 的脚本。

用法：
    # 默认：使用 snapshots/ 目录下最新的快照
    python3 analyze_snapshot.py

    # 指定快照路径和输出目录
    python3 analyze_snapshot.py --snapshot snapshots/所长林科普_2025-11-18.json --out analyses

依赖：
    pip3 install requests

运行前环境变量：
    需要在环境中设置 `OPENAI_API_KEY` 或 Deepseek 对应的 KEY（详见下文）
"""

import os
import json
import argparse
from glob import glob
from pathlib import Path
from datetime import datetime
import requests
import re
from typing import List, Dict, Any
import numpy as np
from FlagEmbedding import FlagModel


OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_EMBED_URL = "https://api.openai.com/v1/embeddings"
CHAT_MODEL = "gpt-4o"
EMBED_MODEL = "text-embedding-3-small"

# 可在此处直接填写 API Key 或 URL（仅用于本地快速测试；生产环境建议使用环境变量或更安全的密钥管理）
DEFAULT_OPENAI_API_KEY = ""            # <-- 在这里填入 OpenAI API Key（可选）
DEFAULT_DEEPSEEK_API_KEY = None  # 从环境变量 DEEPSEEK_API_KEY 读取
DEFAULT_DEEPSEEK_CHAT_URL = "https://api.deepseek.com/v1/chat/completions"         # <-- 在这里填入 Deepseek chat endpoint（可选）
DEFAULT_DEEPSEEK_EMBED_URL = "https://api.deepseek.com/v1/embeddings"        # <-- 在这里填入 Deepseek embeddings endpoint（可选）

# Deepseek 支持：当 provider 为 'deepseek' 时，脚本会读取下列环境变量或使用上面的默认值
DEEPSEEK_CHAT_URL = os.environ.get("DEEPSEEK_CHAT_URL", DEFAULT_DEEPSEEK_CHAT_URL)
DEEPSEEK_EMBED_URL = os.environ.get("DEEPSEEK_EMBED_URL", DEFAULT_DEEPSEEK_EMBED_URL)



def find_latest_snapshot(snap_dir: Path) -> Path:
    """返回指定目录下按修改时间排序的最新 .json 快照路径，找不到则返回 None。"""
    files = sorted(snap_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def load_snapshot(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt_for_profile(user_desc: str, notes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """构建发送给聊天模型的 prompt（以 messages 列表形式返回）。

    包含用户描述（user_desc）和若干条笔记的 title/desc/tags 作为样例。
    """
    # 组装笔记内容：title + desc + tags
    sample_notes = []
    for n in notes[:50]:
        tags = n.get("tag_list") or []
        if isinstance(tags, (list, tuple)):
            tags_s = ", ".join(tags)
        elif isinstance(tags, dict):
            tags_s = ", ".join(tags.values())
        else:
            tags_s = str(tags)
        t = f"Title: {n.get('title','')}\nDesc: {n.get('desc','')}\nTags: {tags_s}"
        sample_notes.append(t)

    notes_text = "\n\n".join(sample_notes)

    system = (
        "你是一个有用的助手，负责从给定的用户描述和示例笔记中提取精简的用户画像（user_style）、内容主题（content_topic）和内容分类（categories）。"
        "请严格返回一个包含三个键的 JSON 对象：\"user_style\"、\"content_topic\" 和 \"categories\"。"
        "\n- \"user_style\" 应为一个对象，包含字段：\"persona\"（1-2 句的简短描述）、\"tone\"（描述写作/视频语气的词语）、"
        "以及 \"interests\"（列出主要兴趣关键词）。"
        "\n- \"content_topic\" 应为一个列表，包含总结性的话题关键词或短语。"
        "\n- \"categories\" 应为一个列表，包含1-3个最匹配的类别，从以下选项中选择：Lifestyle（生活方式）、Fashion（时尚）、Food（美食）、"
        "Fitness（健身）、Tech（科技）、Wellness（身心健康）、Finance（财经）。\n"
    )

    user_msg = (
        f"用户描述:\n{user_desc}\n\n示例笔记（title/desc/tags）：\n{notes_text}\n\n"
        "请仅输出 JSON 对象。示例格式：\n"
        "{\"user_style\": {\"persona\": \"...\", \"tone\": \"...\", \"interests\": [\"...\"]}, "
        "\"content_topic\": [\"topic1\", \"topic2\"], "
        "\"categories\": [\"Lifestyle\", \"Food\"]}"
    )

    return [{"role": "system", "content": system}, {"role": "user", "content": user_msg}]


def call_chat(api_key: str, messages: List[Dict[str, str]], provider: str = "openai") -> str:
    """调用聊天模型的通用函数。

    参数：
      - api_key: 对应服务的 API Key（OpenAI 或 Deepseek）
      - messages: OpenAI-style 的 messages 列表
      - provider: 'openai' 或 'deepseek'

    注意：本函数向指定的 URL 发送与 OpenAI 兼容的请求体。如果 Deepseek 的接口格式不同，
    请将 `DEEPSEEK_CHAT_URL` 指向一个兼容层（proxy），或修改本函数以匹配 Deepseek 的实际请求格式。
    """
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": CHAT_MODEL, "messages": messages, "temperature": 0.0}


    # 根据 provider 选择请求 URL 和 模型
    if provider == "deepseek":
        url = DEEPSEEK_CHAT_URL or os.environ.get("DEEPSEEK_CHAT_URL")
        payload["model"] = "deepseek-chat"
    else:
        url = OPENAI_CHAT_URL
        # payload["model"] already defaults to CHAT_MODEL (gpt-4o)


    if not url:
        raise RuntimeError(f"未配置 provider '{provider}' 的 chat URL")

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # 解析返回：优先按 OpenAI 返回结构读取；对 Deepseek 或其它兼容结构做兼容处理
    if provider == "openai":
        return data["choices"][0]["message"]["content"]
    if "choices" in data and isinstance(data["choices"], list):
        c = data["choices"][0]
        if isinstance(c.get("message"), dict) and c["message"].get("content"):
            return c["message"]["content"]
        if c.get("text"):
            return c.get("text")

    # 兜底：尝试读取顶层的 text 字段
    if data.get("text"):
        return data.get("text")

    raise RuntimeError("无法解析聊天接口返回内容")


def extract_json(text: str) -> Any:
    """尝试从模型返回的文本中解析出第一个 JSON 对象（{...}）。

    有时候模型会输出额外说明文本，本函数会提取第一段符合 JSON 语法的子串并解析。
    """
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    raise ValueError("未在助手返回中找到可解析的 JSON")


def call_embeddings(api_key: str, inputs: List[str], provider: str = "openai") -> List[List[float]]:
    """调用向量化（embeddings）接口的通用函数。

    参数：
      - api_key: 对应服务的 API Key（OpenAI 或 Deepseek）
      - inputs: 待向量化的文本列表
      - provider: 'openai' 或 'deepseek'

    注意：本函数发送与 OpenAI 兼容的请求体；如果 Deepseek 要求不同，请修改此处或使用 proxy。
    """
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": EMBED_MODEL, "input": inputs}

    if provider == "deepseek":
        url = DEEPSEEK_EMBED_URL or os.environ.get("DEEPSEEK_EMBED_URL")
    else:
        url = OPENAI_EMBED_URL

    if not url:
        raise RuntimeError(f"未配置 provider '{provider}' 的 embeddings URL")

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # 解析 OpenAI 风格的返回
    if "data" in data and isinstance(data["data"], list):
        return [d.get("embedding") for d in data["data"]]

    # Deepseek 风格的兜底解析（假设返回顶层的 embeddings 列表）
    if data.get("embeddings") and isinstance(data.get("embeddings"), list):
        return data.get("embeddings")

    raise RuntimeError("无法解析 embeddings 接口的返回内容")


def main():
    parser = argparse.ArgumentParser(description="Generate user profile via GPT and embeddings from a snapshot JSON")
    parser.add_argument("--snapshot", help="Path to snapshot JSON (default: latest in snapshots/)")
    parser.add_argument("--out", default="analyses", help="Output directory to save profile and embeddings")
    args = parser.parse_args()

    snap_dir = Path(__file__).resolve().parent / "snapshots"
    snap_path = Path(args.snapshot) if args.snapshot else find_latest_snapshot(snap_dir)
    if not snap_path or not snap_path.exists():
        raise SystemExit(f"Snapshot not found: {snap_path}")

    snapshot = load_snapshot(snap_path)
    user = snapshot.get("user") or {}
    notes = snapshot.get("notes") or []

    user_desc = user.get("desc", "")

    provider = os.environ.get("AI_PROVIDER", "openai")
    api_key = None
    if provider == "openai":
        # 优先使用环境变量 OPENAI_API_KEY，其次使用脚本顶部的 DEFAULT_OPENAI_API_KEY
        api_key = os.environ.get("OPENAI_API_KEY") or DEFAULT_OPENAI_API_KEY
    elif provider == "deepseek":
        # 优先使用环境变量 DEEPSEEK_API_KEY，其次使用脚本顶部的 DEFAULT_DEEPSEEK_API_KEY
        api_key = os.environ.get("DEEPSEEK_API_KEY") or DEFAULT_DEEPSEEK_API_KEY
    else:
        raise SystemExit(f"Unknown provider: {provider}. Set AI_PROVIDER=openai|deepseek or set appropriate env vars.")

    if not api_key:
        raise SystemExit(f"Please set API key for provider '{provider}' in environment or fill the DEFAULT_* variable in the script.")

    messages = build_prompt_for_profile(user_desc, notes)
    print(f"Calling {provider} GPT to generate profile...")
    chat_text = call_chat(api_key, messages, provider=provider)
    try:
        profile = extract_json(chat_text)
    except Exception as e:
        print("Failed to parse assistant response as JSON. Raw response:\n", chat_text)
        raise

    # Save profile
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    profile_path = out_dir / (snap_path.stem + "__profile.json")
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    print(f"Profile saved to {profile_path}")

    # Build embedding inputs: one for user_style JSON string, one per note (title+desc+tags)
    user_style_text = json.dumps(profile.get("user_style", {}), ensure_ascii=False)
    note_texts = []
    note_ids = []
    for n in notes:
        tags = n.get("tag_list") or []
        if isinstance(tags, dict):
            tags = list(tags.values())
        tags_s = ", ".join(tags) if tags else ""
        txt = f"Title: {n.get('title','')}\nDesc: {n.get('desc','')}\nTags: {tags_s}"
        note_texts.append(txt)
        note_ids.append(n.get("note_id") or n.get("_id") or None)

    embed_inputs = [user_style_text] + note_texts
    print(f"Requesting embeddings for {len(embed_inputs)} items using {provider}...")
    embeddings = call_embeddings(api_key, embed_inputs, provider=provider)

    # Save embeddings: first is user_style, rest correspond to note_ids
    embeds_out = {
        "snapshot": str(snap_path.name),
        "generated_at": datetime.utcnow().isoformat(),
        "user_style_embedding": embeddings[0],
        "notes": [
            {"note_id": nid, "embedding": emb}
            for nid, emb in zip(note_ids, embeddings[1:])
        ],
    }
    embed_path = out_dir / (snap_path.stem + "__embeddings.json")
    with open(embed_path, "w", encoding="utf-8") as f:
        json.dump(embeds_out, f, ensure_ascii=False)
    print(f"Embeddings saved to {embed_path}")


def analyze_user_profile(user_info: Dict[str, Any], notes: List[Dict[str, Any]], embedding_model: FlagModel = None) -> Dict[str, Any]:
    """
    分析用户画像并生成embedding（供pipeline.py调用）
    
    Args:
        user_info: 用户信息字典（从notes[0]['user']提取）
        notes: 笔记列表
        embedding_model: FlagModel实例，用于生成本地embedding
        
    Returns:
        包含profile和embedding的字典
    """
    # 使用Deepseek
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY环境变量未设置")
    
    provider = "deepseek"
    
    # 构建用户描述
    user_desc = f"User: {user_info.get('nickname', 'Unknown')}\nFollowers: {user_info.get('fans', 0)}"
    
    # 构建prompt
    messages = build_prompt_for_profile(user_desc, notes)
    
    # 调用chat API生成profile
    response_text = call_chat(api_key, messages, provider=provider)
    profile = extract_json(response_text)
    
    if not profile:
        raise ValueError("无法解析DeepSeek返回的JSON")
    
    # 生成完整的profile_data结构
    profile_data = {
        "user_basic": {
            "user_id": user_info.get('userid', user_info.get('user_id', '')),
            "nickname": user_info.get('nickname', ''),
            "fans": user_info.get('fans', 0),
            "gender": "未知",
            "avatar": user_info.get('images', ''),
            "desc": "",
            "interaction": 0,
            "ip_location": "",
            "last_modify_ts": int(datetime.now().timestamp() * 1000)
        },
        "content_topics": profile.get("content_topic", []),
        "content_style": [],
        "categories": profile.get("categories", ["Lifestyle"]),  # Extract categories from GPT response
        "audience": [],
        "value_points": [],
        "content_clusters": []
    }
    
    # 提取user_style
    user_style = profile.get("user_style", {})
    if isinstance(user_style, dict):
        persona = user_style.get("persona", "")
        tone = user_style.get("tone", "")
        interests = user_style.get("interests", [])
        
        if isinstance(interests, list):
            profile_data["content_style"] = interests
        
        # 构建embedding文本
        user_style_text = f"{persona} {tone} {' '.join(interests) if isinstance(interests, list) else ''}"
    else:
        user_style_text = str(user_style)
    
    # 使用本地模型生成embedding
    print("  生成embedding...")
    if embedding_model is None:
        # 如果没有传入model，临时创建一个
        embedding_model = FlagModel(
            "BAAI/bge-small-zh-v1.5",
            query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
            use_fp16=True
        )
    
    vec = embedding_model.encode([user_style_text])  # 返回 numpy array shape (1, dim)
    if hasattr(vec, "tolist"):
        emb = vec.tolist()[0]
    else:
        emb = np.array(vec).tolist()
    
    profile_data["user_style_embedding"] = emb
    
    return profile_data


if __name__ == "__main__":
    main()
