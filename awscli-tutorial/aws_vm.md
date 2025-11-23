# AWS EC2 간단한 웹페이지 자동 생성 사용자 스크립트 (tee 버전)

이 파일은 AWS EC2 인스턴스 생성 시 User Data에 넣어  
간단한 웹페이지를 자동으로 띄우는 스크립트 예시입니다.

---

## User Data 스크립트 (Ubuntu Server 기준)

아래 스크립트를 EC2 생성 화면의 **User data** 입력창에 그대로 붙여넣습니다.

```bash
#!/bin/bash

# 패키지 목록 업데이트
apt update -y

# Apache2 웹서버 설치
apt install -y apache2

# Apache 자동 시작 설정 및 시작
systemctl enable apache2
systemctl start apache2

# tee를 사용하여 간단한 HTML 페이지 생성
echo "<h1>Cloud Computing Lab: Launching a VM with a Web Server Installed</h1>" | sudo tee /var/www/html/index.html > /dev/null

```
