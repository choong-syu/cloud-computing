from flask import Flask, render_template_string
import requests
import socket

app = Flask(__name__)

METADATA_BASE = "http://169.254.169.254/latest"


def get_imds_token():
    """
    AWS EC2 Instance Metadata Service v2 토큰 발급
    """
    try:
        response = requests.put(
            f"{METADATA_BASE}/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=1
        )
        if response.status_code == 200:
            return response.text
    except Exception:
        pass
    return None


def get_metadata(path, default="확인 불가"):
    """
    EC2 메타데이터 조회
    """
    token = get_imds_token()
    headers = {}

    if token:
        headers["X-aws-ec2-metadata-token"] = token

    try:
        response = requests.get(
            f"{METADATA_BASE}/meta-data/{path}",
            headers=headers,
            timeout=1
        )
        if response.status_code == 200:
            return response.text
    except Exception:
        pass

    return default


def get_local_ip_fallback():
    """
    메타데이터 조회 실패 시 OS 기준 내부 IP 확인
    """
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception:
        return "확인 불가"


@app.route("/")
def index():
    instance_id = get_metadata("instance-id")
    private_ip = get_metadata("local-ipv4", get_local_ip_fallback())
    public_ip = get_metadata("public-ipv4", "Public IP 없음 또는 확인 불가")
    az = get_metadata("placement/availability-zone")
    instance_type = get_metadata("instance-type")
    hostname = socket.gethostname()

    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>Cloud Computing VPC Network Test</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #e8f1ff, #f7fbff);
                color: #1f2937;
            }

            .container {
                max-width: 900px;
                margin: 60px auto;
                background: white;
                border-radius: 24px;
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
                padding: 40px;
            }

            .badge {
                display: inline-block;
                background: #2563eb;
                color: white;
                padding: 8px 16px;
                border-radius: 999px;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 16px;
            }

            h1 {
                margin: 0;
                font-size: 34px;
                color: #0f172a;
            }

            .subtitle {
                margin-top: 12px;
                font-size: 18px;
                line-height: 1.6;
                color: #475569;
            }

            .network-box {
                margin-top: 32px;
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
            }

            .card {
                border: 1px solid #dbeafe;
                background: #f8fbff;
                border-radius: 18px;
                padding: 24px;
            }

            .card-title {
                font-size: 15px;
                color: #64748b;
                margin-bottom: 8px;
            }

            .card-value {
                font-size: 24px;
                font-weight: bold;
                color: #1d4ed8;
                word-break: break-all;
            }

            .notice {
                margin-top: 32px;
                padding: 20px;
                background: #ecfdf5;
                border: 1px solid #bbf7d0;
                border-radius: 16px;
                color: #166534;
                line-height: 1.7;
            }

            .flow {
                margin-top: 30px;
                padding: 20px;
                border-radius: 16px;
                background: #f1f5f9;
                font-size: 16px;
                text-align: center;
                color: #334155;
            }

            .footer {
                margin-top: 30px;
                font-size: 14px;
                color: #64748b;
                text-align: center;
            }

            @media (max-width: 700px) {
                .network-box {
                    grid-template-columns: 1fr;
                }

                .container {
                    margin: 20px;
                    padding: 28px;
                }

                h1 {
                    font-size: 28px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="badge">Cloud Computing Lab</div>

            <h1>VPC 네트워크 테스트 웹 서버</h1>

            <p class="subtitle">
                이 화면은 클라우드컴퓨팅 수업 실습을 통해 생성한 
                <strong>Public Subnet의 가상머신</strong>에서 제공되는 웹 페이지입니다.<br>
                학생들은 이 화면을 통해 현재 웹 브라우저가 클라우드 환경의 EC2 웹 서버에 접속했음을 확인할 수 있습니다.
            </p>

            <div class="network-box">
                <div class="card">
                    <div class="card-title">Private IP</div>
                    <div class="card-value">{{ private_ip }}</div>
                </div>

                <div class="card">
                    <div class="card-title">Public IP</div>
                    <div class="card-value">{{ public_ip }}</div>
                </div>

                <div class="card">
                    <div class="card-title">Instance ID</div>
                    <div class="card-value">{{ instance_id }}</div>
                </div>

                <div class="card">
                    <div class="card-title">Availability Zone</div>
                    <div class="card-value">{{ az }}</div>
                </div>

                <div class="card">
                    <div class="card-title">Instance Type</div>
                    <div class="card-value">{{ instance_type }}</div>
                </div>

                <div class="card">
                    <div class="card-title">Hostname</div>
                    <div class="card-value">{{ hostname }}</div>
                </div>
            </div>

            <div class="flow">
                사용자 브라우저 → Internet → Internet Gateway → Public Subnet → Public VM 웹 서버
            </div>

            <div class="notice">
                <strong>실습 의미</strong><br>
                이 웹 페이지가 보인다는 것은 Public Subnet의 라우팅 테이블에 
                <strong>0.0.0.0/0 → Internet Gateway</strong> 경로가 설정되어 있고, 
                보안 그룹 또는 NACL에서 HTTP 트래픽이 허용되어 있다는 의미입니다.
            </div>

            <div class="footer">
                Sahmyook University · Cloud Computing · VPC Network Test
            </div>
        </div>
    </body>
    </html>
    """

    return render_template_string(
        html,
        private_ip=private_ip,
        public_ip=public_ip,
        instance_id=instance_id,
        az=az,
        instance_type=instance_type,
        hostname=hostname
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
