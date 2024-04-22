from flask import Flask, request, jsonify
import pyodbc
import json

app = Flask(__name__)

def load_config():
    """載入資料庫配置"""
    with open('config.json') as f:
        data = json.load(f)
    return data['dbConfig']

def get_db_connection():
    """建立資料庫連接"""
    config = load_config()
    conn_str = f"DRIVER={{SQL Server}};SERVER={config['server']};DATABASE={config['database']};UID={config['username']};PWD={config['password']};"
    conn = pyodbc.connect(conn_str)
    return conn

def create_items_table():
    """創建items表格如果它不存在"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[items]') AND type in (N'U'))
    CREATE TABLE items (
        id INT PRIMARY KEY IDENTITY(1,1),
        name NVARCHAR(255),
        description NVARCHAR(255)
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/api/items', methods=['POST', 'GET'])
def items():
    """處理對items的POST和GET請求"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            new_item = request.json
            cursor.execute("INSERT INTO items (name, description) OUTPUT INSERTED.id, INSERTED.name, INSERTED.description VALUES (?, ?)", (new_item['name'], new_item['description']))
            item = cursor.fetchone()
            conn.commit()
            return jsonify({'id': item[0], 'name': item[1], 'description': item[2]}), 201

        elif request.method == 'GET':
            cursor.execute("SELECT id, name, description FROM items")
            items = [{'id': row[0], 'name': row[1], 'description': row[2]} for row in cursor.fetchall()]
            return jsonify(items)
    except Exception as e:
        app.logger.error(f"發生錯誤：{request.method} at /api/items: {str(e)}")
        return jsonify({"error": "內部服務器錯誤", "message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def single_item(id):
    """處理對單個item的GET, PUT, DELETE請求"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'GET':
            cursor.execute("SELECT id, name, description FROM items WHERE id = ?", (id,))
            item = cursor.fetchone()
            if item:
                return jsonify({'id': item[0], 'name': item[1], 'description': item[2]})
            else:
                return jsonify({"error": "項目未找到"}), 404

        elif request.method == 'PUT':
            item = request.json
            cursor.execute("UPDATE items SET name = ?, description = ? OUTPUT INSERTED.name, INSERTED.description WHERE id = ?", (item['name'], item['description'], id))
            updated_item = cursor.fetchone()
            conn.commit()
            return jsonify({'name': updated_item[0], 'description': updated_item[1]})

        elif request.method == 'DELETE':
            cursor.execute("DELETE FROM items WHERE id = ?", (id,))
            conn.commit()
            return '', 204

    except Exception as e:
        app.logger.error(f"發生錯誤：{request.method} at /api/items/{id}: {str(e)}")
        return jsonify({"error": "內部服務器錯誤"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    create_items_table()  # 確保在應用啟動前表格存在
    app.run(debug=True)
