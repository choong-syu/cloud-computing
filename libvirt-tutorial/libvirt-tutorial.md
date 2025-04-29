# Libvirt 실습 가이드

본 문서는 클라우드컴퓨팅 수업의 libvirt 튜토리얼에 대한 실습 가이드임.

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
```

### 1-3. 현재 경로에서 다운로드된 img 파일 확인
```bash
ls -l
```

### 1-4. 실습에 필요한 라이브러리 일괄 설치
```bash
apt update && apt install -y libvirt-clients libvirt-daemon-system virtinst cloud-image-utils python3-libvirt guestfs-tools qemu-utils

```

### 1-5. 다운로드한 img 파일의 포멧 확인
```bash
qemu-img info noble-server-cloudimg-amd64.img
```


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

### 3-6. `vi` 텍스트 에디터를 사용하여 `user-data2` 파일을 수정

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

```

### 3-12. 복사한 이미지 파일들 확인
```bash
ls /var/lib/libvirt/images/
```
* 총 4개의 파일이 확인되어야 함.


---



# 4. 가상 머신 정의 및 시작
* 가상 머신을 정의하고 시작하는 두 가지 방법이 있음
1) `virt-install`
2) `virsh define` & `virsh start `

### 4-1. `virt-install`를 통한 가상 머신 정의 및 시작
```bash
virt-install \
--name=vm01 \
--ram=2048 \
--vcpus=2 \
--os-variant detect=on,name=generic \
--disk path=/var/lib/libvirt/images/noble-server-cloudimg-amd64-vm01.img,device=disk,bus=virtio \
--disk path=/var/lib/libvirt/images/vm01-init.iso,device=cdrom \
--network network=vir-network,model=virtio,mac=52:54:00:12:34:58 \
--noautoconsole \
--console pty \
--serial pty \
--boot hd \
--import

```

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
  <memory unit='KiB'>2097152</memory>
  <vcpu placement='static'>2</vcpu>
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
* user-data를 위한 디스크 이미지: `/var/lib/libvirt/images/vm02-init.qcow2`
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
* VM에 할당된 IP는 환경에 따라 다를 수 있음

### 4-15. 가상 머신 접속
```bash
virsh console vm02
```

### 4-16. 가상 머신 접속 후 계정/비번 입력하여 로그인
* login ID: ubuntu
* login PW: 1111

### 4-17. 가상 머신 간의 연결 상태를 테스트
```bash
ping <vm-ip-address>
```
* `<vm-ip-address>`에 상대방 VM의 인터페이스에 할당되어 있는 IP 주소를 기입하여 명령어 실행
* VM에 할당된 IP는 환경에 따라 다를 수 있음
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


### 5-3. 복제 가상 머신을 start
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


### 5-5. machine id 재설정 및 reboot
- Ubuntu 시스템을 DHCP 서버로부터 “새로운 장비”처럼 인식받게 하기 위해 클라이언트 식별 정보를 초기화
```bash
sudo cloud-init clean
sudo rm -f /etc/machine-id
sudo systemd-machine-id-setup
sudo reboot

```


### 5-6. clone된 가상 머신에서 ip address 확인
- id/pw 입력하여 로그인 후 아래 입력하여 ip 주소 확인
```bash
ip address

```

### 5-7. 가상 머신에서 빠져나오기
* Escape character is `Ctrl + ]`

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
* Allocation:     OS 기준으로 현재 파일 시스템 상에서 할당된 데이터 크기
* Physical:       호스트 디스크에서 실제로 물리적 블록으로 사용된 크기

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



# 7. 가상 머신의 일시 중단(suspend) 및 재게(resume) 

### 7-1. 가상 머신의 일시 중단(suspend)
```bash
virsh suspend vm02
```

### 7-2. 가상 머신 목록에서 일시정지된(paused 상태) 가상 머신 확인
```bash
virsh list
```
* suspend한 vm의 상태는 paused 상태로 변경되어 있음

### 7-3. 가상 머신의 재게(resume) 
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



# 8. 가상 머신의 종료(shutdown, destory)와 시작(start)

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
- **주의**: restore 전에 save된 vm을 undefine 하면 도메인 정보가 없어지므로 virsh restore는 실패됨
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
virsh domifstat vm02 vnet3
```
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


### 12-5. 윈도우에서 가상머신까지 접근할 수 있도록 네트워크 환경 구성
* 하이퍼바이저 역할을 수행하는 우분투에서 아래와 같은 명령어 필요
```bash
iptables -t nat -I PREROUTING -d [우분투의 IP] -p tcp --dport 8080 -j DNAT --to-destination [Apache 서버가 구동중인 가상머신의 IP]:80
```
* NAT (Network Address Translation) 테이블을 수정하겠다는 의미임
* 외부에서 우분투 서버의 특정 포트(8080)로 들어오는 TCP 트래픽을 가상 머신에서 구동 중인 아파치 서버의 80번 포트로 전달
```bash
iptables -t filter -I FORWARD -p tcp -d [Apache 서버가 구동중인 가상머신의 IP] --dport 80 -j ACCEPT
```
* NAT 규칙에 의해 변경된 목적지 주소 (가상 머신의 IP)로 가는 트래픽을 허용함의 의미

### 12-5. 네트워크 자동화 구성 스크립트 생성
```bash
vi network.sh
```
* 아래 bash 스크립트를 복사하여 vi에 붙여넣기
```bash
#!/bin/bash

# 0. 인자로 받은 VM 이름 사용 (기본값: vm01)
VM_NAME=${1:-vm01}
echo "[1] VM 이름: $VM_NAME"

# 2. VM의 MAC 주소 추출
VM_MAC=$(virsh domiflist "$VM_NAME" | awk '/vnet/ {print $5}')
if [ -z "$VM_MAC" ]; then
  echo "MAC 주소를 찾을 수 없습니다. VM 이름을 확인하세요."
  exit 1
fi
echo "[2] VM MAC 주소: $VM_MAC"

# 3. 연결된 libvirt 네트워크 이름 추출
NETWORK_NAME=$(virsh domiflist "$VM_NAME" | awk '/vnet/ {print $3}')
if [ -z "$NETWORK_NAME" ]; then
  echo "VM의 네트워크 이름을 찾을 수 없습니다."
  exit 1
fi
echo "[3] libvirt 네트워크 이름: $NETWORK_NAME"

# 4. virsh net-info 로 브리지 이름 추출
BRIDGE_NAME=$(virsh net-info "$NETWORK_NAME" | awk '/Bridge:/ {print $2}')
if [ -z "$BRIDGE_NAME" ]; then
  echo "브리지 이름을 찾을 수 없습니다. net-info 실패."
  exit 1
fi
echo "[4] 브리지 이름: $BRIDGE_NAME"

# 5. virsh domifaddr 결과에서 IP 주소 추출 (정규 파싱)
VM_IP=$(virsh domifaddr "$VM_NAME" | awk '/vnet/ && /ipv4/ {print $4}' | cut -d/ -f1)
if [ -z "$VM_IP" ]; then
  echo "VM의 IP 주소를 찾을 수 없습니다. IP가 아직 할당되지 않았거나 VM이 비활성 상태일 수 있습니다."
  exit 1
fi
echo "[5] VM IP 주소: $VM_IP"

# 6. Ubuntu 호스트의 외부 인터페이스 및 IP 확인
HOST_IFACE=$(ip route | grep default | awk '{print $5}')
HOST_IP=$(ip addr show "$HOST_IFACE" | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
if [ -z "$HOST_IP" ]; then
  echo "호스트 IP를 찾을 수 없습니다. 인터페이스: $HOST_IFACE"
  exit 1
fi
echo "[6] 호스트 인터페이스: $HOST_IFACE"
echo "[7] 호스트 IP 주소: $HOST_IP"

# 7. iptables 포워딩 규칙 (PREROUTING)
PREROUTING_CMD="iptables -t nat -I PREROUTING -d $HOST_IP -p tcp --dport 8080 -j DNAT --to-destination $VM_IP:80"
echo "[8] 실행: $PREROUTING_CMD"
sudo $PREROUTING_CMD

# 8. iptables 포워딩 허용 규칙 (FORWARD)
FORWARD_CMD="iptables -t filter -I FORWARD -p tcp -d $VM_IP --dport 80 -j ACCEPT"
echo "[9] 실행: $FORWARD_CMD"
sudo $FORWARD_CMD

# 9. 참고: 삭제 명령어 안내 (표시만)
echo
echo "[참고] 아래 명령으로 해당 iptables 규칙을 삭제할 수 있습니다:"
echo "sudo iptables -t nat -D PREROUTING -d $HOST_IP -p tcp --dport 8080 -j DNAT --to-destination $VM_IP:80"
echo "sudo iptables -t filter -D FORWARD -p tcp -d $VM_IP --dport 80 -j ACCEPT"
echo

# 10. 접속 안내
echo "[접속 안내] 웹브라우저에서 다음 주소로 접속해 웹페이지를 확인할 수 있습니다:"
echo "http://$HOST_IP:8080"


```
* 스크립트 실행
```bash
bash network.sh
```

### 12-6. 윈도우의 웹브라우저에서 아파치 서버 접근하기
* 윈도우 웹브라우저에서 `[우분투의 IP]:8080` 주소로 접근


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
    print("Usage: python3 vm_manager.py [create|list|suspend|resume|snapshot]")
    sys.exit(1)

action = sys.argv[1]

# 연결할 libvirt URI를 설정
username = 'test'
ip = '127.0.0.1'
uri = f'qemu+ssh://{username}@{ip}/system'
conn = libvirt.open(uri)

if conn is None:
    print("Failed to open connection to the hypervisor")
    sys.exit(1)

try:
    if action == "create":
        # 생성할 도메인의 XML 정의를 파일에서 불러오기
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
        # 모든 도메인을 조회
        vms = conn.listDomainsID()
        print("Current VMs:")
        for vm_id in vms:
            vm = conn.lookupByID(vm_id)
            print(f"- {vm.name()}")
            state, maxmem, mem, cpus, cput = vm.info()
            print('The state is ' + str(state))
            print('The max memory is ' + str(maxmem))
            print('The memory is ' + str(mem))
            print('The number of cpus is ' + str(cpus))
            print('The cpu time is ' + str(cput))

    elif action == "suspend":
        # 모든 도메인을 일시 정지
        vms = conn.listDomainsID()
        for vm_id in vms:
            vm = conn.lookupByID(vm_id)
            vm.suspend()
        print("All running domains have been suspended.")

    elif action == "resume":
        # 모든 도메인을 재개
        vms = conn.listDomainsID()
        for vm_id in vms:
            vm = conn.lookupByID(vm_id)
            if vm.info()[0] == 3:  # 3: Paused
                vm.resume()
        print("All paused domains have been resumed.")

    elif action == "snapshot":
        # 첫 번째 도메인에 대해 스냅샷 생성
        vm_id = conn.listDomainsID()[0]
        vm = conn.lookupByID(vm_id)
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

finally:
    # 연결 종료
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
python3 script.py suspend
```

* 가상 머신 재개
```bash
python3 script.py resume
```

* 가상 머신 스냅샷 생성
```bash
python3 script.py snapshot
```

* 가상 머신 스냅샷 생성
```bash
virsh snapshot-list <vm명>
```
