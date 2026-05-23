from typing import Dict, Iterable, List

from neis_mcp.models import ApiParameter, NeisApiDefinition

BASE_URL = "https://open.neis.go.kr/hub"


def param(id_: str, name_ko: str, description: str = "") -> ApiParameter:
    return ApiParameter(id=id_, name_ko=name_ko, description=description)


API_DEFINITIONS: Dict[str, NeisApiDefinition] = {
    "get_school_info": NeisApiDefinition(
        tool_name="get_school_info",
        title="학교기본정보",
        api_res="schoolInfo",
        description="학교명, 주소, 전화번호, 홈페이지, 설립, 남녀공학 여부 등 학교 기본정보를 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/schoolInfo?ATPT_OFCDC_SC_CODE=T10&Type=json&pIndex=1&pSize=100",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "학교를 관리하는 시도교육청 기관코드"),
            param("SD_SCHUL_CODE", "행정표준코드", "각급 기관의 행정표준코드"),
            param("SCHUL_NM", "학교명", "학교의 명칭"),
            param("SCHUL_KND_SC_NM", "학교종류명", "학교의 종류"),
            param("LCTN_SC_NM", "시도명", "학교가 소속된 시도명"),
            param("FOND_SC_NM", "설립명", "학교 설립주체 구분"),
        ],
    ),
    "get_meal_service_diet_info": NeisApiDefinition(
        tool_name="get_meal_service_diet_info",
        title="급식식단정보",
        api_res="mealServiceDietInfo",
        description="학교 급식의 요리명, 원산지, 칼로리, 영양정보 등 일자별 식단 정보를 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE=T10&SD_SCHUL_CODE=9290083",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "시도교육청구분코드"),
            param("SD_SCHUL_CODE", "행정표준코드", "행정표준코드"),
            param("MMEAL_SC_CODE", "식사코드", "식사구분코드"),
            param("MLSV_YMD", "급식일자", "YYYYMMDD 형식 급식일자"),
            param("MLSV_FROM_YMD", "급식시작일자", "YYYYMMDD 형식 조회 시작일"),
            param("MLSV_TO_YMD", "급식종료일자", "YYYYMMDD 형식 조회 종료일"),
        ],
    ),
    "get_academy_instruction_info": NeisApiDefinition(
        tool_name="get_academy_instruction_info",
        title="학원교습소정보",
        api_res="acaInsTiInfo",
        description="학원 및 교습소의 등록상태, 정원, 분야, 계열, 과정, 수강료 공개 정보를 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/acaInsTiInfo?ATPT_OFCDC_SC_CODE=T10",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "시도교육청코드"),
            param("ADMST_ZONE_NM", "행정구역명", "행정구역명"),
            param("ACA_ASNUM", "학원지정번호", "학원지정번호"),
            param("ACA_NM", "학원명", "학원명"),
            param("REALM_SC_NM", "분야명", "분야명"),
            param("LE_ORD_NM", "교습계열명", "교습계열명"),
            param("LE_CRSE_NM", "교습과정명", "교습과정명"),
        ],
    ),
    "get_high_school_timetable": NeisApiDefinition(
        tool_name="get_high_school_timetable",
        title="고등학교시간표",
        api_res="hisTimetable",
        description="고등학교의 학년도, 학교, 계열, 학과, 학기, 학년, 강의실, 교시별 시간표를 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/hisTimetable?ATPT_OFCDC_SC_CODE=T10&SD_SCHUL_CODE=9290079",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "학교를 관리하는 시도교육청 기관코드"),
            param("SD_SCHUL_CODE", "행정표준코드", "각급 기관의 행정표준코드"),
            param("AY", "학년도", "한 학년의 과정을 배우는 기간"),
            param("SEM", "학기", "학기"),
            param("ALL_TI_YMD", "시간표일자", "YYYYMMDD 형식 시간표일자"),
            param("DGHT_CRSE_SC_NM", "주야과정명", "주간/야간 과정 구분"),
            param("ORD_SC_NM", "계열명", "교육과정 계열명"),
            param("DDDEP_NM", "학과명", "학과명"),
            param("GRADE", "학년", "학년"),
            param("CLRM_NM", "강의실명", "강의실명"),
            param("CLASS_NM", "학급명", "학급명"),
            param("TI_FROM_YMD", "시간표시작일자", "YYYYMMDD 형식 조회 시작일"),
            param("TI_TO_YMD", "시간표종료일자", "YYYYMMDD 형식 조회 종료일"),
        ],
    ),
    "get_school_schedule": NeisApiDefinition(
        tool_name="get_school_schedule",
        title="학사일정",
        api_res="SchoolSchedule",
        description="학교별 주요 행사 일자, 행사명, 행사내용, 학년별 행사 여부 등 학사일정을 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/SchoolSchedule?ATPT_OFCDC_SC_CODE=T10&SD_SCHUL_CODE=9296071",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "시도교육청구분코드"),
            param("SD_SCHUL_CODE", "행정표준코드", "행정표준코드"),
            param("DGHT_CRSE_SC_NM", "주야과정명", "주야과정구분명"),
            param("SCHUL_CRSE_SC_NM", "학교과정명", "학교과정구분명"),
            param("AA_YMD", "학사일자", "YYYYMMDD 형식 학사일자"),
            param("AA_FROM_YMD", "학사시작일자", "YYYYMMDD 형식 조회 시작일"),
            param("AA_TO_YMD", "학사종료일자", "YYYYMMDD 형식 조회 종료일"),
        ],
    ),
    "get_middle_school_timetable": NeisApiDefinition(
        tool_name="get_middle_school_timetable",
        title="중학교시간표",
        api_res="misTimetable",
        description="중학교의 학년도, 학교, 학기, 학년, 학급, 교시별 시간표를 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/misTimetable?ATPT_OFCDC_SC_CODE=T10&SD_SCHUL_CODE=7003714",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "학교를 관리하는 시도교육청 기관코드"),
            param("SD_SCHUL_CODE", "행정표준코드", "각급 기관의 행정표준코드"),
            param("AY", "학년도", "학년도"),
            param("SEM", "학기", "학기"),
            param("ALL_TI_YMD", "시간표일자", "YYYYMMDD 형식 시간표일자"),
            param("DGHT_CRSE_SC_NM", "주야과정명", "주간/야간 과정 구분"),
            param("GRADE", "학년", "학년"),
            param("CLASS_NM", "학급명", "학급명"),
            param("PERIO", "교시", "교시"),
            param("TI_FROM_YMD", "시간표시작일자", "YYYYMMDD 형식 조회 시작일"),
            param("TI_TO_YMD", "시간표종료일자", "YYYYMMDD 형식 조회 종료일"),
        ],
    ),
    "get_elementary_school_timetable": NeisApiDefinition(
        tool_name="get_elementary_school_timetable",
        title="초등학교시간표",
        api_res="elsTimetable",
        description="초등학교의 학년도, 학교, 학기, 학년, 학급, 교시별 시간표를 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/elsTimetable?ATPT_OFCDC_SC_CODE=T10&SD_SCHUL_CODE=9296037",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "학교를 관리하는 시도교육청 기관코드"),
            param("SD_SCHUL_CODE", "행정표준코드", "각급 기관의 행정표준코드"),
            param("AY", "학년도", "학년도"),
            param("SEM", "학기", "학기"),
            param("ALL_TI_YMD", "시간표일자", "YYYYMMDD 형식 시간표일자"),
            param("GRADE", "학년", "학년"),
            param("CLASS_NM", "학급명", "학급명"),
            param("PERIO", "교시", "교시"),
            param("TI_FROM_YMD", "시간표시작일자", "YYYYMMDD 형식 조회 시작일"),
            param("TI_TO_YMD", "시간표종료일자", "YYYYMMDD 형식 조회 종료일"),
        ],
    ),
    "get_class_info": NeisApiDefinition(
        tool_name="get_class_info",
        title="학급정보",
        api_res="classInfo",
        description="학교의 학년도, 학년, 주야과정, 학교과정, 계열, 학과별 학급 정보를 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/classInfo?ATPT_OFCDC_SC_CODE=T10&SD_SCHUL_CODE=9296037",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "시도교육청코드"),
            param("SD_SCHUL_CODE", "행정표준코드", "행정표준코드"),
            param("AY", "학년도", "학년도"),
            param("GRADE", "학년", "학년"),
            param("DGHT_CRSE_SC_NM", "주야과정명", "주야과정명"),
            param("SCHUL_CRSE_SC_NM", "학교과정명", "학교과정명"),
            param("ORD_SC_NM", "계열명", "계열명"),
            param("DDDEP_NM", "학과명", "학과명"),
        ],
    ),
    "get_school_major_info": NeisApiDefinition(
        tool_name="get_school_major_info",
        title="학교학과정보",
        api_res="schoolMajorinfo",
        description="고등학교 및 특수학교 시간표 조회 조건에 활용할 수 있는 학교 학과 정보를 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/schoolMajorinfo?ATPT_OFCDC_SC_CODE=T10",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "시도교육청코드"),
            param("SD_SCHUL_CODE", "행정표준코드", "행정표준코드"),
            param("DGHT_CRSE_SC_NM", "주야과정명", "주야과정명"),
            param("ORD_SC_NM", "계열명", "계열명"),
        ],
    ),
    "get_school_affiliation_info": NeisApiDefinition(
        tool_name="get_school_affiliation_info",
        title="학교계열정보",
        api_res="schulAflcoinfo",
        description="고등학교 및 특수학교 시간표 조회 조건에 활용할 수 있는 학교 계열 정보를 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/schulAflcoinfo?ATPT_OFCDC_SC_CODE=T10",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "시도교육청코드"),
            param("SD_SCHUL_CODE", "행정표준코드", "행정표준코드"),
            param("DGHT_CRSE_SC_NM", "주야과정명", "주야과정명"),
        ],
    ),
    "get_special_school_timetable": NeisApiDefinition(
        tool_name="get_special_school_timetable",
        title="특수학교시간표",
        api_res="spsTimetable",
        description="특수학교의 학년도, 학교, 학기, 학년, 과정, 강의실, 교시별 시간표를 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/spsTimetable?ATPT_OFCDC_SC_CODE=T10&SD_SCHUL_CODE=9290083",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "학교를 관리하는 시도교육청 기관코드"),
            param("SD_SCHUL_CODE", "행정표준코드", "각급 기관의 행정표준코드"),
            param("AY", "학년도", "학년도"),
            param("SEM", "학기", "학기"),
            param("ALL_TI_YMD", "시간표일자", "YYYYMMDD 형식 시간표일자"),
            param("SCHUL_CRSE_SC_NM", "학교과정명", "학교에서 운영 중인 교육과정 구분명"),
            param("GRADE", "학년", "학년"),
            param("CLRM_NM", "강의실명", "강의실명"),
            param("CLASS_NM", "학급명", "학급명"),
            param("PERIO", "교시", "교시"),
            param("TI_FROM_YMD", "시간표시작일자", "YYYYMMDD 형식 조회 시작일"),
            param("TI_TO_YMD", "시간표종료일자", "YYYYMMDD 형식 조회 종료일"),
        ],
    ),
    "get_timetable_classroom_info": NeisApiDefinition(
        tool_name="get_timetable_classroom_info",
        title="시간표강의실정보",
        api_res="tiClrminfo",
        description="고등학교 시간표 조회 조건에 활용할 수 있는 강의실 정보를 조회합니다.",
        sample_url="https://open.neis.go.kr/hub/tiClrminfo?ATPT_OFCDC_SC_CODE=T10&SD_SCHUL_CODE=9290071",
        parameters=[
            param("ATPT_OFCDC_SC_CODE", "시도교육청코드", "시도교육청코드"),
            param("SD_SCHUL_CODE", "행정표준코드", "행정표준코드"),
            param("AY", "학년도", "학년도"),
            param("GRADE", "학년", "학년"),
            param("SEM", "학기", "학기"),
            param("SCHUL_CRSE_SC_NM", "학교과정명", "학교과정명"),
            param("DGHT_CRSE_SC_NM", "주야과정명", "주야과정명"),
            param("ORD_SC_NM", "계열명", "계열명"),
            param("DDDEP_NM", "학과명", "학과명"),
        ],
    ),
}


def list_api_definitions() -> List[NeisApiDefinition]:
    return list(API_DEFINITIONS.values())


def api_parameter_ids(api: NeisApiDefinition) -> Iterable[str]:
    return (parameter.id for parameter in api.parameters)
