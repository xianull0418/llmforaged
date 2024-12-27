from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# 讯飞星火配置
SPARK_API_URL = "https://spark-api-open.xf-yun.com/v1/chat/completions"
SPARK_API_PASSWORD = "cxfqTyjdsIUSZAuiIEmk:RlEQkMmvidjewrNLYwkT"

# 存储对话历史
conversations = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        # 获取或创建会话历史
        if session_id not in conversations:
            conversations[session_id] = []

        # 添加用户消息
        conversations[session_id].append({
            "role": "user",
            "content": message
        })

        # 准备请求数据
        request_data = {
            "model": "lite",  # 使用 Spark Lite 版本
            "messages": conversations[session_id],
            "temperature": 0.7,
            "max_tokens": 2048
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SPARK_API_PASSWORD}"
        }

        # 发送请求
        response = requests.post(
            SPARK_API_URL,
            headers=headers,
            json=request_data,
            timeout=30
        )
        
        print(f"Request data: {json.dumps(request_data, ensure_ascii=False)}")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:  # 成功
                ai_response = result['choices'][0]['message']['content']
                
                # 保存AI回复到会话历史
                conversations[session_id].append({
                    "role": "assistant",
                    "content": ai_response
                })

                # 如果对话历史太长，删除最早的对话
                if len(conversations[session_id]) > 10:
                    conversations[session_id] = conversations[session_id][-10:]

                return jsonify({
                    'answer': ai_response,
                    'status': 'success'
                })
            else:
                raise Exception(f"API Error: {result}")
        else:
            raise Exception(f"HTTP Error: {response.status_code}, Body: {response.text}")

    except Exception as e:
        error_message = str(e)
        print(f"Error in chat endpoint: {error_message}")
        
        # 根据错误类型返回不同的提示
        if "10007" in error_message:
            message = "请等待上一个问题回复完成后再提问"
        elif "10013" in error_message or "10014" in error_message:
            message = "您的问题可能涉及敏感内容，请调整后重试"
        elif "10907" in error_message:
            message = "对话内容过长，请精简后重试"
        elif "11200" in error_message:
            message = "服务授权错误，请联系管理员"
        elif "11201" in error_message:
            message = "今日使用量已达上限，请明天再试"
        elif "11202" in error_message or "11203" in error_message:
            message = "服务繁忙，请稍后重试"
        else:
            message = "服务暂时出现问题，请稍后再试"

        return jsonify({
            'answer': message,
            'status': 'error',
            'error': error_message
        }), 500

@app.route('/')
def index():
    nav_content = render_template('nav.html')
    return render_template('index.html', nav_content=nav_content)

@app.route('/ai-chat')
def ai_chat():
    nav_content = render_template('nav.html')
    return render_template('ai_chat.html', nav_content=nav_content)

@app.route('/medical-analysis')
def medical_analysis():
    nav_content = render_template('nav.html')
    return render_template('medical_analysis.html', nav_content=nav_content)

@app.route('/health-assessment')
def health_assessment():
    nav_content = render_template('nav.html')
    return render_template('health_assessment.html', nav_content=nav_content)

if __name__ == '__main__':
    app.run(debug=True) 