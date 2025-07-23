#!/usr/bin/env python3
"""
WebDriver内存泄漏修复测试脚本
用于验证Firefox进程清理是否有效
"""

import psutil
import time
import gc
from driver.wx import WX_API

def get_memory_usage():
    """获取当前进程内存使用情况"""
    current_process = psutil.Process()
    memory_info = current_process.memory_info()
    return {
        'rss': memory_info.rss / 1024 / 1024,  # MB
        'vms': memory_info.vms / 1024 / 1024   # MB
    }

def count_firefox_processes():
    """统计Firefox相关进程数量"""
    count = 0
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            if 'firefox' in proc_name or 'geckodriver' in proc_name:
                count += 1
                processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return count, processes

def test_webdriver_memory_cleanup():
    """测试WebDriver内存清理效果"""
    print("=" * 60)
    print("WebDriver内存泄漏修复测试")
    print("=" * 60)
    
    # 初始状态
    initial_memory = get_memory_usage()
    initial_processes, _ = count_firefox_processes()
    
    print(f"初始内存使用: RSS={initial_memory['rss']:.2f}MB, VMS={initial_memory['vms']:.2f}MB")
    print(f"初始Firefox进程数: {initial_processes}")
    print()
    
    # 模拟多次WebDriver使用
    for i in range(3):
        print(f"第 {i+1} 轮测试:")
        
        try:
            # 创建WX实例但不实际登录
            wx = WX_API
            wx.Clean()  # 清理二维码文件
            
            # 检查内存使用
            current_memory = get_memory_usage()
            current_processes, proc_list = count_firefox_processes()
            
            print(f"  当前内存: RSS={current_memory['rss']:.2f}MB, VMS={current_memory['vms']:.2f}MB")
            print(f"  Firefox进程数: {current_processes}")
            if proc_list:
                print(f"  进程列表: {proc_list}")
            
            # 清理资源
            wx.Close()
            
            # 等待进程清理
            time.sleep(2)
            
            # 强制垃圾回收
            gc.collect()
            
            # 检查清理后状态
            after_memory = get_memory_usage()
            after_processes, after_proc_list = count_firefox_processes()
            
            print(f"  清理后内存: RSS={after_memory['rss']:.2f}MB, VMS={after_memory['vms']:.2f}MB")
            print(f"  清理后Firefox进程数: {after_processes}")
            if after_proc_list:
                print(f"  残留进程: {after_proc_list}")
            
            print()
            
        except Exception as e:
            print(f"  测试过程中出现错误: {str(e)}")
            print()
    
    # 最终状态
    final_memory = get_memory_usage()
    final_processes, final_proc_list = count_firefox_processes()
    
    print("=" * 60)
    print("测试结果汇总:")
    print(f"内存变化: RSS {initial_memory['rss']:.2f}MB -> {final_memory['rss']:.2f}MB (差值: {final_memory['rss'] - initial_memory['rss']:+.2f}MB)")
    print(f"进程变化: {initial_processes} -> {final_processes} (差值: {final_processes - initial_processes:+d})")
    
    if final_processes > initial_processes:
        print("⚠️  警告: 存在进程泄漏!")
        if final_proc_list:
            print("残留进程:")
            for proc in final_proc_list:
                print(f"  - {proc}")
    else:
        print("✅ 进程清理正常")
    
    memory_increase = final_memory['rss'] - initial_memory['rss']
    if memory_increase > 50:  # 50MB阈值
        print("⚠️  警告: 内存使用增长过多!")
    else:
        print("✅ 内存使用正常")
    
    print("=" * 60)

if __name__ == "__main__":
    test_webdriver_memory_cleanup()