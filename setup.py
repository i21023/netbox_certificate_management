from setuptools import find_packages, setup

setup(
    name='netbox-certificate-management',
    version='0.1',
    description='A simple plugin for netbox to document certificates',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "cryptography>=43.0.0",
        "requests>=2.32.3",
        "django-mptt>=0.16.0"
    ]
)