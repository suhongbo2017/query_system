import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import server_connect
from flask import Flask, render_template, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

# 创建日志目录
if not os.path.exists('logs'):
    os.makedirs('logs')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('material_query')
handler = RotatingFileHandler(
    'logs/material_query.log',
    maxBytes=10000000,  # 10MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
logger.addHandler(handler)

# 创建应用
app = Flask(__name__)

# 如果在反向代理后面运行，需要此配置
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# 配置
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'your-secret-key-here'),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800,  # 30分钟
)

# 错误处理
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f'Page not found: {request.url}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Server Error: {error}')
    return render_template('500.html'), 500

# 路由
@app.route('/')
def index():
    logger.info(f'Access index page from IP: {request.remote_addr}')
    return render_template('queryMaterial.html')

@app.route('/queryMaterial', methods=['GET', 'POST'])
def queryMateria():
    try:
        if request.method == 'GET':
            return render_template('queryMaterial.html')
            
        q_data = request.form.get('material')
        if not q_data:
            logger.warning(f'Empty query from IP: {request.remote_addr}')
            return render_template('queryMaterial.html')

        # 记录查询
        logger.info(f'Query material: {q_data} from IP: {request.remote_addr}')

        # 数据查询
        datas = server_connect.queryMaterial(q_data)
        
        if datas is None or datas.empty:
            logger.info(f'No data found for query: {q_data}')
            return render_template('queryMaterial.html', data='未查询到数据，请检查你的输入。')
        
        # 记录查询结果
        logger.info(f'Found {len(datas)} results for query: {q_data}')
        return render_template('queryMaterial.html', datas=datas.iterrows())
            
    except Exception as e:
        logger.error(f'Error during query: {str(e)}', exc_info=True)
        return render_template('queryMaterial.html', data='查询出错，请稍后重试。')

# 健康检查端点
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == "__main__":
    # 生产环境配置
    app.config.update(
        ENV='production',
        DEBUG=False,
        TESTING=False
    )
    
    # 启动服务器
    try:
        logger.info('Starting server in production mode')
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('PORT', 8000)),
            debug=False,
            threaded=True
        )
    except Exception as e:
        logger.critical(f'Failed to start server: {str(e)}', exc_info=True)
