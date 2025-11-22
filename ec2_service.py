"""
AWS EC2 实例管理服务层
提供 EC2 实例的查询、启动和停止功能
"""
import boto3
from typing import List, Dict, Optional, Callable
from botocore.exceptions import ClientError, NoCredentialsError
from concurrent.futures import ThreadPoolExecutor, as_completed


class EC2Service:
    """EC2 实例管理服务类"""

    # 常用 AWS 区域列表
    COMMON_REGIONS = [
        'us-east-1', 'us-west-2',
        'ap-southeast-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-south-1',
        'eu-west-1', 'eu-central-1',
    ]

    def __init__(self, region_name: Optional[str] = None):
        """
        初始化 EC2 服务

        Args:
            region_name: AWS 区域名称，None 表示使用默认配置
        """
        try:
            # 获取默认区域
            session = boto3.Session()
            self.default_region = region_name or session.region_name or 'us-east-1'
            self.ec2_client = boto3.client('ec2', region_name=self.default_region)
            self.region_name = self.default_region
            self.ec2_clients = {}  # 缓存多个区域的客户端
        except NoCredentialsError:
            raise Exception("未找到 AWS 凭证，请配置 AWS credentials")
        except Exception as e:
            raise Exception(f"初始化 EC2 客户端失败: {str(e)}")

    def get_client_for_region(self, region: str):
        """获取指定区域的 EC2 客户端（带缓存）"""
        if region not in self.ec2_clients:
            self.ec2_clients[region] = boto3.client('ec2', region_name=region)
        return self.ec2_clients[region]

    def list_instances_in_region(self, region: str) -> List[Dict[str, str]]:
        """获取指定区域的实例列表"""
        try:
            client = self.get_client_for_region(region)
            response = client.describe_instances()
            instances = []

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    # 提取实例名称
                    name = 'N/A'
                    if 'Tags' in instance:
                        for tag in instance['Tags']:
                            if tag['Key'] == 'Name':
                                name = tag['Value']
                                break

                    # 提取公网 IP
                    public_ip = instance.get('PublicIpAddress', 'N/A')

                    # 提取私有 IP
                    private_ip = instance.get('PrivateIpAddress', 'N/A')

                    instances.append({
                        'id': instance['InstanceId'],
                        'name': name,
                        'state': instance['State']['Name'],
                        'type': instance['InstanceType'],
                        'public_ip': public_ip,
                        'private_ip': private_ip,
                        'region': region,  # 添加区域信息
                        'launch_time': instance.get('LaunchTime', '').strftime('%Y-%m-%d %H:%M:%S') if instance.get('LaunchTime') else 'N/A'
                    })

            return instances
        except ClientError as e:
            # 某些区域可能无权限访问，返回空列表而不抛出异常
            return []
        except Exception as e:
            return []

    def list_instances(self) -> List[Dict[str, str]]:
        """
        获取当前区域的 EC2 实例列表

        Returns:
            实例信息列表，每个实例包含 ID、名称、状态、类型、IP 等信息
        """
        return self.list_instances_in_region(self.region_name)

    def list_all_instances(self, progress_callback: Optional[Callable[[str, int, int], None]] = None) -> List[Dict[str, str]]:
        """
        并行获取所有区域的实例列表

        Args:
            progress_callback: 进度回调函数 (region, current, total)

        Returns:
            所有区域的实例列表
        """
        all_instances = []
        total_regions = len(self.COMMON_REGIONS)

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_region = {
                executor.submit(self.list_instances_in_region, region): region
                for region in self.COMMON_REGIONS
            }

            completed = 0
            for future in as_completed(future_to_region):
                region = future_to_region[future]
                completed += 1
                try:
                    instances = future.result()
                    all_instances.extend(instances)
                    if progress_callback:
                        progress_callback(region, completed, total_regions)
                except Exception:
                    pass

        return all_instances

    def start_instance(self, instance_id: str, region: str) -> bool:
        """
        启动指定的 EC2 实例

        Args:
            instance_id: 实例 ID
            region: 实例所在区域

        Returns:
            操作是否成功
        """
        try:
            client = self.get_client_for_region(region)
            client.start_instances(InstanceIds=[instance_id])
            return True
        except ClientError as e:
            error_msg = e.response['Error']['Message']
            raise Exception(f"启动实例 {instance_id} 失败: {error_msg}")
        except Exception as e:
            raise Exception(f"启动实例时发生错误: {str(e)}")

    def stop_instance(self, instance_id: str, region: str) -> bool:
        """
        停止指定的 EC2 实例

        Args:
            instance_id: 实例 ID
            region: 实例所在区域

        Returns:
            操作是否成功
        """
        try:
            client = self.get_client_for_region(region)
            client.stop_instances(InstanceIds=[instance_id])
            return True
        except ClientError as e:
            error_msg = e.response['Error']['Message']
            raise Exception(f"停止实例 {instance_id} 失败: {error_msg}")
        except Exception as e:
            raise Exception(f"停止实例时发生错误: {str(e)}")

    def reboot_instance(self, instance_id: str, region: str) -> bool:
        """
        重启指定的 EC2 实例

        Args:
            instance_id: 实例 ID
            region: 实例所在区域

        Returns:
            操作是否成功
        """
        try:
            client = self.get_client_for_region(region)
            client.reboot_instances(InstanceIds=[instance_id])
            return True
        except ClientError as e:
            error_msg = e.response['Error']['Message']
            raise Exception(f"重启实例 {instance_id} 失败: {error_msg}")
        except Exception as e:
            raise Exception(f"重启实例时发生错误: {str(e)}")

    def get_instance_state(self, instance_id: str) -> Optional[str]:
        """
        获取实例当前状态

        Args:
            instance_id: 实例 ID

        Returns:
            实例状态字符串，如 'running', 'stopped' 等
        """
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            if response['Reservations']:
                instance = response['Reservations'][0]['Instances'][0]
                return instance['State']['Name']
            return None
        except Exception as e:
            raise Exception(f"获取实例状态失败: {str(e)}")

    def get_instance_status_checks(self, instance_id: str, region: str) -> Dict[str, str]:
        """
        获取实例的健康检查状态

        Args:
            instance_id: 实例 ID
            region: 实例所在区域

        Returns:
            包含 instance_state, system_status, instance_status 的字典
        """
        try:
            client = self.get_client_for_region(region)
            response = client.describe_instance_status(InstanceIds=[instance_id])

            if response['InstanceStatuses']:
                status = response['InstanceStatuses'][0]
                return {
                    'instance_state': status['InstanceState']['Name'],
                    'system_status': status['SystemStatus']['Status'],
                    'instance_status': status['InstanceStatus']['Status'],
                }
            else:
                # 实例可能处于停止状态，没有状态检查信息
                return {
                    'instance_state': 'unknown',
                    'system_status': 'unknown',
                    'instance_status': 'unknown',
                }
        except ClientError as e:
            error_msg = e.response['Error']['Message']
            raise Exception(f"获取实例状态检查失败: {error_msg}")
        except Exception as e:
            raise Exception(f"获取实例状态检查时发生错误: {str(e)}")
