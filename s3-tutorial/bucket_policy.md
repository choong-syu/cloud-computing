# S3 버킷 정책 설정 파일 예시

아래 JSON 코드는 S3 버킷 정책의 예시입니다.  
이 정책은 모든 사용자가 해당 버킷에 대해 모든 S3 작업을 수행할 수 있도록 허용합니다.  
실제 환경에 맞게 버킷 이름을 수정하여 사용하세요.

## 🔧 버킷 정책 JSON

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement1",
            "Principal": "*",
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "[버킷 ARN을 여기에 붙여넣기]/*"
        }
    ]
}
