import boto3

access_key = 'AWS_액세스_키'
secret_key = 'AWS_비밀_액세스_키'

# S3 클라이언트 생성
s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
# s3 = boto3.client('s3') # aws configure로 직접 계정 설정한 경우

# 버킷 목록 가져오기
response = s3.list_buckets()
buckets = response['Buckets']
print('버킷 목록 조회')
for bucket in buckets:
    print(bucket['Name'])

# 업로드할 파일 경로와 S3 버킷 및 객체 키 지정
local_file_path = '업로드할_파일의_로컬_경로'
bucket_name = 'S3_버킷_이름'
s3_object_key = 'S3_객체_키'

# 파일 업로드
print(local_file_path, '파일 업로드')
s3.upload_file(local_file_path, bucket_name, s3_object_key)
print('파일 업로드 완료')
