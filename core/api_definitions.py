# -*- coding: utf-8 -*-
"""
API Definitions for ReinfoLib QGIS Plugin

Contains metadata and configuration for all supported APIs.

ReinfoLib API URL Format:
- Non-tile APIs: {endpoint}?param1=value1&param2=value2
- Tile APIs: {endpoint}?response_format=geojson&z={zoom}&x={x}&y={y}&other_params
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ApiInfo:
    """Information about a single API endpoint."""

    api_id: str
    name_ja: str
    name_en: str
    endpoint: str
    category: str
    geometry_type: Optional[str]  # 'point', 'polygon', 'line', or None
    output_format: str  # 'json', 'geojson', 'pbf'
    uses_tile: bool
    description_ja: str
    description_en: str
    required_params: List[str] = field(default_factory=list)  # Additional required params


class ApiDefinitions:
    """Registry of all supported API endpoints."""

    BASE_URL = 'https://www.reinfolib.mlit.go.jp/ex-api/external'

    # Categories
    CAT_PRICE = 'price'
    CAT_URBAN = 'urban'
    CAT_FACILITY = 'facility'
    CAT_DISASTER = 'disaster'
    CAT_OTHER = 'other'

    CATEGORIES = {
        CAT_PRICE: {'ja': '価格情報', 'en': 'Price Information'},
        CAT_URBAN: {'ja': '都市計画', 'en': 'Urban Planning'},
        CAT_FACILITY: {'ja': '周辺施設', 'en': 'Facilities'},
        CAT_DISASTER: {'ja': '防災情報', 'en': 'Disaster Information'},
        CAT_OTHER: {'ja': 'その他', 'en': 'Other'},
    }

    # API Definitions
    APIS: Dict[str, ApiInfo] = {
        # ===== Price Information APIs =====
        'XIT001': ApiInfo(
            api_id='XIT001',
            name_ja='不動産価格情報',
            name_en='Real Estate Price',
            endpoint=f'{BASE_URL}/XIT001',
            category=CAT_PRICE,
            geometry_type=None,
            output_format='json',
            uses_tile=False,
            description_ja='不動産取引価格・成約価格情報（テーブルデータ）',
            description_en='Real estate transaction prices',
            required_params=['area', 'year'],
        ),
        'XIT002': ApiInfo(
            api_id='XIT002',
            name_ja='市区町村一覧',
            name_en='Municipality List',
            endpoint=f'{BASE_URL}/XIT002',
            category=CAT_PRICE,
            geometry_type=None,
            output_format='json',
            uses_tile=False,
            description_ja='都道府県内市区町村一覧（テーブルデータ）',
            description_en='List of municipalities in prefecture',
            required_params=['area'],
        ),
        'XPT001': ApiInfo(
            api_id='XPT001',
            name_ja='不動産価格ポイント',
            name_en='Real Estate Price Points',
            endpoint=f'{BASE_URL}/XPT001',
            category=CAT_PRICE,
            geometry_type='point',
            output_format='geojson',
            uses_tile=True,
            description_ja='不動産取引価格の位置情報（地図表示可）',
            description_en='Real estate transaction price locations',
            required_params=['from', 'to'],
        ),
        'XPT002': ApiInfo(
            api_id='XPT002',
            name_ja='地価公示・地価調査ポイント',
            name_en='Land Price Points',
            endpoint=f'{BASE_URL}/XPT002',
            category=CAT_PRICE,
            geometry_type='point',
            output_format='geojson',
            uses_tile=True,
            description_ja='地価公示・地価調査の位置情報（地図表示可）',
            description_en='Land price survey locations',
            required_params=['year'],
        ),

        # ===== Urban Planning APIs =====
        'XKT001': ApiInfo(
            api_id='XKT001',
            name_ja='都市計画区域/区域区分',
            name_en='Urban Planning Area',
            endpoint=f'{BASE_URL}/XKT001',
            category=CAT_URBAN,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='都市計画区域・市街化区域・調整区域',
            description_en='Urban planning and urbanization areas',
        ),
        'XKT002': ApiInfo(
            api_id='XKT002',
            name_ja='用途地域',
            name_en='Zoning',
            endpoint=f'{BASE_URL}/XKT002',
            category=CAT_URBAN,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='用途地域（住居・商業・工業等）',
            description_en='Land use zoning areas',
        ),
        'XKT003': ApiInfo(
            api_id='XKT003',
            name_ja='立地適正化計画',
            name_en='Location Optimization',
            endpoint=f'{BASE_URL}/XKT003',
            category=CAT_URBAN,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='居住誘導区域・都市機能誘導区域',
            description_en='Location optimization plan areas',
        ),
        'XKT014': ApiInfo(
            api_id='XKT014',
            name_ja='防火・準防火地域',
            name_en='Fire Prevention Area',
            endpoint=f'{BASE_URL}/XKT014',
            category=CAT_URBAN,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='防火地域・準防火地域',
            description_en='Fire prevention zones',
        ),
        'XKT028': ApiInfo(
            api_id='XKT028',
            name_ja='地区計画',
            name_en='District Plan',
            endpoint=f'{BASE_URL}/XKT028',
            category=CAT_URBAN,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='地区計画区域',
            description_en='District plan areas',
        ),
        'XKT030': ApiInfo(
            api_id='XKT030',
            name_ja='都市計画道路',
            name_en='Urban Planning Roads',
            endpoint=f'{BASE_URL}/XKT030',
            category=CAT_URBAN,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='都市計画道路',
            description_en='Urban planning roads',
        ),
        'XKT031': ApiInfo(
            api_id='XKT031',
            name_ja='人口集中地区',
            name_en='Densely Inhabited District',
            endpoint=f'{BASE_URL}/XKT031',
            category=CAT_URBAN,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='DID（人口集中地区）',
            description_en='Densely Inhabited District (DID)',
        ),

        # ===== Facility APIs =====
        'XKT004': ApiInfo(
            api_id='XKT004',
            name_ja='小学校区',
            name_en='Elementary School District',
            endpoint=f'{BASE_URL}/XKT004',
            category=CAT_FACILITY,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='小学校の通学区域',
            description_en='Elementary school attendance areas',
        ),
        'XKT005': ApiInfo(
            api_id='XKT005',
            name_ja='中学校区',
            name_en='Junior High School District',
            endpoint=f'{BASE_URL}/XKT005',
            category=CAT_FACILITY,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='中学校の通学区域',
            description_en='Junior high school attendance areas',
        ),
        'XKT006': ApiInfo(
            api_id='XKT006',
            name_ja='学校',
            name_en='Schools',
            endpoint=f'{BASE_URL}/XKT006',
            category=CAT_FACILITY,
            geometry_type='point',
            output_format='geojson',
            uses_tile=True,
            description_ja='学校施設の位置',
            description_en='School facility locations',
        ),
        'XKT007': ApiInfo(
            api_id='XKT007',
            name_ja='保育園・幼稚園等',
            name_en='Nurseries/Kindergartens',
            endpoint=f'{BASE_URL}/XKT007',
            category=CAT_FACILITY,
            geometry_type='point',
            output_format='geojson',
            uses_tile=True,
            description_ja='保育園・幼稚園・こども園',
            description_en='Nurseries and kindergartens',
        ),
        'XKT010': ApiInfo(
            api_id='XKT010',
            name_ja='医療機関',
            name_en='Medical Facilities',
            endpoint=f'{BASE_URL}/XKT010',
            category=CAT_FACILITY,
            geometry_type='point',
            output_format='geojson',
            uses_tile=True,
            description_ja='病院・診療所',
            description_en='Hospitals and clinics',
        ),
        'XKT011': ApiInfo(
            api_id='XKT011',
            name_ja='福祉施設',
            name_en='Welfare Facilities',
            endpoint=f'{BASE_URL}/XKT011',
            category=CAT_FACILITY,
            geometry_type='point',
            output_format='geojson',
            uses_tile=True,
            description_ja='高齢者・障害者・児童福祉施設',
            description_en='Welfare facilities',
        ),
        'XKT015': ApiInfo(
            api_id='XKT015',
            name_ja='駅別乗降客数',
            name_en='Station Ridership',
            endpoint=f'{BASE_URL}/XKT015',
            category=CAT_FACILITY,
            geometry_type='point',
            output_format='geojson',
            uses_tile=True,
            description_ja='鉄道駅の位置・乗降客数',
            description_en='Train station ridership data',
        ),
        'XKT022': ApiInfo(
            api_id='XKT022',
            name_ja='図書館',
            name_en='Libraries',
            endpoint=f'{BASE_URL}/XKT022',
            category=CAT_FACILITY,
            geometry_type='point',
            output_format='geojson',
            uses_tile=True,
            description_ja='図書館',
            description_en='Libraries',
        ),
        'XKT023': ApiInfo(
            api_id='XKT023',
            name_ja='市区町村役場等',
            name_en='Municipal Offices',
            endpoint=f'{BASE_URL}/XKT023',
            category=CAT_FACILITY,
            geometry_type='point',
            output_format='geojson',
            uses_tile=True,
            description_ja='役場・公民館等',
            description_en='Municipal offices and community centers',
        ),

        # ===== Disaster APIs =====
        'XKT026': ApiInfo(
            api_id='XKT026',
            name_ja='洪水浸水想定区域',
            name_en='Flood Inundation Area',
            endpoint=f'{BASE_URL}/XKT026',
            category=CAT_DISASTER,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='洪水浸水想定区域',
            description_en='Flood inundation hazard areas',
        ),
        'XKT027': ApiInfo(
            api_id='XKT027',
            name_ja='高潮浸水想定区域',
            name_en='Storm Surge Area',
            endpoint=f'{BASE_URL}/XKT027',
            category=CAT_DISASTER,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='高潮浸水想定区域',
            description_en='Storm surge hazard areas',
        ),
        'XKT029': ApiInfo(
            api_id='XKT029',
            name_ja='土砂災害警戒区域',
            name_en='Landslide Hazard Area',
            endpoint=f'{BASE_URL}/XKT029',
            category=CAT_DISASTER,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='土砂災害警戒区域・特別警戒区域',
            description_en='Landslide hazard zones',
        ),
        'XGT001': ApiInfo(
            api_id='XGT001',
            name_ja='指定緊急避難場所',
            name_en='Emergency Shelters',
            endpoint=f'{BASE_URL}/XGT001',
            category=CAT_DISASTER,
            geometry_type='point',
            output_format='geojson',
            uses_tile=True,
            description_ja='指定緊急避難場所',
            description_en='Designated emergency shelters',
        ),
        'XKT018': ApiInfo(
            api_id='XKT018',
            name_ja='災害危険区域',
            name_en='Disaster Risk Area',
            endpoint=f'{BASE_URL}/XKT018',
            category=CAT_DISASTER,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='建築基準法に基づく災害危険区域',
            description_en='Disaster risk areas under Building Standards Act',
        ),
        'XKT025': ApiInfo(
            api_id='XKT025',
            name_ja='大規模盛土造成地',
            name_en='Large Fill Areas',
            endpoint=f'{BASE_URL}/XKT025',
            category=CAT_DISASTER,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='大規模盛土造成地',
            description_en='Large-scale fill land areas',
        ),

        # ===== Other APIs =====
        'XKT013': ApiInfo(
            api_id='XKT013',
            name_ja='将来推計人口メッシュ',
            name_en='Population Projection Mesh',
            endpoint=f'{BASE_URL}/XKT013',
            category=CAT_OTHER,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='将来推計人口（2020-2050年）',
            description_en='Population projection mesh (2020-2050)',
        ),
        'XKT019': ApiInfo(
            api_id='XKT019',
            name_ja='自然公園地域',
            name_en='Natural Parks',
            endpoint=f'{BASE_URL}/XKT019',
            category=CAT_OTHER,
            geometry_type='polygon',
            output_format='geojson',
            uses_tile=True,
            description_ja='国立公園・国定公園等',
            description_en='National and quasi-national parks',
        ),
    }

    @classmethod
    def get_api(cls, api_id: str) -> Optional[ApiInfo]:
        """Get API info by ID."""
        return cls.APIS.get(api_id)

    @classmethod
    def get_apis_by_category(cls, category: str) -> List[ApiInfo]:
        """Get all APIs in a category."""
        return [api for api in cls.APIS.values() if api.category == category]

    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get all category keys."""
        return list(cls.CATEGORIES.keys())

    @classmethod
    def get_category_name(cls, category: str, lang: str = 'ja') -> str:
        """Get localized category name."""
        cat_info = cls.CATEGORIES.get(category, {})
        return cat_info.get(lang, category)

    @classmethod
    def get_tile_apis(cls) -> List[ApiInfo]:
        """Get all APIs that use tile coordinates."""
        return [api for api in cls.APIS.values() if api.uses_tile]
