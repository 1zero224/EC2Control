# EC2Control

<p align="center">
  <img src="assets/logo.png" alt="EC2 Control Logo" width="200"/>
</p>

<p align="center">
  <strong>A convenient tool for managing EC2 instance start/stop operations</strong>
</p>

<p align="center">
  <strong>English</strong> | <a href="./README.md">简体中文</a>
</p>

<p align="center">
  [![Build Status](https://github.com/1zero224/EC2Control/workflows/build/badge.svg)](https://github.com/1zero224/EC2Control/actions/workflows/build.yml)
  [![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
  [![Flet](https://img.shields.io/badge/Flet-0.23.0+-02569B?style=for-the-badge&logo=flutter&logoColor=white)](#)
  [![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](#)
  [![Boto3](https://img.shields.io/badge/Boto3-1.26.0+-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](#)
  [![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)
</p>


## Features

- View EC2 instances across all AWS regions
- One-click start, stop, and reboot instances
- Filter by region
- Pin instances to top
- Dark/Light theme toggle
- English/Chinese interface switch



## User Guide

### 1. Download the Application

Go to the [Releases](https://github.com/1zero224/EC2Control/releases) page and download the latest `EC2Manager.exe` file.

### 2. Install AWS CLI

Visit the [AWS CLI Official Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and follow the instructions.

**Verify installation:**
```bash
aws --version
```

### 3. Create IAM User and Configure Permissions

1. Log in to the [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Go to Policies panel, click "Create policy", select "Policy editor - JSON", and paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "EC2ReadPermissions",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeRegions",
                "ec2:DescribeTags",
                "ec2:GetConsoleScreenshot",
                "ec2:GetConsoleOutput"
            ],
            "Resource": "*"
        },
        {
            "Sid": "EC2WritePermissions",
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:RebootInstances"
            ],
            "Resource": "*"
        }
    ]
}
```

3. Go to Users panel, click "Create user", then in "Set permissions" page, click "Attach policies directly" and select the policy you just created
4. In the user details page, click "Security credentials", create an access key, select "Command Line Interface (CLI)" use case, and save the Access Key ID and Secret Access Key

### 4. Configure AWS Credentials

Use the `aws configure` command to set up credentials:

```bash
aws configure
```

Enter the following when prompted:

```
AWS Access Key ID [None]: Your Access Key ID
AWS Secret Access Key [None]: Your Secret Access Key
Default region name [None]: Default region (e.g., us-east-1, enter your most frequently used region)
Default output format [None]: json
```

### 5. Launch the Application

Double-click `EC2Manager.exe` to start using the application.

---

## Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python main.py
```

### Build Executable

```bash
flet pack main.py --name "EC2Control" --icon "assets/icon.ico" --product-name "EC2Control"
```

The executable will be generated in the `dist` directory.

> **Code Quality:** This project uses Ruff, Black, and isort for code quality checks. See `pyproject.toml` for configuration. CI runs checks automatically.

### Project Structure

```
aws_ec2_gui/
│
├── .github/                     # GitHub configuration
│   └── workflows/               # GitHub Actions workflows
│       ├── build.yml            # Build and code quality checks
│       └── release.yml          # Auto release
│
├── assets/                      # Static resources
│   ├── logo.png                 # Logo
│   └── icon.ico                 # Icon
│
├── src/                         # Source code
│   ├── config/                  # Configuration module
│   │   ├── __init__.py
│   │   ├── constants.py         # Constants
│   │   └── settings.py          # Settings management
│   │
│   ├── core/                    # Core business logic
│   │   ├── __init__.py
│   │   ├── ec2_service.py       # EC2 service wrapper
│   │   └── cache_manager.py     # Cache management
│   │
│   ├── ui/                      # User interface
│   │   ├── __init__.py
│   │   ├── app.py               # Main application UI
│   │   ├── components/          # UI components
│   │   │   ├── __init__.py
│   │   │   ├── toolbar.py       # Toolbar
│   │   │   ├── instance_table.py # Instance table
│   │   │   └── console.py       # Console output
│   │   └── themes/              # Theme system
│   │       ├── __init__.py
│   │       ├── i18n.py          # Internationalization
│   │       └── font_scale.py    # Font scaling
│   │
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   └── screen_utils.py      # Screen utilities
│   │
│   └── main.py                  # Application entry
│
├── main.py                      # Launch script
├── requirements.txt             # Project dependencies
├── pyproject.toml               # Project configuration
├── README.md                    # Chinese documentation
└── README_EN.md                 # English documentation
```



## Contributing

Feel free to send issue reports and submit pull requests — all contributions are appreciated.



## License

This project is open-sourced under the [MIT License](LICENSE).
