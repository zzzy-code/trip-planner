"""高德地图MCP服务封装"""

import json
import re
from typing import List, Dict, Any, Optional
from hello_agents.tools import MCPTool
from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo

# 全局MCP工具实例
_amap_mcp_tool = None


def _extract_json(result_text: str) -> Optional[Any]:
    """从 MCP 工具返回的文本中提取并解析 JSON 对象"""
    if not result_text:
        return None
    try:
        return json.loads(result_text)
    except Exception:
        pass
    json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', result_text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except Exception:
            pass
    return None


def get_amap_mcp_tool() -> MCPTool:
    """
    获取高德地图MCP工具实例(单例模式)
    
    Returns:
        MCPTool实例
    """
    global _amap_mcp_tool
    
    if _amap_mcp_tool is None:
        settings = get_settings()
        
        if not settings.amap_api_key:
            raise ValueError("高德地图API Key未配置,请在.env文件中设置AMAP_API_KEY")
        
        # 创建MCP工具
        _amap_mcp_tool = MCPTool(
            name="amap",
            description="高德地图服务,支持POI搜索、路线规划、天气查询等功能",
            server_command=["uvx", "amap-mcp-server"],
            env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
            auto_expand=True  # 自动展开为独立工具
        )
        
        print("高德地图MCP工具初始化成功")
        print(f"   工具数量: {len(_amap_mcp_tool._available_tools)}")
        
        # 打印可用工具列表
        if _amap_mcp_tool._available_tools:
            print("   可用工具:")
            for tool in _amap_mcp_tool._available_tools[:5]:  # 只打印前5个
                print(f"     - {tool.get('name', 'unknown')}")
            if len(_amap_mcp_tool._available_tools) > 5:
                print(f"     ... 还有 {len(_amap_mcp_tool._available_tools) - 5} 个工具")
    
    return _amap_mcp_tool


class AmapService:
    """高德地图服务封装类"""
    
    def __init__(self):
        """初始化服务"""
        self.mcp_tool = get_amap_mcp_tool()
    
    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        """
        搜索POI
        
        Args:
            keywords: 搜索关键词
            city: 城市
            citylimit: 是否限制在城市范围内
            
        Returns:
            POI信息列表
        """
        try:
            # 调用MCP工具
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_text_search",
                "arguments": {
                    "keywords": keywords,
                    "city": city,
                    "citylimit": str(citylimit).lower()
                }
            })
            
            # 解析结果
            print(f"POI搜索结果: {result[:200]}...")
            
            data = _extract_json(result)
            pois = []
            if isinstance(data, dict) and "pois" in data:
                for item in data["pois"]:
                    loc_str = item.get("location", "")
                    coords = loc_str.split(",") if loc_str and "," in loc_str else ["0.0", "0.0"]
                    try:
                        lng, lat = float(coords[0]), float(coords[1])
                    except (ValueError, IndexError):
                        lng, lat = 0.0, 0.0
                    pois.append(
                        POIInfo(
                            id=item.get("id", ""),
                            name=item.get("name", ""),
                            type=item.get("typecode", item.get("type", "景点")),
                            address=item.get("address", "") if isinstance(item.get("address"), str) else "",
                            location=Location(longitude=lng, latitude=lat),
                            tel=item.get("tel") if isinstance(item.get("tel"), str) and item.get("tel") else None
                        )
                    )
            return pois
            
        except Exception as e:
            print(f"POI搜索失败: {str(e)}")
            return []
    
    def get_weather(self, city: str) -> List[WeatherInfo]:
        """
        查询天气
        
        Args:
            city: 城市名称
            
        Returns:
            天气信息列表
        """
        try:
            # 调用MCP工具
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_weather",
                "arguments": {
                    "city": city
                }
            })
            
            print(f"天气查询结果: {result[:200]}...")
            
            data = _extract_json(result)
            weather_list = []
            if isinstance(data, dict) and "forecasts" in data:
                for item in data["forecasts"]:
                    weather_list.append(
                        WeatherInfo(
                            date=item.get("date", ""),
                            day_weather=item.get("dayweather", ""),
                            night_weather=item.get("nightweather", ""),
                            day_temp=item.get("daytemp", 0),
                            night_temp=item.get("nighttemp", 0),
                            wind_direction=item.get("daywind", ""),
                            wind_power=item.get("daypower", "")
                        )
                    )
            return weather_list
            
        except Exception as e:
            print(f"天气查询失败: {str(e)}")
            return []
    
    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """
        规划路线
        
        Args:
            origin_address: 起点地址
            destination_address: 终点地址
            origin_city: 起点城市
            destination_city: 终点城市
            route_type: 路线类型 (walking/driving/transit)
            
        Returns:
            路线信息
        """
        try:
            # 根据路线类型选择工具
            tool_map = {
                "walking": "maps_direction_walking_by_address",
                "driving": "maps_direction_driving_by_address",
                "transit": "maps_direction_transit_integrated_by_address"
            }
            
            tool_name = tool_map.get(route_type, "maps_direction_walking_by_address")
            
            # 构建参数
            arguments = {
                "origin_address": origin_address,
                "destination_address": destination_address
            }
            
            # 公共交通需要城市参数
            if route_type == "transit":
                if origin_city:
                    arguments["origin_city"] = origin_city
                if destination_city:
                    arguments["destination_city"] = destination_city
            else:
                # 其他路线类型也可以提供城市参数提高准确性
                if origin_city:
                    arguments["origin_city"] = origin_city
                if destination_city:
                    arguments["destination_city"] = destination_city
            
            # 调用MCP工具
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": tool_name,
                "arguments": arguments
            })
            
            print(f"路线规划结果: {result[:200]}...")
            
            data = _extract_json(result)
            if isinstance(data, dict) and "route" in data:
                route = data["route"]
                paths = route.get("paths", [])
                if paths:
                    path = paths[0]
                    distance = float(path.get("distance", 0))
                    duration = int(path.get("duration", 0))
                    steps = path.get("steps", [])
                    instruction_list = [step.get("instruction") for step in steps if step.get("instruction")]
                    description = " ➔ ".join(instruction_list[:5]) if instruction_list else "路线规划成功"
                    return {
                        "distance": distance,
                        "duration": duration,
                        "route_type": route_type,
                        "description": description,
                        "raw": data
                    }
            return {
                "distance": 0.0,
                "duration": 0,
                "route_type": route_type,
                "description": "路线规划获取完成"
            }
            
        except Exception as e:
            print(f"路线规划失败: {str(e)}")
            return {}
    
    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """
        地理编码(地址转坐标)

        Args:
            address: 地址
            city: 城市

        Returns:
            经纬度坐标
        """
        try:
            arguments = {"address": address}
            if city:
                arguments["city"] = city

            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_geo",
                "arguments": arguments
            })

            print(f"地理编码结果: {result[:200]}...")

            data = _extract_json(result)
            items = []
            if isinstance(data, dict):
                items = data.get("return") or data.get("geocodes") or []
            if items and isinstance(items, list):
                loc_str = items[0].get("location", "")
                if loc_str and "," in loc_str:
                    lng_str, lat_str = loc_str.split(",")
                    return Location(longitude=float(lng_str), latitude=float(lat_str))

            return None

        except Exception as e:
            print(f"地理编码失败: {str(e)}")
            return None

    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """
        获取POI详情

        Args:
            poi_id: POI ID

        Returns:
            POI详情信息
        """
        try:
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_search_detail",
                "arguments": {
                    "id": poi_id
                }
            })

            print(f"POI详情结果: {result[:200]}...")

            data = _extract_json(result)
            if isinstance(data, dict):
                return data

            return {"raw": result}

        except Exception as e:
            print(f"获取POI详情失败: {str(e)}")
            return {}


# 创建全局服务实例
_amap_service = None


def get_amap_service() -> AmapService:
    """获取高德地图服务实例(单例模式)"""
    global _amap_service
    
    if _amap_service is None:
        _amap_service = AmapService()
    
    return _amap_service

