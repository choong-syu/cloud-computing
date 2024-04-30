# Windows용 AWS CLI 실습 가이드

본 문서는 클라우드컴퓨팅 수업의 Windows용 AWS CLI 튜토리얼에 대한 실습 가이드입니다.

## 1. 최신 버전의 AWS CLI 설치 또는 업데이트
1. [링크](https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/getting-started-install.html) 로 접근하여 `AWS CLI 설치 및 업데이트 지침` 하단에 `Windows` 펼치기
2. `윈도우용 AWS CLI MSI 설치 프로그램 다운로드 및 실행 (64비트)` 하단의 [링크](https://awscli.amazonaws.com/AWSCLIV2.msi) 클릭
3. `AWSCLIV2.msi` 파일 다운로드 및 실행
4. 모두 `next` 버튼을 눌러 설치 진행.
5. 설치 완료 후 `명령 프롬프트` 창 실행
6. 아래와 같이 입력 후, 관련 내용이 출력되는 지 확인
   ```bash
   aws help
   ```

## 2. AWS CLI에서 리소스 조회 및 관리하기 위한 관리자 권한 사용자 생성
1. 웹브라우저에서 AWS의 [IAM 서비스](http://console.aws.amazon.com/iam)로 접근
2. `IAM > 사용자 > 사용자 생성`
   1. 사용자 이름 입력
   2. 다음 버튼 클릭
3. 권한 설정
   1. 직접 정책 연결 선택
   2. `AdministratorAccess` 를 검색하여 왼쪽에 체크
      -  AWS 계정에 대한 관리자 권한을 부여하는 IAM(Identity and Access Management) 정책 
   3. 다음 버튼 클릭
4. 검토 및 생성
   1. 내용 확인 후 
   2. 사용자 생성 버튼 클릭

## 3. 생성한 사용자의 액세스 키 (Access Key) 발급
1. `IAM > 사용자 > 사용자 아이디` 클릭
2. `보안 자격 증명` 탭 클릭
3. `액세스 키 만들기` 버튼 클릭
   - `Access Key`는 AWS의 다양한 서비스에 프로그래매틱 방식(즉, 코드나 소프트웨어를 통해)으로 접근할 수 있도록 해주는 자격증명임. API 호출이나 AWS CLI(Command Line Interface), SDKs(Software Development Kits) 등을 사용할 때 필요함.
4. 액세스 키 모범 사례 및 대안
   1. `Command Line Interface(CLI)` 클릭
   2. 아래 체크박스 체크 
   3. 다음 클릭
5. 설명 태그 설정 - 선택 사항
   1. `액세스 키 만들기` 클릭
6. 액세스 키 검색
   1. `액세스 키`와 `비밀 액세스 키`를 별도로 저장
      - 분실하거나 잊어버린 비밀 액세스 키는 검색할 수 없음. 대신 새 액세스 키를 생성하고 이전 키를 비활성화할 수 있음.
   * `Access Key`란?
      - 클라우드 서비스에서 사용되는 두 부분으로 구성된 키(ID와 비밀 키)
      - 프로그래밍 방식의 인증에 사용
      - `Access Key ID`: 공개적으로 사용되는 ID로, 사용자를 식별하는 데 사용됨
      - `Secret Access Key`: 개인 키로, API 요청을 서명하는 데 사용되며 절대 공개되어서는 안 됨. 이 키는 보안에 매우 중요하며, 신중하게 관리해야 함.

## 4. AWS CLI에서 사용자 인증 정보 설정
- AWS CLI는 '프로파일(Profile)'이라는 개념을 사용하여, 다양한 사용자의 자격증명을 관리함
- AWS CLI를 사용하는 개발자나 관리자는 서로 다른 계정, 리전, 권한 설정 등을 필요로 할 수 있기 때문에, 프로파일을 통해 이러한 다양한 환경을 손쉽게 전환하며 작업할 수 있음

### 4-1. 프로파일(Profile)
- AWS CLI 프로파일에 저장되는 정보는 크게 두 가지 범주로 나눌 수 있음
    1.  자격증명 (~/.aws/credentials 파일에 저장됨):  AWS 서비스에 액세스할 때 필요한 인증 정보를 저장
        1.  AWS Access Key ID (`aws_access_key_id`): Access Key ID
        2.  AWS Secret Access Key (`aws_secret_access_key`): Secret Access Key
        3.  예시
            ```bash 
            [default]
            aws_access_key_id = your_access_key_id
            aws_secret_access_key = your_secret_access_key

            [dev-profile]
            aws_access_key_id = your_dev_access_key_id
            aws_secret_access_key = your_dev_secret_access_key
            ```
    2.  구성 정보 (~/.aws/config 파일에 저장됨): 구성 파일은 자격증명 파일과 함께 사용되며, AWS CLI의 동작과 관련된 추가 설정 정보를 저장
        1.  Region (region): AWS 서비스가 위치한 지리적 지역임. CLI 명령이 실행될 때 대상 리전을 지정함.
        2.  Output Format (output): CLI 명령의 실행 결과로 반환되는 데이터의 형식을 지정함.
            -  가능한 형식은 json, text, table
        3. 예시
            ```bash
            [default]
            region = us-west-2
            output = json

            [profile dev-profile]
            region = us-east-1
            output = text
            ```

### 4-2. 프로파일 설정 및 확인 방법
- 프로파일을 설정하는 방법들
    1.  대화형 프로파일 자격증명 및 구성 설정
        1.  명령 프롬프트 창에 `aws configure` 입력
        2.  아래 순서대로 정보 입력
            1.  AWS Access Key ID
            2.  AWS Secret Access Key
            3.  Region Name (e.g. `ap-northeast-2`)
            4.  Output Format (e.g. `json`)
    2.  명령줄 기반 프로파일 자격증명 및 구성 설정
        1.  명령줄에서 AWS CLI 구성을 세부적으로 변경하는 방법임.
        2.  `aws configure set` 명령을 사용한 기본 사용법
            ```bash
            aws configure set variable_name value [--profile profile-name]
            ```
        3.  각 속성 변경 예시
            1. 액세스 키 및 비밀 키 설정
                ```bash
                aws configure set aws_access_key_id YOUR_ACCESS_KEY_ID
                aws configure set aws_secret_access_key YOUR_SECRET_ACCESS_KEY
                ```
            2. 리전 설정 변경
                ```bash
                aws configure set region REGION
                ```
            3. 출력 형식 변경
                ```bash
                aws configure set output OUTPUT
                ```
- 특정 프로파일을 생성하거나 구성하는 방법
    1.  `--profile [설정하고자 하는 프로필 이름]`을 옵션으로 지정
    2.  대화형 프로파일 자격증명 및 구성 설정 예시
        ``` bash
        aws configure --profile new-profile
        ```  
    4.  명령줄 기반 프로파일 자격증명 및 구성 설정 예시
        ``` bash
        aws configure set region ap-northeast-2 --profile new-profile 
        aws configure set aws_access_key_id YOUR_ACCESS_KEY_ID --profile new-profile 
        aws configure set aws_secret_access_key YOUR_SECRET_ACCESS_KEY --profile new-profile
        aws configure set output json --profile new-profile 
        ```  
    
- 프로파일을 확인하는 방법들
    - 설정된 프로파일을 확인하기 위해 다음 명령을 사용
        - 현재 시점에 설정된 프로필의 사용자 정보 확인
            ``` bash
            aws configure list
            ```
        - `new-profile` 라는 이름의 프로필 사용자 정보 확인
            ``` bash
            aws configure list --profile new-profile
            ```
    - 설정된 모든 프로파일 정보를 아래 파일들을 통하여 확인 가능
        - Credentials 파일: C:\Users\[Your-Username]\.aws\credentials
        - Config 파일: C:\Users\[Your-Username]\.aws\config
    
- 프로필 명시적 지정 방법
    - aws 명령을 수행할 때 사용되는 자격증명의 프로필을 명시적으로 지정하는 방법
        ``` bash
        set AWS_PROFILE=[프로필 이름]
        ```
        - 예시
            ``` bash
            set AWS_PROFILE=new-profile
            ```
    - aws 명령을 수행할 때 사용되는 명시적인 자격증명의 프로필 설정을 취소하는 방법 (default 프로필을 사용)
        ``` bash
        set AWS_PROFILE=
        ```

- 현재 AWS 명령을 수행할 때 사용되는 AWS 자격증명이 무엇인지 확인하는 방법
    - 올바른 AWS 자격증명으로 실행되고 있는지 확인하는 용도
    - 아래 명령어 실행
        ```bash
        aws sts get-caller-identity
        ```
### 4-3.임시 보안 자격증명
- AWS 리소스에 대한 임시 액세스가 필요할 때, `AWS Security Token Service (STS)`를 사용하여 일시적인 보안 자격증명을 생성할 수 있음
- 유즈케이스
    - 일시적으로 조직에 합류한 임시 직원이나 계약자에게 필요한 기간 동안만 리소스에 접근할 수 있는 권한을 부여
    - 인턴 개발자가 기존 애플리케이션을 테스트할 때, 프로덕션 데이터베이스나 중요 시스템에 임시로 접근할 수 있는 권한을 부여
    - 특정 보고서를 생성하거나 분석을 위해 일시적으로 데이터에 접근해야 할 때, 임시 자격증명을 사용하여 해당 기간 동안만 데이터 접근을 허용
- AWS STS와 토큰
    - AWS Security Token Service (STS)는 AWS 사용자에게 임시 보안 자격증명을 제공하는 서비스이며 세 가지 주요 요소가 포함됨.
        1. `액세스 키 ID (Access Key ID)`
        2. `비밀 액세스 키 (Secret Access Key)`
        3. `세션 토큰 (Session Token)`: 임시 자격증명에 추가되는 보안 요소로, 이 토큰이 포함된 자격증명을 가지고 AWS 리소스에 접근할 수 있음
    - 이 자격증명을 사용하면 지정된 유효 시간 동안만 AWS 리소스에 접근할 수 있으며, **유효 시간이 지나면 자동으로 접근이 차단**됨.
- 임시 보안 자격증명을 발급 받는 방법
    - 기본 임시 토큰 발급
        ```bash
        aws sts get-session-token
        ```
        - 가장 기본적인 형태의 임시 자격증명을 발급
        - 발급된 자격증명은 기본적으로 12시간 동안 유효
        - 액세스 키 ID, 비밀 액세스 키, 세션토큰, 유효기간 값을 얻을 수 있음
    - 유효 시간 설정을 통한 임시 토큰 발급
        ```bash
        aws sts get-session-token --duration-seconds 3600
        ```
        - 이 옵션을 사용하면 자격증명의 유효 시간을 조정할 수 있음.
        - 최소값: 900초 (15분)
        - 최대값: 129600초 (36시간)
## 5. Amazon Simple Systems Manager (SSM)를 통한 정보 조회
- Amazon Simple Systems Manager는 AWS 환경에서 인프라 관리, 보안 및 규정 준수를 도와주는 관리 서비스
- 인프라 상태의 조회, 설정 변경, 자동화된 스크립트 실행 등 다양한 작업을 수행할 수 있음
- SSM을 활용하기 위해 필요한 개념들
    - SSM Parameter Store
        - AWS 환경 내에서 `매개변수(Parameters)`을 안전하게 저장하고 관리할 수 있는 서비스
    - 매개변수(Parameters): 시스템이나 프로그램이 작업을 수행하기 위해 필요한 정보이며 종류는 크게 두 가지임.
        1. **AWS 서비스 관련 파라미터 (AWS-Managed Parameters or Public Parameters)**
            - AWS에서 관리하는 파라미터로, 특정 AWS 서비스와 연관된 정보를 제공함.
            - 예를 들면,
                - AWS에서 지원하는 지역(Regions) 목록
                - AWS 서비스 목록
                - EC2 서비스 엔드포인트
                - 특정 리전에서 사용 가능한 가용 영역(Availability Zones)
        2. **사용자 정의 파라미터 (Custom Parameters)**
            - 사용자가 직접 생성하고 관리하는 파라미터
            - 특정 애플리케이션의 설정, 비밀번호, 데이터베이스 문자열, API 키 등과 같은 민감한 정보를 안전하게 저장하고 관리
    - 경로 (Path)
        - 특정 파라미터 또는 파라미터 그룹을 식별하는 데 사용되는 주소
        - 경로를 통해 파라미터 스토어 내의 구성 데이터나 설정을 계층적으로 접근 가능
        - AWS의 서비스 관련 파라미터들에 대한 경로들 예제
            - `/aws/service/list`: AWS에서 제공하는 전체 서비스에 대한 경로 목록
            - `/aws/service/global-infrastructure/regions`: AWS에서 지원하는 모든 지역(Regions) 목록
            - `/aws/service/global-infrastructure/regions/ap-northeast-2/services`: 특정 리전에서 제공하는 AWS 서비스 목록
            - `/aws/service/global-infrastructure/regions/ap-northeast-2/services/ec2/endpoint`: 특정 리전의 EC2 서비스 엔드포인트
            - ``: 특정 리전에서 사용 가능한 가용 영역
- SSM 관련 AWS CLI 명령어 사용 방법
    ```bash
    aws ssm get-parameters-by-path --path [PATH] --query [QUERY] --output [OUTPUT]
    ```
    - SSM의 특정 경로의 매개변수들을 조회하는 명령어
    - `--path [PATH]`: 이 옵션은 조회하고자 하는 파라미터들이 저장된 경로를 지정함. 경로는 /로 시작하며, 계층적 구조를 가질 수 있음. 예를 들어, /application/dev/database 경로에서 개발 환경의 데이터베이스 관련 파라미터를 조회할 수 있음.
    - `--query [QUERY]`: --query 옵션은 조회 결과에서 필요한 부분만을 추출하기 위해 사용됨. 이 옵션은 JMESPath(JSON Matching Expressions Path) 쿼리 언어를 사용함. 예를 들어, Parameters[].Value 쿼리는 반환된 파라미터 목록에서 각 파라미터의 값을 추출함. 이를 통해 결과 데이터를 더욱 정제하여 사용할 수 있음.
    - `--output [OUTPUT]`: --output 옵션은 명령어의 실행 결과가 어떻게 출력될지를 결정함. 가능한 값은 json, text, table, yaml 등이 있음.
- SSM 관련 AWS CLI 명령어 사용 예제
    1. AWS에서 제공하는 경로(Path) 목록 조회
        ```bash
        aws ssm get-parameters-by-path --path /aws/service/list --query Parameters[].Value --output json
        ```
    2. AWS의 리전 목록 및 목록 개수 조회
        ```bash
        aws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions --query Parameters[].Value
        ```
        ```bash
        aws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions --query length(Parameters[].Value)
        ```
    3. AWS의 전체 서비스 목록 및 목록 개수 조회
        ```bash
        aws ssm get-parameters-by-path --path /aws/service/global-infrastructure/services --query Parameters[].Value
        ```
        ```bash
        aws ssm get-parameters-by-path --path /aws/service/global-infrastructure/services --query length(Parameters[].Value)
        ```
    4. `ap-northeast-2` 리전에서 제공하는 AWS 서비스 목록 및 목록 개수 조회
        ```bash
        aws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions/ap-northeast-2/services --query Parameters[].Value
        ```
        ```bash
        aws ssm get-parameters-by-path --path /aws/service/global-infrastructure/regions/ap-northeast-2/services --query length(Parameters[].Value)
        ```
    5. `ap-northeast-2` 리전의 EC2 서비스 엔드포인트
        ```bash
        aws ssm get-parameter --name /aws/service/global-infrastructure/regions/ap-northeast-2/services/ec2/endpoint --query Parameter.Value
        ```
    6. `ap-northeast-2` 리전에서 사용 가능한 모든 가용 영역(Availability Zone) 정보 조회
        ```bash
        aws ec2 describe-availability-zones --region ap-northeast-2 --query AvailabilityZones[].ZoneName
        ```
  