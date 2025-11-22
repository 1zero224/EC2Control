"""
AWS EC2 实例管理服务层
提供 EC2 实例的查询、启动和停止功能
"""

from collections.abc import Callable


class EC2Service:
    """EC2 实例管理服务类"""

    def __init__(self, region_name: str | None = None):
        """
        初始化 EC2 服务

        Args:
            region_name: AWS 区域名称，None 表示使用默认配置
        """
        # 延迟导入 boto3，减少启动时间
        import boto3
        from botocore.exceptions import NoCredentialsError

        try:
            # 获取默认区域
            session = boto3.Session()
            self.default_region = region_name or session.region_name or "us-east-1"
            self.ec2_client = boto3.client("ec2", region_name=self.default_region)
            self.region_name = self.default_region
            self.ec2_clients = {}  # 缓存多个区域的客户端
            self._available_regions = None  # 缓存可用区域列表
        except NoCredentialsError:
            raise Exception("未找到 AWS 凭证，请配置 AWS credentials")
        except Exception as e:
            raise Exception(f"初始化 EC2 客户端失败: {str(e)}")

    def get_available_regions(self) -> list[str]:
        """
        获取账户的所有可用区域列表（带缓存）

        Returns:
            可用区域名称列表
        """
        from botocore.exceptions import ClientError

        if self._available_regions is not None:
            return self._available_regions

        try:
            # 使用 EC2 客户端获取所有区域
            response = self.ec2_client.describe_regions()
            self._available_regions = [region["RegionName"] for region in response["Regions"]]
            return self._available_regions
        except ClientError as e:
            # 如果获取失败，使用常用区域列表作为后备
            error_msg = e.response["Error"]["Message"]
            raise Exception(f"获取可用区域失败: {error_msg}")
        except Exception as e:
            raise Exception(f"获取可用区域时发生错误: {str(e)}")

    def get_client_for_region(self, region: str):
        """获取指定区域的 EC2 客户端（带缓存）"""
        import boto3

        if region not in self.ec2_clients:
            self.ec2_clients[region] = boto3.client("ec2", region_name=region)
        return self.ec2_clients[region]

    def list_instances_in_region(self, region: str) -> list[dict[str, str]]:
        """获取指定区域的实例列表"""
        from botocore.exceptions import ClientError

        try:
            client = self.get_client_for_region(region)
            response = client.describe_instances()
            instances = []

            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    # 提取实例名称
                    name = "N/A"
                    if "Tags" in instance:
                        for tag in instance["Tags"]:
                            if tag["Key"] == "Name":
                                name = tag["Value"]
                                break

                    # 提取公网 IP
                    public_ip = instance.get("PublicIpAddress", "N/A")

                    # 提取私有 IP
                    private_ip = instance.get("PrivateIpAddress", "N/A")

                    instances.append(
                        {
                            "id": instance["InstanceId"],
                            "name": name,
                            "state": instance["State"]["Name"],
                            "type": instance["InstanceType"],
                            "public_ip": public_ip,
                            "private_ip": private_ip,
                            "region": region,  # 添加区域信息
                            "launch_time": (
                                instance.get("LaunchTime", "").strftime("%Y-%m-%d %H:%M:%S")
                                if instance.get("LaunchTime")
                                else "N/A"
                            ),
                        }
                    )

            return instances
        except ClientError:
            # 某些区域可能无权限访问，返回空列表而不抛出异常
            return []
        except Exception:
            return []

    def list_instances(self) -> list[dict[str, str]]:
        """
        获取当前区域的 EC2 实例列表

        Returns:
            实例信息列表，每个实例包含 ID、名称、状态、类型、IP 等信息
        """
        return self.list_instances_in_region(self.region_name)

    def list_all_instances(
        self, progress_callback: Callable[[str, int, int], None] | None = None
    ) -> list[dict[str, str]]:
        """
        并行获取所有区域的实例列表

        Args:
            progress_callback: 进度回调函数 (region, current, total)

        Returns:
            所有区域的实例列表
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # 动态获取账户的所有可用区域
        try:
            available_regions = self.get_available_regions()
        except Exception:
            # 如果获取区域失败，返回空列表
            return []

        all_instances = []
        total_regions = len(available_regions)

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_region = {
                executor.submit(self.list_instances_in_region, region): region
                for region in available_regions
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
                    # 忽略单个区域的错误，继续处理其他区域
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
        from botocore.exceptions import ClientError

        try:
            client = self.get_client_for_region(region)
            client.start_instances(InstanceIds=[instance_id])
            return True
        except ClientError as e:
            error_msg = e.response["Error"]["Message"]
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
        from botocore.exceptions import ClientError

        try:
            client = self.get_client_for_region(region)
            client.stop_instances(InstanceIds=[instance_id])
            return True
        except ClientError as e:
            error_msg = e.response["Error"]["Message"]
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
        from botocore.exceptions import ClientError

        try:
            client = self.get_client_for_region(region)
            client.reboot_instances(InstanceIds=[instance_id])
            return True
        except ClientError as e:
            error_msg = e.response["Error"]["Message"]
            raise Exception(f"重启实例 {instance_id} 失败: {error_msg}")
        except Exception as e:
            raise Exception(f"重启实例时发生错误: {str(e)}")

    def get_instance_state(self, instance_id: str) -> str | None:
        """
        获取实例当前状态

        Args:
            instance_id: 实例 ID

        Returns:
            实例状态字符串，如 'running', 'stopped' 等
        """
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            if response["Reservations"]:
                instance = response["Reservations"][0]["Instances"][0]
                return instance["State"]["Name"]
            return None
        except Exception as e:
            raise Exception(f"获取实例状态失败: {str(e)}")

    def get_instance_status_checks(self, instance_id: str, region: str) -> dict[str, str]:
        """
        获取实例的健康检查状态

        Args:
            instance_id: 实例 ID
            region: 实例所在区域

        Returns:
            包含 instance_state, system_status, instance_status 的字典
        """
        from botocore.exceptions import ClientError

        try:
            client = self.get_client_for_region(region)
            response = client.describe_instance_status(InstanceIds=[instance_id])

            if response["InstanceStatuses"]:
                status = response["InstanceStatuses"][0]
                return {
                    "instance_state": status["InstanceState"]["Name"],
                    "system_status": status["SystemStatus"]["Status"],
                    "instance_status": status["InstanceStatus"]["Status"],
                }
            else:
                # 实例可能处于停止状态，没有状态检查信息
                return {
                    "instance_state": "unknown",
                    "system_status": "unknown",
                    "instance_status": "unknown",
                }
        except ClientError as e:
            error_msg = e.response["Error"]["Message"]
            raise Exception(f"获取实例状态检查失败: {error_msg}")
        except Exception as e:
            raise Exception(f"获取实例状态检查时发生错误: {str(e)}")
