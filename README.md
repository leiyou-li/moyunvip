# M3U 解密工具

这个项目会定期从 https://tv.iill.top/m3u/Gather 获取数据，解密并生成新的文件。

## 自动更新
- 每12小时自动更新一次
- 最新的解密结果保存在 `output.txt` 文件中
- 可以在 Actions 页面手动触发更新

## 文件说明
- `decrypt_script.py`: 主解密脚本
- `接口解密脚本.py`: 解密核心功能
- `output.txt`: 解密后的输出文件 