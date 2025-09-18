"""
系统资源数据收集器
使用psutil收集CPU、内存、磁盘、网络等系统指标
"""

import psutil
import threading
import time
from typing import Dict, Any
from loguru import logger

from app.monitoring.metrics import system_metrics
from app.core.config import settings


class SystemCollector:
    """系统资源收集器"""
    
    def __init__(self):
        self.running = False
        self.collector_thread = None
        self.interval = settings.COLLECTION_INTERVAL
        
    def start(self):
        """启动收集器"""
        if self.running:
            return
            
        self.running = True
        self.collector_thread = threading.Thread(target=self._collect_loop, daemon=True)
        self.collector_thread.start()
        logger.info("🔄 系统资源收集器已启动")
        
    def stop(self):
        """停止收集器"""
        self.running = False
        if self.collector_thread:
            self.collector_thread.join()
        logger.info("⏹️ 系统资源收集器已停止")
        
    def _collect_loop(self):
        """收集循环"""
        while self.running:
            try:
                self._collect_cpu_metrics()
                self._collect_memory_metrics()
                self._collect_disk_metrics()
                self._collect_network_metrics()
                self._collect_process_metrics()
                self._collect_system_info()
                
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"❌ 收集系统指标时出错: {e}")
                time.sleep(self.interval)
    
    def _collect_cpu_metrics(self):
        """收集CPU指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            for i, percent in enumerate(cpu_percent):
                system_metrics.cpu_usage_percent.labels(cpu=f'cpu{i}', mode='total').set(percent)
            
            # CPU负载平均值
            load_avg = psutil.getloadavg()
            periods = ['1min', '5min', '15min']
            for period, load in zip(periods, load_avg):
                system_metrics.cpu_load_avg.labels(period=period).set(load)
                
        except Exception as e:
            logger.error(f"❌ 收集CPU指标失败: {e}")
    
    def _collect_memory_metrics(self):
        """收集内存指标"""
        try:
            # 虚拟内存
            virtual_memory = psutil.virtual_memory()
            system_metrics.memory_usage_bytes.labels(type='total').set(virtual_memory.total)
            system_metrics.memory_usage_bytes.labels(type='available').set(virtual_memory.available)
            system_metrics.memory_usage_bytes.labels(type='used').set(virtual_memory.used)
            system_metrics.memory_usage_bytes.labels(type='free').set(virtual_memory.free)
            
            system_metrics.memory_usage_percent.labels(type='virtual').set(virtual_memory.percent)
            
            # 交换内存
            swap_memory = psutil.swap_memory()
            system_metrics.memory_usage_bytes.labels(type='swap_total').set(swap_memory.total)
            system_metrics.memory_usage_bytes.labels(type='swap_used').set(swap_memory.used)
            system_metrics.memory_usage_bytes.labels(type='swap_free').set(swap_memory.free)
            
            system_metrics.memory_usage_percent.labels(type='swap').set(swap_memory.percent)
            
        except Exception as e:
            logger.error(f"❌ 收集内存指标失败: {e}")
    
    def _collect_disk_metrics(self):
        """收集磁盘指标"""
        try:
            # 磁盘使用情况
            disk_usage = psutil.disk_usage('/')
            system_metrics.disk_usage_bytes.labels(
                device='root', mountpoint='/', type='total'
            ).set(disk_usage.total)
            system_metrics.disk_usage_bytes.labels(
                device='root', mountpoint='/', type='used'
            ).set(disk_usage.used)
            system_metrics.disk_usage_bytes.labels(
                device='root', mountpoint='/', type='free'
            ).set(disk_usage.free)
            
            system_metrics.disk_usage_percent.labels(
                device='root', mountpoint='/'
            ).set(disk_usage.percent)
            
            # 所有磁盘分区
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    device = partition.device.replace('/', '_')
                    mountpoint = partition.mountpoint
                    
                    system_metrics.disk_usage_bytes.labels(
                        device=device, mountpoint=mountpoint, type='total'
                    ).set(partition_usage.total)
                    system_metrics.disk_usage_bytes.labels(
                        device=device, mountpoint=mountpoint, type='used'
                    ).set(partition_usage.used)
                    system_metrics.disk_usage_bytes.labels(
                        device=device, mountpoint=mountpoint, type='free'
                    ).set(partition_usage.free)
                    
                    system_metrics.disk_usage_percent.labels(
                        device=device, mountpoint=mountpoint
                    ).set(partition_usage.percent)
                    
                except PermissionError:
                    # 跳过无权限访问的分区
                    continue
                    
        except Exception as e:
            logger.error(f"❌ 收集磁盘指标失败: {e}")
    
    def _collect_network_metrics(self):
        """收集网络指标"""
        try:
            # 网络IO统计
            net_io = psutil.net_io_counters(pernic=True)
            for interface, io in net_io.items():
                system_metrics.network_bytes_total.labels(
                    interface=interface, direction='sent'
                )._value._value = io.bytes_sent
                
                system_metrics.network_bytes_total.labels(
                    interface=interface, direction='recv'
                )._value._value = io.bytes_recv
                
                system_metrics.network_packets_total.labels(
                    interface=interface, direction='sent'
                )._value._value = io.packets_sent
                
                system_metrics.network_packets_total.labels(
                    interface=interface, direction='recv'
                )._value._value = io.packets_recv
                
        except Exception as e:
            logger.error(f"❌ 收集网络指标失败: {e}")
    
    def _collect_process_metrics(self):
        """收集进程指标"""
        try:
            # 进程统计
            process_count = len(psutil.pids())
            system_metrics.process_count.labels(state='total').set(process_count)
            
            # 按状态统计进程
            running_count = 0
            sleeping_count = 0
            zombie_count = 0
            
            for proc in psutil.process_iter(['status']):
                try:
                    status = proc.info['status']
                    if status == psutil.STATUS_RUNNING:
                        running_count += 1
                    elif status == psutil.STATUS_SLEEPING:
                        sleeping_count += 1
                    elif status == psutil.STATUS_ZOMBIE:
                        zombie_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            system_metrics.process_count.labels(state='running').set(running_count)
            system_metrics.process_count.labels(state='sleeping').set(sleeping_count)
            system_metrics.process_count.labels(state='zombie').set(zombie_count)
            
        except Exception as e:
            logger.error(f"❌ 收集进程指标失败: {e}")
    
    def _collect_system_info(self):
        """收集系统信息"""
        try:
            # 系统信息
            uname = psutil.os.uname()
            
            # 获取处理器信息，Linux系统使用machine字段
            processor_info = 'unknown'
            try:
                if hasattr(uname, 'processor'):
                    processor_info = uname.processor
                else:
                    # Linux系统使用machine字段作为处理器架构信息
                    processor_info = uname.machine
            except:
                processor_info = 'unknown'
            
            system_metrics.system_info.info({
                'system': uname.sysname,
                'node': uname.nodename,
                'release': uname.release,
                'version': uname.version,
                'machine': uname.machine,
                'processor': processor_info,
                'boot_time': str(psutil.boot_time()),
                'cpu_count': str(psutil.cpu_count()),
                'cpu_count_logical': str(psutil.cpu_count(logical=True))
            })
            
        except Exception as e:
            logger.error(f"❌ 收集系统信息失败: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """获取当前系统指标快照"""
        try:
            return {
                'cpu': {
                    'usage_percent': psutil.cpu_percent(interval=1),
                    'load_avg': psutil.getloadavg(),
                    'count': psutil.cpu_count()
                },
                'memory': {
                    'virtual': psutil.virtual_memory()._asdict(),
                    'swap': psutil.swap_memory()._asdict()
                },
                'disk': {
                    'root': psutil.disk_usage('/')._asdict(),
                    'partitions': [
                        {
                            'device': p.device,
                            'mountpoint': p.mountpoint,
                            'fstype': p.fstype,
                            'usage': psutil.disk_usage(p.mountpoint)._asdict()
                        }
                        for p in psutil.disk_partitions()
                        if p.mountpoint != '/'
                    ]
                },
                'network': {
                    'io_counters': psutil.net_io_counters()._asdict(),
                    'connections': len(psutil.net_connections())
                },
                'processes': {
                    'count': len(psutil.pids()),
                    'top_cpu': [
                        {
                            'pid': p.info['pid'],
                            'name': p.info['name'],
                            'cpu_percent': p.info['cpu_percent']
                        }
                        for p in sorted(
                            psutil.process_iter(['pid', 'name', 'cpu_percent']),
                            key=lambda x: x.info['cpu_percent'] or 0,
                            reverse=True
                        )[:10]
                    ]
                }
            }
        except Exception as e:
            logger.error(f"❌ 获取系统指标快照失败: {e}")
            return {}