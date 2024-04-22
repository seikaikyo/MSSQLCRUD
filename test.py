import requests
import unittest

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ 設置測試類變量。 """
        cls.base_url = 'http://localhost:5000/api/items'
        cls.item_id = None
        print("初始化測試設置，API基礎URL設置為:", cls.base_url)

    def test_1_post_item(self):
        """ 測試創建新項目的POST請求 """
        print("\n正在執行POST測試...")
        item = {"name": "Test Item", "description": "This is a test item"}
        response = requests.post(self.base_url, json=item)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json())
        TestAPI.item_id = response.json().get('id')
        print(f"創建項目成功，項目ID: {TestAPI.item_id}")

    def test_2_get_items(self):
        """ 測試獲取所有項目的GET請求 """
        print("\n正在執行GET所有項目測試...")
        response = requests.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertTrue(len(response.json()) > 0)
        print(f"獲取到的項目數量: {len(response.json())}")

    def test_3_get_item_by_id(self):
        """ 測試通過ID獲取單個項目的GET請求 """
        if not TestAPI.item_id:
            self.skipTest("項目ID未設置")
        print("\n正在執行GET單個項目測試...")
        url = f"{self.base_url}/{TestAPI.item_id}"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        print("獲取到的項目內容:", response.json())

    def test_4_update_item(self):
        """ 測試更新項目的PUT請求 """
        if not TestAPI.item_id:
            self.skipTest("項目ID未設置")
        print("\n正在執行PUT更新項目測試...")
        updated_item = {"name": "Updated Item", "description": "Updated description"}
        url = f"{self.base_url}/{TestAPI.item_id}"
        response = requests.put(url, json=updated_item)
        self.assertEqual(response.status_code, 200)
        print("更新後的項目內容:", response.json())

    def test_5_delete_item(self):
        """ 測試刪除項目的DELETE請求 """
        if not TestAPI.item_id:
            self.skipTest("項目ID未設置")
        print("\n正在執行DELETE項目測試...")
        url = f"{self.base_url}/{TestAPI.item_id}"
        response = requests.delete(url)
        self.assertEqual(response.status_code, 204)
        response = requests.get(url)
        self.assertEqual(response.status_code, 404)
        print("項目已被刪除，無法再次獲取。")

if __name__ == '__main__':
    unittest.main()
