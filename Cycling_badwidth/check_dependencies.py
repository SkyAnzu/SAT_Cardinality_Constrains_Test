"""
Script kiểm tra và cài đặt các thư viện cần thiết cho CBP solver
"""

import sys
import subprocess

def install_package(package_name):
    """Cài đặt package qua pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Kiểm tra và cài đặt các thư viện cần thiết"""
    dependencies = {
        'numpy': 'numpy',
        'scipy': 'scipy', 
        'python-sat': 'python-sat[pblib,aiger]'
    }
    
    missing_packages = []
    
    for package_name, pip_name in dependencies.items():
        try:
            if package_name == 'python-sat':
                import pysat
            else:
                __import__(package_name)
            print(f"✅ {package_name} đã được cài đặt")
        except ImportError:
            print(f"❌ {package_name} chưa được cài đặt")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\nCần cài đặt: {missing_packages}")
        response = input("Có muốn cài đặt tự động không? (y/n): ")
        
        if response.lower() == 'y':
            for package in missing_packages:
                print(f"Đang cài đặt {package}...")
                if install_package(package):
                    print(f"✅ Đã cài đặt {package}")
                else:
                    print(f"❌ Lỗi khi cài đặt {package}")
        else:
            print("Vui lòng cài đặt thủ công:")
            for package in missing_packages:
                print(f"  pip install {package}")
    else:
        print("\n🎉 Tất cả thư viện đã sẵn sàng!")

if __name__ == "__main__":
    check_and_install_dependencies()
