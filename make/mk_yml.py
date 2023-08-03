# Embulk yml 파라미터
# oracle : https://www.rubydoc.info/gems/embulk-input-oracle/0.10.1
#          https://www.rubydoc.info/gems/embulk-output-oracle/0.8.7
# mysql  : 
import datetime as dt
import sys
import os
import re
import module.common as cm
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class YmlConfig:
    def __init__(self):
        # 변수 초기화
        self.execItem = {}
        self.configItem = {}
        self.query = ''
        self.configItem['query'] = ''
        self.configItem['table'] = ''
        self.execItem['max_threads'] = 1
        self.execItem['min_output_tasks'] = 1

        # TODO: type 별로 인자값 넣기
        self.setDriverPath('Oracle')

    def setDriverPath(self, type):
        # TODO: type -> oracle / mysql 따라 jdbc 경로 따로 지정
        if type == 'Oracle':
            self.configItem = {'driver_path' : fr"{cm.ROOT_PATH}\env\lib\ojdbc8.jar"}
        
        elif type == 'MySQL':
            pass

    def setType(self, type):
        self.configItem['type'] = type

    def setIp(self, ip):
        self.configItem['ip'] = ip
    
    def setPort(self, port):
        self.configItem['port'] = port

    def setUser(self, user):
        self.configItem['user'] = user
    
    def setPw(self, pw):
        self.configItem['pw'] = pw

    def setSid(self,sid):
        self.configItem['sid'] = sid
    
    def setQuery(self, str):
        # schema__table_name -> schema와 table명 분리
        item = str.split("__")

        # 최상위 항목이 스키마인 경우 Query 형태로 변환
        if item[0] != 'Query':
            self.configItem['schema'] = item[0]
            self.configItem['table'] = item[1]
            # Query 형태로 저장
            self.query = f"\"select * from {item[0]}.{item[1]}\""
            self.configItem['query'] = self.query

        # 최상위 항목이 Query인 경우
        else:
            self.configItem['query'] = f"\"{item[1]}\""
            # 'from' 다음의 문자열 추출
            afterFrom = item[1].lower().split('from', 1)[1].strip()
            # '.'을 기준으로 단어 분리
            words = afterFrom.split('.')
            self.configItem['schema'] = words[0]
            self.configItem['table'] = words[1]
        
    def setMaxThreads(self,maxThreads):
        self.execItem['max_threads'] = maxThreads
    
    def setMinOutputTasks(self, minOutputTasks):
        self.execItem['min_output_tasks'] = minOutputTasks

def exec(srcYmlConfig, tgtYmlConfig):
    # yml 파일 저장할 디렉토리 없으면 생성
    cm.createDir(cm.ROOT_PATH + r'\files\yml')

    # 날짜_테이블명.yml 포맷으로 생성
    ymlPath = fr'{cm.ROOT_PATH}\files\yml'
    date = dt.datetime.now()
    ymlPath += '\\' + srcYmlConfig.configItem['schema'] + '.' + srcYmlConfig.configItem['table'] + '_' + date.strftime("%Y%m%d") + '.yml'

    # 파일 Open
    f = open(ymlPath, 'w')

    # yml 파일 작성 - PARALLEL
    f.write(f'exec:\n')
    for k, v in srcYmlConfig.execItem.items():
        f.write(f'  {k}: {v}\n')

    # yml 파일 작성 - SOURCE DB 정보 
    f.write(f'in:\n')
    for k, v in srcYmlConfig.configItem.items():
        # SOURCE에는 schema, table 없이 query 항목만 작성
        if k != 'schema' and k != 'table':
            f.write(f'  {k}: {v}\n')
    
    # yml 파일 작성 - TARGET DB 정보 
    f.write(f'\nout:\n')
    for k, v in tgtYmlConfig.configItem.items():
        # TARGET에는 query 항목 없이 schema, table만 작성
        if k != 'query':
            f.write(f'  {k}: {v}\n')
    
    f.close()