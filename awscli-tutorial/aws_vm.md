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


# Private Subnet에 있는 인스턴스로 SSH 접속하는 방법

Private Subnet에 있는 EC2 인스턴스는 인터넷에서 직접 접근할 수 없습니다.  
하지만 다음 두 가지 방법을 사용하면 안전하게 SSH 접속이 가능합니다.

---

## 방법 1: Bastion (Jump) Host 이용 – 두 단계 접속

1. Public Subnet에 있는 Bastion Host에 먼저 접속합니다.
   ```bash
   ssh -i "mykey.pem" ubuntu@[Public-IP]
   ```

2. Bastion Host 내부에서 Private 인스턴스로 접속합니다.
   ```bash
   ssh ubuntu@[Private-IP]
   ```

### 준비 사항
- Public Subnet에 **Bastion Host** 필요  
- Private 인스턴스의 **Private IP** 필요  
- 두 인스턴스 모두에 사용 가능한 **동일한 PEM 키 파일**

---

## 방법 2: ProxyCommand를 사용하여 한 번에 SSH 접속

ProxyCommand를 사용하면 Public 인스턴스를 중계 서버(proxy)로 활용하여  
**한 줄 SSH 명령어로 Private 인스턴스에 접속**할 수 있습니다.

### SSH 템플릿

```bash
ssh -i "[개인 키]" -o ProxyCommand="ssh -W %h:%p [public-username]@[public-IP] -i [개인 키]" [private-username]@[private-IP]
```

- `-W %h:%p` : SSH Proxy Forwarding  
- Public 인스턴스를 "중계 서버(Jump Host)"로 사용  
- 두 인스턴스 모두 동일한 PEM 키 필요

---

## 예제

**Public 인스턴스**  
- 사용자: `ubuntu`  
- Public IP: `3.35.220.80`  
- 키 파일: `test-key.pem`

**Private 인스턴스**  
- 사용자: `ubuntu`  
- Private IP: `10.0.1.163`
- 키 파일: `test-key.pem`

### 실제 접속 명령

```bash
ssh -i "test-key.pem" -o ProxyCommand="ssh -W %h:%p ubuntu@3.35.220.80 -i test-key.pem" ubuntu@10.0.1.163
```

---

