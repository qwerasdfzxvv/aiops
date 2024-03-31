import unittest
from unittest.mock import patch, MagicMock
from polaris.diy import MonitorData

class TestMonitorData(unittest.TestCase):

    @patch('polaris.diy.requests.get')
    @patch('polaris.diy.threading.Thread')
    def test_run(self, mock_thread, mock_get):
        # 模拟返回正常的API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': {'value': 20}}
        mock_get.return_value = mock_response

        # 实例化MonitorData对象
        monitor_data = MonitorData()

        # 由于fetch_data是MonitorData的方法，我们需要模拟它
        # 但是这里我们只关心它是否被调用以及传递的参数是否正确
        with patch.object(monitor_data, 'fetch_data', return_value=mock_response.json.return_value) as mock_fetch_data:
            # 由于is_data_abnormal是MonitorData的方法，我们需要模拟它
            # 假设在测试中，我们定义正常和异常数据的边界值
            monitor_data.is_data_abnormal = MagicMock(return_value=False)

            # 运行待测函数
            monitor_data.run()

            # 检查fetch_data是否被正确调用了
            mock_fetch_data.assert_called()
            # 检查是否未启动发送通知的线程
            mock_thread.assert_not_called()

        # 测试异常情况
        # 模拟API响应抛出异常
        mock_get.side_effect = Exception("Connection error")

        with patch.object(monitor_data, 'fetch_data', side_effect=Exception("Connection error")) as mock_fetch_data:
            monitor_data.run()
            # 因为发生异常，发送通知的线程也不应该被启动
            mock_thread.assert_not_called()

if __name__ == '__main__':
    unittest.main()
