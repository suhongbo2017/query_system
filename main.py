import server_connect
from flask import Flask ,render_template,request,flash,redirect,url_for
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap5
import secrets

app= Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 16 字节的安全随机密钥
bootstrap= Bootstrap5(app)

@app.route('/queryMaterial',methods= ['get','post'])
def queryMateria():
    try:
        q_data = request.form.get('material')
        print("输入的内容是", q_data)
        
        if q_data is None:
            return render_template('queryMaterial.html')

        # 如果输入中包含"/"
        if '/' in q_data:
            try:
                q_data = q_data.split('/')
                print('多个查询中的第一个查询值是', q_data[0])
                datas = server_connect.queryMaterial(q_data[0])
                print('第二个查询值是', q_data[1])
                result = datas.loc[(datas['物料名称'].str.contains(q_data[1])) | (datas['规格型号'].str.contains(q_data[1]))]
                print(22, result)
                return render_template('queryMaterial.html', datas=result.iterrows())
            except Exception as e:
                print(f"处理多条件查询时出错: {e}")
                return render_template('queryMaterial.html', data='多条件查询格式错误，请检查输入格式。')

        datas = server_connect.queryMaterial(q_data)
        print('flask中', datas)
        
        if datas.empty:
            print('data is empty')
            message = '未查询到数据，请检查你的输入。'
            return render_template('queryMaterial.html', data=message)
        else:
            print('数据 is OK 这是本部数据')
            return render_template('queryMaterial.html', datas=datas.iterrows())
            
    except Exception as e:
        print(f"查询过程中发生错误: {e}")
        return render_template('queryMaterial.html', data='查询出错，请稍后重试。')
