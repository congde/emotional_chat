#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个性化配置系统测试脚本
验证所有组件是否正常工作
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import json
from sqlalchemy import create_engine, text
from backend.services.prompt_composer import PromptComposer, get_all_role_templates
from backend.services.personalization_service import PersonalizationService
from backend.database import DatabaseManager, UserPersonalization

print("=" * 70)
print("个性化配置系统测试")
print("=" * 70)
print()

# 测试1: 检查数据库表
print("✓ 测试1: 检查数据库表是否存在...")
try:
    from backend.database import engine
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'user_personalizations'
        """))
        count = result.fetchone()[0]
        if count == 1:
            print("  ✅ user_personalizations表已存在")
        else:
            print("  ❌ user_personalizations表不存在")
            print("     请运行: mysql -u root -p emotional_chat < backend/migrations/add_personalization_table.sql")
            sys.exit(1)
except Exception as e:
    print(f"  ❌ 数据库连接失败: {e}")
    sys.exit(1)

print()

# 测试2: 检查角色模板
print("✓ 测试2: 检查角色模板...")
try:
    templates = get_all_role_templates()
    print(f"  ✅ 找到 {len(templates)} 个角色模板:")
    for template in templates:
        print(f"     - {template['icon']} {template['name']}: {template['description']}")
except Exception as e:
    print(f"  ❌ 角色模板加载失败: {e}")
    sys.exit(1)

print()

# 测试3: 测试PromptComposer
print("✓ 测试3: 测试Prompt生成...")
try:
    test_config = {
        "user_id": "test_user",
        "role": "温暖倾听者",
        "role_name": "心语",
        "personality": "温暖耐心",
        "tone": "温和",
        "style": "简洁",
        "formality": 0.3,
        "enthusiasm": 0.5,
        "empathy_level": 0.8,
        "humor_level": 0.3,
        "response_length": "medium",
        "use_emoji": False,
        "core_principles": ["永不评判", "倾听优先"],
        "safety_level": "standard"
    }
    
    composer = PromptComposer(test_config)
    prompt = composer.compose(
        context="用户说：今天心情不太好",
        emotion_state={"emotion": "sad", "intensity": 6.5}
    )
    
    print(f"  ✅ Prompt生成成功 (长度: {len(prompt)} 字符)")
    print(f"  示例片段: {prompt[:200]}...")
except Exception as e:
    print(f"  ❌ Prompt生成失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 测试4: 测试PersonalizationService
print("✓ 测试4: 测试个性化服务...")
try:
    service = PersonalizationService()
    
    # 测试默认配置
    default_config = service._get_default_config("test_user_2")
    print(f"  ✅ 默认配置生成成功")
    print(f"     角色: {default_config['role']}")
    print(f"     名称: {default_config['role_name']}")
    print(f"     语气: {default_config['tone']}")
except Exception as e:
    print(f"  ❌ 个性化服务测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 测试5: 测试数据库操作
print("✓ 测试5: 测试数据库读写...")
try:
    with DatabaseManager() as db:
        # 检查是否已有测试用户
        existing = db.db.query(UserPersonalization).filter(
            UserPersonalization.user_id == "test_demo_user"
        ).first()
        
        if existing:
            print("  ℹ️  测试用户已存在，删除旧数据...")
            db.db.delete(existing)
            db.db.commit()
        
        # 创建测试配置
        test_user_config = UserPersonalization(
            user_id="test_demo_user",
            role="智慧导师",
            role_name="智者",
            personality="理性洞察",
            tone="沉稳",
            style="详细",
            formality=0.7,
            enthusiasm=0.3,
            empathy_level=0.6,
            humor_level=0.2,
            response_length="long",
            use_emoji=False,
            core_principles=json.dumps(["引导思考", "多角度分析"], ensure_ascii=False),
            learning_mode=True,
            safety_level="standard",
            context_window=15
        )
        
        db.db.add(test_user_config)
        db.db.commit()
        
        print("  ✅ 测试配置写入成功")
        
        # 读取验证
        saved_config = db.db.query(UserPersonalization).filter(
            UserPersonalization.user_id == "test_demo_user"
        ).first()
        
        if saved_config:
            print(f"  ✅ 配置读取成功")
            print(f"     用户ID: {saved_config.user_id}")
            print(f"     角色: {saved_config.role}")
            print(f"     名称: {saved_config.role_name}")
            print(f"     配置版本: {saved_config.config_version}")
        else:
            print("  ❌ 配置读取失败")
            
except Exception as e:
    print(f"  ❌ 数据库操作失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 测试6: 集成测试
print("✓ 测试6: 端到端集成测试...")
try:
    service = PersonalizationService()
    
    with DatabaseManager() as db:
        # 获取刚才创建的配置
        user_config = service.get_user_config("test_demo_user", db.db)
        
        # 创建Prompt组合器
        composer = PromptComposer(user_config)
        
        # 生成个性化Prompt
        personalized_prompt = composer.compose(
            context="用户说：我在考虑换工作，但有些犹豫",
            emotion_state={"emotion": "anxious", "intensity": 5.5}
        )
        
        print("  ✅ 端到端测试成功")
        print(f"  生成的个性化Prompt长度: {len(personalized_prompt)} 字符")
        print()
        print("  示例Prompt片段:")
        print("  " + "-" * 66)
        for line in personalized_prompt.split('\n')[:15]:
            if line.strip():
                print(f"  {line[:66]}")
        print("  " + "-" * 66)
        
except Exception as e:
    print(f"  ❌ 集成测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("测试完成！")
print("=" * 70)
print()
print("📋 下一步操作:")
print("1. 启动后端服务: cd /home/workSpace/emotional_chat && uvicorn backend.app:app --reload")
print("2. 测试API: curl http://localhost:8000/api/personalization/templates")
print("3. 启动前端: cd frontend && npm start")
print("4. 访问: http://localhost:3000")
print()





