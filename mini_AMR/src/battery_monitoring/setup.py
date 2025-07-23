from setuptools import find_packages, setup

package_name = 'battery_monitoring'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        ('share/' + package_name + '/launch', ['launch/battery_diagnostics.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='palmzaawow',
    maintainer_email='palmrock4@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'battery_publisher = battery_monitoring.battery_state_publisher:main',
            'diagnostics_subscriber = battery_monitoring.diagnostics_subscriber:main',
            'fault_injector = battery_monitoring.fault_injector:main', 
        ],
    },
)
