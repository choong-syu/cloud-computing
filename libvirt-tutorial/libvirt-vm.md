# Libvirt 실습 가이드 — 학생별 외부 서버 VM 환경

본 문서는 [기존 libvirt 튜토리얼](libvirt-tutorial.md)을 학생별 외부 서버 `vm*` 환경에 맞게 수정한 실습 가이드임.

> **실행 위치**: Windows PowerShell → SSH로 접속한 외부 서버 `vm*` → 그 안에 생성하는 내부 VM `vm01`, `vm02` 순서임. 별도 표시가 없으면 명령어는 **외부 서버의 root 셸**에서 실행함. `virsh console`로 접속한 동안에는 **내부 VM의 ubuntu 셸**에서 실행함. `Ctrl + ]`는 VM을 끄는 것이 아니라 외부 서버 셸로 돌아오는 키임.
>
> **자원 기준**: 외부 서버 RAM 약 2GB, CPU 2개, `/dev/kvm` 사용 가능 환경. 내부 VM은 각각 **512MB**로 설정하고, 복제 실습 후 clone을 종료하여 동시에 최대 2대만 실행함. 512MB는 이 기본 실습용 설정이며 추가 프로그램이나 부하 실습에는 메모리 증설이 필요함.
>
> 각자의 외부 서버는 독립된 실습 환경이므로 내부 이름 `vm01`, `vm02`, `vir-network`는 모든 학생이 그대로 사용함. 외부 서버의 배정 번호와 내부 VM 이름을 혼동하지 않음.
>
> 처음 실습하는 서버를 기준으로 함. 재실행할 때는 기존 VM·네트워크·파일의 존재를 먼저 확인하고, 다른 실습 데이터를 덮어쓰지 않음. 내부 VM의 비밀번호 `1111`은 이 격리된 교육 환경에서만 사용함.

### 외부 서버 접속 — Windows PowerShell
아래 `44` 두 곳을 본인에게 배정된 번호로 변경하고, 개인별로 전달받은 SSH 비밀번호를 입력함.
```powershell
ssh "student44:vm44@gate.su-cloud.syu.ac.kr" -p 2222
```
접속 후 다음 명령으로 배정된 서버와 자원을 확인함.
```bash
hostname
free -h
nproc
ls -l /dev/kvm
df -h /
```

# 1. 실습 준비
* 실습 시에 원활한 작업을 위해 슈퍼유저 권한을 가지고 로그인

### 1-1. 실습을 위한 권한 설정 (슈퍼유저로 로그인)
```bash
sudo -i
```
* `pwd` 명령어를 입력해보면 root 계정의 home 경로인 `/root`로 변경된 것을 확인할 수 있음

### 1-2. 클라우드 전용 Ubuntu OS 이미지 파일 다운로드
```bash
wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
wget -O SHA256SUMS https://cloud-images.ubuntu.com/noble/current/SHA256SUMS
grep ' noble-server-cloudimg-amd64.img$\| \*noble-server-cloudimg-amd64.img$' SHA256SUMS | sha256sum -c -
```

> `OK`를 확인한 뒤 진행함. `current` 이미지는 갱신되므로 배포 날짜에 따라 버전·용량이 달라질 수 있음. 수업 담당자는 수업에 사용할 이미지와 SHA256을 함께 보관하는 것을 권장함.

### 1-3. 현재 경로에서 다운로드된 img 파일 확인
```bash
ls -l
```

### 1-4. 실습에 필요한 라이브러리 일괄 설치
```bash
apt update && apt install -y libvirt-clients libvirt-daemon-system virtinst cloud-image-utils python3-libvirt guestfs-tools qemu-utils

```

### 1-5. 다운로드한 img 파일의 포맷 확인
```bash
qemu-img info noble-server-cloudimg-amd64.img
```
- `file format: qcow2` 확인


---



# 2. 가상 네트워크 정의
간단한 가상 네트워크 정의 xml 파일을 vir-network.xml라는 이름으로 작성하기

### 2-1. `vi` 텍스트 에디터를 사용하여 `vir-network.xml` 파일을 생성

```bash
vi vir-network.xml
```
```bash
:set paste
```
* vi나 vim에서 외부에서 복사한 코드를 붙여넣을 때, 자동 들여쓰기(auto indent)가 적용되어  
코드의 원래 들여쓰기가 어긋나는 문제가 발생할 수 있음.
* 이를 방지하기 위해 명령 모드로 진입하여 **`:set paste`** 명령어를 사용


### 2-2. `vi` 에디터가 열리면 입력 모드 `i` 입력 후, 아래의 XML 코드를 입력 및 저장하고 나오기 (`esc 키` -> :`wq`)
```xml
<network>
  <name>vir-network</name>
  <bridge name="virbr1"/>
  <forward mode="nat"/>
  <ip address="192.168.123.1" netmask="255.255.255.0">
    <dhcp>
      <range start="192.168.123.2" end="192.168.123.254"/>
    </dhcp>
  </ip>
</network>
```

### 2-3. 작성된 문서 확인
```bash
cat vir-network.xml
```

### 2-4. 가상 네트워크 정의
```bash
virsh net-define vir-network.xml
```

### 2-5. 가상 네트워크 목록에서 정의된(inactive 상태) 네트워크 확인
```bash
virsh net-list --all
```

### 2-6. 현재 리눅스 네트워크 구성 확인
```bash
ip address
```
* 아직 `virbr1` 브릿지가 보이지 않음

### 2-7. 가상 네트워크 시작
```bash
virsh net-start vir-network
```

### 2-8. 가상 네트워크 목록에서 시작된(active 상태) 네트워크 확인
```bash
virsh net-list --all
```

### 2-9. 현재 리눅스 네트워크 구성 확인
```bash
ip address
```
* `virbr1` 브릿지가 확인됨

### 2-10. 가상 네트워크 가 부팅 시 자동으로 시작되도록 설정
```bash
virsh net-autostart vir-network
```

### 2-11. 가상 네트워크 정보 조회
```bash
virsh net-info vir-network
```


---



# 3. 가상 머신의 초기화 작업 준비
* cloud-init: 가상 머신 또는 클라우드 인스턴스에서 초기화 및 설정 작업을 자동화하기 위한 프로그램

### 3-1. VM 별 user-data 및 meta-data 파일 준비를 위한 폴더 생성
- VM 이미지 및 cloud-init 데이터를 보관하는 기본 경로
  `/var/lib/libvirt/images/`
- VM 별로 다음과 같은 서브 디렉토리를 생성
  `/var/lib/libvirt/images/vm01`  
  `/var/lib/libvirt/images/vm02`
```bash
mkdir -p /var/lib/libvirt/images/vm01 /var/lib/libvirt/images/vm02
```
```bash
ls /var/lib/libvirt/images
```

### 3-2. `vi` 텍스트 에디터를 사용하여 `user-data` 파일을 생성

```bash
vi /var/lib/libvirt/images/vm01/user-data

```

### 3-3. `vi` 에디터가 열리면 입력 모드 `i` 입력 후, 아래의 YAML 코드를 입력 및 저장하고 나오기 (`esc 키` -> :`wq`)
```yaml
#cloud-config
hostname: vm01
manage_etc_hosts: true
users:
  - name: ubuntu
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups:
      - users
      - admin
    shell: /bin/bash
    plain_text_passwd: "1111"
    lock_passwd: false
ssh_pwauth: true
disable_root: false
```
* `#cloud-config`는 클라우드 컴퓨팅 환경에서 가상 머신(VM) 또는 서버 인스턴스를 초기 설정할 때 사용되는 특수한 주석임
* `Cloud-init`이 이를 인식하고 실행

### 3-4. `vm01`을 위해 작성된 `user-data` 확인
```bash
cat /var/lib/libvirt/images/vm01/user-data

```

### 3-5. `vm02`을 위해 작성된 `vm01`의 `user-data`를 복사
```bash
cp /var/lib/libvirt/images/vm01/user-data /var/lib/libvirt/images/vm02/user-data

```

### 3-6. `vi` 텍스트 에디터를 사용하여 `user-data` 파일을 수정

```bash
vi /var/lib/libvirt/images/vm02/user-data

```

### 3-7. `vi` 에디터가 열리면 입력 모드 `i` 입력 후, 아래 YAML 코드 수정 및 저장하고 나오기 (`esc 키` -> :`wq`)
```yaml
#cloud-config
hostname: vm02
manage_etc_hosts: true
users:
  - name: ubuntu
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups:
      - users
      - admin
    shell: /bin/bash
    plain_text_passwd: "1111"
    lock_passwd: false
ssh_pwauth: true
disable_root: false
```
* `hostname`의 `vm01`을 `vm02`로 변경

### 3-8. 작성된 문서 확인
```bash
cat /var/lib/libvirt/images/vm02/user-data

```

### 3-9 VM 별 meta-data 파일 생성
- 각 VM에서 cloud-init이 인식할 수 있도록, VM 별로 고유한 `instance-id` 값을 가진 `meta-data` 파일을 생성
```bash
echo "instance-id: vm01" > /var/lib/libvirt/images/vm01/meta-data
echo "instance-id: vm02" > /var/lib/libvirt/images/vm02/meta-data

```

### 3-10. VM 별로 ISO 이미지를 생성
- cloud-init을 이용하여 VM의 초기 설정(user-data, meta-data)을 자동화하기 위해 VM 별로 ISO 이미지를 생성하여 CD-ROM 형태로 마운트
```bash
cd /var/lib/libvirt/images/
genisoimage -output vm01-init.iso -V cidata -r -J vm01/user-data vm01/meta-data
genisoimage -output vm02-init.iso -V cidata -r -J vm02/user-data vm02/meta-data

```
- `vm01-init.iso`: `vm01` VM에 사용할 cloud-init ISO 이미지의 이름
- `-V cidata`: ISO의 볼륨 이름을 `cidata`로 설정 (cloud-init의 NoCloud 방식에서 필수)
- `-r -J`: ISO 파일 시스템 호환성을 위한 옵션 (Rock Ridge와 Joliet)
- `vm01/user-data`, `vm01/meta-data`: ISO에 포함할 cloud-init 설정 파일들


### 3-11. 이미지 파일들의 위치 조정
```bash
cd ~
cp noble-server-cloudimg-amd64.img /var/lib/libvirt/images/noble-server-cloudimg-amd64-vm01.img
cp noble-server-cloudimg-amd64.img /var/lib/libvirt/images/noble-server-cloudimg-amd64-vm02.img

# 최초 부팅 전에 가상 디스크를 확장함. cloud-init이 첫 부팅 시 파티션/파일시스템을 확장함.
qemu-img resize /var/lib/libvirt/images/noble-server-cloudimg-amd64-vm01.img 8G
qemu-img resize /var/lib/libvirt/images/noble-server-cloudimg-amd64-vm02.img 8G

```

### 3-12. 복사한 이미지 파일들 확인
```bash
ls /var/lib/libvirt/images/
```
* 이미지/ISO 파일 4개와 `vm01`, `vm02` 디렉터리 2개가 확인되어야 함.


---



# 4. 가상 머신 정의 및 시작
* 가상 머신을 정의하고 시작하는 두 가지 방법이 있음
1) `virt-install`
2) `virsh define` & `virsh start `

### 4-1. `virt-install`를 통한 가상 머신 정의 및 시작
```bash
virt-install \
--name=vm01 \
--ram=512 \
--vcpus=2 \
--os-variant ubuntu24.04 \
--disk path=/var/lib/libvirt/images/noble-server-cloudimg-amd64-vm01.img,device=disk,bus=virtio \
--disk path=/var/lib/libvirt/images/vm01-init.iso,device=cdrom \
--network network=vir-network,model=virtio,mac=52:54:00:12:34:58 \
--noautoconsole \
--console pty \
--serial pty \
--boot hd \
--import

```

* Ubuntu 권장 메모리보다 적다는 경고가 나올 수 있음. 이 가이드는 2GB 외부 서버에서 기본 실습을 수행하도록 512MB로 제한한 설정이며, 메모리 부족으로 작업이 중단되면 실행 중인 clone을 종료하고 호스트 여유 메모리를 확인함.

### 4-2. 가상 머신 목록에서 `running` 상태인 `vm01` 가상 머신 확인
```bash
virsh list --all
```

### 4-3. 가상 머신 접속
```bash
virsh console vm01
```

### 4-4. 가상 머신 접속 후 계정/비번 입력하여 로그인
* login ID: ubuntu
* login PW: 1111
* 첫 부팅에는 시간이 걸림. 로그인 프롬프트가 보이지 않으면 잠시 기다린 뒤 Enter를 누름. `running`은 초기화 완료를 의미하지 않음.
* 로그인 후 **내부 VM**에서 아래 명령을 실행하여 `status: done`과 루트 디스크 확장을 확인한 뒤 진행함.
```bash
cloud-init status --wait
df -h /
```

### 4-5. 가상 머신에서 빠져나오기
* Escape character is `Ctrl + ]`

### 4-6. `vi` 텍스트 에디터를 사용하여 `vm02.xml` 파일을 생성
```bash
vi vm02.xml
```
* `vm02`의 정의를 위함

### 4-7. `vi` 에디터가 열리면 입력 모드 `i` 입력 후, 아래 XML 코드와 같이 입력 및 저장하고 나오기 (`esc 키` -> :`wq`)
```xml
<domain type='kvm'>
  <name>vm02</name>
  <memory unit='KiB'>524288</memory>
  <vcpu placement='static'>2</vcpu>
  <features>
    <acpi/>
    <apic/>
  </features>
  <os>
    <type arch='x86_64'>hvm</type>
    <boot dev='hd'/>
  </os>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='/var/lib/libvirt/images/noble-server-cloudimg-amd64-vm02.img'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='/var/lib/libvirt/images/vm02-init.iso'/>
      <target dev='hdc' bus='ide'/>
      <readonly/>
    </disk>
    <interface type='network'>
      <mac address='52:54:00:12:34:59'/>
      <source network='vir-network'/>
      <model type='virtio'/>
    </interface>
    <console type='pty'>
        <target port='0'/>
    </console>
    <serial type='pty'>
        <target port='0'/>
    </serial>
  </devices>
</domain>

```
* 가상 머신 이름: `vm02`
* Ubuntu 디스크 이미지: `/var/lib/libvirt/images/noble-server-cloudimg-amd64-vm02.img`로
* user-data를 위한 디스크 이미지: `/var/lib/libvirt/images/vm02-init.iso`
* 인터페이스의 mac 주소(mac 주소가 서로 달라야 가상머신 간에 통신 가능): `52:54:00:12:34:59`

### 4-8. 작성된 문서 확인
```bash
cat vm02.xml
```

### 4-9. 가상 머신 정의
```bash
virsh define vm02.xml
```

### 4-10. 가상 머신 목록에서 정의된(shut off 상태) 가상 머신 확인
```bash
virsh list --all
```

### 4-11. 가상 머신 시작
```bash
virsh start vm02
```

### 4-12. 가상 머신 목록에서 정의된(running 상태) 가상 머신 확인
```bash
virsh list --all
```

### 4-13. 가상 머신들 기본정보 출력
```bash
virsh dominfo vm01 && virsh dominfo vm02
```
* `hvm(Hardware Virtual Machine)`: 가상 머신(VM)이 하드웨어 가상화 기술(`Intel VT-x` 또는 `AMD-V`)을 사용하여 구동된다는 것을 의미

### 4-14. 가상 머신들에 할당된 IP 주소를 확인
```bash
virsh domifaddr vm01 && virsh domifaddr vm02
```
* VM에 할당된 IP는 환경에 따라 다를 수 있음. 출력이 비어 있으면 부팅 및 DHCP 할당을 기다린 뒤 다시 조회함

### 4-15. 가상 머신 접속
```bash
virsh console vm02
```

### 4-16. 가상 머신 접속 후 계정/비번 입력하여 로그인
* login ID: ubuntu
* login PW: 1111
* 첫 부팅에는 시간이 걸림. 로그인 프롬프트가 보이지 않으면 잠시 기다린 뒤 Enter를 누름. `running`은 초기화 완료를 의미하지 않음.
* 로그인 후 **내부 VM**에서 아래 명령을 실행하여 `status: done`과 루트 디스크 확장을 확인한 뒤 진행함.
```bash
cloud-init status --wait
df -h /
```

### 4-17. 가상 머신 간의 연결 상태를 테스트
```bash
ping -c 3 <vm-ip-address>
```
* `<vm-ip-address>`에 상대방 VM의 인터페이스에 할당되어 있는 IP 주소를 기입하여 명령어 실행
* VM에 할당된 IP는 환경에 따라 다를 수 있음. 출력이 비어 있으면 부팅 및 DHCP 할당을 기다린 뒤 다시 조회함
* 아래는 실행 결과
```bash
ubuntu@vm02:~$ ping  192.168.123.78
PING 192.168.123.78 (192.168.123.78) 56(84) bytes of data.
64 bytes from 192.168.123.78: icmp_seq=1 ttl=64 time=3.59 ms
64 bytes from 192.168.123.78: icmp_seq=2 ttl=64 time=0.807 ms
64 bytes from 192.168.123.78: icmp_seq=3 ttl=64 time=0.902 ms
64 bytes from 192.168.123.78: icmp_seq=4 ttl=64 time=0.589 ms
64 bytes from 192.168.123.78: icmp_seq=5 ttl=64 time=0.888 ms
64 bytes from 192.168.123.78: icmp_seq=6 ttl=64 time=1.06 ms
```

### 4-18. 가상 머신에서 빠져나오기
* Escape character is `Ctrl + ]`


---



# 5. 가상 머신 복제(clone)

### 5-1. 복제하려는 원본 가상 머신을 shutdown
```bash
virsh shutdown vm01
```
```bash
virsh list --all
```


* `shutdown`은 종료 요청임. `virsh domstate vm01`이 **`shut off`**가 될 때까지 확인한 다음 복제함.

### 5-2. 원본 가상 머신을 기반으로 clone 가상 머신 생성 (virt-clone 사용)
- `virt-clone` 명령어를 사용하면 기존 가상 머신(`vm01`)을 기반으로 빠르게 복제 가상 머신(`vm01-clone`)을 생성할 수 있음
- 복제본은 디스크 이미지도 함께 복사되며 원본 VM과 동일한 설정을 유지함.
```bash
virt-clone \
--original vm01 \
--name vm01-clone \
--file /var/lib/libvirt/images/noble-server-cloudimg-amd64-vm01-clone.img
```
- 원본 디스크를 새로운 디스크로 복사 후 복제가 완료되면 vm01-clone이 libvirt에 등록됨  
`Allocating 'noble-server-cloudimg-amd64-vm01-clone.img'                                          | 1.7 GB  00:00:14 ...`  
`Clone 'vm01-clone' created successfully.`


### 5-3. 복제 가상 머신의 초기화 데이터 준비 및 start
외부 서버에서 clone 전용 hostname/instance-id와 ISO를 준비함. 원본의 초기화 ISO를 그대로 사용하면 내부 이름이 `vm01`로 남음.
```bash
mkdir -p /var/lib/libvirt/images/vm01-clone
sed 's/^hostname: vm01$/hostname: vm01-clone/' /var/lib/libvirt/images/vm01/user-data > /var/lib/libvirt/images/vm01-clone/user-data
echo "instance-id: vm01-clone" > /var/lib/libvirt/images/vm01-clone/meta-data
genisoimage -output /var/lib/libvirt/images/vm01-clone-init.iso -V cidata -r -J /var/lib/libvirt/images/vm01-clone/user-data /var/lib/libvirt/images/vm01-clone/meta-data
CLONE_CDROM=$(LC_ALL=C virsh domblklist vm01-clone --details | awk '$2 == "cdrom" {print $3; exit}')
virsh change-media vm01-clone "$CLONE_CDROM" /var/lib/libvirt/images/vm01-clone-init.iso --config
```
이제 복제 VM을 시작함.
```bash
virsh start vm01-clone
```
```bash
virsh list --all
```


### 5-4. 복제 가상 머신에 접속
```bash
virsh console vm01-clone
```


* `ubuntu` / `1111`로 로그인한 뒤 아래 명령이 완료될 때까지 기다림.
```bash
cloud-init status --wait
```

### 5-5. machine id 재설정 및 reboot
- Ubuntu 시스템을 DHCP 서버로부터 “새로운 장비”처럼 인식받게 하기 위해 클라이언트 식별 정보를 초기화
```bash
sudo cloud-init clean --machine-id
sudo reboot

```


* 위 초기화 명령은 **clone 내부에서만** 실행함. 재부팅 중 콘솔이 끊기면 외부 서버에서 `virsh console vm01-clone`으로 다시 접속함.

### 5-6. clone된 가상 머신에서 ip address 확인
- id/pw 입력하여 로그인 후 초기화 완료와 복제 VM의 이름·식별자·IP를 확인함. hostname과 instance-id는 `vm01-clone`, machine-id와 MAC 주소는 원본과 달라야 함.
```bash
cloud-init status --wait
hostname
cat /var/lib/cloud/data/instance-id
cat /etc/machine-id
ip address

```

### 5-7. 가상 머신에서 빠져나오기
* 복제 직후 외부 서버의 `virsh domifaddr`에는 이전 DHCP 임대 주소가 잠시 함께 표시될 수 있음. 실제 사용 중인 주소는 바로 위의 **clone 내부 `ip address`** 결과로 확인함.
* Escape character is `Ctrl + ]`

### 5-8. 복제 VM 종료 후 원본 VM 재시작 — 외부 서버
2GB 외부 서버의 메모리를 아끼고 다음 실습에서 `vm01`을 사용하기 위해 아래 순서로 진행함.
```bash
virsh shutdown vm01-clone
virsh domstate vm01-clone
```
`shut off`가 된 것을 확인한 뒤 원본을 시작함.
```bash
virsh start vm01
virsh list --all
```
`vm01`, `vm02`는 running, `vm01-clone`은 shut off인 상태로 다음 장을 진행함.

---



# 6. 가상 머신의 블록(block)

### 6-1. 가상 머신의 블록 장치 목록을 나열
```bash
virsh domblklist vm02
```
* 아래와 같이 두개의 블록 디스크 확인 가능
```bash
 Target   Source
------------------------------------------------------------------------
 vda      /var/lib/libvirt/images/noble-server-cloudimg-amd64-vm02.img
 hdc      /var/lib/libvirt/images/vm02-init.iso
```
- `vda`: VirtIO 인터페이스로 연결된 Ubuntu 운영체제 디스크
- `hdc`: IDE CD-ROM 방식으로 연결된 cloud-init 설정용 ISO 파일

### 6-2. 가상 머신의 블록 장치에 대한 정보를 조회
```bash
virsh domblkinfo vm02 vda
```
* Capacity:       VM 입장에서의 논리적 전체 디스크 크기 (바이트 단위)
* Allocation:     이미지 파일에 실제 할당된 공간 (바이트 단위, 저장 방식에 따라 의미가 달라질 수 있음)
* Physical:       파일 기반 이미지에서는 이미지 파일의 논리적 크기 (바이트 단위). 희소 파일은 Allocation과 다를 수 있음

### 6-3. 가상 머신에서 블록 장치의 I/O 통계 정보 조회
```bash
virsh domblkstat vm01 vda
```
* rd_req (Read Requests):  `vda` 디스크에 대해 읽기 작업이 수행된 총 횟수
* rd_bytes (Read Bytes): 읽기 요청을 통해 읽은 총 데이터 크기 (바이트 단위)
* wr_req (Write Requests): `vda` 디스크에 대해 쓰기 작업이 수행된 총 횟수
* wr_bytes (Write Bytes): 쓰기 요청을 통해 쓴 총 데이터 크기 (바이트 단위)
* flush_operations: 디스크에 버퍼에 있던 데이터를 실제 디스크에 반영한(동기화한) 작업의 총 횟수
* rd_total_times (Total Time for Read Operations in nanoseconds): 모든 읽기 작업에 걸린 총 시간
* wr_total_times (Total Time for Write Operations in nanoseconds): 모든 쓰기 작업에 걸린 총 시간
* flush_total_times (Total Time for Flush Operations in nanoseconds): 모든 flush 작업(디스크 동기화)에 걸린 총 시간



---



# 7. 가상 머신의 일시 중단(suspend) 및 재개(resume) 

### 7-1. 가상 머신의 일시 중단(suspend)
```bash
virsh suspend vm02
```

### 7-2. 가상 머신 목록에서 일시정지된(paused 상태) 가상 머신 확인
```bash
virsh list
```
* suspend한 vm의 상태는 paused 상태로 변경되어 있음

### 7-3. 가상 머신의 재개(resume) 
```bash
virsh resume vm02
```
* resume한 vm의 상태는 running 상태로 변경되어 있음

### 7-4. 가상 머신 목록에서 가상 머신 상태 확인
```bash
virsh list
```
* suspend한 vm의 상태는 running 상태로 변경되어 있음


---



# 8. 가상 머신의 종료(shutdown, destroy)와 시작(start)

### 8-1. 가상 머신의 종료
* `destroy`: 전원을 갑자기 꺼버리는 것과 동일함 (VM이 먹통 됐을 때, 정상 종료가 안 될 때)
* `shutdown`: 가상 머신에게 정상적인 종료를 요청 (VM 안에서 서비스 종료, 디스크 정리 등 정상 종료 절차를 거쳐야 할 때)
```bash
virsh destroy vm02
```
  
### 8-2. 가상 머신 목록에서 종료된(shut off 상태) 가상 머신 확인
```bash
virsh list --all
```
* destroy한 vm의 상태는 shut off 상태로 변경되어 있음

### 8-3. 가상 머신의 시작
```bash
virsh start vm02
```

### 8-4. 가상 머신 목록에서 가상 머신 상태 확인
```bash
virsh list
```
* vm의 상태는 running 상태로 변경되어 있음


---


# 9. 가상 머신 상태 저장(save) 및 복원(restore) 실습

### 9-1. 작업할 VM 이름 확인
```bash
virsh list

```

### 9-2. VM 상태 저장
```bash
virsh save vm01 vm01.sav

```
```bash
ls

```
- vm01이 종료되고 현재 경로에 vm01.sav 파일로 현재 상태가 저장됨

### 9-3. 저장된 VM이 목록에서 없어짐을 확인
```bash
virsh list

```

### 9-4. 저장된 상태 복원 (restore)
- **주의**: 이 실습에서는 도메인 정의를 유지함. 정의만 `undefine`한 경우에도 save 파일과 디스크가 남아 있으면 복원될 수 있지만 임시 도메인(`Persistent: no`)이 될 수 있음. `undefine`과 디스크 삭제는 서로 다름.
```bash
virsh restore vm01.sav

```

### 9-5. 복원된 가상머신을 목록에서 확인
```bash
virsh list

```


---


# 10. 가상 머신의 스냅샷(Snapshot)
* 가상 머신의 현재 상태를 캡처하는 기술
* 가상 머신의 메모리 상태, 디스크 이미지 및 가상 머신의 상태 정보를 포함
* 가상 머신의 이전 상태를 저장하므로 가상 머신에서 오류가 발생한 경우 이전 상태로 복원할 수 있음
* 스냅샷은 가상 머신의 특정 시점에서 생성할 수 있음

### 10-1. 가상 머신의 스냅샷을 커멘드 라인으로 생성
```bash
virsh snapshot-create-as vm02 --name initial-version
```

### 10-2. 가상 머신의 스냅샷 목록 확인
```bash
virsh snapshot-list vm02
```

### 10-3. 가상 머신 내부에 파일을 생성
```bash
virsh console vm02
```
* vm02 가상머신에 접속
```bash
touch hello_vm02
```
* vm 가상 머신 내에 빈 파일 생성
* 추후에 스냅샷으로 복원할 경우 파일이 사라짐을 확인하기 위함
```bash
ls -l
```
* 생성된 파일 확인
  
### 10-4. 가상 머신에서 빠져나오기
* Escape character is `Ctrl + ]`

### 10-5. 가상 머신 `vm02`의 스냅샷 `initial-version`으로 되돌리기(revert)
```bash
virsh snapshot-revert vm02 initial-version
```

### 10-6. 가상 머신 내부에 파일 확인
```bash
virsh console vm02
```
* vm02 가상머신에 접속
```bash
ls -l
```
* 기존 hello_vm02 파일이 없음을 확인 (`initial-version`의 스냅샷으로 되돌아갔다는 의미임)
  
### 10-7. 가상 머신에서 빠져나오기
* Escape character is `Ctrl + ]`

### 10-8. 가상 머신 스냅샷 삭제
```bash
virsh snapshot-delete vm02 initial-version
```

### 10-9. 가상 머신 스냅샷 목록 확인
```bash
virsh snapshot-list vm02
```


---



# 11. 가상 머신의 네트워크 구성 확인하기

### 11-1. 현재 호스트에서 사용 가능한 가상 네트워크 목록을 출력
```bash
virsh net-list --all
```

### 11-2. 시스템의 네트워크 인터페이스 목록 확인
```bash
virsh iface-list
```
* 가상 환경에서 네트워크 구성과 트러블슈팅을 할 때 유용

### 11-3. 가상 머신의 네트워크 인터페이스 목록 출력
```bash
virsh domifaddr vm02
```
* 가상 인터페이스의 MAC 주소(2계층)와 IP 주소(3계층) 확인 가능

### 11-4. 가상 머신의 특정 네트워크 인터페이스에 대한 네트워크 I/O 통계 정보 출력
* 가상 머신의 인터페이스 사용량과 관련된 세부 정보를 확인할 때 사용
* 빌링, 네트워크 트래픽 분석, 성능 모니터링, 문제 해결 등에 유용
```bash
virsh domiflist vm02
VM_IFACE=$(LC_ALL=C virsh domiflist vm02 | awk '$2 == "network" {print $1; exit}')
virsh domifstat vm02 "$VM_IFACE"
```
* `vnet` 뒤의 번호는 시작·복원할 때 바뀔 수 있으므로 위에서 현재 인터페이스를 조회함.
* `rx_bytes`: 수신된 총 바이트 수 (수신한 총 데이터 양 (외부 -> VM))
* `rx_packets`: 수신된 총 패킷 수 (참고 통계용)
* `rx_errs`:수신 과정에서 발생한 에러의 수 (성능 진단용, 품질 문제 확인용)
* `rx_drop`: 드롭된 수신 패킷 수 (성능 진단용, 품질 문제 확인용)
* `tx_bytes`: 송신된 총 바이트 수 (송신한 총 데이터 양 (VM -> 외부))
* `tx_packets`: 송신된 총 패킷 수 (참고 통계용)
* `tx_errs`:송신 과정에서 발생한 에러의 수 (성능 진단용, 품질 문제 확인용)
* `tx_drop`: 드롭된 송신 패킷 수 (성능 진단용, 품질 문제 확인용)


---



# 12. 가상 머신에 간단한 웹서버 구동하기

### 12-1. 가상머신에 콘솔로 접속
```bash
virsh console vm01
```

### 12-2. Apache 웹 서버 설치
```bash
sudo apt update
```
* 패키지 매니저를 업데이트하여 최신 패키지 목록을 가져옴.
```bash
sudo apt install apache2 -y
```
* 아파치 웹 서버를 설치

### 12-3. 웹 페이지(index.html) 수정
```bash
sudo rm -f /var/www/html/index.html && sudo vi /var/www/html/index.html
```
* `/var/www/html/`: Linux 시스템에서 Apache 웹 서버의 기본 웹 컨텐츠 디렉토리
* `index.html`: 웹 디렉토리의 기본 문서
```bash
:set paste
```
* 외부에서 복사한 내용을 붙여넣을 때 포맷이 망가지지 않도록 설정

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎉 VM 아파치 서버 실습 성공! 🎉</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');

        body {
            font-family: 'Noto Sans KR', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            color: #333;
            text-align: center;
        }

        .container {
            background-color: #ffffff;
            padding: 40px 50px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            animation: fadeIn 1s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 20px;
            font-weight: 700;
        }

        p {
            font-size: 1.2em;
            line-height: 1.6;
            color: #555;
            margin-bottom: 15px;
        }

        .highlight {
            color: #e74c3c;
            font-weight: bold;
            font-size: 1.3em;
        }

        /* --- 가상화 애니메이션 스타일 시작 --- */
        .virtualization-scene {
            margin-top: 30px; /* 위쪽 문단과의 간격 */
            margin-bottom: 20px; /* 아래쪽 footer와의 간격 */
            padding: 20px;
            border-radius: 8px;
            background-color: #e9ecef; /* 배경색 살짝 추가 */
            position: relative; /* 내부 요소 배치 기준 */
        }

        .vm-container {
            display: flex; /* VM들을 가로로 배열 */
            justify-content: center; /* 가운데 정렬 */
            gap: 25px; /* VM 사이 간격 */
            margin-bottom: 10px; /* 하이퍼바이저와의 간격 */
            position: relative;
            z-index: 1; /* 하이퍼바이저보다 위에 오도록 */
        }

        .vm {
            font-size: 2.5em; /* VM 아이콘 크기 */
            animation-name: jump;
            animation-duration: 1s; /* 점프 애니메이션 속도 */
            animation-timing-function: ease-in-out;
            animation-iteration-count: infinite;
            position: relative; /* transform 적용 기준 */
        }

        /* 순서대로 점프하도록 애니메이션 지연 시간 설정 */
        .vm:nth-child(1) {
            animation-delay: 0s;
        }
        .vm:nth-child(2) {
            animation-delay: 0.2s; /* 두 번째 VM은 0.2초 뒤 시작 */
        }
        .vm:nth-child(3) {
            animation-delay: 0.4s; /* 세 번째 VM은 0.4초 뒤 시작 */
        }
        /* VM 개수가 더 많으면 nth-child(4), (5) ... 추가 */


        .hypervisor-layer {
            background-color: #adb5bd; /* 하이퍼바이저 색상 */
            color: white;
            padding: 8px 0;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: bold;
            text-align: center;
            width: 80%; /* 너비 조절 */
            margin: 0 auto; /* 가운데 정렬 */
            position: relative;
            z-index: 0;
        }

        /* 점프 애니메이션 정의 */
        @keyframes jump {
            0%, 100% {
                transform: translateY(0); /* 시작과 끝은 제자리 */
            }
            50% {
                transform: translateY(-25px); /* 중간에 위로 점프 (값 조절 가능) */
            }
        }
        /* --- 가상화 애니메이션 스타일 끝 --- */


        .footer {
            margin-top: 30px;
            font-size: 0.9em;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 실습 성공! 🚀</h1>
        <p>
            축하합니다! 여러분은 지금 <span class="highlight">자신이 직접 생성한 가상머신</span>에서
            동작하는 아파치 웹 서버에 접속했습니다!
        </p>
        <div class="virtualization-scene">
            <div class="vm-container">
                <div class="vm">🖥️</div>
                <div class="vm">🖥️</div>
                <div class="vm">🖥️</div>
                </div>
            <div class="hypervisor-layer">Hypervisor</div>
        </div>
    </div>
</body>
</html>
```
* 입력 모드로 전환 후, 위 내용을 작성
* 명령 모드로 전환 후, 저장하고 나오기 (:`wq`)
```bash
curl 127.0.0.1
```
* 현재 구동되고 있는 웹서버에 웹페이지 요청
* `index.html`의 내용이 응답으로 나타나는지 확인


### 12-4. 가상 머신에서 빠져나오기
* Escape character is `Ctrl + ]`


### 12-5. SSH 터널로 Windows에서 웹 서버에 접근
외부 서버 `vm*`의 IP는 사설 주소이므로, 해당 IP에 8080 포워딩만 설정해도 Windows에서 접근하지 못할 수 있음. 이 환경에서는 이미 접속에 사용하는 SSH 게이트웨이를 통해 내부 VM의 80번 포트로 터널을 연결함. 별도의 `iptables` 규칙은 필요하지 않음.

먼저 **외부 서버 root 셸**에서 `vm01`의 현재 IP를 확인함.
```bash
virsh domifaddr vm01
```
다음은 **Windows에서 새 PowerShell 창을 열어** 실행함. `44` 두 곳은 본인의 배정 번호로, `192.168.123.78`은 위에서 확인한 내부 VM IP로 변경함.
```powershell
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:18080:192.168.123.78:80 -p 2222 "student44:vm44@gate.su-cloud.syu.ac.kr"
```
개인별 SSH 비밀번호 입력 후 프롬프트가 돌아오지 않는 것은 터널이 유지되고 있는 정상 상태임. 이 창을 열어 둠. 포트 사용 중 오류가 나면 `18080`을 다른 빈 포트로 바꾸고 브라우저 주소도 함께 변경함.

### 12-6. Windows 웹브라우저에서 Apache 서버 접근
브라우저에서 `http://127.0.0.1:18080/`을 열어 실습 성공 화면을 확인함. VM이 실행 중이고 Apache가 동작 중이어야 함. 확인 후 터널 PowerShell 창에서 `Ctrl + C`로 종료함.


---



# 13. libvirt-python으로 가상 머신 생성

### 13-1. 기존 vm02을 destroy 및 undefine
```bash
virsh destroy vm02
```
```bash
virsh undefine vm02
```

### 13-2. 가상 머신 상태 확인
```bash
virsh list --all
```

### 13-3. `vi` 텍스트 에디터를 사용하여 `script.py` 파일을 생성
```bash
vi script.py
```

### 13-4. `vi` 에디터가 열리면 입력 모드 `i` 입력 후, 아래의 코드를 입력 및 저장하고 나오기 (`esc 키` -> :`wq`)
```python
import libvirt
import sys

if len(sys.argv) < 2:
    print("Usage: python3 script.py [create|list|suspend|resume|snapshot] [vm-name]")
    sys.exit(1)

action = sys.argv[1]
vm_name = sys.argv[2] if len(sys.argv) > 2 else 'vm02'
if action not in ('create', 'list', 'suspend', 'resume', 'snapshot'):
    sys.exit('Unknown action: ' + action)

# 외부 서버 root 셸에서 로컬 libvirt에 연결
uri = 'qemu:///system'
conn = None

try:
    conn = libvirt.open(uri)
    if action == "create":
        # 이 실습의 create는 /root/vm02.xml로 vm02를 다시 정의함
        if vm_name != 'vm02':
            sys.exit('create supports vm02 only in this example')
        with open("/root/vm02.xml", "r") as file:
            domain_xml = file.read()

        # 도메인을 정의하고 저장
        domain = conn.defineXML(domain_xml)
        if domain is None:
            print("Failed to define a domain.")
            sys.exit(1)

        # 도메인을 생성
        if domain.create() < 0:
            print("Cannot boot the domain.")
            sys.exit(1)
        print(f"Domain {domain.name()} created and started.")

    elif action == "list":
        # 종료된 VM을 포함한 모든 도메인을 조회
        print("Current VMs:")
        for vm in conn.listAllDomains():
            print(f"- {vm.name()}")
            state, maxmem, mem, cpus, cput = vm.info()
            print('The state is ' + str(state))
            print('The max memory is ' + str(maxmem))
            print('The memory is ' + str(mem))
            print('The number of cpus is ' + str(cpus))
            print('The cpu time is ' + str(cput))

    elif action == "suspend":
        vm = conn.lookupByName(vm_name)
        if vm.state()[0] != libvirt.VIR_DOMAIN_RUNNING:
            sys.exit(f'{vm_name} is not running')
        vm.suspend()
        print(f"Domain {vm_name} suspended.")

    elif action == "resume":
        vm = conn.lookupByName(vm_name)
        if vm.state()[0] != libvirt.VIR_DOMAIN_PAUSED:
            sys.exit(f'{vm_name} is not paused')
        vm.resume()
        print(f"Domain {vm_name} resumed.")

    elif action == "snapshot":
        # 지정한 도메인의 스냅샷 생성
        vm = conn.lookupByName(vm_name)
        if vm.state()[0] != libvirt.VIR_DOMAIN_RUNNING:
            sys.exit(f'{vm_name} is not running')
        if 'Snapshot1' in vm.snapshotListNames():
            sys.exit(f'{vm_name}: Snapshot1 already exists; choose or delete the old snapshot first')
        snap = vm.snapshotCreateXML("""
        <domainsnapshot>
            <name>Snapshot1</name>
            <description>An example snapshot</description>
        </domainsnapshot>
        """)
        if snap is None:
            print("Failed to create snapshot.")
            sys.exit(1)
        print(f"Snapshot created for domain {vm.name()}.")

except (libvirt.libvirtError, OSError) as error:
    print(f"Error: {error}", file=sys.stderr)
    sys.exit(1)
finally:
    if conn is not None:
        conn.close()

```

## 13-5. 파이썬 스크립트 실행을 통한 가상 머신 관리
* 파이썬 스크립트를 사용하여 다양한 가상 머신 관리 작업을 수행할 수 있음

* 가상 머신 생성
```bash
python3 script.py create
```

* 가상 머신 목록 조회
```bash
python3 script.py list
```

* 가상 머신 일시 정지
```bash
python3 script.py suspend vm02
```

* 가상 머신 재개
```bash
python3 script.py resume vm02
```

* 가상 머신 스냅샷 생성
```bash
python3 script.py snapshot vm02
```

* 가상 머신 스냅샷 목록 확인
```bash
virsh snapshot-list vm02
```


---

# 실습 종료 및 재실행 안내
Windows의 SSH 터널은 `Ctrl + C`로 종료함. **외부 서버 root 셸**에서 실행 중인 실습 VM만 정상 종료함.
```bash
virsh list --all
virsh shutdown vm01
virsh shutdown vm02
virsh list --all
```
`vm01-clone`이 실행 중이면 함께 종료함. 각 VM이 `shut off`가 될 때까지 확인함. 도메인 정의·디스크·스냅샷·초기화 ISO는 다시 살펴볼 수 있도록 보존함. 재부팅 후 실습을 이어갈 때는 네트워크 상태와 VM 시작 여부를 확인함.

처음부터 재실습하려면 본인이 만든 실습 자원만 확인한 뒤 정리해야 함. `virsh undefine`은 도메인 정의를 제거하며 디스크 자체는 별개임. 스냅샷이 있으면 먼저 확인·정리해야 함. 초기 설정을 바꾸어 다시 시험하려면 기존에 부팅한 디스크를 그대로 재사용하지 말고 원본 이미지에서 새 복사본을 준비함. 기존 데이터가 필요하면 삭제 전에 백업함.
